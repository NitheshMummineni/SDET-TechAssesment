"""Reusable HTTP client wrapper around the Requests library."""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Optional
from urllib.parse import urljoin

import requests
from requests import Response
from requests.exceptions import RequestException, Timeout

from config.config import Settings, get_settings
from utils.ssl_setup import enable_system_certificate_store

enable_system_certificate_store()


class APIClientError(Exception):
    """Raised when the API client cannot complete a request."""


class APIClient:
    """HTTP client with shared base URL, timeout, and header handling."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self._settings = settings or get_settings()
        self._session = requests.Session()
        self._session.headers.update(self._settings.default_headers)

    @property
    def base_url(self) -> str:
        return self._settings.base_url.rstrip("/")

    @property
    def timeout(self) -> int:
        return self._settings.request_timeout

    def _build_url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        normalized = path if path.startswith("/") else f"/{path}"
        return urljoin(f"{self.base_url}/", normalized.lstrip("/"))

    def _merge_headers(
        self, headers: Optional[Mapping[str, str]]
    ) -> MutableMapping[str, str]:
        merged: MutableMapping[str, str] = dict(self._session.headers)
        if headers:
            merged.update(headers)
        return merged

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Optional[Any] = None,
        data: Optional[Any] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Response:
        url = self._build_url(path)
        effective_timeout = timeout if timeout is not None else self.timeout
        try:
            return self._session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json,
                data=data,
                headers=self._merge_headers(headers),
                timeout=effective_timeout,
                verify=self._settings.ssl_verify,
            )
        except Timeout as exc:
            raise APIClientError(
                f"Request timed out after {effective_timeout}s: {method} {url}"
            ) from exc
        except RequestException as exc:
            raise APIClientError(
                f"Request failed: {method} {url} — {exc}"
            ) from exc

    def get(
        self,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Response:
        return self._request(
            "GET", path, params=params, headers=headers, timeout=timeout
        )

    def post(
        self,
        path: str,
        *,
        json: Optional[Any] = None,
        data: Optional[Any] = None,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Response:
        return self._request(
            "POST",
            path,
            json=json,
            data=data,
            params=params,
            headers=headers,
            timeout=timeout,
        )

    def put(
        self,
        path: str,
        *,
        json: Optional[Any] = None,
        data: Optional[Any] = None,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Response:
        return self._request(
            "PUT",
            path,
            json=json,
            data=data,
            params=params,
            headers=headers,
            timeout=timeout,
        )

    def patch(
        self,
        path: str,
        *,
        json: Optional[Any] = None,
        data: Optional[Any] = None,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Response:
        return self._request(
            "PATCH",
            path,
            json=json,
            data=data,
            params=params,
            headers=headers,
            timeout=timeout,
        )

    def delete(
        self,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Response:
        return self._request(
            "DELETE", path, params=params, headers=headers, timeout=timeout
        )

    def close(self) -> None:
        self._session.close()