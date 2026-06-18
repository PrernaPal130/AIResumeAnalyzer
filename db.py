"""PostgreSQL storage helpers for analysis reports."""

from __future__ import annotations

import os
from datetime import datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    desc,
    select,
)
from sqlalchemy.engine import Engine


metadata = MetaData()

analysis_reports = Table(
    "analysis_reports",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("resume_filename", String(255), nullable=False),
    Column("job_description", Text, nullable=False),
    Column("match_score", Integer, nullable=False),
    Column("similarity_score", Float, nullable=False),
    Column("keyword_score", Float, nullable=False),
    Column("required_score", Float, nullable=True),
    Column("preferred_score", Float, nullable=True),
    Column("keywords_found", JSON, nullable=False),
    Column("missing_skills", JSON, nullable=False),
    Column("required_skills", JSON, nullable=False),
    Column("preferred_skills", JSON, nullable=False),
    Column("missing_required_skills", JSON, nullable=False),
    Column("missing_preferred_skills", JSON, nullable=False),
    Column("suggestions", JSON, nullable=False),
    Column("full_report", JSON, nullable=False),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
)


def _database_url() -> str | None:
    """Read DATABASE_URL and normalize older postgres URL schemes."""
    url = os.getenv("DATABASE_URL")
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def get_engine() -> Engine | None:
    """Create a SQLAlchemy engine when DATABASE_URL is configured."""
    url = _database_url()
    if not url:
        return None
    return create_engine(url, pool_pre_ping=True)


def init_database() -> bool:
    """Create database tables if a database is configured."""
    engine = get_engine()
    if engine is None:
        return False

    metadata.create_all(engine)
    return True


def save_analysis_report(
    result: dict, resume_filename: str, job_description: str
) -> int | None:
    """Save an analysis result and return the inserted database id."""
    engine = get_engine()
    if engine is None:
        return None

    values = {
        "resume_filename": resume_filename,
        "job_description": job_description,
        "match_score": result["match_score"],
        "similarity_score": result["similarity_score"],
        "keyword_score": result["keyword_score"],
        "required_score": result.get("required_score"),
        "preferred_score": result.get("preferred_score"),
        "keywords_found": result["keywords_found"],
        "missing_skills": result["missing_skills"],
        "required_skills": result["required_skills"],
        "preferred_skills": result["preferred_skills"],
        "missing_required_skills": result["missing_required_skills"],
        "missing_preferred_skills": result["missing_preferred_skills"],
        "suggestions": result["suggestions"],
        "full_report": result,
        "created_at": datetime.utcnow(),
    }

    with engine.begin() as connection:
        existing_columns = {
            column["name"] for column in connection.dialect.get_columns(connection, "analysis_reports")
        }
        values = {
            key: value for key, value in values.items() if key in existing_columns
        }
        inserted = connection.execute(
            analysis_reports.insert().returning(analysis_reports.c.id), values
        )
        return inserted.scalar_one()


def list_analysis_reports(limit: int = 20) -> list[dict]:
    """Return recent analysis reports for a history view."""
    engine = get_engine()
    if engine is None:
        return []

    query = (
        select(analysis_reports)
        .order_by(desc(analysis_reports.c.created_at))
        .limit(limit)
    )

    with engine.connect() as connection:
        rows = connection.execute(query).mappings().all()

    reports = []
    for row in rows:
        item = dict(row)
        item["created_at"] = item["created_at"].isoformat(timespec="seconds")
        reports.append(item)
    return reports
