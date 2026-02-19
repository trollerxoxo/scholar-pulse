from typing import List
from .base import Provider
from ..models import Paper, Query
import httpx
from datetime import date

class SemanticScholarProvider:
    def __init__(self, api_key: str | None = None):
        self.base_url = "https://api.semanticscholar.org/graph/v1/paper"
        self.api_key = api_key

    async def search(self, query: Query) -> List[Paper]:
        query_string = " ".join(query.keywords)
        headers = {"x-api-key": self.api_key} if self.api_key else {}
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/search", params={"query": query_string, "limit": query.max_results, 
            "fields": "title,authors,abstract,externalIds,url,openAccessPdf,citationCount,publicationDate"}, 
            headers=headers)
            response.raise_for_status()
            return [self._to_paper(paper) for paper in response.json()["data"]]
    
    def _to_paper(self, paper: dict) -> Paper:
        external_ids = paper.get("externalIds") or {}
        return Paper(
            id=paper["paperId"],
            title=paper["title"],
            authors=[author["name"] for author in (paper["authors"] or [])],
            doi=external_ids.get("DOI") or None,
            abstract=paper["abstract"] or "",
            url=paper["url"] or "",
            pdf_url=(paper.get("openAccessPdf") or {}).get("url"),
            citation_count=paper["citationCount"] or 0,
            arxiv_id=external_ids.get("ArXiv") or None,
            openalex_id=external_ids.get("OpenAlex") or None,
            keywords=[],
            source_provider="semantic_scholar",
            relevance_score=None,
            published_date=paper["publicationDate"],
        )