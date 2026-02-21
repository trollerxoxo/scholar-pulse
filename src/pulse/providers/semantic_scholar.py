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
        params = {
            "query": query_string,
            "limit": query.max_results,
            "fields": "title,authors,abstract,externalIds,url,openAccessPdf,citationCount,publicationDate"
        }
        if query.date_from:
            params["year"] = f"{query.date_from.year}-{query.date_to.year}" if query.date_to else f"{query.date_from.year}-"        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/search", 
            params=params,
            headers=headers)
            response.raise_for_status()
            papers = []
            for item in response.json()["data"]:
                try:
                    papers.append(self._to_paper(item))
                except Exception:
                    continue
            return papers
    
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
            published_date=paper.get("publicationDate") or "",
        )