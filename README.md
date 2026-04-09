# Synthetic Tax Dataset Generator

This project generates synthetic US individual tax datasets with questionnaire PDFs,
supporting documents, executive summaries, planned-form packets, and official-template
filled outputs for the blank forms available in the local workspace.

## Live demo

- Temporary public demo: [https://cold-parents-joke.loca.lt](https://cold-parents-joke.loca.lt)
- GitHub repository: [Synthetic-US-Tax-Dataset-Generator](https://github.com/singhradhika26986-ops/Synthetic-US-Tax-Dataset-Generator)

Note: the public demo uses a temporary tunnel to a local Streamlit process, so the URL
will stay active only while the local app process is running.

## Current coverage

- States: `CA`, `TX`, `NY`, `IL`, `FL`
- Tax years: `2020` through `2025`
- Difficulty tiers:
  - `Level 1`
  - `Level 2`
  - `Level 3`
- Scenario coverage:
  - W-2 employment
  - interest and dividends
  - stock sales
  - retirement income
  - 1099-NEC / 1099-MISC income
  - K-1 income
  - rental income
  - foreign income
  - ACA marketplace forms
  - dependents, credits, deductions, and estimated payments

## What the generator produces

Each synthetic case can include:

- `questionnaire.pdf`
- `supporting_docs/`
- `tax_forms/`
- `executive_summary.pdf`
- `case_data.json`
- `template_filled/`

The `template_filled` folder contains field-filled outputs for the blank templates that
exist locally under `templates/`. The current template-filler implementation covers the
federal, state, and supporting-document blanks listed in
[`docs/final_requirement_audit.md`](docs/final_requirement_audit.md).

## Install

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

Or install the Streamlit app dependencies directly:

```powershell
pip install -r requirements.txt
```

## Common commands

Generate a pilot batch:

```powershell
python .\generate_tax_datasets.py --count 20 --output-dir output\pilot_batch
```

Generate the 2025 relevance set:

```powershell
python .\generate_tax_datasets.py --preset taxyear-2025-relevance --output-dir output\relevance_2025
```

Generate the full production batch:

```powershell
python .\generate_tax_datasets.py --count 2000 --output-dir output\final_2000
```

Run the Streamlit demo app locally:

```powershell
streamlit run .\streamlit_app.py
```

Split the full batch into weekly deliveries:

```powershell
python .\tools\split_into_weekly_batches.py
```

Export template field inventory:

```powershell
python .\tools\export_template_inventory.py
```

## Repository note

Large generated outputs, client-provided sample files, and downloaded blank templates are
ignored in Git for repository health. This repository is intended to track the generator
code, tooling, and documentation. Delivery artifacts stay local or should be shared
through zip files, cloud storage, or release assets.

## Streamlit deployment

This repository includes a Streamlit entrypoint at [`streamlit_app.py`](streamlit_app.py).

To deploy it on Streamlit Community Cloud:

1. Open your workspace at [share.streamlit.io](https://share.streamlit.io/).
2. Click `Create app`.
3. Select this GitHub repository and choose `streamlit_app.py` as the entrypoint.
4. Deploy the app and optionally choose a custom subdomain.

Official Streamlit docs:

- [Deploy your app on Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [File organization for your Community Cloud app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization)

## Project files

- Entry point: [`generate_tax_datasets.py`](generate_tax_datasets.py)
- Streamlit app: [`streamlit_app.py`](streamlit_app.py)
- Generator logic: [`src/synthetic_tax_generator/generator.py`](src/synthetic_tax_generator/generator.py)
- PDF bundle rendering: [`src/synthetic_tax_generator/pdf_renderer.py`](src/synthetic_tax_generator/pdf_renderer.py)
- Official template filling: [`src/synthetic_tax_generator/template_filler.py`](src/synthetic_tax_generator/template_filler.py)
- Final audit: [`docs/final_requirement_audit.md`](docs/final_requirement_audit.md)
