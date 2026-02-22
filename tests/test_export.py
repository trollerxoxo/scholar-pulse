import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from pulse.export import export_markdown, export_bibtex, download_pdfs
from helpers import make_paper


# --- Markdown export ---

def test_export_markdown_creates_file(tmp_path):
    papers = [make_paper()]
    out = export_markdown(papers, str(tmp_path / "digest.md"))
    assert out.exists()


def test_export_markdown_contains_title(tmp_path):
    papers = [make_paper(title="BIM Compliance Paper")]
    out = export_markdown(papers, str(tmp_path / "digest.md"))
    content = out.read_text()
    assert "BIM Compliance Paper" in content


def test_export_markdown_contains_authors(tmp_path):
    papers = [make_paper(authors=["Smith, J.", "Doe, A."])]
    out = export_markdown(papers, str(tmp_path / "digest.md"))
    content = out.read_text()
    assert "Smith, J." in content
    assert "Doe, A." in content


def test_export_markdown_formats_score(tmp_path):
    papers = [make_paper(relevance_score=0.75)]
    out = export_markdown(papers, str(tmp_path / "digest.md"))
    content = out.read_text()
    assert "0.750" in content  # 3 decimal places


def test_export_markdown_multiple_papers(tmp_path):
    papers = [make_paper("p1", "Paper One"), make_paper("p2", "Paper Two")]
    out = export_markdown(papers, str(tmp_path / "digest.md"))
    content = out.read_text()
    assert "1. Paper One" in content
    assert "2. Paper Two" in content


# --- BibTeX export ---

def test_export_bibtex_creates_file(tmp_path):
    papers = [make_paper()]
    out = export_bibtex(papers, str(tmp_path / "digest.bib"))
    assert out.exists()


def test_export_bibtex_contains_entry(tmp_path):
    papers = [make_paper(id="p1", title="A Great Paper", published_date=__import__('datetime').date(2025, 6, 1))]
    out = export_bibtex(papers, str(tmp_path / "digest.bib"))
    content = out.read_text()
    assert "@article{p1," in content
    assert "A Great Paper" in content
    assert "2025" in content


def test_export_bibtex_author_format(tmp_path):
    """BibTeX uses 'and' to separate authors."""
    papers = [make_paper(authors=["Smith, J.", "Doe, A."])]
    out = export_bibtex(papers, str(tmp_path / "digest.bib"))
    content = out.read_text()
    assert "Smith, J. and Doe, A." in content


def test_export_bibtex_omits_none_doi(tmp_path):
    """DOI field should not appear if it's None."""
    papers = [make_paper(doi=None)]
    out = export_bibtex(papers, str(tmp_path / "digest.bib"))
    content = out.read_text()
    assert "doi = {None}" not in content
    assert "  doi" not in content


# --- PDF skip guard ---

def test_download_pdfs_skips_existing_file(tmp_path):
    """download_pdfs should skip the download if the file already exists."""
    existing_pdf = tmp_path / "paper.pdf"
    existing_pdf.write_bytes(b"existing content")

    mock_client = MagicMock()
    mock_client.get = AsyncMock()

    asyncio.run(download_pdfs(mock_client, "http://example.com/paper.pdf", existing_pdf))

    # The HTTP client should never have been called
    mock_client.get.assert_not_called()
    # And the file should remain unchanged
    assert existing_pdf.read_bytes() == b"existing content"
