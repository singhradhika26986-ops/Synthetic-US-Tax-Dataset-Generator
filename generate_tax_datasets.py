from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
WHEELS = ROOT / "wheels"
for wheel in WHEELS.glob("pypdf-*.whl"):
    if str(wheel) not in sys.path:
        sys.path.insert(0, str(wheel))

from synthetic_tax_generator.cli import main


if __name__ == "__main__":
    main()
