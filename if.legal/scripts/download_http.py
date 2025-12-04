"""HTTP downloader helper."""
from __future__ import annotations

import hashlib
import os
from dataclasses import asdict, dataclass
from typing import Dict, Optional

import requests


@dataclass
class DownloadResult:
    inventory_path: str
    document_name: str
    url: str
    local_path: str
    status: str
    bytes: int = 0
    sha256: str = ""
    notes: str = ""
    http_status: Optional[int] = None

    def to_dict(self) -> Dict[str, str]:
        data = asdict(self)
        # Align field name with manifest expectation
        data["url_used"] = data.pop("url")
        return data


def download_file(url: str, out_path: str, timeout: int = 30) -> Dict[str, str]:
    """Download a file over HTTP to ``out_path`` with SHA-256 integrity.

    Returns a manifest-friendly dictionary with status and metadata.
    """
    resp = requests.get(url, stream=True, timeout=timeout)
    resp.raise_for_status()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    h = hashlib.sha256()
    bytes_written = 0
    with open(out_path, "wb") as f:
        for chunk in resp.iter_content(32768):
            if chunk:
                f.write(chunk)
                h.update(chunk)
                bytes_written += len(chunk)
    return {
        "url": url,
        "local_path": out_path,
        "bytes": bytes_written,
        "sha256": h.hexdigest(),
        "status": "success",
        "notes": "",
    }


def safe_http_download(url: str, out_path: str, inventory_path: str, document_name: str) -> DownloadResult:
    try:
        info = download_file(url, out_path)
        return DownloadResult(
            inventory_path=inventory_path,
            document_name=document_name,
            url=url,
            local_path=out_path,
            status="success",
            bytes=info.get("bytes", 0),
            sha256=info.get("sha256", ""),
            notes=info.get("notes", ""),
            http_status=200,
        )
    except requests.exceptions.HTTPError as exc:
        status_code = exc.response.status_code if exc.response else None
        status = "requires_login" if status_code and status_code in {401, 403} else "error"
        return DownloadResult(
            inventory_path=inventory_path,
            document_name=document_name,
            url=url,
            local_path=out_path,
            status=status,
            notes=f"HTTP error: {exc}",
            http_status=status_code,
        )
    except requests.exceptions.SSLError as exc:
        return DownloadResult(
            inventory_path=inventory_path,
            document_name=document_name,
            url=url,
            local_path=out_path,
            status="error",
            notes=f"SSL error: {exc}",
        )
    except requests.exceptions.RequestException as exc:
        return DownloadResult(
            inventory_path=inventory_path,
            document_name=document_name,
            url=url,
            local_path=out_path,
            status="error",
            notes=f"Request error: {exc}",
        )


__all__ = ["download_file", "safe_http_download", "DownloadResult"]

