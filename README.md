# Synthetic Tax Dataset Generator

This project scaffolds a pilot-ready pipeline for synthetic US individual tax datasets.

## What it does

- Generates unique fake taxpayer profiles
- Produces logically consistent income, withholding, credits, and refund/balance values
- Exports a folder per case
- Writes a batch manifest summarizing state/year/level distribution
- Creates PDF outputs for:
  - Input questionnaire
  - Supporting income documents
  - Supplemental supporting documents
  - Federal return summary
  - State return summary
  - Executive summary

## Requirements coverage in the current scaffold

- States: `CA`, `TX`, `NY`, `IL`, `FL`
- Tax years: `2020` through `2025`
- Difficulty tiers:
  - `Level 1`
  - `Level 2`
  - `Level 3`
- Scenario support for:
  - dependents
  - estimated payments
  - itemized deductions
  - retirement income
  - stock sales
  - nonemployee income
  - K-1 income
  - rental income
  - foreign income
  - ACA marketplace statements

## Current assumptions

- Output is synthetic only
- Forms are rendered as simple text-based PDFs rather than filling official templates
- Federal filing is modeled with simplified logic across single, head-of-household, and joint-style scenarios
- State logic is currently supported for `CA`, `NY`, `IL`, `TX`, and `FL`
- `TX` and `FL` generate no state income tax due

Once the real sample package and PDF templates are added, the generator can be extended to map values into those exact forms.

## Install

## Generate a pilot batch

```powershell
python .\generate_tax_datasets.py --count 20 --output-dir output\pilot_batch
```

Generate the 2025 relevance set:

```powershell
python .\generate_tax_datasets.py --preset taxyear-2025-relevance --output-dir output\relevance_2025
```

Split a full production run into weekly delivery batches:

```powershell
python .\tools\split_into_weekly_batches.py
```

## Check workspace readiness

```powershell
python .\tools\check_workspace_readiness.py
```

## Inspect template PDFs

```powershell
python .\tools\inspect_pdf_templates.py
```

## Folder structure

Each case is written to its own folder:

```text
output/
  pilot_batch/
    case_0001/
      questionnaire.pdf
      supporting_docs/
        w2_primary.pdf
        1099_int.pdf
      tax_forms/
        form_1040_summary.pdf
        state_return_summary.pdf
      executive_summary.pdf
      case_data.json
```

The JSON file contains the richer scenario data:

- taxpayer profile
- dependents
- income documents
- deductions and credits
- compliance details
- planned federal and state forms
- supplemental supporting documents

Each batch also includes `batch_manifest.json` with:

- counts by state
- counts by tax year
- counts by difficulty level
- per-case planning summary

## Next step when templates arrive

Add template PDFs under `templates/` and replace the placeholder `TemplateRenderer` hooks in [src/synthetic_tax_generator/pdf_renderer.py](C:/Users/ASUS/Desktop/dataset%20content%20production/src/synthetic_tax_generator/pdf_renderer.py).
