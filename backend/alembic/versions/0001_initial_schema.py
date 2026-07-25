"""Initial database schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-07-25 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = '0001_initial_schema'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    op.create_table(
        'project_analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('tech_stack', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_analyses_id'), 'project_analyses', ['id'], unique=False)

    op.create_table(
        'repositories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('html_url', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('stars', sa.Integer(), nullable=True),
        sa.Column('forks', sa.Integer(), nullable=True),
        sa.Column('open_issues', sa.Integer(), nullable=True),
        sa.Column('last_commit_date', sa.String(), nullable=True),
        sa.Column('abandonment_score', sa.Float(), nullable=True),
        sa.Column('is_abandoned', sa.Integer(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('raw_metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['analysis_id'], ['project_analyses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_repositories_id'), 'repositories', ['id'], unique=False)

    op.create_table(
        'diagnoses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('repository_id', sa.Integer(), nullable=False),
        sa.Column('root_cause', sa.String(), nullable=False),
        sa.Column('failure_category', sa.String(), nullable=False),
        sa.Column('technical_debt_level', sa.String(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('key_takeaways', sa.JSON(), nullable=False),
        sa.Column('tavily_context', sa.Text(), nullable=True),
        sa.Column('embedding', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_diagnoses_id'), 'diagnoses', ['id'], unique=False)

    op.create_table(
        'dependency_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.Integer(), nullable=False),
        sa.Column('package_name', sa.String(), nullable=False),
        sa.Column('ecosystem', sa.String(), nullable=False),
        sa.Column('vulnerability_count', sa.Integer(), nullable=True),
        sa.Column('maintenance_score', sa.Float(), nullable=True),
        sa.Column('supply_chain_risk', sa.String(), nullable=True),
        sa.Column('snyk_findings', sa.JSON(), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['analysis_id'], ['project_analyses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dependency_reports_id'), 'dependency_reports', ['id'], unique=False)

    op.create_table(
        'failure_clusters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.Integer(), nullable=False),
        sa.Column('cluster_name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('repo_count', sa.Integer(), nullable=True),
        sa.Column('risk_level', sa.String(), nullable=True),
        sa.Column('affected_repos', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['analysis_id'], ['project_analyses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_failure_clusters_id'), 'failure_clusters', ['id'], unique=False)

    op.create_table(
        'roadmaps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.Integer(), nullable=False),
        sa.Column('phases_json', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['analysis_id'], ['project_analyses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roadmaps_id'), 'roadmaps', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_roadmaps_id'), table_name='roadmaps')
    op.drop_table('roadmaps')
    op.drop_index(op.f('ix_failure_clusters_id'), table_name='failure_clusters')
    op.drop_table('failure_clusters')
    op.drop_index(op.f('ix_dependency_reports_id'), table_name='dependency_reports')
    op.drop_table('dependency_reports')
    op.drop_index(op.f('ix_diagnoses_id'), table_name='diagnoses')
    op.drop_table('diagnoses')
    op.drop_index(op.f('ix_repositories_id'), table_name='repositories')
    op.drop_table('repositories')
    op.drop_index(op.f('ix_project_analyses_id'), table_name='project_analyses')
    op.drop_table('project_analyses')
