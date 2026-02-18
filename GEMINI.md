# Project Specification: `scholar-pulse`

## Core Project Identity

* **Name:** `scholar-pulse`
* **CLI Entrypoint:** `pulse`
* **Purpose:** A CLI tool for PhD students to aggregate, rank, and export top literature review papers for synthesis in NotebookLM.
* **Tech Stack:** Python 3.12+, `uv` (package manager), `Typer` (CLI), `Rich` (TUI), `Pydantic` (Models), `httpx` (Async API calls).

---

## Architecture

**Layered Architecture** — each layer depends only on the layer below it.

```
┌─────────────────────────────────────┐
│  main.py  (CLI / Presentation)      │  ← Typer commands, Rich tables
├─────────────────────────────────────┤
│  service.py  (Business Logic)       │  ← Ranking, orchestration, search
├─────────────────────────────────────┤
│  providers/  (Data Access)          │  ← arXiv, Semantic Scholar, OpenAlex
│  storage.py  (Persistence)          │  ← Local JSON read/write
│  export.py   (Output)              │  ← Markdown/BibTeX export for NotebookLM
├─────────────────────────────────────┤
│  models.py  (Domain Models)         │  ← Pydantic schemas
│  config.py  (Configuration)         │  ← TOML config + .env loading
└─────────────────────────────────────┘
```

### Project Structure

```
scholar-pulse/
├── src/pulse/
│   ├── __init__.py
│   ├── main.py            # CLI command definitions (Typer app)
│   ├── models.py           # Pydantic schemas: Paper, SearchQuery, RankingConfig
│   ├── config.py           # Config loading (~/.scholar-pulse/config.toml + .env)
│   ├── service.py          # Search orchestration, ranking algorithm, caching
│   ├── storage.py          # Local JSON persistence (papers.json)
│   ├── export.py           # Export to Markdown/BibTeX for NotebookLM upload
│   └── providers/
│       ├── __init__.py     # Provider protocol + registry
│       ├── base.py         # AbstractProvider / Protocol definition
│       ├── semantic_scholar.py
│       ├── openalex.py
│       └── arxiv.py
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   ├── test_service.py
│   ├── test_providers.py
│   └── test_export.py
├── pyproject.toml
├── .env.example            # Template for API keys
├── GEMINI.md
└── README.md
```

### Design Patterns

| Pattern | Where | Why |
|---|---|---|
| **Provider / Strategy** | `providers/base.py` | Each API source implements a common `Provider` protocol. New sources added without touching existing code. |
| **Repository** | `storage.py` | Abstracts JSON file I/O behind `load_papers()` / `save_papers()`. Swappable for Neo4j later. |
| **Service Layer** | `service.py` | Orchestrates providers, runs ranking, manages caching. Single place for business logic. |
| **Configuration Object** | `config.py` | Loads TOML + `.env` into a Pydantic `Settings` model. Validated at startup. |
| **Adapter** | `export.py` | Transforms internal `Paper` objects into Markdown or BibTeX output formats. |

---

## Data Models

### `Paper` (Pydantic BaseModel)

| Field | Type | Source | Notes |
|---|---|---|---|
| `id` | `str` | Computed | SHA-256 hash of `doi` or `arxiv_id` or `openalex_id` |
| `title` | `str` | All providers | |
| `authors` | `list[str]` | All providers | |
| `abstract` | `str` | All providers | |
| `doi` | `str \| None` | Semantic Scholar, OpenAlex | Primary dedup key |
| `arxiv_id` | `str \| None` | arXiv | Fallback dedup key |
| `openalex_id` | `str \| None` | OpenAlex | Fallback dedup key |
| `url` | `str` | All providers | Link to paper |
| `pdf_url` | `str \| None` | All providers | Direct PDF link if available |
| `published_date` | `date` | All providers | |
| `citation_count` | `int` | Semantic Scholar, OpenAlex | |
| `keywords` | `list[str]` | Extracted / provider | |
| `source_provider` | `str` | Internal | Which provider found it |
| `relevance_score` | `float \| None` | Computed | Set by ranking algorithm |
| `saved_at` | `datetime` | Internal | When user bookmarked it |

### `SearchQuery` (Pydantic BaseModel)

