"""
Shared test helpers and fixtures for the scholar-pulse test suite.

Import helpers directly:
    from conftest import make_paper, make_query

Or use fixtures by adding the fixture name to a test function signature.
"""

import pytest
from datetime import date, timedelta

from pulse.models import Paper, Query
from pulse.config import RankingConfig


def make_paper(
    id: str = "p1",
    title: str = "Test Paper",
    citation_count: int = 10,
    published_date: date | None = None,
    keywords: list[str] | None = None,
    doi: str | None = None,
    arxiv_id: str | None = None,
    openalex_id: str | None = None,
    abstract: str = "An abstract.",
    pdf_url: str | None = None,
    authors: list[str] | None = None,
    source_provider: str = "test",
    relevance_score: float | None = None,
) -> Paper:
    """Create a Paper with sensible test defaults. Override any field as needed."""
    return Paper(
        id=id,
        title=title,
        authors=authors or ["Author A"],
        abstract=abstract,
        doi=doi,
        arxiv_id=arxiv_id,
        openalex_id=openalex_id,
        url="http://example.com",
        pdf_url=pdf_url,
        published_date=published_date or date(2024, 1, 1),
        citation_count=citation_count,
        keywords=keywords or [],
        source_provider=source_provider,
        relevance_score=relevance_score,
    )


def make_query(
    keywords: list[str] | None = None,
    categories: list[str] | None = None,
    days: int | None = None,
    max_results: int = 20,
) -> Query:
    """Create a Query with sensible test defaults."""
    return Query(
        keywords=keywords or ["digital twin", "BIM"],
        categories=categories or [],
        date_from=date.today() - timedelta(days=days) if days else None,
        date_to=date.today() if days else None,
        max_results=max_results,
    )


# --- Reusable fixtures ---

@pytest.fixture
def default_query() -> Query:
    return make_query()


@pytest.fixture
def ranking_config() -> RankingConfig:
    return RankingConfig()
