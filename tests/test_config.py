import pytest
from pulse.config import load_config, Settings

def test_load_config():
    config = load_config()
    assert isinstance(config, Settings)
    assert config.search.default_keywords == ["digital twin", "BIM", "compliance automation"]
    assert config.search.default_categories == ["civil engineering", "construction"]
    assert config.search.max_results_per_provider == 20
    assert config.ranking.weight_citation == 0.4
    assert config.ranking.weight_recency == 0.3
    assert config.ranking.weight_keyword == 0.3
    assert config.providers.enabled == ["semantic_scholar", "openalex"]
    assert config.export.default_format == "markdown"
