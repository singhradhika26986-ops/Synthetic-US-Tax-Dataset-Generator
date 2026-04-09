# Tax Dataset Intake Checklist

Current snapshot as of `2026-04-03`.

## Required templates

- [x] Federal main return template (`Form 1040`)
- [x] Supporting document template (`W-2`)
- [x] Some additional federal templates present
- [x] State return templates present for `CA`, `NY`, `IL`
- [ ] Supporting document templates for all required `1099` variants
- [ ] All schedules/forms required by the sample package

## Required sample artifacts

- [x] Input questionnaire or prompt package
- [x] Sample supporting documents
- [x] Sample filled federal/state return PDF
- [x] Sample executive summary / tax calculation sheet

## Rules confirmed from project brief

- [x] Tax years `2020` to `2025`
- [x] Required states `CA`, `TX`, `NY`, `IL`, `FL`
- [x] Difficulty levels `Level 1`, `Level 2`, `Level 3`
- [x] Document count expectation by complexity tier
- [x] Broad income/document families required
- [ ] Whether every output must use exact official field-filled PDFs versus sample-style synthetic replicas

## Current workspace status

- Sample package available under [sample](C:/Users/ASUS/Desktop/dataset%20content%20production/sample)
- Blank template inventory available under [templates](C:/Users/ASUS/Desktop/dataset%20content%20production/templates)
- Generator supports a `2025 relevance` preset and writes batch manifests
- Requirement audit available via [tools/requirement_audit.py](C:/Users/ASUS/Desktop/dataset%20content%20production/tools/requirement_audit.py)
