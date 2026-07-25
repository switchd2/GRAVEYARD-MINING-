from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    project_name: str = Field(..., json_schema_extra={"example": "AI Resume Builder"})
    description: str = Field(..., json_schema_extra={"example": "An AI agent that customizes resumes and generates cover letters for tech roles."})
    tech_stack: list[str] = Field(..., json_schema_extra={"example": ["Next.js", "FastAPI", "PostgreSQL", "OpenAI"]})

class DiagnosisSchema(BaseModel):
    id: int | None = None
    root_cause: str
    failure_category: str
    technical_debt_level: str
    summary: str
    key_takeaways: list[str]
    tavily_context: str | None = None

class RepositorySchema(BaseModel):
    id: int | None = None
    name: str
    full_name: str
    html_url: str
    description: str | None = None
    stars: int
    forks: int
    open_issues: int
    last_commit_date: str | None = None
    abandonment_score: float
    is_abandoned: bool
    language: str | None = None
    diagnosis: DiagnosisSchema | None = None

class DependencyReportSchema(BaseModel):
    id: int | None = None
    package_name: str
    ecosystem: str
    vulnerability_count: int
    maintenance_score: float
    supply_chain_risk: str
    snyk_findings: dict[str, Any] | None = None
    details: dict[str, Any] | None = None

class FailureClusterSchema(BaseModel):
    id: int | None = None
    cluster_name: str
    description: str
    repo_count: int
    risk_level: str
    affected_repos: list[str]

class RiskCheckpointSchema(BaseModel):
    title: str
    risk_level: str  # CRITICAL, HIGH, MEDIUM, LOW
    warning: str
    prevention_strategy: str
    evidence_repos: list[str]

class RoadmapPhaseSchema(BaseModel):
    phase_number: int
    title: str
    description: str
    estimated_duration: str
    key_deliverables: list[str]
    risk_checkpoints: list[RiskCheckpointSchema]

class RoadmapSchema(BaseModel):
    id: int | None = None
    phases: list[RoadmapPhaseSchema]

class AnalysisResponseSchema(BaseModel):
    id: int
    project_name: str
    description: str
    tech_stack: list[str]
    created_at: datetime
    repositories: list[RepositorySchema]
    dependency_reports: list[DependencyReportSchema]
    failure_clusters: list[FailureClusterSchema]
    roadmap: RoadmapSchema
