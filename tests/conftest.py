"""Pytest fixtures shared across API tests."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
import urllib3

# Project root on sys.path so `config` and `utils` imports resolve.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.ssl_setup import enable_system_certificate_store  # noqa: E402

# Must run before requests/urllib3 open HTTPS connections.
enable_system_certificate_store()

from config.config import Settings, get_settings  # noqa: E402
from utils.api_client import APIClient  # noqa: E402

if os.getenv("API_SSL_VERIFY", "true").strip().lower() in ("0", "false", "no", "off"):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Session-scoped application settings."""
    return get_settings()


@pytest.fixture(scope="session")
def base_url(settings: Settings) -> str:
    """API base URL for path construction in tests."""
    return settings.base_url


@pytest.fixture(scope="session")
def api_client(settings: Settings) -> APIClient:
    """Session-scoped API client; closed after the test run."""
    client = APIClient(settings)
    yield client
    client.close()


@pytest.fixture(scope="module")
def posts_list(api_client: APIClient) -> list[dict]:
    """Cached list of all posts for tests that need the full collection."""
    response = api_client.get("/posts")
    response.raise_for_status()
    data = response.json()
    assert isinstance(data, list), "Expected /posts to return a JSON array"
    return data