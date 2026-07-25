from datetime import datetime, timezone

from database import Base
from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship


class ProjectAnalysis(Base):
    __tablename__ = "project_analyses"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    tech_stack = Column(JSON, nullable=False)  # list of strings
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    repositories = relationship("Repository", back_populates="analysis", cascade="all, delete-orphan")
    dependency_reports = relationship("DependencyReport", back_populates="analysis", cascade="all, delete-orphan")
    failure_clusters = relationship("FailureCluster", back_populates="analysis", cascade="all, delete-orphan")
    roadmap = relationship("Roadmap", back_populates="analysis", uselist=False, cascade="all, delete-orphan")


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("project_analyses.id"), nullable=False)
    name = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    html_url = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    open_issues = Column(Integer, default=0)
    last_commit_date = Column(String, nullable=True)
    abandonment_score = Column(Float, default=0.0)  # 0 to 100
    is_abandoned = Column(Integer, default=1) # 1 true, 0 false
    language = Column(String, nullable=True)
    raw_metadata = Column(JSON, nullable=True)

    analysis = relationship("ProjectAnalysis", back_populates="repositories")
    diagnosis = relationship("Diagnosis", back_populates="repository", uselist=False, cascade="all, delete-orphan")


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    root_cause = Column(String, nullable=False)
    failure_category = Column(String, nullable=False)
    technical_debt_level = Column(String, nullable=False)  # High, Medium, Low
    summary = Column(Text, nullable=False)
    key_takeaways = Column(JSON, nullable=False)  # list of strings
    tavily_context = Column(Text, nullable=True)
    embedding = Column(JSON, nullable=True)  # Store embedding vector as list of floats

    repository = relationship("Repository", back_populates="diagnosis")


class DependencyReport(Base):
    __tablename__ = "dependency_reports"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("project_analyses.id"), nullable=False)
    package_name = Column(String, nullable=False)
    ecosystem = Column(String, nullable=False) # npm, PyPI, etc.
    vulnerability_count = Column(Integer, default=0)
    maintenance_score = Column(Float, default=1.0) # 0.0 to 1.0 or 0-100
    supply_chain_risk = Column(String, default="LOW") # LOW, MEDIUM, HIGH, CRITICAL
    snyk_findings = Column(JSON, nullable=True)
    details = Column(JSON, nullable=True)

    analysis = relationship("ProjectAnalysis", back_populates="dependency_reports")


class FailureCluster(Base):
    __tablename__ = "failure_clusters"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("project_analyses.id"), nullable=False)
    cluster_name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    repo_count = Column(Integer, default=0)
    risk_level = Column(String, default="HIGH") # CRITICAL, HIGH, MEDIUM, LOW
    affected_repos = Column(JSON, nullable=False) # list of repo full_names

    analysis = relationship("ProjectAnalysis", back_populates="failure_clusters")


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("project_analyses.id"), nullable=False)
    phases_json = Column(JSON, nullable=False)

    analysis = relationship("ProjectAnalysis", back_populates="roadmap")
