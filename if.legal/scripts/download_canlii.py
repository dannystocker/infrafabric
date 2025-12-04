"""Downloader stub for CanLII."""
from __future__ import annotations

from typing import Dict

from download_http import DownloadResult, safe_http_download


def download_canlii(item: Dict) -> DownloadResult:
    inventory_path = item.get("inventory_path", "canada")
    document_name = item.get("document_name", "unknown")
    url = item.get("url")
    local_path = item.get("local_path", "raw/canada/unknown")
    if not url:
        return DownloadResult(
            inventory_path,
            document_name,
            "",
            local_path,
            "no_direct_link",
            notes="Provide CanLII download URL or API parameters.",
        )
    # Respect robots/terms; full implementation should call official APIs when available.
    return safe_http_download(url, local_path, inventory_path, document_name)


__all__ = ["download_canlii"]
