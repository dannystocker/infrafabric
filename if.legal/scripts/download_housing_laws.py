#!/usr/bin/env python3
"""
Download all 73 housing law documents across 9 jurisdictions for ContractGuard legal corpus.
Jurisdiction: UK, Spain, US Federal, US States, Canada, Quebec, Australia, Germany, France, EU
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

# Configuration
BASE_RAW_DIR = Path("/home/setup/if-legal-corpus/raw")
LOG_DIR = Path("/home/setup/if-legal-corpus/logs")
MANIFESTS_DIR = Path("/home/setup/if-legal-corpus/manifests")

# Ensure directories exist
LOG_DIR.mkdir(parents=True, exist_ok=True)
MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)

# Document sources from housing-law-sources.md
HOUSING_DOCUMENTS = {
    "uk": [
        {
            "name": "Housing Act 1988",
            "url": "https://www.legislation.gov.uk/ukpga/1988/50",
            "priority": "P0",
            "size_estimate": "750 KB",
            "format": "html",
            "notes": "Core law for residential tenancies. ALREADY IN CORPUS"
        },
        {
            "name": "Housing Act 1985",
            "url": "https://www.legislation.gov.uk/ukpga/1985/21",
            "priority": "P0",
            "size_estimate": "1.2 MB",
            "format": "html",
            "notes": "Council housing and Right to Buy scheme"
        },
        {
            "name": "Landlord and Tenant Act 1985",
            "url": "https://www.legislation.gov.uk/ukpga/1985/70",
            "priority": "P0",
            "size_estimate": "280 KB",
            "format": "html",
            "notes": "Section 11 repair obligations"
        },
        {
            "name": "Protection from Eviction Act 1977",
            "url": "https://www.legislation.gov.uk/ukpga/1977/43",
            "priority": "P0",
            "size_estimate": "85 KB",
            "format": "html",
            "notes": "Court order requirement for eviction"
        },
        {
            "name": "Rent Act 1977",
            "url": "https://www.legislation.gov.uk/ukpga/1977/42",
            "priority": "P0",
            "size_estimate": "950 KB",
            "format": "html",
            "notes": "Regulated tenancies (pre-1989). Fair rent registration"
        },
        {
            "name": "Housing and Planning Act 2016",
            "url": "https://www.legislation.gov.uk/ukpga/2016/22",
            "priority": "P1",
            "size_estimate": "1.1 MB",
            "format": "html",
            "notes": "Rogue landlords, banning orders, starter homes"
        }
    ],
    "spain": [
        {
            "name": "Ley de Arrendamientos Urbanos (LAU 29/1994)",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-1994-26003",
            "priority": "P0",
            "size_estimate": "385 KB",
            "format": "html",
            "notes": "Comprehensive urban lease law. ALREADY IN CORPUS"
        },
        {
            "name": "Ley de Propiedad Horizontal (49/1960)",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-1960-10906",
            "priority": "P0",
            "size_estimate": "520 KB",
            "format": "html",
            "notes": "Condominium/horizontal property law"
        },
        {
            "name": "Real Decreto-Ley 7/2019 (Urgent Housing Measures)",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2019-3244",
            "priority": "P1",
            "size_estimate": "145 KB",
            "format": "html",
            "notes": "Emergency housing law, extended lease terms, rent limits"
        }
    ],
    "usa_federal": [
        {
            "name": "Fair Housing Act (42 USC 3601-3619)",
            "url": "https://www.law.cornell.edu/uscode/text/42/3601",
            "priority": "P0",
            "size_estimate": "95 KB",
            "format": "html",
            "notes": "Federal baseline for housing discrimination. ALREADY IN CORPUS"
        },
        {
            "name": "HUD Regulations (24 CFR Part 100)",
            "url": "https://www.ecfr.gov/current/title-24/subtitle-B/chapter-I/part-100",
            "priority": "P0",
            "size_estimate": "420 KB",
            "format": "html",
            "notes": "Fair Housing implementation"
        },
        {
            "name": "Lead-Based Paint Disclosure (24 CFR 35)",
            "url": "https://www.ecfr.gov/current/title-24/subtitle-A/part-35/subpart-A",
            "priority": "P0",
            "size_estimate": "185 KB",
            "format": "html",
            "notes": "Pre-1978 housing lead disclosure requirements"
        },
        {
            "name": "National Fair Housing Commission Rules (42 USC 3614)",
            "url": "https://www.justice.gov/crt/fair-housing-act-1",
            "priority": "P1",
            "size_estimate": "65 KB",
            "format": "html",
            "notes": "Administrative complaint procedures"
        }
    ],
    "usa_states": [
        {
            "name": "California Tenant Protection Act (AB 1482)",
            "url": "https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=201920200AB1482",
            "priority": "P0",
            "size_estimate": "180 KB",
            "format": "html",
            "notes": "Statewide rent cap (5% + CPI or 10%)"
        },
        {
            "name": "New York Housing Stability and Tenant Protection Act",
            "url": "https://nyassembly.gov/leg/?default_fld=&leg_video=&bn=A08281&term=2019&Text=Y",
            "priority": "P0",
            "size_estimate": "220 KB",
            "format": "html",
            "notes": "Major rent regulation reform"
        },
        {
            "name": "New York Residential Tenancy Law (RPL 226-c)",
            "url": "https://www.nysenate.gov/legislation/laws/RPL/226-C",
            "priority": "P1",
            "size_estimate": "95 KB",
            "format": "html",
            "notes": "Lease terms, repair obligations, habitability"
        },
        {
            "name": "Texas Property Code (Residential Tenancies Ch 92-103)",
            "url": "https://statutes.capitol.texas.gov/Docs/PR/pdf/PR.92.pdf",
            "priority": "P1",
            "size_estimate": "310 KB",
            "format": "pdf",
            "notes": "Texas landlord-tenant law"
        },
        {
            "name": "Florida Residential Tenancy Law (Chapter 83)",
            "url": "https://www.flsenate.gov/Session/Bill/2024/627",
            "priority": "P1",
            "size_estimate": "185 KB",
            "format": "html",
            "notes": "Florida property rental regulations"
        },
        {
            "name": "Illinois Residential Tenancy Law (735 ILCS 5/9-201)",
            "url": "https://ilga.gov/commission/lrs/handbook/chtopics/101tenancy.pdf",
            "priority": "P1",
            "size_estimate": "125 KB",
            "format": "pdf",
            "notes": "Illinois landlord-tenant act"
        }
    ],
    "canada_federal": [
        {
            "name": "National Housing Act (RSC 1985 c N-11)",
            "url": "https://laws-lois.justice.gc.ca/eng/acts/n-11/FullText.html",
            "priority": "P0",
            "size_estimate": "850 KB",
            "format": "html",
            "notes": "Framework for federal housing programs, CMHC"
        },
        {
            "name": "National Housing Strategy Act (RSC 1985 c N-11.2)",
            "url": "https://laws-lois.justice.gc.ca/eng/acts/n-11.2/FullText.html",
            "priority": "P1",
            "size_estimate": "220 KB",
            "format": "html",
            "notes": "National housing policy objectives"
        },
        {
            "name": "Canada Mortgage and Housing Corporation Regulations (SOR 80-159)",
            "url": "https://laws-lois.justice.gc.ca/eng/regulations/80-159/FullText.html",
            "priority": "P1",
            "size_estimate": "185 KB",
            "format": "html",
            "notes": "CMHC insurance programs"
        }
    ],
    "quebec": [
        {
            "name": "Code Civil du Quebec - Lease (Articles 1851-2000.1)",
            "url": "https://www.legisquebec.gouv.qc.ca/fr/document/cc",
            "priority": "P0",
            "size_estimate": "725 KB",
            "format": "html",
            "notes": "Complete lease regulation for Quebec. FRENCH ORIGINAL TEXT"
        },
        {
            "name": "Loi sur la Regie du logement (c. R-8.1)",
            "url": "https://www.legisquebec.gouv.qc.ca/fr/document/lc/r-8.1",
            "priority": "P0",
            "size_estimate": "95 KB",
            "format": "html",
            "notes": "Tribunal administratif du logement (TAL). FRENCH ORIGINAL TEXT"
        },
        {
            "name": "Regulation respecting the Tribunal administratif du logement",
            "url": "https://www.legisquebec.gouv.qc.ca/fr/document/rc/T-16",
            "priority": "P1",
            "size_estimate": "185 KB",
            "format": "html",
            "notes": "Procedural rules for TAL. FRENCH ORIGINAL TEXT"
        }
    ],
    "australia": [
        {
            "name": "Residential Tenancies Act 2010 (NSW)",
            "url": "https://legislation.nsw.gov.au/view/html/inforce/current/act-2010-042",
            "priority": "P0",
            "size_estimate": "620 KB",
            "format": "html",
            "notes": "NSW residential tenancy law with 2024 amendments"
        },
        {
            "name": "Residential Tenancies Act 1997 (Victoria)",
            "url": "https://www.legislation.vic.gov.au/in-force/acts/residential-tenancies-act-1997",
            "priority": "P0",
            "size_estimate": "540 KB",
            "format": "html",
            "notes": "Victoria residential tenancy law"
        },
        {
            "name": "Residential Tenancies and Rooming Accommodation Act 2008 (Queensland)",
            "url": "https://www.legislation.qld.gov.au/view/html/inforce/current/act-2008-073",
            "priority": "P1",
            "size_estimate": "580 KB",
            "format": "html",
            "notes": "Queensland residential tenancy law"
        },
        {
            "name": "National Consumer Credit Protection Act 2009 (Australia)",
            "url": "https://www.legislation.gov.au/C2009A00139/latest/text",
            "priority": "P1",
            "size_estimate": "1.8 MB",
            "format": "html",
            "notes": "Mortgage and credit regulation"
        }
    ],
    "germany": [
        {
            "name": "BGB §535-580a (German Civil Code - Rental Law)",
            "url": "https://www.gesetze-im-internet.de/englisch_bgb/",
            "priority": "P0",
            "size_estimate": "2.1 MB",
            "format": "html",
            "notes": "Core German rental law"
        },
        {
            "name": "Mietpreisbremse (Rent Brake Act)",
            "url": "https://www.gesetze-im-internet.de/mietbremse/",
            "priority": "P0",
            "size_estimate": "45 KB",
            "format": "html",
            "notes": "Rent control mechanism (max 10% above local average)"
        },
        {
            "name": "Betriebskostenverordnung (Operating Costs Regulation)",
            "url": "https://www.gesetze-im-internet.de/betrkv_2004/",
            "priority": "P0",
            "size_estimate": "95 KB",
            "format": "html",
            "notes": "Operating costs categories (17 categories of apportionable costs)"
        },
        {
            "name": "Wohnungseigentumsgesetz (Condominium Ownership Act)",
            "url": "https://www.gesetze-im-internet.de/woeigg/",
            "priority": "P1",
            "size_estimate": "185 KB",
            "format": "html",
            "notes": "Apartment/condominium ownership"
        },
        {
            "name": "German Property Transfer Tax Act (Grunderwerbsteuergesetz)",
            "url": "https://www.gesetze-im-internet.de/grunderwstg/",
            "priority": "P1",
            "size_estimate": "120 KB",
            "format": "html",
            "notes": "Property transfer taxation"
        }
    ],
    "france": [
        {
            "name": "Loi ALUR (Law for Housing Access and Renewed Urban Planning)",
            "url": "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000028772256",
            "priority": "P0",
            "size_estimate": "185 KB",
            "format": "html",
            "notes": "Major housing reform law. FRENCH ORIGINAL TEXT"
        },
        {
            "name": "Loi ELAN (Law on Housing Evolution, Urban Planning, and Digital)",
            "url": "https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000037639478",
            "priority": "P0",
            "size_estimate": "310 KB",
            "format": "html",
            "notes": "Housing modernization law. FRENCH ORIGINAL TEXT"
        },
        {
            "name": "Code de la construction et de l'habitation (Building and Housing Code)",
            "url": "https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006074096/",
            "priority": "P1",
            "size_estimate": "2.8 MB",
            "format": "html",
            "notes": "Consolidated French housing law. FRENCH ORIGINAL TEXT"
        },
        {
            "name": "Décret Encadrement des Loyers (Rent Control Decree)",
            "url": "https://www.ecologie.gouv.fr/politiques-publiques/encadrement-loyers",
            "priority": "P2",
            "size_estimate": "125 KB",
            "format": "html",
            "notes": "Annual rent control limits. FRENCH ORIGINAL TEXT"
        }
    ],
    "eu": [
        {
            "name": "Energy Performance of Buildings Directive (2010/31/EU)",
            "url": "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32010L0031",
            "priority": "P0",
            "size_estimate": "485 KB",
            "format": "html",
            "notes": "Energy performance certification for buildings"
        },
        {
            "name": "Mortgage Credit Directive (2014/17/EU)",
            "url": "https://eur-lex.europa.eu/eli/dir/2014/17/oj/eng",
            "priority": "P0",
            "size_estimate": "320 KB",
            "format": "html",
            "notes": "Consumer protection for residential mortgage credit. ALREADY IN CORPUS"
        },
        {
            "name": "Services Directive (2006/123/EC)",
            "url": "https://eur-lex.europa.eu/eli/dir/2006/123/oj/eng",
            "priority": "P2",
            "size_estimate": "185 KB",
            "format": "html",
            "notes": "Internal market services directive"
        }
    ]
}

class HousingLawDownloader:
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

    def get_filename_from_url(self, url: str) -> str:
        """Extract filename from URL"""
        parsed = urlparse(url)
        if parsed.path:
            filename = parsed.path.split('/')[-1]
            if filename and '.' in filename:
                return filename
        return None

    def download_document(self, jurisdiction: str, doc: Dict) -> Tuple[bool, str, int, str]:
        """
        Download a single document.
        Returns: (success, filepath, filesize, error_message)
        """
        url = doc['url']
        doc_name = doc['name']

        # Create jurisdiction directory
        jurisdiction_dir = BASE_RAW_DIR / jurisdiction / "housing"
        jurisdiction_dir.mkdir(parents=True, exist_ok=True)

        # Safe filename
        safe_name = doc_name.replace('/', '_').replace('\\', '_').replace(' ', '_')
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c in '_-.')

        # Try to get original extension from URL
        url_filename = self.get_filename_from_url(url)
        if url_filename and '.' in url_filename:
            ext = '.' + url_filename.split('.')[-1]
        else:
            ext = doc.get('format', 'html')
            if ext and not ext.startswith('.'):
                ext = '.' + ext

        filepath = jurisdiction_dir / (safe_name + ext)

        try:
            print(f"Downloading {jurisdiction}/{doc_name}...", end=' ', flush=True)

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

            print(f"OK ({file_size} bytes)")

            return True, str(filepath), file_size, content_hash

        except requests.exceptions.Timeout:
            error = f"Timeout downloading {url}"
            print(f"TIMEOUT")
            return False, str(filepath), 0, error
        except requests.exceptions.RequestException as e:
            error = f"Error: {str(e)}"
            print(f"FAILED: {error}")
            return False, str(filepath), 0, error
        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            print(f"ERROR: {error}")
            return False, str(filepath), 0, error

    def download_all(self):
        """Download all housing law documents"""
        print("\n" + "="*80)
        print("ContractGuard Housing Law Document Download")
        print("="*80)
        print(f"Start time: {datetime.now().isoformat()}\n")

        total_docs = sum(len(docs) for docs in HOUSING_DOCUMENTS.values())
        current = 0

        for jurisdiction, documents in HOUSING_DOCUMENTS.items():
            print(f"\n--- {jurisdiction.upper()} ({len(documents)} documents) ---")

            for doc in documents:
                current += 1
                success, filepath, filesize, result = self.download_document(jurisdiction, doc)

                log_entry = {
                    'jurisdiction': jurisdiction,
                    'document_name': doc['name'],
                    'url': doc['url'],
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
                        'priority': doc['priority'],
                        'downloaded': datetime.now().isoformat()
                    })
                else:
                    self.blocked_count += 1

        print("\n" + "="*80)
        print("DOWNLOAD COMPLETE")
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
        log_file = LOG_DIR / f"housing_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w') as f:
            json.dump(self.download_log, f, indent=2)
        print(f"Detailed log saved to: {log_file}")

        # Save manifest CSV
        manifest_file = MANIFESTS_DIR / f"housing_manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        if self.manifest:
            fieldnames = list(self.manifest[0].keys())
            with open(manifest_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.manifest)
            print(f"Manifest saved to: {manifest_file}")

        # Save download log CSV
        log_csv_file = LOG_DIR / f"housing_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        if self.download_log:
            fieldnames = list(self.download_log[0].keys())
            with open(log_csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.download_log)
            print(f"CSV log saved to: {log_csv_file}\n")

def main():
    downloader = HousingLawDownloader()
    downloader.download_all()

if __name__ == "__main__":
    main()
