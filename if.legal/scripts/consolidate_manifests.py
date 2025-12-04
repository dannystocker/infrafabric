#!/usr/bin/env python3
"""
Consolidate all manifest CSV files into a single master manifest.
Handles different CSV formats and removes duplicates.
"""

import os
import csv
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import hashlib

def detect_jurisdiction(local_path: str) -> str:
    """Detect jurisdiction from local_path."""
    if not local_path:
        return "unknown"

    path_lower = local_path.lower()

    # Map jurisdiction detection
    if "spain" in path_lower:
        return "spain"
    elif "uk" in path_lower or "united.kingdom" in path_lower:
        return "uk"
    elif "usa-ca" in path_lower or "/ca/" in path_lower:
        return "us-ca"
    elif "usa-ny" in path_lower or "/ny/" in path_lower:
        return "us-ny"
    elif "usa-tx" in path_lower or "/tx/" in path_lower:
        return "us-tx"
    elif "usa-fl" in path_lower or "/fl/" in path_lower:
        return "us-fl"
    elif "us" in path_lower or "usa" in path_lower or "federal" in path_lower:
        return "us-federal"
    elif "canada" in path_lower or "quebec" in path_lower:
        if "quebec" in path_lower:
            return "quebec"
        return "canada"
    elif "australia" in path_lower or "au" in path_lower:
        return "australia"
    elif "germany" in path_lower or "de" in path_lower:
        return "germany"
    elif "france" in path_lower or "fr" in path_lower:
        return "france"
    elif "eu" in path_lower or "europe" in path_lower:
        return "eu"
    else:
        return "unknown"

def detect_vertical(document_name: str, local_path: str = "") -> str:
    """Detect legal vertical from document name and path."""
    combined = f"{document_name} {local_path}".lower()

    # Map vertical detection
    if any(w in combined for w in ["housing", "landlord", "tenant", "rental", "eviction"]):
        return "housing"
    elif any(w in combined for w in ["insurance", "cover", "claim", "policy"]):
        return "insurance"
    elif any(w in combined for w in ["construction", "building", "lien", "contractor", "payment bond"]):
        return "construction"
    elif any(w in combined for w in ["criminal", "crime", "fraud", "bribery", "money.launder", "offense"]):
        return "criminal"
    elif any(w in combined for w in ["copyright", "patent", "trademark", "intellectual.property", "work.for.hire", "ownership"]):
        return "ip"
    elif any(w in combined for w in ["contract", "agreement", "terms", "condition"]):
        return "contracts"
    elif any(w in combined for w in ["employment", "labor", "work", "worker", "employee"]):
        return "employment"
    elif any(w in combined for w in ["tax", "accounting", "irpf", "iva"]):
        return "tax"
    elif any(w in combined for w in ["privacy", "data", "gdpr"]):
        return "privacy"
    elif any(w in combined for w in ["property", "real.estate", "mortgage", "cadastr"]):
        return "property"
    else:
        return "general"

def parse_manifests(manifest_dir: str) -> dict:
    """Parse all CSV manifests and return consolidated data."""

    manifest_path = Path(manifest_dir)
    all_records = {}  # key: local_path, value: record

    # CSV files to process
    csv_files = list(manifest_path.glob("*.csv"))
    print(f"Found {len(csv_files)} CSV manifest files")

    for csv_file in sorted(csv_files):
        print(f"\nProcessing {csv_file.name}...")

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                # Handle missing headers by reading first row as header
                if reader.fieldnames is None:
                    f.seek(0)
                    first_row = next(f)
                    continue

                row_count = 0
                for row in reader:
                    # Skip empty rows and metadata rows
                    if not any(row.values()) or row.get("inventory_path") == "Summary Statistics":
                        continue

                    # Normalize field names
                    local_path = (
                        row.get("local_path") or
                        row.get("filepath") or
                        row.get("path") or
                        ""
                    )

                    document_name = (
                        row.get("document_name") or
                        row.get("document") or
                        row.get("name") or
                        ""
                    )

                    url = (
                        row.get("url_used") or
                        row.get("url") or
                        row.get("source_url") or
                        ""
                    )

                    status = (
                        row.get("status") or
                        ""
                    )

                    # Normalize status values - handle SUCCESS vs success
                    status_lower = status.lower() if status else ""

                    # Skip placeholder rows
                    if status == "no_direct_link":
                        continue

                    # For insurance manifest: can have local_path missing but document_name present
                    # In that case, create a derived local_path
                    if not local_path and document_name:
                        # For insurance manifest without local_path, we'll add a computed one
                        local_path = f"raw/unprocessed/{document_name.replace(' ', '_').lower()}"

                    if not document_name:
                        continue

                    # Use local_path as unique key
                    if local_path and local_path not in all_records:
                        all_records[local_path] = {
                            "document_name": document_name,
                            "url": url,
                            "local_path": local_path,
                            "status": status,
                            "bytes": row.get("bytes") or row.get("size_bytes") or row.get("file_size_bytes") or "0",
                            "sha256": row.get("sha256") or row.get("sha256_hash") or "",
                            "source_manifest": csv_file.name,
                            "jurisdiction": row.get("jurisdiction") or detect_jurisdiction(local_path),
                            "legal_vertical": row.get("category") or detect_vertical(document_name, local_path),
                            "download_date": row.get("timestamp") or row.get("downloaded_date") or row.get("download_timestamp") or "2025-11-28",
                            "priority": row.get("priority", "P1"),
                            "notes": row.get("notes", "")
                        }
                        row_count += 1

                print(f"  -> Extracted {row_count} valid records from {csv_file.name}")

        except Exception as e:
            print(f"  ERROR processing {csv_file.name}: {e}")
            continue

    return all_records

