import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Base, engine, SessionLocal
from schemas.schemas import AnalyzeRequest
from services.ai_service import AIService
from services.analysis_service import AnalysisService
from services.github_service import GitHubService
from services.security_service import SecurityService


async def run_verification():
    print("=== Starting Graveyard Mining System Pipeline Verification ===")

    # Init DB tables for test
    Base.metadata.create_all(bind=engine)
    print("[1/5] Database initialized successfully.")

    # 1. Test GitHubService
    github_svc = GitHubService()
    repos = await github_svc.search_repositories("AI Resume Builder", ["Next.js", "FastAPI"], max_results=3)
    print(f"[2/5] GitHub Search returned {len(repos)} repositories.")

    # 2. Test SecurityService
    security_svc = SecurityService()
    deps = await security_svc.analyze_dependencies(["Next.js", "FastAPI", "PostgreSQL"])
    print(f"[3/5] Security audit completed for {len(deps)} packages.")

    # 3. Test AIService
    ai_svc = AIService()
    diag = await ai_svc.diagnose_repository_failure(
        repo_name="sample-repo",
        description="sample description",
        readme_excerpt="This project is no longer maintained.",
        issues=[{"title": "Outdated dependencies", "body": "Cannot build"}],
        abandonment_score=75.0
    )
    print(f"[4/5] AI Diagnosis completed. Root cause: {diag.get('root_cause')}")

    # 4. Test Full Orchestrator (AnalysisService)
    analysis_svc = AnalysisService()
    db = SessionLocal()
    try:
        req = AnalyzeRequest(
            project_name="Test Verification Project",
            description="Testing new domain service orchestrator pipeline",
            tech_stack=["Next.js", "FastAPI"]
        )
        res = await analysis_svc.run(req, db)
        print(f"[5/5] Full AnalysisService pipeline completed. Report ID: {res.get('id')}")
        print("=== Verification Successful! ===")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_verification())
