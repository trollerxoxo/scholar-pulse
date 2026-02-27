from pulse.models import Paper, Query
from pulse.config import RankingConfig, load_config, Settings
import math
import json
from datetime import date, datetime, timedelta
from pathlib import Path
import asyncio
from pulse.providers import get_provider

def rank_papers(papers: list[Paper], query: Query, config: RankingConfig) -> list[Paper]:
    
    if not papers:
        return []
    
    max_citations_in_set = max(p.citation_count for p in papers)
    if max_citations_in_set > 0:
        wc = config.weight_citation
        wr = config.weight_recency
        wk = config.weight_keyword
    else:
        wk = config.weight_keyword + (config.weight_citation/2)
        wr = config.weight_recency + (config.weight_citation/2)
        wc = 0

    query_keyword = set(keyword.lower() for keyword in query.keywords)
    
    for paper in papers:
        if max_citations_in_set > 0:
            C_norm = math.log( 1 + paper.citation_count) / math.log(1 + max_citations_in_set)
        else:
            C_norm = 0

        paper_keyword = set(keyword.lower() for keyword in paper.keywords)
        matching_keywords = query_keyword.intersection(paper_keyword)
        S = len(matching_keywords)/len(query_keyword) if query_keyword else 0
       

        days_since_publication = (date.today() - paper.published_date).days
        Recency = 1 / (days_since_publication + 1)
        
        R = wc * C_norm + wr * Recency + wk * S
       
        paper.relevance_score = R

    return sorted(papers, key=lambda p: p.relevance_score, reverse=True)

def deduplicate(papers: list[Paper]) -> list[Paper]:
    unique_papers = {}
    for paper in papers:
        key = paper.doi or paper.arxiv_id or paper.openalex_id or paper.id
        
        if key:
            if key not in unique_papers:
                unique_papers[key] = paper
            else:
                existing = unique_papers[key]   
                existing_metadata_field_count = sum((1 for value in existing.model_dump().values() if value not in [None, ""]))
                new_metadata_field_count = sum((1 for value in paper.model_dump().values() if value not in [None, ""]))
                if new_metadata_field_count > existing_metadata_field_count:
                    unique_papers[key] = paper
    return list(unique_papers.values())

async def run_digest(top_n: int = 5, days: int = 30) -> list[Paper]:
    settings = load_config()
    query = Query(
        keywords=settings.search.default_keywords,
        categories=settings.search.default_categories,
        max_results=settings.search.max_results_per_provider,
        date_from=date.today() - timedelta(days=days),
        date_to=date.today()
    )

    cache_dir = Path("~/.scholar-pulse/cache").expanduser()
    _cleanup_stale_cache(cache_dir)
    cache_key = _cache_key(query, days)
    cache_file = cache_dir / f"{cache_key}.json"
    cached_papers = _load_cache(cache_file)
    if cached_papers:
        return cached_papers[:top_n]
    
    ranked_papers = await _fetch_and_rank(query, settings)
    _save_cache(cache_file, ranked_papers)
    return ranked_papers[:top_n]

async def search(query: str, categories: str | None = None) -> list[Paper]:
    settings = load_config()
    query = [q.strip() for q in query.split(",") if q]
    categories = [c.strip() for c in categories.split(",") if c] if categories else settings.search.default_categories
    query = Query(
        keywords=query,
        categories=categories,
        max_results=settings.search.max_results_per_provider,
        date_from=date.today() - timedelta(days=30),
        date_to=date.today()
    )

    ranked_papers = await _fetch_and_rank(query, settings)
    return ranked_papers

async def _fetch_and_rank(query: Query, settings: Settings) -> list[Paper]:
    provider_credentials = {
        "semantic_scholar": {"api_key": settings.semantic_scholar_api_key},
        "openalex": {"email": settings.openalex_email},
    }
    providers = [
        get_provider(name)(**provider_credentials.get(name, {}))
        for name in settings.providers.enabled
    ]
    tasks = [provider.search(query) for provider in providers]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_papers = []
    for result in results:
        if isinstance(result, Exception):
            print(f"Error fetching papers: {result}")
        else:
            all_papers.extend(result)
    
    unique_papers = deduplicate(all_papers)
    ranked_papers = rank_papers(unique_papers, query, settings.ranking)

    return ranked_papers

def _cache_key(query: Query, days: int) -> str:
    import hashlib, json
    raw = json.dumps({
        "keywords": query.keywords,
        "categories": query.categories,
        "max_results": query.max_results,
        "date_from": (date.today() - timedelta(days=days)).isoformat(),
        "date_to": query.date_to.isoformat(),
    }, sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()[:16]

def _load_cache(cache_file: Path) -> list[Paper] | None:
    if not cache_file.exists():
        return None
    try:
        with open(cache_file) as f:
            return [Paper(**p) for p in json.load(f)]
    except Exception as e:
        print(f"Error loading cache: {e}")
        return None

def _save_cache(cache_file: Path, papers: list[Paper]) -> None:
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_file, "w") as f:
        json.dump([p.model_dump(mode="json") for p in papers], f, indent=2)

def _cleanup_stale_cache(cache_dir: Path) -> None:
    if not cache_dir.exists():
        return
    now = datetime.now().timestamp()
    for f in cache_dir.glob("*.json"):
        try:
            age = now - f.stat().st_mtime
            if age > 3600:
                f.unlink()
        except Exception as e:
            print(f"Error cleaning up cache: {e}")