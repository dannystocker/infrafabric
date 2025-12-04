"""Downloader for open datasets (e.g., CUAD, LEDGAR)."""
from __future__ import annotations

import os
from typing import Dict

from download_http import DownloadResult, safe_http_download


def download_dataset(item: Dict) -> DownloadResult:
    inventory_path = item.get("inventory_path", "datasets")
    document_name = item.get("document_name", "dataset")
    url = item.get("url")
    filename = item.get("filename") or (
        document_name.replace(" ", "_") + (".zip" if url and url.endswith(".zip") else "")
    )
    local_path = item.get("local_path") or os.path.join("raw/datasets", filename)
    if not url:
        return DownloadResult(
            inventory_path,
            document_name,
            "",
            local_path,
            "no_direct_link",
            notes="Add dataset URL to proceed",
        )
    return safe_http_download(url, local_path, inventory_path, document_name)


__all__ = ["download_dataset"]
