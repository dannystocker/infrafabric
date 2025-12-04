#!/usr/bin/env python3
"""
Phase 2: Download remaining housing law documents with alternative sources.
Handle blocked documents and 404s with fallback URLs.
"""

import os
import sys
import json
import csv
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from urllib.parse import urlparse

BASE_RAW_DIR = Path("/home/setup/if-legal-corpus/raw")
LOG_DIR = Path("/home/setup/if-legal-corpus/logs")
MANIFESTS_DIR = Path("/home/setup/if-legal-corpus/manifests")

# Documents that failed in Phase 1 with alternative URLs
PHASE2_DOCUMENTS = {
    "usa_states": [
        {
            "name": "Illinois Residential Tenancy Law (735 ILCS 5/9-201)",
            "url": "https://www.cyberdriveillinois.com/departments/index/register/home.html",
            "alt_url": "https://sos.illinois.gov/departments/index/register/home.html",
            "priority": "P1",
            "notes": "Illinois Secretary of State website (alternative)"
        }
    ],
    "canada_federal": [
        {
            "name": "Canada Mortgage and Housing Corporation Regulations (SOR 80-159)",
            "url": "https://laws-lois.justice.gc.ca/eng/regulations/80-159/page-1.html",
            "alt_url": "https://canlii.org/en/ca/laws/regu/sor-80-159/latest/sor-80-159.html",
            "priority": "P1",
            "notes": "Using CanLII as fallback source"
        }
    ],
    "quebec": [
        {
            "name": "Code Civil du Quebec - Lease (Articles 1851-2000.1)",
            "url": "https://www.legisquebec.gouv.qc.ca/en/document/cc",
            "alt_url": "https://canlii.org/en/qc/laws/stat/ccq/latest/ccq.html",
            "priority": "P0",
            "notes": "Using CanLII English translation as fallback"
        }
    ],
    "germany": [
        {
            "name": "Mietpreisbremse (Rent Brake Act)",
            "url": "https://www.gesetze-im-internet.de/mietbremse_2015/",
            "alt_url": "https://www.bundesregierung.de/breg-de/themen/miete/mietpreisbremse-1821558",
            "priority": "P0",
            "notes": "Alternative: German Federal Government portal"
        },
        {
            "name": "Betriebskostenverordnung (Operating Costs Regulation)",
            "url": "https://www.gesetze-im-internet.de/betrkv/",
            "alt_url": "https://www.bmwsb.bund.de/",
            "priority": "P0",
            "notes": "Alternative: Federal Ministry of Building"
        },
        {
            "name": "German Property Transfer Tax Act (Grunderwerbsteuergesetz)",
            "url": "https://www.gesetze-im-internet.de/grunderwstg_1997/",
            "alt_url": "https://www.finanzen.de/",
            "priority": "P1",
            "notes": "Alternative: German Finance portal"
        }
    ],
    "france": [
        {
            "name": "Loi ALUR (Law for Housing Access and Renewed Urban Planning)",
            "url": "https://www.legifrance.gouv.fr/download/pdf/legitext/000028772256",
            "alt_url": "https://www.dossierfamilial.com/lois/loi-alur.html",
            "priority": "P0",
            "notes": "Using third-party legal database as fallback"
        },
        {
            "name": "Loi ELAN (Law on Housing Evolution, Urban Planning, and Digital)",
            "url": "https://www.legifrance.gouv.fr/download/pdf/legitext/000037639478",
            "alt_url": "https://www.dossierfamilial.com/lois/loi-elan.html",
            "priority": "P0",
            "notes": "Using third-party legal database as fallback"
        },
        {
            "name": "Code de la construction et de l'habitation (Building and Housing Code)",
            "url": "https://www.legifrance.gouv.fr/download/pdf/legitext/000006074096",
            "alt_url": "https://www.dossierfamilial.com/codes/code-construction-habitation.html",
            "priority": "P1",
            "notes": "Using third-party legal database as fallback"
        }
    ]
}

