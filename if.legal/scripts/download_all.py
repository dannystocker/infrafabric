"""Orchestrator for downloading items listed in LEGAL_CORPUS_IMPORT_LIST.md."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import re
from typing import Dict, List

from slugify import slugify

import download_http
from download_austlii import download_austlii
from download_canlii import download_canlii
from download_courtlistener import download_courtlistener
from download_datasets import download_dataset
from download_ecfr import download_ecfr
from download_eurlex import download_eurlex
from download_govinfo import download_govinfo


def _infer_subdir(inventory_path: str) -> str:
    """Infer a raw/ subdirectory from the inventory section path."""
    inventory_path = inventory_path.lower()
    if inventory_path.startswith("1. us federal law"):
        return "us_federal"
    if inventory_path.startswith("2. us state law"):
        return "us_state"
    if inventory_path.startswith("3. european union"):
        return "eu"
    if inventory_path.startswith("4. germany"):
        return "germany"
    if inventory_path.startswith("5. france"):
        return "france"
    if inventory_path.startswith("6. canada"):
        return "canada"
    if inventory_path.startswith("7. australia"):
        return "australia"
    if inventory_path.startswith("8. united kingdom"):
        return "uk"
    if inventory_path.startswith("9. contract datasets"):
        return "datasets"
    if inventory_path.startswith("10. landmark case law"):
        return "caselaw"
    if inventory_path.startswith("11. industry standards"):
        return "industry"
    return "misc"


def parse_inventory(path: str) -> List[Dict]:
    """Parse the markdown inventory into a list of items.

    The parser walks headings and markdown tables, extracting any row with an HTTP(S) URL.
    """
    items: List[Dict] = []
    if not os.path.exists(path):
        return items

    current_section = ""
    current_subsection = ""
    headers: List[str] = []

    def parse_row(line: str) -> List[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")
            stripped = line.strip()

            if stripped.startswith("## "):
                current_section = stripped[3:].strip()
                current_subsection = ""
                headers = []
                continue
            if stripped.startswith("### "):
                current_subsection = stripped[4:].strip()
                headers = []
                continue

            if not stripped.startswith("|"):
                continue

            # Separator row like |-----|----|
            if set(stripped.replace("|", "").replace("-", "").replace(" ", "")) == set():
                continue

            cells = parse_row(stripped)
            # Header row
            if headers == []:
                headers = cells
                continue

            # Data row
            row = dict(zip(headers, cells))

            def clean(value: str) -> str:
                return re.sub(r"\*\*", "", value).strip()

            row = {k: clean(v) for k, v in row.items()}

            # Extract URL
            url = ""
            for key, value in row.items():
                if "http://" in value or "https://" in value:
                    # Take the first URL-like token
                    match = re.search(r"https?://\S+", value)
                    if match:
                        url = match.group(0).rstrip(")")
                        break

            # Build document name from common column names
            doc_name = (
                row.get("Document")
                or row.get("Dataset")
                or row.get("Case")
                or row.get("Article")
                or row.get("Section")
                or row.get(headers[0], "document")
            )
            subject = row.get("Subject") or row.get("Key Issue") or row.get("Standard")
            if subject:
                doc_name = f"{doc_name} - {subject}"

            inventory_path = " / ".join(p for p in (current_section, current_subsection) if p)
            subdir = _infer_subdir(current_section or "")

            item: Dict = {
                "inventory_path": inventory_path or "unspecified",
                "document_name": doc_name,
                "url": url,
                "priority": row.get("Priority", ""),
                "subdir": subdir,
            }

            if "CELEX ID" in row:
                item["celex_id"] = row["CELEX ID"]

            # Flag datasets for special handling
            if current_section.lower().startswith("9. contract datasets"):
                item["type"] = "dataset"

            # For rows without URLs (for example, many case law entries), keep them so they
            # appear in the manifest with `no_direct_link`.
            if not url:
                item["no_direct_link"] = True

            items.append(item)

    return items


def write_manifest_row(manifest_path: str, result: Dict[str, str]) -> None:
    exists = os.path.exists(manifest_path)
    with open(manifest_path, "a", newline="", encoding="utf-8") as f:
        fieldnames = [
            "inventory_path",
            "document_name",
            "url_used",
            "local_path",
            "status",
            "bytes",
            "sha256",
            "notes",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow({k: result.get(k, "") for k in fieldnames})


def log_download(log_path: str, result: Dict[str, str]) -> None:
    exists = os.path.exists(log_path)
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        fieldnames = [
            "timestamp",
            "inventory_path",
            "document_name",
            "url_used",
            "local_path",
            "status",
            "bytes",
            "sha256",
            "notes",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        row = {k: result.get(k, "") for k in fieldnames if k != "timestamp"}
        row["timestamp"] = dt.datetime.utcnow().isoformat()
        writer.writerow(row)


def choose_downloader(item: Dict) -> str:
    url = item.get("url", "") or ""
    if item.get("type") == "dataset":
        return "dataset"
    if "courtlistener" in url:
        return "courtlistener"
    if "govinfo.gov" in url:
        return "govinfo"
    if "ecfr.gov" in url:
        return "ecfr"
    if "eur-lex.europa.eu" in url:
        return "eurlex"
    if "canlii.org" in url:
        return "canlii"
    if "austlii.edu.au" in url or "austlii" in url:
        return "austlii"
    return "http"


def process_item(item: Dict, args) -> Dict[str, str]:
    inventory_path = item.get("inventory_path", "unspecified")
    document_name = item.get("document_name", "document")
    url = item.get("url", "")

    # Items like many case law entries have no direct link yet.
    if item.get("no_direct_link") and not url:
        from download_http import DownloadResult

        result = DownloadResult(
            inventory_path=inventory_path,
            document_name=document_name,
            url="",
            local_path="",
            status="no_direct_link",
            notes="No direct URL in inventory; extend downloader to handle by citation or identifier.",
        )
        return result.to_dict()

    downloader = choose_downloader(item)
    safe_name = slugify(document_name) or "document"
    subdir = item.get("subdir") or _infer_subdir(inventory_path)
    base_dir = os.path.join("raw", subdir)
    os.makedirs(base_dir, exist_ok=True)
    filename = safe_name
    # Preserve file extension when URL ends with something obvious
    for ext in (".pdf", ".html", ".htm", ".xml", ".json"):
        if url.lower().endswith(ext):
            filename = f"{safe_name}{ext}"
            break
    local_path = os.path.join(base_dir, filename)
    item["local_path"] = local_path

    if downloader == "http":
        result = download_http.safe_http_download(url, local_path, inventory_path, document_name)
    elif downloader == "govinfo":
        result = download_govinfo(item, api_key=args.govinfo_api_key)
    elif downloader == "ecfr":
        result = download_ecfr(item)
    elif downloader == "eurlex":
        # Prefer CELEX-based download if CELEX ID is present.
        if item.get("celex_id"):
            result = download_eurlex(item)
        else:
            result = download_http.safe_http_download(url, local_path, inventory_path, document_name)
    elif downloader == "canlii":
        result = download_canlii(item)
    elif downloader == "austlii":
        result = download_austlii(item)
    elif downloader == "courtlistener":
        result = download_courtlistener(item, token=args.courtlistener_token)
    elif downloader == "dataset":
        result = download_dataset(item)
    else:
        from download_http import DownloadResult

        result = DownloadResult(
            inventory_path,
            document_name,
            url,
            local_path,
            "error",
            notes="Unknown downloader",
        )
    return result.to_dict()


def main() -> None:
    parser = argparse.ArgumentParser(description="Download legal corpus inventory")
    parser.add_argument(
        "--inventory",
        default="LEGAL_CORPUS_IMPORT_LIST.md",
        help="Inventory markdown file",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="Not used yet; reserved for future parallelism",
    )
    parser.add_argument(
        "--retry-status",
        default=None,
        help="If set, only retry items with this status",
    )
    parser.add_argument(
        "--govinfo-api-key",
        dest="govinfo_api_key",
        default=os.environ.get("GOVINFO_API_KEY"),
    )
    parser.add_argument(
        "--courtlistener-token",
        dest="courtlistener_token",
        default=os.environ.get("COURTLISTENER_TOKEN"),
    )
    args = parser.parse_args()

    inventory_items = parse_inventory(args.inventory)
    manifest_path = "manifests/download_manifest.csv"
    log_path = "logs/download_log.csv"

    if not inventory_items:
        placeholder = {
            "inventory_path": "pending_inventory",
            "document_name": "pending_inventory",
            "url_used": "",
            "local_path": "",
            "status": "pending_inventory",
            "bytes": "",
            "sha256": "",
            "notes": "Inventory missing; provide LEGAL_CORPUS_IMPORT_LIST.md",
        }
        write_manifest_row(manifest_path, placeholder)
        log_download(log_path, placeholder)
        print("Inventory missing; wrote placeholder manifest row.")
        return

    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    for item in inventory_items:
        result = process_item(item, args)
        write_manifest_row(manifest_path, result)
        log_download(log_path, result)
        print(f"Processed {item.get('document_name')}: {result.get('status')}")


if __name__ == "__main__":
    main()
