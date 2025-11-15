#!/usr/bin/env python3
"""
Markdown Table to CSV Converter
Extracts tables from markdown files and converts them to CSV format
"""

import re
import csv
import sys
from pathlib import Path

def extract_tables_from_md(md_content):
    """Extract all tables from markdown content"""
    tables = []
    lines = md_content.split('\n')

    current_table = []
    in_table = False

    for line in lines:
        # Check if line looks like a table row (contains |)
        if '|' in line:
            # Skip separator rows (---|---|---)
            if re.match(r'^\s*\|[\s\-:|]+\|\s*$', line):
                continue

            in_table = True
            # Clean and split the row
            cells = [cell.strip() for cell in line.split('|')]
            # Remove empty first/last cells (from leading/trailing |)
            cells = [c for c in cells if c]
            current_table.append(cells)
        else:
            # End of table
            if in_table and current_table:
                tables.append(current_table)
                current_table = []
                in_table = False

    # Don't forget the last table
    if current_table:
        tables.append(current_table)

    return tables

def tables_to_csv(tables, output_prefix="table"):
    """Convert tables to CSV files"""
    output_files = []

    for idx, table in enumerate(tables, 1):
        if not table:
            continue

        filename = f"{output_prefix}_{idx}.csv"

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(table)

        output_files.append(filename)
        print(f"✓ Created: {filename} ({len(table)} rows)")

    return output_files

def main():
    if len(sys.argv) < 2:
        print("Usage: python md-table-to-csv.py <markdown-file> [output-prefix]")
        print("\nExample:")
        print("  python md-table-to-csv.py ZEN-YACHTING-ONE-PAGE-PLAN-FOR-JOE.md magazines")
        print("\nThis will extract all tables and save them as:")
        print("  magazines_1.csv, magazines_2.csv, etc.")
        sys.exit(1)

    input_file = sys.argv[1]
    output_prefix = sys.argv[2] if len(sys.argv) > 2 else "table"

    # Read markdown file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)

    # Extract tables
    print(f"\nExtracting tables from: {input_file}")
    tables = extract_tables_from_md(content)

    if not tables:
        print("No tables found in the markdown file")
        sys.exit(0)

    print(f"Found {len(tables)} table(s)\n")

    # Convert to CSV
    output_files = tables_to_csv(tables, output_prefix)

    print(f"\n✓ Successfully extracted {len(output_files)} table(s)")
    print(f"  Output files: {', '.join(output_files)}")

if __name__ == "__main__":
    main()
