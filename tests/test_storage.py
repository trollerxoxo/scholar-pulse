import pytest
from pulse.storage import load_papers, save_papers
from pulse.models import Paper

def test_load_papers(tmp_path, monkeypatch):
    monkeypatch.setattr("pulse.storage.DATA_FILE", tmp_path / "papers.json")
    papers = load_papers()
    assert type(papers) == list
    assert all(isinstance(paper, Paper) for paper in papers)

def test_save_papers(tmp_path, monkeypatch):
    monkeypatch.setattr("pulse.storage.DATA_FILE", tmp_path / "papers.json")
    papers = [Paper(
        id="1",
        title="Test Paper",
        authors=["Test Author"],
        abstract="Test Abstract",
        doi="test-doi",
        arxiv_id="test-arxiv",
        openalex_id="test-openalex",
        url="test-url",
        pdf_url="test-pdf-url",
        published_date="2022-01-01",
        citation_count=10,
        keywords=["test", "paper"],
        source_provider="test-provider",
        relevance_score=0.5,
        saved_at="2022-01-01T00:00:00"
    )]
    save_papers(papers)
    loaded_papers = load_papers()
    assert loaded_papers == papers