| Field | Type | Description |
|---|---|---|
| `keywords` | `list[str]` | Search terms |
| `categories` | `list[str]` | arXiv categories or OpenAlex concepts |
| `date_from` | `date \| None` | Filter: published after |
| `date_to` | `date \| None` | Filter: published before |
| `max_results` | `int` | Per-provider result limit (default: 20) |

### `RankingConfig` (Pydantic BaseModel)

| Field | Type | Default | Description |
|---|---|---|---|
| `weight_citations` | `float` | `0.4` | w₁ — citation impact weight |
| `weight_recency` | `float` | `0.3` | w₂ — recency weight |
| `weight_keyword` | `float` | `0.3` | w₃ — keyword match weight |

---

## API Providers

### Tier 1 (v1 — implemented first)

| Provider | Coverage | Auth | Key Feature |
|---|---|---|---|
| **Semantic Scholar** | CS, engineering, broad | Free (API key for higher limits) | Citation counts, TLDR summaries, recommendations |
| **OpenAlex** | 474M+ works, global, strong engineering | Free (polite pool with email) | Broad civil engineering coverage, concepts taxonomy |

### Tier 2 (v2 — future)

| Provider | Coverage | Auth | Key Feature |
|---|---|---|---|
| **arXiv** | CS, physics, math preprints | Free, no key | Latest preprints, category-based browsing |
| **Scopus/Elsevier** | Comprehensive, institutional | API key required | Gold standard for citation analysis |
| **CORE** | Open-access full-text | Free | Full-text access to OA papers |

### Provider Protocol

```python
class PaperProvider(Protocol):
    async def search(self, query: SearchQuery) -> list[Paper]: ...
    async def get_paper(self, paper_id: str) -> Paper | None: ...
```

---

## Ranking Algorithm

### Relevance Score Formula

```
R = w₁ · C_norm + w₂ · Recency + w₃ · S
```

| Symbol | Name | Computation |
|---|---|---|
| `C_norm` | Normalized citations | `log(1 + citations) / log(1 + max_citations_in_set)` |
| `Recency` | Recency score | `1 / (days_since_publication + 1)`, then normalized to [0, 1] |
| `S` | Keyword similarity | `matching_keywords / total_query_keywords` (Jaccard-like on abstract) |
| `w₁, w₂, w₃` | Tunable weights | Configured in `config.toml`, defaults: `0.4, 0.3, 0.3` |

**Graceful degradation:** If citation data is unavailable, the algorithm redistributes weight equally across `Recency` and `S`.

---

## CLI Commands

### Primary Workflow — Automated Digest

The **hero command**. Configure your research interests once, then run weekly.

| Command | Description | Example |
|---|---|---|
| `pulse digest` | Auto-search, rank, show top N papers | `pulse digest` |
| `pulse digest --top 10` | Show top 10 instead of default 5 | `pulse digest --top 10` |
| `pulse digest --export pdf` | Also download open-access PDFs | `pulse digest --export pdf` |
| `pulse digest --export md` | Also generate markdown digest file | `pulse digest --export md` |
| `pulse digest --since 7d` | Only papers from last 7 days | `pulse digest --since 7d` |

**What `pulse digest` does under the hood:**
1. Reads configured keywords + categories from `config.toml`
2. Queries all enabled providers in parallel (async)
3. Deduplicates across providers (by DOI/arXiv ID/OpenAlex ID)
4. Ranks by Relevance Score formula
5. Filters out papers already seen in previous runs
6. Displays top N in a Rich table with scores
7. Optionally exports (PDF download, Markdown, BibTeX)

### Secondary Workflow — Manual Exploration

For ad-hoc deep dives outside your configured interests.

| Command | Description | Example |
|---|---|---|
| `pulse search <query>` | Manual search with custom query | `pulse search "material passport BIM"` |
| `pulse list` | List saved/bookmarked papers | `pulse list --sort score` |
| `pulse save <paper_id>` | Bookmark a paper from results | `pulse save a1b2c3` |
| `pulse remove <paper_id>` | Remove from saved papers | `pulse remove a1b2c3` |
| `pulse export` | Export saved papers | `pulse export --format pdf --output ./papers/` |

### Configuration Commands