class HousingLawDownloaderPhase2:
    def __init__(self):
        self.download_log = []
        self.manifest = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.total_bytes = 0
        self.success_count = 0
        self.blocked_count = 0

    def calculate_hash(self, content: bytes) -> str:
        """Calculate SHA-256 hash of content"""
        return hashlib.sha256(content).hexdigest()

    def download_document(self, jurisdiction: str, doc: Dict) -> Tuple[bool, str, int, str, str]:
        """
        Download a single document with fallback URLs.
        Returns: (success, filepath, filesize, hash_or_error, source_url)
        """
        doc_name = doc['name']

        # Try primary URL first, then fallback
        urls_to_try = [doc['url']]
        if 'alt_url' in doc:
            urls_to_try.append(doc['alt_url'])

        # Create jurisdiction directory
        jurisdiction_dir = BASE_RAW_DIR / jurisdiction / "housing"
        jurisdiction_dir.mkdir(parents=True, exist_ok=True)

        # Safe filename
        safe_name = doc_name.replace('/', '_').replace('\\', '_').replace(' ', '_')
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c in '_-.')

        filepath = jurisdiction_dir / (safe_name + ".html")

        print(f"Downloading {jurisdiction}/{doc_name}...", end=' ', flush=True)

        for attempt, url in enumerate(urls_to_try):
            try:
                response = self.session.get(url, timeout=30, allow_redirects=True)
                response.raise_for_status()

                content = response.content

                # Save file
                with open(filepath, 'wb') as f:
                    f.write(content)

                file_size = len(content)
                content_hash = self.calculate_hash(content)

                self.total_bytes += file_size
                self.success_count += 1

                source = "primary" if attempt == 0 else "fallback"
                print(f"OK ({file_size} bytes, {source})")

                return True, str(filepath), file_size, content_hash, url

            except requests.exceptions.Timeout:
                if attempt == len(urls_to_try) - 1:
                    print(f"TIMEOUT (all URLs failed)")
                    return False, str(filepath), 0, f"Timeout on all URLs", ""
                continue
            except requests.exceptions.RequestException as e:
                if attempt == len(urls_to_try) - 1:
                    error = f"All URLs failed: {str(e)}"
                    print(f"FAILED: {error}")
                    return False, str(filepath), 0, error, ""
                continue
            except Exception as e:
                if attempt == len(urls_to_try) - 1:
                    error = f"Unexpected error: {str(e)}"
                    print(f"ERROR: {error}")
                    return False, str(filepath), 0, error, ""
                continue

        return False, str(filepath), 0, "All URLs failed", ""

    def download_all(self):
        """Download Phase 2 documents"""
        print("\n" + "="*80)
        print("ContractGuard Housing Law Document Download - PHASE 2")
        print("Alternative Sources & Fallback URLs")
        print("="*80)
        print(f"Start time: {datetime.now().isoformat()}\n")

        total_docs = sum(len(docs) for docs in PHASE2_DOCUMENTS.values())
        current = 0

        for jurisdiction, documents in PHASE2_DOCUMENTS.items():
            print(f"\n--- {jurisdiction.upper()} ({len(documents)} documents) ---")

            for doc in documents:
                current += 1
                success, filepath, filesize, result, source_url = self.download_document(jurisdiction, doc)

                log_entry = {
                    'jurisdiction': jurisdiction,
                    'document_name': doc['name'],
                    'primary_url': doc['url'],
                    'fallback_url': doc.get('alt_url', ''),
                    'source_used': source_url,
                    'priority': doc['priority'],
                    'status': 'success' if success else 'failed',
                    'filepath': filepath if success else '',
                    'filesize': filesize,
                    'hash': result if success else '',
                    'error': '' if success else result,
                    'timestamp': datetime.now().isoformat()
                }

                self.download_log.append(log_entry)

                if success:
                    self.manifest.append({
                        'jurisdiction': jurisdiction,
                        'document': doc['name'],
                        'filepath': filepath,
                        'filesize': filesize,
                        'hash_sha256': result,
                        'source_url': source_url,
                        'priority': doc['priority'],
                        'phase': 'phase2',
                        'downloaded': datetime.now().isoformat()
                    })
                else:
                    self.blocked_count += 1

        print("\n" + "="*80)
        print("PHASE 2 DOWNLOAD COMPLETE")
        print("="*80)
        self.print_summary()
        self.save_logs()

    def print_summary(self):
        """Print download summary"""
        print(f"\nDocuments attempted: {self.success_count + self.blocked_count}")
        print(f"Successfully downloaded: {self.success_count}")
        print(f"Blocked/Failed: {self.blocked_count}")
        print(f"Total bytes downloaded: {self.total_bytes / (1024*1024):.2f} MB")
        print(f"Completion time: {datetime.now().isoformat()}\n")

    def save_logs(self):
        """Save download logs and manifests"""
        # Save detailed log as JSON
        log_file = LOG_DIR / f"housing_download_phase2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w') as f:
            json.dump(self.download_log, f, indent=2)
        print(f"Phase 2 log saved to: {log_file}")

        # Save manifest CSV
        manifest_file = MANIFESTS_DIR / f"housing_manifest_phase2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        if self.manifest:
            fieldnames = list(self.manifest[0].keys())
            with open(manifest_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.manifest)
            print(f"Phase 2 manifest saved to: {manifest_file}\n")

def main():
    downloader = HousingLawDownloaderPhase2()
    downloader.download_all()

if __name__ == "__main__":
    main()
