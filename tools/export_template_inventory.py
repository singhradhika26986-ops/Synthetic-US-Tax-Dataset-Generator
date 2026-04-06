from __future__ import annotations

from pathlib import Path

from synthetic_tax_generator.template_mapping import write_template_inventory


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    target = root / "docs" / "template_field_inventory.json"
    write_template_inventory(root / "templates", target)
    print(target)


if __name__ == "__main__":
    main()
