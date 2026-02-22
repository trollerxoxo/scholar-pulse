from pulse.models import Paper
from pathlib import Path
from datetime import datetime
from typing import List
import httpx
import asyncio

def export_markdown(papers: List[Paper], output_path: str = "./digest.md") -> Path:
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Scholar Pulse Digest\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for i, paper in enumerate(papers, 1):
            f.write(f"## {i}. {paper.title}\n")
            
            authors_str = ", ".join(paper.authors) if paper.authors else "Unknown"
            f.write(f"- **Authors:** {authors_str}\n")
            f.write(f"- **Published:** {paper.published_date}\n")
            f.write(f"- **Citations:** {paper.citation_count}\n")
            
            score_str = f"{paper.relevance_score:.3f}" if paper.relevance_score is not None else "N/A"
            f.write(f"- **Score:** {score_str}\n")
            
            link = paper.url or paper.doi or paper.pdf_url or paper.openalex_id or paper.arxiv_id or ""
            if link:
                f.write(f"- **Link:** {link}\n")
                
            f.write(f"- **Source:** {paper.source_provider}\n\n")
            
            if paper.abstract:
                f.write(f"> {paper.abstract}\n\n")
                
            f.write("---\n\n")
            
    return Path(output_path)

def export_bibtex(papers: List[Paper], output_path: str = "./digest.bib") -> Path:
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        for paper in papers:
            f.write(f"@article{{{paper.id},\n")
            f.write(f"  title = {{{paper.title}}},\n")
            f.write(f"  author = {{{' and '.join(paper.authors)}}},\n")
            f.write(f"  journal = {{{paper.source_provider}}},\n")
            f.write(f"  year = {{{paper.published_date.year}}},\n")
            
            if paper.doi:
                f.write(f"  doi = {{{paper.doi}}},\n")
            if paper.url:
                f.write(f"  url = {{{paper.url}}},\n")
            if paper.abstract:
                f.write(f"  abstract = {{{paper.abstract}}},\n")
            
            score_str = f"{paper.relevance_score:.3f}" if paper.relevance_score is not None else "N/A"
            f.write(f"  note = {{Citations: {paper.citation_count}, Score: {score_str}}}\n")
            f.write("}\n\n")
            
    return Path(output_path)

async def export_pdfs(papers: List[Paper], output_path: str = "./papers") -> Path:
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    paper_with_pdf = [p for p in papers if p.pdf_url]
    
    # Use a standard User-Agent to prevent 403 Forbidden errors from publishers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient(headers=headers) as client:
        tasks = []
        for paper in paper_with_pdf:
            safe_title = "".join(c for c in paper.title if c.isalnum() or c in " _-")
            tasks.append(download_pdfs(client, paper.pdf_url, output_dir / f"{safe_title}.pdf"))
        await asyncio.gather(*tasks)
    return output_dir

async def download_pdfs(client:httpx.AsyncClient, url: str, path: Path):
    if path.exists():
        return
    try:
        response = await client.get(url, timeout=10, follow_redirects=True)
        response.raise_for_status()
        with open(path, "wb") as f:
            f.write(response.content)
    except Exception as e:
        print(f"Error downloading {url}: {e}")