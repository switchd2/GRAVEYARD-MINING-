from typing import Any

from logging_config import get_logger
from schemas.schemas import AnalyzeRequest
from services.ai_service import AIService
from services.clustering import cluster_diagnoses
from services.github_service import GitHubService
from services.report_service import ReportService
from services.security_service import SecurityService
from sqlalchemy.orm import Session

logger = get_logger("AnalysisService")

class AnalysisService:
    def __init__(
        self,
        github_service: GitHubService = None,
        ai_service: AIService = None,
        security_service: SecurityService = None,
        report_service: ReportService = None
    ):
        self.github = github_service or GitHubService()
        self.ai = ai_service or AIService()
        self.security = security_service or SecurityService()
        self.report = report_service or ReportService()

    async def run(self, req: AnalyzeRequest, db: Session) -> dict[str, Any]:
        """
        Main orchestration pipeline for Graveyard Mining.
        Identical signature and behavior, modularized for background workers.
        """
        logger.info(f"Starting analysis for project: {req.project_name}")

        # 1. Save initial ProjectAnalysis record
        project = self.report.save_project(db, req)

        # 2. Search GitHub for similar dead repos
        keywords = req.project_name
        search_results = await self.github.search_repositories(keywords, req.tech_stack, max_results=6)

        repo_diagnoses_data = []

        for item in search_results:
            owner = item.get("owner", {}).get("login", "")
            repo_name = item.get("name", "")
            full_name = item.get("full_name", f"{owner}/{repo_name}")
            description = item.get("description", "") or ""

            # Fetch extra details (README, commit date, issues)
            details = await self.github.fetch_repo_details(owner, repo_name)
            last_commit_date = details.get("last_commit_date")

            # Abandonment Score
            abandonment_score = self.github.calculate_abandonment_score(item, last_commit_date)

            # Web Context (Tavily)
            web_context = await self.github.search_failure_context(repo_name, ", ".join(req.tech_stack))

            # LLM Diagnosis
            diag_dict = await self.ai.diagnose_repository_failure(
                repo_name=repo_name,
                description=description,
                readme_excerpt=details.get("readme", ""),
                issues=details.get("recent_issues", []),
                abandonment_score=abandonment_score,
                tavily_context=web_context
            )

            # Embedding
            emb = await self.ai.generate_embedding(f"{diag_dict.get('root_cause')} {diag_dict.get('summary')}")

            # Save Repository & Diagnosis records
            repo_db = self.report.save_repository(
                db=db,
                analysis_id=project.id,
                item=item,
                details=details,
                abandonment_score=abandonment_score,
                diag_dict=diag_dict,
                web_context=web_context,
                embedding=emb
            )

            repo_diagnoses_data.append({
                "repo_name": full_name,
                "diagnosis": {**diag_dict, "embedding": emb}
            })

        # 3. Cluster Diagnoses
        clusters_data = await cluster_diagnoses(repo_diagnoses_data, self.ai)
        self.report.save_clusters(db, project.id, clusters_data)

        # 4. Dependency Health Check
        dep_reports = await self.security.analyze_dependencies(req.tech_stack)
        self.report.save_dependencies(db, project.id, dep_reports)

        # 5. Roadmap Generation & Risk Injection
        raw_roadmap = await self.ai.generate_roadmap(req.project_name, req.description, req.tech_stack)
        annotated_phases = self.security.inject_risk_annotations(raw_roadmap, clusters_data, dep_reports)
        self.report.save_roadmap(db, project.id, annotated_phases)

        logger.info(f"Completed analysis {project.id} for project: {req.project_name}")
        return self.report.serialize_analysis(project)
