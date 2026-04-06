from __future__ import annotations

import json
from pathlib import Path

from .pdf_utils import load_pdf_reader


def extract_template_fields(pdf_path: Path) -> dict:
    PdfReader = load_pdf_reader()
    reader = PdfReader(str(pdf_path))
    fields = reader.get_fields() or {}
    return {
        "path": str(pdf_path),
        "page_count": len(reader.pages),
        "field_count": len(fields),
        "fields": list(fields.keys()),
    }


def build_template_inventory(templates_root: Path) -> dict:
    inventory = {"federal": [], "state": [], "supporting_docs": []}
    for bucket in inventory:
        folder = templates_root / bucket
        if not folder.exists():
            continue
        for pdf_path in sorted(folder.glob("*.pdf")):
            inventory[bucket].append(extract_template_fields(pdf_path))
    return inventory


def write_template_inventory(templates_root: Path, target: Path) -> Path:
    inventory = build_template_inventory(templates_root)
    target.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    return target
