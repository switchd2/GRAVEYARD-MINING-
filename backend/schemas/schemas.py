from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class AnalyzeRequest(BaseModel):
    project_name: str = Field(..., example="AI Resume Builder")
    description: str = Field(..., example="An AI agent that customizes resumes and generates cover letters for tech roles.")
    tech_stack: List[str] = Field(..., example=["Next.js", "FastAPI", "PostgreSQL", "OpenAI"])

class DiagnosisSchema(BaseModel):
    id: Optional[int] = None
    root_cause: str
    failure_category: str
    technical_debt_level: str
    summary: str
    key_takeaways: List[str]
    tavily_context: Optional[str] = None

class RepositorySchema(BaseModel):
    id: Optional[int] = None
    name: str
    full_name: str
    html_url: str
    description: Optional[str] = None
    stars: int
    forks: int
    open_issues: int
    last_commit_date: Optional[str] = None
    abandonment_score: float
    is_abandoned: bool
    language: Optional[str] = None
    diagnosis: Optional[DiagnosisSchema] = None

class DependencyReportSchema(BaseModel):
    id: Optional[int] = None
    package_name: str
    ecosystem: str
    vulnerability_count: int
    maintenance_score: float
    supply_chain_risk: str
    snyk_findings: Optional[Dict[str, Any]] = None
    details: Optional[Dict[str, Any]] = None

class FailureClusterSchema(BaseModel):
    id: Optional[int] = None
    cluster_name: str
    description: str
    repo_count: int
    risk_level: str
    affected_repos: List[str]

class RiskCheckpointSchema(BaseModel):
    title: str
    risk_level: str  # CRITICAL, HIGH, MEDIUM, LOW
    warning: str
    prevention_strategy: str
    evidence_repos: List[str]

class RoadmapPhaseSchema(BaseModel):
    phase_number: int
    title: str
    description: str
    estimated_duration: str
    key_deliverables: List[str]
    risk_checkpoints: List[RiskCheckpointSchema]

class RoadmapSchema(BaseModel):
    id: Optional[int] = None
    phases: List[RoadmapPhaseSchema]

class AnalysisResponseSchema(BaseModel):
    id: int
    project_name: str
    description: str
    tech_stack: List[str]
    created_at: datetime
    repositories: List[RepositorySchema]
    dependency_reports: List[DependencyReportSchema]
    failure_clusters: List[FailureClusterSchema]
    roadmap: RoadmapSchema
