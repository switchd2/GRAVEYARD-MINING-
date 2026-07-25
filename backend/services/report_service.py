from typing import Any

from models.models import (
    DependencyReport,
    Diagnosis,
    FailureCluster,
    ProjectAnalysis,
    Repository,
    Roadmap,
)
from schemas.schemas import AnalyzeRequest
from sqlalchemy.orm import Session


class ReportService:
    def save_project(self, db: Session, req: AnalyzeRequest) -> ProjectAnalysis:
        project = ProjectAnalysis(
            project_name=req.project_name,
            description=req.description,
            tech_stack=req.tech_stack
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    def save_repository(
        self,
        db: Session,
        analysis_id: int,
        item: dict[str, Any],
        details: dict[str, Any],
        abandonment_score: float,
        diag_dict: dict[str, Any],
        web_context: str,
        embedding: list[float]
    ) -> Repository:
        owner = item.get("owner", {}).get("login", "")
        repo_name = item.get("name", "")
        full_name = item.get("full_name", f"{owner}/{repo_name}")
        html_url = item.get("html_url", "")
        description = item.get("description", "") or ""
        stars = item.get("stargazers_count", 0)
        forks = item.get("forks_count", 0)
        open_issues = item.get("open_issues_count", 0)
        language = item.get("language", "")
        last_commit_date = details.get("last_commit_date")

        repo_db = Repository(
            analysis_id=analysis_id,
            name=repo_name,
            full_name=full_name,
            html_url=html_url,
            description=description,
            stars=stars,
            forks=forks,
            open_issues=open_issues,
            last_commit_date=last_commit_date,
            abandonment_score=abandonment_score,
            is_abandoned=1 if abandonment_score > 40 else 0,
            language=language,
            raw_metadata=item
        )
        db.add(repo_db)
        db.commit()
        db.refresh(repo_db)

        diag_db = Diagnosis(
            repository_id=repo_db.id,
            root_cause=diag_dict.get("root_cause", ""),
            failure_category=diag_dict.get("failure_category", ""),
            technical_debt_level=diag_dict.get("technical_debt_level", "High"),
            summary=diag_dict.get("summary", ""),
            key_takeaways=diag_dict.get("key_takeaways", []),
            tavily_context=web_context,
            embedding=embedding
        )
        db.add(diag_db)
        db.commit()

        return repo_db

    def save_clusters(self, db: Session, analysis_id: int, clusters: list[dict[str, Any]]) -> None:
        for c in clusters:
            cluster_db = FailureCluster(
                analysis_id=analysis_id,
                cluster_name=c.get("cluster_name"),
                description=c.get("description"),
                repo_count=c.get("repo_count", 0),
                risk_level=c.get("risk_level", "HIGH"),
                affected_repos=c.get("affected_repos", [])
            )
            db.add(cluster_db)
        db.commit()

    def save_dependencies(self, db: Session, analysis_id: int, reports: list[dict[str, Any]]) -> None:
        for d in reports:
            dep_db = DependencyReport(
                analysis_id=analysis_id,
                package_name=d.get("package_name"),
                ecosystem=d.get("ecosystem"),
                vulnerability_count=d.get("vulnerability_count", 0),
                maintenance_score=d.get("maintenance_score", 1.0),
                supply_chain_risk=d.get("supply_chain_risk", "LOW"),
                snyk_findings=d.get("snyk_findings"),
                details=d.get("details")
            )
            db.add(dep_db)
        db.commit()

    def save_roadmap(self, db: Session, analysis_id: int, phases: list[dict[str, Any]]) -> None:
        roadmap_db = Roadmap(
            analysis_id=analysis_id,
            phases_json={"phases": phases}
        )
        db.add(roadmap_db)
        db.commit()

    def serialize_analysis(self, project: ProjectAnalysis) -> dict[str, Any]:
        return {
            "id": project.id,
            "project_name": project.project_name,
            "description": project.description,
            "tech_stack": project.tech_stack,
            "created_at": project.created_at.isoformat(),
            "repositories": [
                {
                    "id": r.id,
                    "name": r.name,
                    "full_name": r.full_name,
                    "html_url": r.html_url,
                    "description": r.description,
                    "stars": r.stars,
                    "forks": r.forks,
                    "open_issues": r.open_issues,
                    "last_commit_date": r.last_commit_date,
                    "abandonment_score": r.abandonment_score,
                    "is_abandoned": bool(r.is_abandoned),
                    "language": r.language,
                    "diagnosis": {
                        "root_cause": r.diagnosis.root_cause,
                        "failure_category": r.diagnosis.failure_category,
                        "technical_debt_level": r.diagnosis.technical_debt_level,
                        "summary": r.diagnosis.summary,
                        "key_takeaways": r.diagnosis.key_takeaways,
                        "tavily_context": r.diagnosis.tavily_context
                    } if r.diagnosis else None
                } for r in project.repositories
            ],
            "dependency_reports": [
                {
                    "id": dr.id,
                    "package_name": dr.package_name,
                    "ecosystem": dr.ecosystem,
                    "vulnerability_count": dr.vulnerability_count,
                    "maintenance_score": dr.maintenance_score,
                    "supply_chain_risk": dr.supply_chain_risk,
                    "snyk_findings": dr.snyk_findings,
                    "details": dr.details
                } for dr in project.dependency_reports
            ],
            "failure_clusters": [
                {
                    "id": fc.id,
                    "cluster_name": fc.cluster_name,
                    "description": fc.description,
                    "repo_count": fc.repo_count,
                    "risk_level": fc.risk_level,
                    "affected_repos": fc.affected_repos
                } for fc in project.failure_clusters
            ],
            "roadmap": {
                "id": project.roadmap.id if project.roadmap else None,
                "phases": project.roadmap.phases_json.get("phases", []) if project.roadmap else []
            }
        }
