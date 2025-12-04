"""Downloader for the eCFR v1 API or HTML endpoints."""
from __future__ import annotations

from typing import Dict

import requests

from download_http import DownloadResult


def download_ecfr(item: Dict, api_base: str = "https://api.ecfr.gov/v1") -> DownloadResult:
    inventory_path = item.get("inventory_path", "us_federal")
    document_name = item.get("document_name", "unknown")
    path = item.get("path") or item.get("url")
    local_path = item.get("local_path", "raw/us_federal/ecfr_unknown.json")

    url = path if path and path.startswith("http") else f"{api_base}{path}" if path else api_base
    params = item.get("params") or {}
    try:
        resp = requests.get(url, params=params, timeout=30)
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

    import os

    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    try:
        # Try JSON first, fall back to raw text
        try:
            content = resp.json()
            import json

            with open(local_path, "w", encoding="utf-8") as f:
                json.dump(content, f)
            pretty_path = f"{local_path}.pretty.json"
            with open(pretty_path, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=2)
            raw_bytes = resp.content
        except ValueError:
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(resp.text)
            raw_bytes = resp.content
    except Exception as exc:  # noqa: BLE001
        return DownloadResult(inventory_path, document_name, url, local_path, "error", notes=str(exc))

    import hashlib

    h = hashlib.sha256(raw_bytes)
    return DownloadResult(
        inventory_path,
        document_name,
        url,
        local_path,
        "success",
        bytes=len(raw_bytes),
        sha256=h.hexdigest(),
        http_status=resp.status_code,
    )


__all__ = ["download_ecfr"]
