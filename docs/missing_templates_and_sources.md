# Missing Templates And Official Sources

Updated based on official sources checked on `2026-04-03`.

## Current workspace status

Already present:

- [blank_1040.pdf](C:/Users/ASUS/Desktop/dataset%20content%20production/templates/federal/blank_1040.pdf)
- [blank_w2.pdf](C:/Users/ASUS/Desktop/dataset%20content%20production/templates/supporting_docs/blank_w2.pdf)
- Complete sample package under [sample](C:/Users/ASUS/Desktop/dataset%20content%20production/sample)

Still missing:

- Federal schedules and additional forms
- State blank forms for `CA`, `NY`, `IL`
- Additional supporting-document templates (`1099` variants, etc.)

## Federal forms

- Form 1040 hub: [IRS - About Form 1040](https://www.irs.gov/forms-pubs/about-form-1040)
- Schedules hub: [IRS - Schedules for Form 1040](https://www.irs.gov/forms-pubs/schedules-for-form-1040)
- Schedule A: [IRS - About Schedule A](https://www.irs.gov/forms-pubs/about-schedule-a-form-1040)
- Schedule B: [IRS - About Schedule B](https://www.irs.gov/forms-pubs/about-schedule-b-form-1040)
- Schedule C: [IRS - About Schedule C](https://www.irs.gov/forms-pubs/about-schedule-c-form-1040)
- Schedule D: [IRS - About Schedule D](https://www.irs.gov/forms-pubs/about-schedule-d-form-1040)
- Schedule E: [IRS - About Schedule E](https://www.irs.gov/forms-pubs/about-schedule-e-form-1040)
- Schedule SE: [IRS - About Schedule SE](https://www.irs.gov/forms-pubs/about-schedule-se-form-1040)
- Form 4562: [IRS - About Form 4562](https://www.irs.gov/forms-pubs/about-form-4562)
- Form 2441: [IRS - About Form 2441](https://www.irs.gov/forms-pubs/about-form-2441)
- Form 8863: [IRS - About Form 8863](https://www.irs.gov/forms-pubs/about-form-8863)
- Schedule 8812: [IRS - About Schedule 8812](https://www.irs.gov/forms-pubs/about-schedule-8812-form-1040)
- Form 1116: [IRS - Form 1116 instructions page](https://www.irs.gov/instructions/i1116)
- Form 8949: [IRS - About Form 8949](https://www.irs.gov/forms-pubs/about-form-8949)
- Form 8606: [IRS - About Form 8606](https://www.irs.gov/forms-pubs/about-form-8606)
- Form 1040-ES: [IRS - About Form 1040-ES](https://www.irs.gov/forms-pubs/about-form-1040-es)
- Form 1040-V: [IRS - About Form 1040](https://www.irs.gov/forms-pubs/about-form-1040)

Practical note:

- The IRS "About" pages usually expose the current revision PDF link for that form.
- For `Schedules 1–3`, use the [Form 1040 hub](https://www.irs.gov/forms-pubs/about-form-1040), which explicitly lists those numbered schedules.

## State forms

- California Form 540 booklet and form source: [FTB - 2024 Form 540 booklet](https://www.ftb.ca.gov/forms/2024/2024-540-booklet.html)
- New York IT-201 fill-in form: [NY Tax - 2024 IT-201 fill-in PDF](https://www.tax.ny.gov/pdf/2024/inc/it201_2024_fill_in_2d.pdf)
- New York IT-201 instructions: [NY Tax - 2024 IT-201-I](https://www.tax.ny.gov/forms/html-instructions/2024/it/it201i-2024.htm)
- Illinois IL-1040 fill-in form: [Illinois DOR - 2024 IL-1040 PDF](https://tax.illinois.gov/content/dam/soi/en/web/tax/forms/incometax/documents/currentyear/individual/il-1040.pdf)
- Illinois IL-1040 instructions: [Illinois DOR - 2024 IL-1040 instructions PDF](https://tax.illinois.gov/content/dam/soi/en/web/tax/forms/incometax/documents/currentyear/individual/il-1040-instr.pdf)

Important note:

- `Texas` and `Florida` generally do not have a personal state income tax return for individuals.
- For this project, that likely means using a `no state return / residency note` approach for those states unless the boss gives a different requirement. This is an inference from the official state tax context.

## Supporting-document templates

Likely needed but not yet available as blank templates:

- `1099-INT`
- `1099-DIV`
- `1099-B`
- `1099-R`
- `1099-NEC`
- `1099-MISC`
- `Schedule K-1`
- `1095-A`
- `1098`

Practical fallback if official blanks are not provided:

- Use the sample files in [sample/supporting_docs](C:/Users/ASUS/Desktop/dataset%20content%20production/sample/supporting_docs) as visual references.
- Generate synthetic replica PDFs with the same general structure, but with clearly synthetic data.

## Best next action

1. Download federal PDFs from the IRS links above into [templates/federal](C:/Users/ASUS/Desktop/dataset%20content%20production/templates/federal)
2. Download CA/NY/IL state PDFs into [templates/state](C:/Users/ASUS/Desktop/dataset%20content%20production/templates/state)
3. If official supporting-doc blanks are unavailable, continue with sample-style synthetic replicas for W-2/1099/K-1/1095-A/1098 documents
