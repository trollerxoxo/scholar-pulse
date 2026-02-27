import typer
from rich import print
from rich.table import Table
import asyncio
from pulse import service, config
from pulse import export as export_module
from typing import Annotated
from pathlib import Path
from pydantic import BaseModel

app = typer.Typer()
config_app = typer.Typer()
app.add_typer(config_app, name="config")

@app.callback()
def callback():
    """📚 Scholar Pulse — Automated research paper discovery for PhD students."""

@app.command("digest")
def digest(top_n: Annotated[int, typer.Option(min=1, max=100)] = 10,
           days: Annotated[int, typer.Option(min=1)] = 30,
           export: Annotated[str, typer.Option(help="Export format: md or bibtex")] = None,
           export_path: Annotated[str, typer.Option(help="Export path")] = None):
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
    if export == "md":
        kwargs = {"output_path": export_path} if export_path else {}
        path = export_module.export_markdown(papers, **kwargs)
        print(f"\n[green]Exported to {path.absolute()}[/green]")
    elif export == "bibtex":
        kwargs = {"output_path": export_path} if export_path else {}
        path = export_module.export_bibtex(papers, **kwargs)
        print(f"\n[green]Exported to {path.absolute()}[/green]")
    elif export == "pdf":
        kwargs = {"output_path": export_path} if export_path else {}
        print("\n[cyan]Downloading PDFs...[/cyan]")
        path = asyncio.run(export_module.export_pdfs(papers, **kwargs))
        print(f"\n[green]Downloaded PDFs to {path.absolute()}[/green]")
    elif export:
        print(f"\n[red]Unknown export format: {export}[/red]")

@app.command("search")
def search(query: Annotated[str, typer.Argument(help="Search query (comma separated)")], categories: Annotated[str, typer.Option(help="Categories (comma separated)")] = None):
    papers = asyncio.run(service.search(query, categories))
    table = Table(title="📚 Scholar Pulse Search", show_lines=True, expand=True)
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

@config_app.command("show")
def config_show():
    settings = config.load_config()
    # setting is a nested dictionary
    table = Table(title="📚 Scholar Pulse Config", show_lines=True, expand=True)
    table.add_column("Key", style="bold cyan", min_width=20)
    table.add_column("Value", style="white", ratio=3, no_wrap=False)

    for section, options in settings.model_dump().items():
        if isinstance(options, dict):
            for key, value in options.items():
                if type(value) == list:
                    value = ", ".join(value)
                table.add_row(f"{section}.{key}", str(value))
        else:
            if section in ("semantic_scholar_api_key", "openalex_email") and options:
                options = "•" * (len(str(options)) - 6) + str(options)[-6:]
            table.add_row(section, str(options))
    print(table)

@config_app.command("set")
def config_set(key: str, value: Annotated[str, typer.Argument(help="Value to set")]):
    import tomli_w, tomllib, json
    try:
        value = json.loads(value)
    except json.JSONDecodeError:
        value = value
    settings = config.load_config()

    for name, section in settings:
        if not isinstance(section, BaseModel):
            continue
        if hasattr(section, key):
            setattr(section, key, value)
            break
    else:
        print(f"[red]Unknown key: {key}[/red]")
        print("Available keys:")
        print([field for name, section in settings if isinstance(section, BaseModel) for field in type(section).model_fields])
        return
    config.save_config(settings)
    print(f"[green]Set {key} to {value}[/green]")

@config_app.command("init")
def config_init():
    config_path = Path("~/.scholar-pulse/config.toml").expanduser()
    if config_path.exists():
        if not typer.confirm("Config already exists. Overwrite?"):
            return

    default_keywords = typer.prompt("Default Keywords (comma separated)", type=str)
    default_categories = typer.prompt("Default Categories (comma separated)", type=str)
    max_results_per_provider = typer.prompt("max_results_per_provider", type=int)
    weight_citation = typer.prompt("weight_citation", type=float)
    weight_recency = typer.prompt("weight_recency", type=float)
    weight_keyword = typer.prompt("weight_keyword", type=float)
    enabled = typer.prompt("enabled (comma separated)", type=str)
    default_format = typer.prompt("default_format", type=str)
    if not typer.confirm("Save config?", abort=True):
        return
    print("\n[yellow]Set your API keys in .env — see .env.example[/yellow]")

    config.save_config(config.Settings(
        search=config.SearchConfig(
            default_keywords=[k.strip() for k in default_keywords.split(",")],
            default_categories=[c.strip() for c in default_categories.split(",")],
            max_results_per_provider=max_results_per_provider),
        ranking=config.RankingConfig(
            weight_citation=weight_citation,
            weight_recency=weight_recency,
            weight_keyword=weight_keyword),
        providers=config.ProviderConfig(
            enabled=[e.strip() for e in enabled.split(",")]),
        export=config.OutputConfig(
            default_format=default_format)
    ))
    print("[green]Config initialized[/green]")
    config_show()

if __name__ == "__main__":
    app()