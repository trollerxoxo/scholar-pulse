import typer
from rich import print
from rich.table import Table
import asyncio
from pulse import service
from typing import Annotated


app = typer.Typer()

@app.callback()
def callback():
    """📚 Scholar Pulse — Automated research paper discovery for PhD students."""

@app.command("digest")
def digest(top_n: Annotated[int, typer.Option(min=1, max=100)] = 10,
           days: Annotated[int, typer.Option(min=1)] = 30):
    papers = asyncio.run(service.run_digest(top_n=top_n, days=days))
    table = Table(title=f"📚 Scholar Pulse Digest ({days} days)", show_lines=True, expand=True)
    table.add_column("#", justify="right", style="bold cyan", width=3)
    table.add_column("Title", style="white", ratio=3, no_wrap=False)
    table.add_column("Citations", justify="right", style="green", min_width=5)
    table.add_column("Date", style="yellow", min_width=10)
    table.add_column("Score", justify="right", style="magenta", min_width=5)
    table.add_column("Source", style="dim", min_width=8)
    
    for i, paper in enumerate(papers, 1):
        table.add_row(
            str(i), 
            paper.title, 
            str(paper.citation_count), 
            str(paper.published_date),
            f"{paper.relevance_score:.3f}" if paper.relevance_score else "N/A",
            paper.source_provider
        )
    print(table)

if __name__ == "__main__":
    app()