from typing import Protocol, List
from ..models import Paper, Query

class Provider(Protocol):
    async def search(self, query: Query) -> List[Paper]:
        """Search for papers matching the query."""
        ...

    async def get_paper(self, paper_id: str) -> Paper | None:
        """Get a paper by its ID."""
        ...