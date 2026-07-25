import asyncio
from typing import Any

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Request, status
from logging_config import get_logger
from models.models import ProjectAnalysis
from schemas.schemas import AnalyzeRequest
from services.analysis_service import AnalysisService
from services.report_service import ReportService
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

logger = get_logger("Routes")
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api", tags=["analysis"])
analysis_service = AnalysisService()
report_service = ReportService()

@router.post("/analyze", response_model=dict[str, Any])
@limiter.limit("7/minute")
async def analyze_project(request: Request, req: AnalyzeRequest, db: Session = Depends(get_db)):
    """
    Main orchestration endpoint for Graveyard Mining.
    Delegates pipeline execution to AnalysisService with a 120-second timeout guard.
    """
    try:
        return await asyncio.wait_for(analysis_service.run(req, db), timeout=120.0)
    except asyncio.TimeoutError:
        logger.error(f"Analysis timed out for project: {req.project_name}")
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail={
                "success": False,
                "error": {
                    "code": "ANALYSIS_TIMEOUT",
                    "message": "The repository analysis pipeline exceeded the 120-second threshold."
                }
            }
        )
    except Exception as e:
        logger.exception(f"Unhandled exception during project analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "ANALYSIS_FAILED",
                    "message": "An error occurred while executing the project analysis pipeline."
                }
            }
        )

@router.get("/analyses", response_model=list[dict[str, Any]])
@limiter.limit("40/minute")
def list_analyses(request: Request, db: Session = Depends(get_db)):
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

@router.get("/analysis/{analysis_id}", response_model=dict[str, Any])
@limiter.limit("40/minute")
def get_analysis_by_id(request: Request, analysis_id: int, db: Session = Depends(get_db)):
    project = db.query(ProjectAnalysis).filter(ProjectAnalysis.id == analysis_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Analysis with ID {analysis_id} was not found."
                }
            }
        )
    return report_service.serialize_analysis(project)
