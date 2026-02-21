import httpx
from typing import List
from ..models import Paper, Query

class OpenAlexProvider:
    def __init__(self, email:str | None = None):
        self.base_url = "https://api.openalex.org/works"
        self.email = email

    async def search(self, query: Query) -> List[Paper]:
        query_string = " ".join(query.keywords)
        params = {"search": query_string, 
            "per_page": query.max_results, 
            "mailto": (self.email if self.email else "")}
        if query.date_from or query.date_to:
            filters = []
            if query.date_from:
                filters.append(f"from_publication_date:{query.date_from}")
            if query.date_to:
                filters.append(f"to_publication_date:{query.date_to}")
            params["filter"] = ",".join(filters)    
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}", params=params)
            response.raise_for_status()
            return [self._to_paper(paper) for paper in response.json()["results"]]
    
    def _to_paper(self, paper: dict) -> Paper:
        return Paper(
            id=paper["id"],
            title=paper["title"],
            authors=[author["author"]["display_name"] for author in (paper["authorships"] or [])],
            doi=paper.get("doi", "").removeprefix("https://doi.org/") if paper.get("doi") else "",
            abstract=paper.get("abstract") or "",
            url=paper.get("doi") or f"https://openalex.org/works/{paper['id']}",
            pdf_url=paper.get("primary_location", {}).get("pdf_url"),
            citation_count=paper["cited_by_count"] or 0,
            arxiv_id=None,
            openalex_id=paper["id"],
            keywords=[keyword["display_name"] for keyword in (paper["keywords"] or [])],
            source_provider="openalex",
            relevance_score=None,
            published_date=paper["publication_date"],
        )