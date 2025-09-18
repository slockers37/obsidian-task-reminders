import pytest
import os
from config import load_config

def test_load_config_success(monkeypatch, tmp_path):
    config_content = """
vault_path: "/test/vault"
timezone: "America/New_York"
gotify:
  url: "http://test.gotify"
retry:
  max_attempts: 3
  backoff_factor: 1.0
"""
    config_file = tmp_path / "config.yml"
    config_file.write_text(config_content)
    
    monkeypatch.setenv("GOTIFY_TOKEN", "test_token")
    
    config = load_config(str(config_file))
    
    assert config.vault_path == "/test/vault"
    assert config.timezone == "America/New_York"
    assert config.gotify.url == "http://test.gotify"
    assert config.gotify.token == "test_token"
    assert config.retry.max_attempts == 3
    assert config.retry.backoff_factor == 1.0

def test_load_config_missing_token(tmp_path):
    config_content = """
vault_path: "/test/vault"
timezone: "America/New_York"
gotify:
  url: "http://test.gotify"
retry:
  max_attempts: 3
  backoff_factor: 1.0
"""
    config_file = tmp_path / "config.yml"
    config_file.write_text(config_content)
    
    # Unset the environment variable to test the failure case
    if "GOTIFY_TOKEN" in os.environ:
        del os.environ["GOTIFY_TOKEN"]

    with pytest.raises(ValueError, match="GOTIFY_TOKEN environment variable not set."):
        load_config(str(config_file))
