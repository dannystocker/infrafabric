"""Downloader for EUR-Lex content using SPARQL metadata."""
from __future__ import annotations

from typing import Dict

import requests

from download_http import DownloadResult

SPARQL_ENDPOINT = "https://eur-lex.europa.eu/sparql"


def fetch_metadata(celex_id: str) -> Dict:
    query = f"""
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT ?work ?pdf WHERE {{
  ?work cdm:resource_legal_id_celex "{celex_id}" .
  OPTIONAL {{ ?expression cdm:expression_belongs_to_work ?work .
             ?manifestation cdm:manifestation_manifests_expression ?expression .
             ?pdf cdm:manifestation_file_type 'pdf' .
             ?pdf cdm:manifestation_access_url ?pdf }}
}}
"""
    resp = requests.get(SPARQL_ENDPOINT, params={"format": "json", "query": query}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def download_eurlex(item: Dict) -> DownloadResult:
    inventory_path = item.get("inventory_path", "eu")
    document_name = item.get("document_name", item.get("celex_id", "unknown"))
    celex_id = item.get("celex_id")
    local_path = item.get("local_path", f"raw/eu/{document_name}.pdf")
    if not celex_id:
        return DownloadResult(inventory_path, document_name, "", local_path, "error", notes="Missing celex_id")

    try:
        metadata = fetch_metadata(celex_id)
    except requests.exceptions.RequestException as exc:  # type: ignore[attr-defined]
        return DownloadResult(inventory_path, document_name, "", local_path, "error", notes=f"SPARQL error: {exc}")

    pdf_url = None
    bindings = metadata.get("results", {}).get("bindings", [])
    if bindings:
        pdf_url = bindings[0].get("pdf", {}).get("value")
    if not pdf_url:
        return DownloadResult(
            inventory_path,
            document_name,
            "",
            local_path,
            "no_direct_link",
            notes="No PDF link found in SPARQL metadata",
        )

    try:
        info = requests.get(pdf_url, stream=True, timeout=30)
        info.raise_for_status()
    except requests.exceptions.RequestException as exc:  # type: ignore[attr-defined]
        return DownloadResult(inventory_path, document_name, pdf_url, local_path, "error", notes=str(exc))

    import os

    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    import hashlib

    h = hashlib.sha256()
    bytes_written = 0
    with open(local_path, "wb") as f:
        for chunk in info.iter_content(32768):
            if chunk:
                f.write(chunk)
                h.update(chunk)
                bytes_written += len(chunk)
    return DownloadResult(
        inventory_path,
        document_name,
        pdf_url,
        local_path,
        "success",
        bytes=bytes_written,
        sha256=h.hexdigest(),
        http_status=info.status_code,
    )


__all__ = ["download_eurlex"]
