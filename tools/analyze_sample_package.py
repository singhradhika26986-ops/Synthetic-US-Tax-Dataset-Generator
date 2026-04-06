from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def files_in(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [str(p.relative_to(ROOT)) for p in sorted(path.rglob("*")) if p.is_file()]


def main() -> None:
    sample = {
        "input": files_in(ROOT / "sample" / "input"),
        "supporting_docs": files_in(ROOT / "sample" / "supporting_docs"),
        "tax_forms": files_in(ROOT / "sample" / "tax_forms"),
        "summary": files_in(ROOT / "sample" / "summary"),
    }
    templates = {
        "federal": files_in(ROOT / "templates" / "federal"),
        "state": files_in(ROOT / "templates" / "state"),
        "supporting_docs": files_in(ROOT / "templates" / "supporting_docs"),
    }
    gaps = {
        "missing_state_templates": len(templates["state"]) == 0,
        "sample_present": all(bool(sample[key]) for key in sample),
        "missing_key_blank_templates": [
            name
            for name, present in {
                "Form 1040": bool(templates["federal"]),
                "W-2": bool(templates["supporting_docs"]),
                "State forms": bool(templates["state"]),
            }.items()
            if not present
        ],
    }
    print(json.dumps({"sample": sample, "templates": templates, "gaps": gaps}, indent=2))


if __name__ == "__main__":
    main()
