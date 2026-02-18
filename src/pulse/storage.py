import json
from pathlib import Path
from typing import List

from .models import Paper

DATA_FILE = Path.home() / ".scholar-pulse" / "papers.json"
if not DATA_FILE.exists():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_papers() -> List[Paper]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r") as f:
        return [Paper.model_validate(paper) for paper in json.load(f)]

def save_papers(papers: List[Paper]) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump([paper.model_dump(mode='json') for paper in papers], f, indent=4)