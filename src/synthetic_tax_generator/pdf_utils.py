from __future__ import annotations

import glob
import sys
from pathlib import Path


def ensure_pypdf_import() -> None:
    try:
        import pypdf  # noqa: F401
        return
    except Exception:
        pass

    wheel_matches = glob.glob(str(Path(__file__).resolve().parents[2] / "wheels" / "pypdf-*.whl"))
    if wheel_matches:
        sys.path.insert(0, wheel_matches[0])


def load_pdf_reader():
    ensure_pypdf_import()
    from pypdf import PdfReader

    return PdfReader
