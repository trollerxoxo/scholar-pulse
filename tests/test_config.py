import pytest
import tomli_w
from pulse.config import load_config, save_config, Settings


# --- load_config tests ---

def test_load_config_defaults(tmp_path):
    """When no config file exists, load_config returns defaults."""
    config = load_config(config_path=tmp_path / "config.toml")
    assert isinstance(config, Settings)
    assert config.search.default_keywords == ["digital twin", "BIM", "compliance automation"]
    assert config.search.default_categories == ["civil engineering", "construction"]
    assert config.search.max_results_per_provider == 20
    assert config.ranking.weight_citation == 0.4
    assert config.ranking.weight_recency == 0.3
    assert config.ranking.weight_keyword == 0.3
    assert config.providers.enabled == ["semantic_scholar", "openalex"]
    assert config.export.default_format == "md"


def test_load_config_reads_toml(tmp_path):
    """load_config reads values from a TOML file."""
    config_file = tmp_path / "config.toml"
    toml_data = {
        "search": {"default_keywords": ["concrete", "steel"]},
        "ranking": {"weight_citation": 0.8},
    }
    with open(config_file, "wb") as f:
        tomli_w.dump(toml_data, f)

    config = load_config(config_path=config_file)
    assert config.search.default_keywords == ["concrete", "steel"]
    assert config.ranking.weight_citation == 0.8
    # Unset fields keep their defaults
    assert config.ranking.weight_recency == 0.3
    assert config.providers.enabled == ["semantic_scholar", "openalex"]


# --- save_config tests ---

def test_save_config_creates_file(tmp_path):
    """save_config creates a valid TOML file."""
    config_file = tmp_path / "config.toml"
    settings = Settings()
    save_config(settings, config_path=config_file)
    assert config_file.exists()


def test_save_config_excludes_secrets(tmp_path):
    """save_config does not write API keys or email to TOML."""
    config_file = tmp_path / "config.toml"
    settings = Settings(
        semantic_scholar_api_key="secret_key_123",
        openalex_email="test@university.edu",
    )
    save_config(settings, config_path=config_file)
    content = config_file.read_text()
    assert "secret_key_123" not in content
    assert "test@university.edu" not in content
    assert "semantic_scholar_api_key" not in content
    assert "openalex_email" not in content


# --- Round-trip tests ---

def test_save_then_load_roundtrip(tmp_path):
    """Settings survive a save → load round-trip."""
    config_file = tmp_path / "config.toml"
    original = Settings()
    original.search.default_keywords = ["AI", "robotics"]
    original.ranking.weight_citation = 0.6

    save_config(original, config_path=config_file)
    loaded = load_config(config_path=config_file)

    assert loaded.search.default_keywords == ["AI", "robotics"]
    assert loaded.ranking.weight_citation == 0.6
    # Unchanged defaults preserved
    assert loaded.ranking.weight_recency == 0.3
    assert loaded.export.default_format == "md"


def test_save_then_load_preserves_all_sections(tmp_path):
    """All config sections survive a round-trip."""
    config_file = tmp_path / "config.toml"
    original = Settings()
    original.providers.enabled = ["openalex"]
    original.export.default_format = "bibtex"

    save_config(original, config_path=config_file)
    loaded = load_config(config_path=config_file)

    assert loaded.providers.enabled == ["openalex"]
    assert loaded.export.default_format == "bibtex"