from pydantic import BaseModel
import tomllib
from pathlib import Path
from dotenv import load_dotenv
import os
import tomli_w

class SearchConfig(BaseModel):
    default_keywords: list[str] = [
        "digital twin", "BIM", 
        "compliance automation"
    ]
    default_categories: list[str] = [
        "civil engineering",
        "construction"
    ]
    max_results_per_provider: int = 20

class RankingConfig(BaseModel):
    weight_citation: float = 0.4
    weight_recency: float = 0.3
    weight_keyword: float = 0.3

class ProviderConfig(BaseModel):
    enabled: list[str] = [
        "semantic_scholar",
        "openalex"
    ]

class OutputConfig(BaseModel):
    default_format: str = "markdown"

class Settings(BaseModel):
    search: SearchConfig = SearchConfig()
    ranking: RankingConfig = RankingConfig()
    providers: ProviderConfig = ProviderConfig()
    export: OutputConfig = OutputConfig()

    semantic_scholar_api_key: str | None = None
    openalex_email: str | None = None

def load_config(config_path: Path | None = None) -> Settings:
    load_dotenv()
    config_path = config_path or Path("~/.scholar-pulse/config.toml").expanduser()
    toml_data = {}
    if config_path.exists():
        with open(config_path, "rb") as f:
            toml_data = tomllib.load(f)
    return Settings(
        **toml_data,
        semantic_scholar_api_key=os.getenv("SEMANTIC_SCHOLAR_API_KEY"),
        openalex_email=os.getenv("OPENALEX_EMAIL"),
    )

def save_config(settings: Settings, config_path: Path | None = None):
    config_path = config_path or Path("~/.scholar-pulse/config.toml").expanduser()
    with open(config_path, "wb") as f:
       tomli_w.dump(settings.model_dump(exclude={'semantic_scholar_api_key', 'openalex_email'}), f)