from __future__ import annotations

import argparse
from pathlib import Path

from .generator import SyntheticTaxDatasetGenerator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate synthetic tax dataset folders.")
    parser.add_argument("--count", type=int, default=20, help="Number of synthetic cases to generate.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output") / "pilot_batch",
        help="Directory where dataset folders will be written.",
    )
    parser.add_argument("--seed", type=int, default=1040, help="Optional seed for reproducible output.")
    parser.add_argument(
        "--preset",
        choices=["balanced", "taxyear-2025-relevance"],
        default="balanced",
        help="Optional generation preset.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    generator = SyntheticTaxDatasetGenerator(seed=args.seed)
    if args.preset == "taxyear-2025-relevance":
        generator.tax_years = [2025]
        generator.states = ["CA", "TX", "NY", "IL", "FL"] * 20
        if args.count == 20:
            args.count = 100
    written_cases = generator.generate_batch(count=args.count, output_dir=args.output_dir)
    print(f"Generated {len(written_cases)} synthetic tax cases in {args.output_dir}")


if __name__ == "__main__":
    main()
