import asyncio
import os
import sys

# Ensure backend path is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base, SessionLocal
from models.models import ProjectAnalysis
from services.github_service import search_repositories
from services.repo_triage import calculate_abandonment_score
from services.dependency_checker import analyze_dependencies
from services.analyzer import diagnose_repository_failure
from services.embeddings import generate_embedding
from services.clustering import cluster_diagnoses
from services.roadmap_generator import generate_project_roadmap
from services.risk_engine import inject_risk_annotations

async def run_verification():
    print("=== Starting Graveyard Mining System Pipeline Verification ===")
    
    # Init DB tables
    Base.metadata.create_all(bind=engine)
    print("[1/6] Database initialized successfully.")

    # 1. Search GitHub
    repos = await search_repositories("AI Resume Builder", ["Next.js", "FastAPI"], max_results=3)
    print(f"[2/6] GitHub Search returned {len(repos)} repositories.")

    # 2. Abandonment Score & Triage
    for r in repos:
        score = calculate_abandonment_score(r)
        print(f"      - {r.get('full_name')}: Abandonment Score = {score}/100")

    # 3. Security & Dependency Check
    deps = await analyze_dependencies(["Next.js", "FastAPI", "PostgreSQL"])
    print(f"[3/6] Dependency audit completed for {len(deps)} packages.")
    for d in deps:
        print(f"      - {d['package_name']} ({d['ecosystem']}): CVEs={d['vulnerability_count']}, Maintenance={d['maintenance_score']}, Risk={d['supply_chain_risk']}")

    # 4. Diagnosis & Embeddings
    sample_repo = repos[0] if repos else {"name": "sample-repo", "description": "sample description"}
    diag = await diagnose_repository_failure(
        repo_name=sample_repo.get("name", "sample"),
        description=sample_repo.get("description", ""),
        readme_excerpt="This project is no longer maintained.",
        issues=[{"title": "Outdated dependencies", "body": "Cannot build on Node 18"}],
        abandonment_score=75.0
    )
    print(f"[4/6] LLM Diagnosis generated.")
    print(f"      Root Cause: {diag.get('root_cause')}")

    emb = await generate_embedding(diag.get("summary", "sample"))
    print(f"      Embedding generated: length={len(emb)}")

    # 5. Clustering
    clusters = await cluster_diagnoses([{"repo_name": "sample/dead-repo", "diagnosis": diag}])
    print(f"[5/6] Failure clustering completed: {len(clusters)} cluster(s) generated.")

    # 6. Roadmap & Risk Annotations
    roadmap = await generate_project_roadmap("AI Resume Builder", "An AI agent customizing resumes", ["Next.js", "FastAPI"])
    annotated = inject_risk_annotations(roadmap, clusters, deps)
    print(f"[6/6] Roadmap generated with {len(annotated)} risk-annotated phases.")
    print("=== Verification Successful! ===")

if __name__ == "__main__":
    asyncio.run(run_verification())
