# Synthetic Tax Dataset Generator

This project generates synthetic US individual tax datasets with questionnaire PDFs,
supporting documents, executive summaries, planned-form packets, and official-template
filled outputs for the blank forms available in the local workspace.

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
[docs/final_requirement_audit.md](C:/Users/ASUS/Desktop/dataset%20content%20production/docs/final_requirement_audit.md).

## Install

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
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

## Project files

- Entry point: [generate_tax_datasets.py](C:/Users/ASUS/Desktop/dataset%20content%20production/generate_tax_datasets.py)
- Generator logic: [generator.py](C:/Users/ASUS/Desktop/dataset%20content%20production/src/synthetic_tax_generator/generator.py)
- PDF bundle rendering: [pdf_renderer.py](C:/Users/ASUS/Desktop/dataset%20content%20production/src/synthetic_tax_generator/pdf_renderer.py)
- Official template filling: [template_filler.py](C:/Users/ASUS/Desktop/dataset%20content%20production/src/synthetic_tax_generator/template_filler.py)
- Final audit: [final_requirement_audit.md](C:/Users/ASUS/Desktop/dataset%20content%20production/docs/final_requirement_audit.md)
