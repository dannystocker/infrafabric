"""Downloader for CourtListener opinions."""
from __future__ import annotations

import json
import os
from typing import Dict, Optional

import requests

from download_http import DownloadResult

COURTLISTENER_BASE = "https://www.courtlistener.com/api/rest/v3/opinions/"


def download_courtlistener(item: Dict, token: Optional[str] = None) -> DownloadResult:
    inventory_path = item.get("inventory_path", "caselaw")
    document_name = item.get("document_name", "unknown")
    opinion_id = item.get("opinion_id")
    url = item.get("url") or (f"{COURTLISTENER_BASE}{opinion_id}/" if opinion_id else None)
    local_path = item.get("local_path", f"raw/caselaw/{document_name}.json")
    if not url:
        return DownloadResult(
            inventory_path,
            document_name,
            "",
            local_path,
            "no_direct_link",
            notes="Provide CourtListener opinion_id or url",
        )

    headers = {"User-Agent": "if-legal-corpus/0.1"}
    if token:
        headers["Authorization"] = f"Token {token}"
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code in {401, 403}:
            return DownloadResult(
                inventory_path,
                document_name,
                url,
                local_path,
                "requires_login",
                http_status=resp.status_code,
                notes="CourtListener token required for this request",
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

    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    try:
        data = resp.json()
    except ValueError:
        return DownloadResult(inventory_path, document_name, url, local_path, "error", notes="Non-JSON response")

    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    pretty_path = f"{local_path}.pretty.json"
    with open(pretty_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    import hashlib

    h = hashlib.sha256(resp.content)
    return DownloadResult(
        inventory_path,
        document_name,
        url,
        local_path,
        "success",
        bytes=len(resp.content),
        sha256=h.hexdigest(),
        http_status=resp.status_code,
    )


__all__ = ["download_courtlistener"]
