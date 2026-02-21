from pydantic import BaseModel, Field
from datetime import datetime, date

class Paper(BaseModel):
    id: str
    title: str
    authors: list[str]
    abstract: str
    doi: str | None
    arxiv_id: str | None
    openalex_id: str | None
    url: str
    pdf_url: str | None
    published_date: date
    citation_count: int
    keywords: list[str]
    source_provider: str
    relevance_score: float | None
    saved_at: datetime = Field(default_factory=datetime.now)

class Query(BaseModel):
    keywords: list[str]
    categories: list[str]
    date_from: date | None = None
    date_to: date | None = None
    max_results: int = 20

class RankingConfig(BaseModel):
    weight_citations: float = 0.4
    weight_recency: float = 0.3
    weight_keyword: float = 0.3