| Command | Description | Example |
|---|---|---|
| `pulse config show` | Display current configuration | `pulse config show` |
| `pulse config set <key> <val>` | Update a config value | `pulse config set ranking.weight_citations 0.5` |
| `pulse config init` | Interactive first-time setup | `pulse config init` |

---

## NotebookLM Integration Strategy

NotebookLM has no public API and **cannot search for papers itself**. It only works with content you upload as sources (PDFs, `.md`, `.txt`, URLs — up to 50 sources per notebook, 500k words each). This means `scholar-pulse` must produce **upload-ready files**.

### Export Formats (priority order for NotebookLM)

1. **PDF download** (`pulse export --format pdf`) — downloads open-access PDFs (via `pdf_url` from providers) to an output folder. These are the **primary sources** you upload to NotebookLM. NotebookLM can then summarize, cross-reference, and synthesize across them.
2. **URL list** (`pulse export --format urls`) — for paywalled papers without a downloadable PDF, exports a list of landing-page URLs. NotebookLM can accept web URLs as sources if the page is publicly accessible.
3. **Markdown digest** (`pulse export --format md`) — a curated `.md` file with metadata, abstracts, and scores. Upload as a **companion index source** to NotebookLM so it has an overview of your collection. Also useful standalone as a reading list.
4. **BibTeX export** (`pulse export --format bib`) — `.bib` file for citation managers (Zotero, Mendeley).

### User Workflow

```
# Weekly automated workflow (primary)
pulse digest --top 10 --export pdf       → auto-find, rank, download top papers
→ Upload PDFs + digest.md to NotebookLM
→ Ask NotebookLM to synthesize, compare, and find gaps across papers

# Ad-hoc exploration workflow (secondary)
pulse search "material passport BIM"     → manual deep dive on specific topic
pulse save <id>                          → bookmark interesting papers
pulse export --format pdf                → download saved papers
```

Future: Google Drive upload via `google-api-python-client` for seamless NotebookLM source sync.

---

## Configuration

### File: `~/.scholar-pulse/config.toml`

```toml
[search]
default_keywords = ["digital twin", "BIM", "compliance automation"]
default_categories = ["civil engineering", "construction"]
max_results_per_provider = 20

[ranking]
weight_citations = 0.4
weight_recency = 0.3
weight_keyword = 0.3

[providers]
enabled = ["semantic_scholar", "openalex"]

[export]
default_format = "markdown"     # "markdown" | "bibtex"
output_directory = "~/scholar-pulse-exports"
```

### File: `.env`

```bash
SEMANTIC_SCHOLAR_API_KEY=your_key_here    # Optional, higher rate limits
OPENALEX_EMAIL=your_email@university.edu  # Required for polite pool
```

### Storage: `~/.scholar-pulse/papers.json`

Local persistence for saved/bookmarked papers with deduplication by `id` (hash of DOI/arXiv ID/OpenAlex ID).

---

## Technical Requirements

1. **Duplicate Detection:** Papers are hashed by DOI → arXiv ID → OpenAlex ID (priority order) using SHA-256. Duplicates across providers are merged, preferring the source with richer metadata.
2. **Ranking Algorithm:** Relevance Score with normalized components and tunable weights. Graceful degradation when citation data is missing.
3. **Async Fetching:** Use `httpx.AsyncClient` to query all enabled providers in parallel via `asyncio.gather()`.
4. **Graceful Degradation:** If a provider fails, log a warning and continue with results from remaining providers. If ranking data is incomplete, fallback to recency sort.
5. **Caching:** Search results cached locally with TTL (time-to-live). Cache stored in `~/.scholar-pulse/cache/`. Prevents redundant API calls during iterative exploration.
6. **Extensibility:** New providers added by implementing the `PaperProvider` protocol and registering in the provider registry. No changes to service layer needed.

---

## Model Design Philosophy

Using **plain Pydantic `BaseModel`** (not SQLModel) because:
- JSON storage doesn't need ORM features
- Pydantic models serialize cleanly to JSON, Markdown, and BibTeX
- Future Neo4j integration: Pydantic models → `neomodel` or `py2neo` node mapping via adapter pattern (no model rewrite needed)
- Knowledge graph readiness: `Paper` can become a node, `cites`/`related_to` become relationships
