"""Downloader stub for AustLII content."""
from __future__ import annotations

from typing import Dict

from download_http import DownloadResult, safe_http_download


def download_austlii(item: Dict) -> DownloadResult:
    inventory_path = item.get("inventory_path", "australia")
    document_name = item.get("document_name", "unknown")
    url = item.get("url")
    local_path = item.get("local_path", "raw/australia/unknown")
    if not url:
        return DownloadResult(
            inventory_path,
            document_name,
            "",
            local_path,
            "no_direct_link",
            notes="Provide AustLII URL; ensure robots.txt allows access.",
        )
    return safe_http_download(url, local_path, inventory_path, document_name)


__all__ = ["download_austlii"]
