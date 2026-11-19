"""Central configuration for API automation."""

from dataclasses import dataclass, field
import os
from typing import Mapping, Union


def _resolve_ssl_verify() -> Union[bool, str]:
    """
    TLS verification: true by default.

    Set API_SSL_VERIFY=false only for local debugging behind misconfigured proxies.
    Set API_CA_BUNDLE=/path/to/corporate-ca.pem to trust a corporate root CA.
    """
    bundle = os.getenv("API_CA_BUNDLE", "").strip()
    if bundle and os.path.isfile(bundle):
        return bundle
    for env_name in ("REQUESTS_CA_BUNDLE", "SSL_CERT_FILE"):
        candidate = os.getenv(env_name, "").strip()
        if candidate and os.path.isfile(candidate):
            return candidate
    flag = os.getenv("API_SSL_VERIFY", "true").strip().lower()
    if flag in ("0", "false", "no", "off"):
        return False
    return True


@dataclass(frozen=True)
class Settings:
    """Application and API settings loaded from environment with sensible defaults."""

    base_url: str = os.getenv(
        "API_BASE_URL", "https://jsonplaceholder.typicode.com"
    )
    request_timeout: int = int(os.getenv("API_REQUEST_TIMEOUT", "30"))
    response_time_threshold_ms: float = float(
        os.getenv("API_RESPONSE_TIME_THRESHOLD_MS", "5000")
    )
    default_headers: Mapping[str, str] = field(
        default_factory=lambda: {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    )
    ssl_verify: Union[bool, str] = field(default_factory=_resolve_ssl_verify)


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return singleton Settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings