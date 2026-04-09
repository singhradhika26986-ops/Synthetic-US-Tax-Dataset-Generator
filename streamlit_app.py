from __future__ import annotations

import io
import json
import sys
import tempfile
import zipfile
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from synthetic_tax_generator.generator import SyntheticTaxDatasetGenerator


def _zip_directory(source_dir: Path) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in source_dir.rglob("*"):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(source_dir))
    buffer.seek(0)
    return buffer.getvalue()


def _build_generator(seed: int, preset: str) -> SyntheticTaxDatasetGenerator:
    generator = SyntheticTaxDatasetGenerator(seed=seed)
    if preset == "2025 Relevance":
        generator.tax_years = [2025]
        generator.states = ["CA", "TX", "NY", "IL", "FL"]
    return generator


def _render_distribution(title: str, values: dict[str, int]) -> None:
    st.markdown(f"**{title}**")
    if not values:
        st.write("No data")
        return
    st.table([{"Label": key, "Count": value} for key, value in values.items()])


st.set_page_config(
    page_title="Synthetic Tax Dataset Generator",
    page_icon="📄",
    layout="wide",
)

st.title("Synthetic US Tax Dataset Generator")
st.caption(
    "Generate small synthetic tax batches, preview the manifest, and download a ZIP package."
)

with st.sidebar:
    st.header("Generation Controls")
    preset = st.selectbox("Preset", ["Balanced", "2025 Relevance"])
    count = st.slider("Number of cases", min_value=1, max_value=20, value=5)
    seed = st.number_input("Seed", min_value=1, max_value=999999, value=1040, step=1)
    generate = st.button("Generate Batch", type="primary", use_container_width=True)

st.info(
    "This live app is optimized for demo-sized batches. Large production runs and official-template "
    "filled outputs that depend on local blank PDFs remain better suited for local execution."
)

if generate:
    with st.spinner("Generating synthetic tax datasets..."):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "streamlit_batch"
            generator = _build_generator(seed=seed, preset=preset)
            written_cases = generator.generate_batch(count=count, output_dir=output_dir)
            manifest = json.loads((output_dir / "batch_manifest.json").read_text(encoding="utf-8"))
            first_case_data = json.loads((written_cases[0] / "case_data.json").read_text(encoding="utf-8"))
            zip_bytes = _zip_directory(output_dir)

    st.success(f"Generated {manifest['total_cases']} synthetic tax cases.")

    top_left, top_mid, top_right = st.columns(3)
    top_left.metric("Cases", manifest["total_cases"])
    top_mid.metric("States Covered", len(manifest["distribution"]["by_state"]))
    top_right.metric("Levels Covered", len(manifest["distribution"]["by_difficulty_level"]))

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Batch Manifest")
        st.json(manifest)

    with col2:
        st.subheader("First Case Preview")
        preview = {
            "case_id": first_case_data["taxpayer"]["case_id"],
            "tax_year": first_case_data["taxpayer"]["tax_year"],
            "difficulty_level": first_case_data["taxpayer"]["difficulty_level"],
            "taxpayer": f"{first_case_data['taxpayer']['first_name']} {first_case_data['taxpayer']['last_name']}",
            "state": first_case_data["taxpayer"]["address"]["state"],
            "filing_status": first_case_data["taxpayer"]["filing_status"],
            "planned_forms": first_case_data["planned_forms"],
            "document_count": first_case_data["document_count"],
        }
        st.json(preview)

    dist1, dist2, dist3 = st.columns(3)
    with dist1:
        _render_distribution("By State", manifest["distribution"]["by_state"])
    with dist2:
        _render_distribution("By Tax Year", manifest["distribution"]["by_tax_year"])
    with dist3:
        _render_distribution("By Difficulty", manifest["distribution"]["by_difficulty_level"])

    st.download_button(
        label="Download Batch ZIP",
        data=zip_bytes,
        file_name="synthetic_tax_batch.zip",
        mime="application/zip",
        use_container_width=True,
    )
else:
    st.subheader("What this app demonstrates")
    st.markdown(
        "- Synthetic taxpayer generation across CA, TX, NY, IL, and FL\n"
        "- Tax year coverage from 2020 to 2025\n"
        "- Difficulty-based scenario generation\n"
        "- Batch manifest creation and downloadable ZIP packaging\n"
        "- A Streamlit-friendly interface for small demo runs"
    )

