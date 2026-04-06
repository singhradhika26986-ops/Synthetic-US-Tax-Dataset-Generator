from __future__ import annotations

import json
import math
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "final_2000"
DEST = ROOT / "output" / "weekly_batches"
BATCH_SIZE = 350


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Source batch not found: {SOURCE}")

    case_dirs = sorted([p for p in SOURCE.iterdir() if p.is_dir() and p.name.startswith("case_")])
    DEST.mkdir(parents=True, exist_ok=True)

    batch_count = math.ceil(len(case_dirs) / BATCH_SIZE)
    manifest: list[dict] = []

    for batch_index in range(batch_count):
        batch_name = f"batch_{batch_index + 1:02d}"
        batch_dir = DEST / batch_name
        batch_dir.mkdir(parents=True, exist_ok=True)
        batch_cases = case_dirs[batch_index * BATCH_SIZE : (batch_index + 1) * BATCH_SIZE]

        for case_dir in batch_cases:
            target = batch_dir / case_dir.name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(case_dir, target)

        manifest.append(
            {
                "batch": batch_name,
                "case_count": len(batch_cases),
                "first_case": batch_cases[0].name if batch_cases else None,
                "last_case": batch_cases[-1].name if batch_cases else None,
            }
        )

    (DEST / "weekly_batch_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Created {batch_count} weekly batches in {DEST}")


if __name__ == "__main__":
    main()
