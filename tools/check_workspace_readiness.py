from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def list_relative_files(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [str(item.relative_to(ROOT)) for item in sorted(path.rglob("*")) if item.is_file()]


def main() -> None:
    report = {
        "templates": {
            "federal": list_relative_files(ROOT / "templates" / "federal"),
            "state": list_relative_files(ROOT / "templates" / "state"),
            "supporting_docs": list_relative_files(ROOT / "templates" / "supporting_docs"),
        },
        "sample": {
            "input": list_relative_files(ROOT / "sample" / "input"),
            "supporting_docs": list_relative_files(ROOT / "sample" / "supporting_docs"),
            "tax_forms": list_relative_files(ROOT / "sample" / "tax_forms"),
            "summary": list_relative_files(ROOT / "sample" / "summary"),
        },
    }
    report["is_ready_for_exact_template_mapping"] = all(
        [
            bool(report["templates"]["federal"]),
            bool(report["templates"]["supporting_docs"]),
            bool(report["sample"]["input"]),
            bool(report["sample"]["supporting_docs"]),
            bool(report["sample"]["tax_forms"]),
            bool(report["sample"]["summary"]),
        ]
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
