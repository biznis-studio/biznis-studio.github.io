#!/usr/bin/env python3
"""CLI: render a Markdown product file to a clean, print-ready PDF.

Thin wrapper around agents/pdf_export.py - see that module for how. Useful
for producing a file to upload somewhere that won't accept .md (e.g.
Gumroad's file picker, observed 2026-07-26).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.pdf_export import export

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python3 scripts/export_pdf.py <markdown_file> [output.pdf]")
        sys.exit(1)
    md_file = Path(sys.argv[1])
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else md_file.with_suffix(".pdf")
    export(md_file, output)
    print(f"Wrote {output} ({output.stat().st_size} bytes)")
