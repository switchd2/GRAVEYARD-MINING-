import pytest
from database import Base, engine, SessionLocal
from schemas.schemas import AnalyzeRequest
from services.ai_service import AIService
from services.security_service import SecurityService
from services.github_service import GitHubService
from services.analysis_service import AnalysisService

@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()

@pytest.mark.asyncio
async def test_ai_service_heuristic_fallback():
    ai = AIService()
    ai.api_key = "" # force fallback
    diag = await ai.diagnose_repository_failure(
        repo_name="test-repo",
        description="test desc",
        readme_excerpt="",
        issues=[],
        abandonment_score=80.0
    )
    assert "root_cause" in diag
    assert "failure_category" in diag

@pytest.mark.asyncio
async def test_ai_service_pseudo_embeddings():
    ai = AIService()
    ai.api_key = "" # force fallback
    emb = await ai.generate_embedding("test embedding text")
    assert len(emb) == 128
    assert isinstance(emb[0], float)

@pytest.mark.asyncio
async def test_security_service():
    sec = SecurityService()
    reports = await sec.analyze_dependencies(["Next.js", "FastAPI"])
    assert len(reports) == 2
    assert reports[0]["package_name"] == "Next.js"
    assert "vulnerability_count" in reports[0]

@pytest.mark.asyncio
async def test_analysis_pipeline_service(setup_db):
    svc = AnalysisService()
    req = AnalyzeRequest(
        project_name="Unit Test App",
        description="Testing modular architecture pipeline",
        tech_stack=["React", "FastAPI"]
    )
    res = await svc.run(req, setup_db)
    assert res["project_name"] == "Unit Test App"
    assert "repositories" in res
    assert "roadmap" in res
