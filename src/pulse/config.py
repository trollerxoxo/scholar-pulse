from pydantic import BaseModel
import tomllib
from pathlib import Path

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

def load_config() -> Settings:
    config_path = Path("~/.scholar-pulse/config.toml").expanduser()
    if config_path.exists():
        with open(config_path, "rb") as f:
            return Settings(**tomllib.load(f))
    return Settings()

