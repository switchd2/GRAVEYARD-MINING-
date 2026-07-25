import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from database import get_db
from models.models import ProjectAnalysis, Repository, Diagnosis, DependencyReport, FailureCluster, Roadmap
from schemas.schemas import AnalyzeRequest, AnalysisResponseSchema

from services.github_service import search_repositories, fetch_repo_details
from services.repo_triage import calculate_abandonment_score
from services.tavily_service import search_failure_context
from services.analyzer import diagnose_repository_failure
from services.embeddings import generate_embedding
from services.clustering import cluster_diagnoses
from services.dependency_checker import analyze_dependencies
from services.roadmap_generator import generate_project_roadmap
from services.risk_engine import inject_risk_annotations

router = APIRouter(prefix="/api", tags=["analysis"])

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_project(req: AnalyzeRequest, db: Session = Depends(get_db)):
    """
    Main orchestration endpoint for Graveyard Mining.
    Executes discovery, triage, diagnosis, embedding, clustering, security audit, roadmap generation, and risk injection.
    """
    # 1. Save ProjectAnalysis record
    project = ProjectAnalysis(
        project_name=req.project_name,
        description=req.description,
        tech_stack=req.tech_stack
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # 2. Search GitHub for similar dead repos
    keywords = req.project_name
    search_results = await search_repositories(keywords, req.tech_stack, max_results=6)
    
    repo_diagnoses_data = []
    repositories_to_db = []

    for item in search_results:
        owner = item.get("owner", {}).get("login", "")
        repo_name = item.get("name", "")
        full_name = item.get("full_name", f"{owner}/{repo_name}")
        html_url = item.get("html_url", "")
        description = item.get("description", "") or ""
        stars = item.get("stargazers_count", 0)
        forks = item.get("forks_count", 0)
        open_issues = item.get("open_issues_count", 0)
        language = item.get("language", "")

        # Fetch extra details (README, commit date, issues)
        details = await fetch_repo_details(owner, repo_name)
        last_commit_date = details.get("last_commit_date")

        # Abandonment Score
        abandonment_score = calculate_abandonment_score(item, last_commit_date)

        # Web Context (Tavily)
        web_context = await search_failure_context(repo_name, ", ".join(req.tech_stack))

        # LLM Diagnosis
        diag_dict = await diagnose_repository_failure(
            repo_name=repo_name,
            description=description,
            readme_excerpt=details.get("readme", ""),
            issues=details.get("recent_issues", []),
            abandonment_score=abandonment_score,
            tavily_context=web_context
        )

        # Embedding
        emb = await generate_embedding(f"{diag_dict.get('root_cause')} {diag_dict.get('summary')}")
        diag_dict["embedding"] = emb

        # Create DB entities
        repo_db = Repository(
            analysis_id=project.id,
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
            embedding=emb
        )
        db.add(diag_db)
        db.commit()

        repo_diagnoses_data.append({
            "repo_name": full_name,
            "diagnosis": diag_dict
        })
        repositories_to_db.append(repo_db)

    # 3. Cluster Diagnoses
    clusters_data = await cluster_diagnoses(repo_diagnoses_data)
    for c in clusters_data:
        cluster_db = FailureCluster(
            analysis_id=project.id,
            cluster_name=c.get("cluster_name"),
            description=c.get("description"),
            repo_count=c.get("repo_count", 0),
            risk_level=c.get("risk_level", "HIGH"),
            affected_repos=c.get("affected_repos", [])
        )
        db.add(cluster_db)
    db.commit()

    # 4. Dependency Health Check
    dep_reports = await analyze_dependencies(req.tech_stack)
    for d in dep_reports:
        dep_db = DependencyReport(
            analysis_id=project.id,
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

    # 5. Roadmap Generation & Risk Injection
    raw_roadmap = await generate_project_roadmap(req.project_name, req.description, req.tech_stack)
    annotated_phases = inject_risk_annotations(raw_roadmap, clusters_data, dep_reports)

    roadmap_db = Roadmap(
        analysis_id=project.id,
        phases_json={"phases": annotated_phases}
    )
    db.add(roadmap_db)
    db.commit()

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


@router.get("/analyses", response_model=List[Dict[str, Any]])
def list_analyses(db: Session = Depends(get_db)):
    analyses = db.query(ProjectAnalysis).order_by(ProjectAnalysis.created_at.desc()).all()
    return [
        {
            "id": a.id,
            "project_name": a.project_name,
            "description": a.description,
            "tech_stack": a.tech_stack,
            "created_at": a.created_at.isoformat(),
            "repo_count": len(a.repositories)
        } for a in analyses
    ]


@router.get("/analysis/{analysis_id}", response_model=Dict[str, Any])
def get_analysis_by_id(analysis_id: int, db: Session = Depends(get_db)):
    project = db.query(ProjectAnalysis).filter(ProjectAnalysis.id == analysis_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Analysis not found")

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
