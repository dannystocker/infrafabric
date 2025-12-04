#!/usr/bin/env python3
"""
Download Spanish Legal Statutes from BOE (Boletín Oficial del Estado)
Integrates with legal corpus and logs all downloads
"""

import os
import sys
import requests
import hashlib
import csv
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import json

# Configuration
BASE_DIR = Path("/home/setup/if-legal-corpus")
RAW_SPAIN_DIR = BASE_DIR / "raw" / "spain"
LOGS_DIR = BASE_DIR / "logs"
MANIFESTS_DIR = BASE_DIR / "manifests"

# Create log CSV path
DOWNLOAD_LOG = LOGS_DIR / "download_log.csv"
MANIFEST_FILE = MANIFESTS_DIR / "download_manifest.csv"

# Ensure directories exist
for d in [LOGS_DIR, MANIFESTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Spanish statutes database
STATUTES = {
    "employment": [
        {
            "name": "Estatuto de los Trabajadores",
            "boe_id": "BOE-A-2015-11430",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430",
            "priority": "P0",
            "notes": "Core employment law. RDL 2/2015"
        },
        {
            "name": "Ley Estatuto Trabajo Autónomo",
            "boe_id": "BOE-A-2007-13409",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2007-13409",
            "priority": "P0",
            "notes": "Self-employed workers statute. Ley 20/2007"
        },
        {
            "name": "Ley Infracciones Sanciones Orden Social",
            "boe_id": "BOE-A-2000-15060",
            "url": "https://www.boe.es/buscar/doc.php?id=BOE-A-2000-15060",
            "priority": "P1",
            "notes": "Labor infractions and penalties. RDL 5/2000"
        },
        {
            "name": "Ley Prevención Riesgos Laborales",
            "boe_id": "BOE-A-1995-24292",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-1995-24292",
            "priority": "P1",
            "notes": "Occupational safety law. Ley 31/1995"
        },
        {
            "name": "Labor Market Reform 2021",
            "boe_id": "BOE-A-2021-21788",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2021-21788",
            "priority": "P2",
            "notes": "Recent labor market reforms. RDL 32/2021"
        }
    ],
    "ip": [
        {
            "name": "Ley Propiedad Intelectual",
            "boe_id": "BOE-A-1996-8930",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-1996-8930",
            "priority": "P0",
            "notes": "Copyright law. RDL 1/1996"
        },
        {
            "name": "Ley Patentes",
            "boe_id": "BOE-A-2015-8328",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2015-8328",
            "priority": "P1",
            "notes": "Patents law. Ley 24/2015"
        },
        {
            "name": "Reglamento Ejecución Ley Patentes",
            "boe_id": "BOE-A-2017-3550",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2017-3550",
            "priority": "P2",
            "notes": "Patent implementation regulations. RD 316/2017"
        },
        {
            "name": "Ley Marcas",
            "boe_id": "BOE-A-2001-23093",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2001-23093",
            "priority": "P1",
            "notes": "Trademarks law. Ley 17/2001"
        },
        {
            "name": "Reglamento Ejecución Ley Marcas",
            "boe_id": "BOE-A-2002-13981",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2002-13981",
            "priority": "P2",
            "notes": "Trademark implementation regulations. RD 687/2002"
        },
        {
            "name": "Ley Secretos Empresariales",
            "boe_id": "BOE-A-2019-2364",
            "url": "https://www.boe.es/buscar/doc.php?id=BOE-A-2019-2364",
            "priority": "P0",
            "notes": "Trade secrets law. Ley 1/2019"
        },
        {
            "name": "Ley Competencia Desleal",
            "boe_id": "BOE-A-1991-628",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-1991-628",
            "priority": "P1",
            "notes": "Unfair competition law. Ley 3/1991"
        }
    ],
    "tax": [
        {
            "name": "Ley IRPF",
            "boe_id": "BOE-A-2006-20764",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2006-20764",
            "priority": "P0",
            "notes": "Income tax law. Ley 35/2006"
        },
        {
            "name": "Ley IVA",
            "boe_id": "BOE-A-1992-28740",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-1992-28740",
            "priority": "P0",
            "notes": "VAT law. Ley 37/1992"
        },
        {
            "name": "Reglamento IVA",
            "boe_id": "BOE-A-1992-28925",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-1992-28925",
            "priority": "P1",
            "notes": "VAT regulations. RD 1624/1992"
        },
        {
            "name": "Normas Control Aduanero Tributario",
            "boe_id": "N/A",
            "url": "https://www.aeat.es/AEAT/Sede",
            "priority": "P2",
            "notes": "Tax administration procedures. RD 1065/2007"
        },
        {
            "name": "Seguridad Social Trabajadores Autónomos",
            "boe_id": "BOE-A-2015-11430",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430",
            "priority": "P0",
            "notes": "Social security for self-employed. RDL 8/2015"
        }
    ],
    "property": [
        {
            "name": "Código Civil",
            "boe_id": "BOE-A-1889-4763",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-1889-4763",
            "priority": "P0",
            "notes": "Civil code. Real Decreto 24 July 1889"
        },
        {
            "name": "Ley Arrendamientos Urbanos",
            "boe_id": "BOE-A-1994-26003",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-1994-26003",
            "priority": "P1",
            "notes": "Urban leases law. Ley 29/1994"
        },
        {
            "name": "Ley Hipotecaria",
            "boe_id": "BOE-A-1946-2453",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-1946-2453",
            "priority": "P2",
            "notes": "Mortgage law. Decreto 8 Feb 1946"
        },
        {
            "name": "Ley Catastro Inmobiliario",
            "boe_id": "BOE-A-2004-4250",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2004-4250",
            "priority": "P2",
            "notes": "Property cadastre law. RDL 1/2004"
        }
    ],
    "accounting": [
        {
            "name": "Plan General Contabilidad",
            "boe_id": "BOE-A-2007-19884",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2007-19884",
            "priority": "P0",
            "notes": "General accounting plan. RD 1514/2007"
        },
        {
            "name": "PGC PYMES",
            "boe_id": "BOE-A-2007-19966",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2007-19966",
            "priority": "P1",
            "notes": "Accounting for SMEs. RD 1515/2007"
        },
        {
            "name": "Código de Comercio",
            "boe_id": "BOE-A-1885-6627",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-1885-6627",
            "priority": "P1",
            "notes": "Commercial code. Real Decreto 22 Aug 1885"
        },
        {
            "name": "Ley Medidas contra Morosidad",
            "boe_id": "BOE-A-2004-21379",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2004-21379",
            "priority": "P1",
            "notes": "Late payment law. Ley 3/2004"
        }
    ],
    "business": [
        {
            "name": "Ley Agencia",
            "boe_id": "BOE-A-1992-12387",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-1992-12387",
            "priority": "P2",
            "notes": "Agency law. Ley 12/1992"
        },
        {
            "name": "Ley Sociedades de Capital",
            "boe_id": "BOE-A-1995-7113",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-1995-7113",
            "priority": "P2",
            "notes": "Capital companies law. Ley 2/1995"
        },
        {
            "name": "GDPR EU 679/2016",
            "boe_id": "EU-679/2016",
            "url": "https://www.boe.es/doue/2016/119/L00001-00088.pdf",
            "priority": "P1",
            "notes": "Data protection regulation. EU 679/2016"
        }
    ]
}

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    invalid_chars = '<>:"|?*\\'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def calculate_sha256(data):
    """Calculate SHA-256 hash of data"""
    return hashlib.sha256(data).hexdigest()

def download_statute(statute, category):
    """Download a single statute from BOE"""

    url = statute['url']
    name = statute['name']
    boe_id = statute['boe_id']

    timestamp = datetime.now().isoformat()

    try:
        # Set proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        print(f"Downloading: {name} ({boe_id})")
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()

        # Get content
        content = response.content

        # Determine file extension based on content type
        content_type = response.headers.get('content-type', 'text/html')
        if 'pdf' in content_type.lower() or url.endswith('.pdf'):
            extension = '.pdf'
        else:
            extension = '.html'

        # Create filename
        safe_name = sanitize_filename(name)
        filename = f"{safe_name}{extension}"
        filepath = RAW_SPAIN_DIR / category / filename

        # Save file
        with open(filepath, 'wb') as f:
            f.write(content)

        # Calculate metrics
        file_size = len(content)
        sha256_hash = calculate_sha256(content)

        # Log entry
        log_entry = {
            'timestamp': timestamp,
            'document_name': name,
            'url': url,
            'local_path': str(filepath),
            'status': 'success',
            'bytes': file_size,
            'sha256': sha256_hash,
            'notes': f"{boe_id} - {statute.get('notes', '')}"
        }

        print(f"  ✓ Success: {filename} ({file_size} bytes)")
        return log_entry

    except requests.exceptions.RequestException as e:
        log_entry = {
            'timestamp': timestamp,
            'document_name': name,
            'url': url,
            'local_path': '',
            'status': 'error',
            'bytes': 0,
            'sha256': '',
            'notes': f"{boe_id} - Error: {str(e)[:100]}"
        }
        print(f"  ✗ Error: {str(e)[:80]}")
        return log_entry
    except Exception as e:
        log_entry = {
            'timestamp': timestamp,
            'document_name': name,
            'url': url,
            'local_path': '',
            'status': 'error',
            'bytes': 0,
            'sha256': '',
            'notes': f"{boe_id} - Unexpected error: {str(e)[:100]}"
        }
        print(f"  ✗ Error: {str(e)[:80]}")
        return log_entry

def main():
    print("=" * 70)
    print("SPANISH LEGAL STATUTES DOWNLOAD")
    print("BOE (Boletín Oficial del Estado)")
    print("=" * 70)
    print()

    all_logs = []
    category_stats = {}

    # Download all statutes by category
    for category, statutes in STATUTES.items():
        print(f"\n[{category.upper()}]")
        print("-" * 70)

        category_stats[category] = {
            'total': len(statutes),
            'success': 0,
            'error': 0,
            'bytes': 0
        }

        for statute in statutes:
            log_entry = download_statute(statute, category)
            all_logs.append(log_entry)

            if log_entry['status'] == 'success':
                category_stats[category]['success'] += 1
                category_stats[category]['bytes'] += log_entry['bytes']
            else:
                category_stats[category]['error'] += 1

    # Write download log
    print("\n" + "=" * 70)
    print("Writing logs...")

    if DOWNLOAD_LOG.exists():
        # Append to existing log
        with open(DOWNLOAD_LOG, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'document_name', 'url', 'local_path', 'status', 'bytes', 'sha256', 'notes'])
            writer.writerows(all_logs)
    else:
        # Create new log
        with open(DOWNLOAD_LOG, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'document_name', 'url', 'local_path', 'status', 'bytes', 'sha256', 'notes'])
            writer.writeheader()
            writer.writerows(all_logs)

    # Write manifest
    if MANIFEST_FILE.exists():
        with open(MANIFEST_FILE, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'document_name', 'url', 'local_path', 'status', 'bytes', 'sha256', 'notes'])
            writer.writerows(all_logs)
    else:
        with open(MANIFEST_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'document_name', 'url', 'local_path', 'status', 'bytes', 'sha256', 'notes'])
            writer.writeheader()
            writer.writerows(all_logs)

    print(f"✓ Download log: {DOWNLOAD_LOG}")
    print(f"✓ Manifest: {MANIFEST_FILE}")

    # Print summary
    print("\n" + "=" * 70)
    print("DOWNLOAD SUMMARY")
    print("=" * 70)

    total_documents = 0
    total_success = 0
    total_error = 0
    total_bytes = 0

    for category in sorted(category_stats.keys()):
        stats = category_stats[category]
        total_documents += stats['total']
        total_success += stats['success']
        total_error += stats['error']
        total_bytes += stats['bytes']

        print(f"\n{category.upper()}:")
        print(f"  Total: {stats['total']}")
        print(f"  Success: {stats['success']}")
        print(f"  Errors: {stats['error']}")
        print(f"  Bytes: {stats['bytes']:,}")

    print("\n" + "-" * 70)
    print("TOTALS:")
    print(f"  Documents Attempted: {total_documents}")
    print(f"  Success Count: {total_success}")
    print(f"  Error Count: {total_error}")
    print(f"  Total Bytes Downloaded: {total_bytes:,}")
    print(f"  Success Rate: {(total_success/total_documents*100):.1f}%")
    print("=" * 70)

if __name__ == "__main__":
    main()
