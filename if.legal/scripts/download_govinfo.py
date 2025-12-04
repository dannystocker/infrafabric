"""Downloader for GovInfo bulk/REST endpoints."""
from __future__ import annotations

from typing import Dict, Optional

import requests

from download_http import DownloadResult


def download_govinfo(item: Dict, api_key: Optional[str] = None) -> DownloadResult:
    """Attempt to download a GovInfo item.

    ``item`` should include ``inventory_path``, ``document_name``, ``url`` (or ``api_endpoint``) and ``local_path``.
    """
    url = item.get("url") or item.get("api_endpoint")
    inventory_path = item.get("inventory_path", "us_federal")
    document_name = item.get("document_name", "unknown")
    local_path = item.get("local_path", "raw/us_federal/unknown")
    headers = {}
    if api_key:
        headers["X-Api-Key"] = api_key
    try:
        resp = requests.get(url, headers=headers, stream=True, timeout=30)
        if resp.status_code in {401, 403}:
            return DownloadResult(
                inventory_path,
                document_name,
                url,
                local_path,
                "requires_login",
                http_status=resp.status_code,
                notes="GovInfo requires API key; set GOVINFO_API_KEY.",
            )
        if resp.status_code == 429:
            return DownloadResult(
                inventory_path,
                document_name,
                url,
                local_path,
                "rate_limited",
                http_status=429,
                notes=resp.headers.get("Retry-After", "Rate limited"),
            )
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:  # type: ignore[attr-defined]
        return DownloadResult(inventory_path, document_name, url, local_path, "error", notes=str(exc))

    # Stream to disk
    bytes_written = 0
    sha256 = ""
    try:
        import hashlib
        import os

        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        h = hashlib.sha256()
        for chunk in resp.iter_content(32768):
            if chunk:
                with open(local_path, "ab") as f:
                    f.write(chunk)
                h.update(chunk)
                bytes_written += len(chunk)
        sha256 = h.hexdigest()
    except Exception as exc:  # noqa: BLE001
        return DownloadResult(inventory_path, document_name, url, local_path, "error", notes=str(exc))

    return DownloadResult(
        inventory_path,
        document_name,
        url,
        local_path,
        "success",
        bytes=bytes_written,
        sha256=sha256,
        http_status=resp.status_code,
    )


__all__ = ["download_govinfo"]