def write_master_manifest(records: dict, output_path: str):
    """Write consolidated manifest to CSV."""

    # Sort records by jurisdiction, then vertical, then document name
    sorted_records = sorted(
        records.values(),
        key=lambda x: (x["jurisdiction"], x["legal_vertical"], x["document_name"])
    )

    # Define column order
    columns = [
        "document_name",
        "jurisdiction",
        "legal_vertical",
        "url",
        "local_path",
        "status",
        "bytes",
        "sha256",
        "download_date",
        "priority",
        "source_manifest",
        "notes"
    ]

    # Write CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()

        for record in sorted_records:
            writer.writerow({col: record.get(col, "") for col in columns})

    print(f"\nWrote {len(sorted_records)} records to {output_path}")
    return len(sorted_records)

def generate_summary(records: dict) -> dict:
    """Generate summary statistics."""

    summary = {
        "total_documents": len(records),
        "by_jurisdiction": defaultdict(int),
        "by_vertical": defaultdict(int),
        "by_status": defaultdict(int),
        "total_bytes": 0,
        "download_success": 0,
    }

    for record in records.values():
        summary["by_jurisdiction"][record["jurisdiction"]] += 1
        summary["by_vertical"][record["legal_vertical"]] += 1
        summary["by_status"][record["status"]] += 1

        try:
            bytes_val = int(record.get("bytes", 0) or 0)
            summary["total_bytes"] += bytes_val
        except:
            pass

        if record.get("status") == "success":
            summary["download_success"] += 1

    # Convert defaultdicts to regular dicts
    summary["by_jurisdiction"] = dict(summary["by_jurisdiction"])
    summary["by_vertical"] = dict(summary["by_vertical"])
    summary["by_status"] = dict(summary["by_status"])

    return summary

def main():
    manifest_dir = "/home/setup/if-legal-corpus/manifests"
    output_path = f"{manifest_dir}/MASTER_MANIFEST_2025-11-28.csv"
    summary_path = f"{manifest_dir}/MASTER_MANIFEST_SUMMARY.json"

    print("=" * 80)
    print("LEGAL CORPUS MANIFEST CONSOLIDATION")
    print("=" * 80)

    # Parse all manifests
    records = parse_manifests(manifest_dir)

    # Write master manifest
    count = write_master_manifest(records, output_path)

    # Generate summary
    summary = generate_summary(records)

    print("\n" + "=" * 80)
    print("CONSOLIDATION SUMMARY")
    print("=" * 80)
    print(f"\nTotal Documents: {summary['total_documents']}")
    print(f"Total Bytes: {summary['total_bytes']:,}")
    print(f"Successful Downloads: {summary['download_success']}")
    print(f"Success Rate: {summary['download_success'] / max(summary['total_documents'], 1) * 100:.1f}%")

    print("\nBy Jurisdiction:")
    for jurisdiction in sorted(summary["by_jurisdiction"].keys()):
        count = summary["by_jurisdiction"][jurisdiction]
        print(f"  {jurisdiction:15} {count:3} documents")

    print("\nBy Legal Vertical:")
    for vertical in sorted(summary["by_vertical"].keys()):
        count = summary["by_vertical"][vertical]
        print(f"  {vertical:15} {count:3} documents")

    print("\nBy Status:")
    for status in sorted(summary["by_status"].keys()):
        count = summary["by_status"][status]
        print(f"  {status:15} {count:3} documents")

    # Write summary JSON
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nSummary written to {summary_path}")
    print(f"Master manifest written to {output_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
