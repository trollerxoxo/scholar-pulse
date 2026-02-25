import tomli_w
from unittest.mock import patch
from typer.testing import CliRunner
from pulse.main import app
from pulse.config import Settings, SearchConfig, RankingConfig, ProviderConfig, OutputConfig

runner = CliRunner()


# --- config show ---

def test_config_show_displays_keys():
    """config show should display all config keys."""
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "default_keywords" in result.output
    assert "weight_citation" in result.output
    assert "default_format" in result.output


def test_config_show_masks_secrets():
    with patch("pulse.main.config.load_config") as mock:
        mock.return_value = Settings(
            semantic_scholar_api_key="secret_key_12345",
            openalex_email="test@university.edu",
        )
        result = runner.invoke(app, ["config", "show"])
    assert "•" in result.output
    assert "secret_key_12345" not in result.output


# --- config set ---

def test_config_set_valid_float(tmp_path):
    """config set should update a float value and persist it."""
    config_file = tmp_path / "config.toml"
    # Create an initial config
    with open(config_file, "wb") as f:
        tomli_w.dump({"ranking": {"weight_citation": 0.4}}, f)

    with patch("pulse.main.config.load_config") as mock_load, \
         patch("pulse.main.config.save_config") as mock_save:
        mock_load.return_value = Settings()
        result = runner.invoke(app, ["config", "set", "weight_citation", "0.6"])

    assert result.exit_code == 0
    assert "Set weight_citation to 0.6" in result.output
    # Verify save was called
    mock_save.assert_called_once()


def test_config_set_valid_string(tmp_path):
    """config set should handle plain string values."""
    with patch("pulse.main.config.load_config") as mock_load, \
         patch("pulse.main.config.save_config") as mock_save:
        mock_load.return_value = Settings()
        result = runner.invoke(app, ["config", "set", "default_format", "bibtex"])

    assert result.exit_code == 0
    assert "Set default_format to bibtex" in result.output


def test_config_set_valid_list():
    """config set should handle JSON list values."""
    with patch("pulse.main.config.load_config") as mock_load, \
         patch("pulse.main.config.save_config") as mock_save:
        mock_load.return_value = Settings()
        result = runner.invoke(app, ["config", "set", "default_keywords", '["AI", "BIM"]'])

    assert result.exit_code == 0
    assert "Set default_keywords to" in result.output


def test_config_set_invalid_key():
    """config set should reject unknown keys and show available keys."""
    with patch("pulse.main.config.load_config") as mock_load, \
         patch("pulse.main.config.save_config") as mock_save:
        mock_load.return_value = Settings()
        result = runner.invoke(app, ["config", "set", "nonexistent_field", "42"])

    assert result.exit_code == 0
    assert "Unknown key" in result.output
    assert "default_keywords" in result.output  # shows available keys
    mock_save.assert_not_called()


# --- config init ---

def test_config_init_creates_config(tmp_path):
    """config init should create a config file from prompted values."""
    config_file = tmp_path / "config.toml"

    with patch("pulse.main.Path") as mock_path_cls, \
         patch("pulse.main.config.save_config") as mock_save, \
         patch("pulse.main.config_show"):
        # Make Path("~/.scholar-pulse/config.toml").expanduser() return our tmp file
        mock_path_instance = mock_path_cls.return_value
        mock_path_instance.expanduser.return_value = config_file

        user_input = "\n".join([
            "BIM, concrete",           # keywords
            "civil engineering",       # categories
            "20",                      # max_results
            "0.4",                     # weight_citation
            "0.3",                     # weight_recency
            "0.3",                     # weight_keyword
            "semantic_scholar",        # enabled
            "markdown",                # default_format
            "y",                       # Save config? confirm
        ])
        result = runner.invoke(app, ["config", "init"], input=user_input)

    assert result.exit_code == 0
    assert "Config initialized" in result.output
    mock_save.assert_called_once()


def test_config_init_aborts_on_no_overwrite(tmp_path):
    """config init should abort if user declines overwrite."""
    config_file = tmp_path / "config.toml"
    # Create existing file
    config_file.write_bytes(b"")

    with patch("pulse.main.Path") as mock_path_cls:
        mock_path_instance = mock_path_cls.return_value
        mock_path_instance.expanduser.return_value = config_file

        result = runner.invoke(app, ["config", "init"], input="n\n")

    assert result.exit_code == 0
    assert "Config initialized" not in result.output