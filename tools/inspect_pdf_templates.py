from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PDF_MARKERS = [b"/AcroForm", b"/XFA", b"/Annots", b"/Fields", b"/NeedAppearances"]


def inspect_pdf(path: Path) -> dict:
    data = path.read_bytes()
    field_names = sorted(
        {
            match.decode("latin1", "ignore")
            for match in re.findall(rb"/T\s*\((.*?)\)", data)
        }
    )
    marker_offsets = {marker.decode(): data.find(marker) for marker in PDF_MARKERS}
    return {
        "path": str(path),
        "size_bytes": len(data),
        "has_acroform": marker_offsets["/AcroForm"] >= 0,
        "marker_offsets": marker_offsets,
        "raw_field_name_count": len(field_names),
        "raw_field_name_preview": field_names[:100],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect PDF templates for field markers.")
    parser.add_argument(
        "paths",
        nargs="*",
        default=["templates"],
        help="Files or directories to inspect.",
    )
    args = parser.parse_args()

    pdf_files: list[Path] = []
    for raw_path in args.paths:
        path = Path(raw_path)
        if path.is_file() and path.suffix.lower() == ".pdf":
            pdf_files.append(path)
        elif path.is_dir():
            pdf_files.extend(sorted(path.rglob("*.pdf")))

    report = [inspect_pdf(path) for path in pdf_files]
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
