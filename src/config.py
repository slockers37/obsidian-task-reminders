import yaml
import os
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class GotifyConfig:
    url: str
    token: str

@dataclass
class RetryConfig:
    max_attempts: int
    backoff_factor: float

@dataclass
class AppConfig:
    vault_path: str
    timezone: str
    gotify: GotifyConfig
    retry: RetryConfig
    task_store_db_path: str
    scheduler_db_path: str

def load_config(path: str = "config.yml") -> AppConfig:
    with open(path, 'r') as f:
        config_data = yaml.safe_load(f)

    gotify_token = os.getenv("GOTIFY_TOKEN")
    if not gotify_token:
        raise ValueError("GOTIFY_TOKEN environment variable not set.")

    config = AppConfig(
        vault_path=config_data['vault_path'],
        timezone=config_data['timezone'],
        gotify=GotifyConfig(
            url=config_data['gotify']['url'],
            token=gotify_token
        ),
        retry=RetryConfig(
            max_attempts=config_data['retry']['max_attempts'],
            backoff_factor=config_data['retry']['backoff_factor']
        ),
        task_store_db_path=config_data['database']['task_store_db_path'],
        scheduler_db_path=config_data['database']['scheduler_db_path']
    )
    return config
