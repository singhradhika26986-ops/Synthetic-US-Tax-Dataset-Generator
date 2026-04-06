from __future__ import annotations

from pathlib import Path

from .models import TaxCase
from .template_filler import TemplateFiller


def _currency(amount: float) -> str:
    sign = "-" if amount < 0 else ""
    return f"{sign}${abs(amount):,.2f}"


class PdfBundleRenderer:
    def __init__(self) -> None:
        self.template_filler = TemplateFiller()

    def render_case_bundle(self, case: TaxCase, case_dir: Path) -> None:
        supporting_dir = case_dir / "supporting_docs"
        forms_dir = case_dir / "tax_forms"
        template_filled_dir = case_dir / "template_filled"
        supporting_dir.mkdir(exist_ok=True)
        forms_dir.mkdir(exist_ok=True)
        template_filled_dir.mkdir(exist_ok=True)

        self._render_questionnaire(case, case_dir / "questionnaire.pdf")
        self._render_w2(case, supporting_dir / "w2_primary.pdf")
        self._render_1099(case, supporting_dir / "1099_int.pdf")
        self._render_additional_supporting_docs(case, supporting_dir)
        self._render_supplemental_supporting_docs(case, supporting_dir)
        self._render_federal_summary(case, forms_dir / "form_1040_summary.pdf")
        self._render_state_summary(case, forms_dir / "state_return_summary.pdf")
        self._render_planned_form_packets(case, forms_dir)
        self._render_executive_summary(case, case_dir / "executive_summary.pdf")
        project_root = Path(__file__).resolve().parents[2]
        self.template_filler.fill_selected_templates(case, project_root / "templates", template_filled_dir)

    def _render_page(self, path: Path, title: str, lines: list[str]) -> None:
        text_lines = [title, ""] + lines
        content_commands = ["BT", "/F1 16 Tf", "72 760 Td"]

        first = True
        for raw_line in text_lines:
            line = self._escape_pdf_text(raw_line)
            if first:
                content_commands.append(f"({line}) Tj")
                first = False
            else:
                content_commands.append("0 -18 Td")
                content_commands.append(f"({line}) Tj")
        content_commands.append("ET")
        content_stream = "\n".join(content_commands).encode("ascii")

        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Count 1 /Kids [3 0 R] >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
            f"<< /Length {len(content_stream)} >>\nstream\n".encode("ascii") + content_stream + b"\nendstream",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        ]

        pdf = bytearray(b"%PDF-1.4\n")
        offsets = [0]
        for index, obj in enumerate(objects, start=1):
            offsets.append(len(pdf))
            pdf.extend(f"{index} 0 obj\n".encode("ascii"))
            pdf.extend(obj)
            pdf.extend(b"\nendobj\n")

        xref_start = len(pdf)
        pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        pdf.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
        pdf.extend(
            (
                f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
                f"startxref\n{xref_start}\n%%EOF\n"
            ).encode("ascii")
        )
        path.write_bytes(pdf)

    def _escape_pdf_text(self, value: str) -> str:
        return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    def _render_questionnaire(self, case: TaxCase, path: Path) -> None:
        tp = case.taxpayer
        dependent_text = ", ".join(f"{dep.full_name} ({dep.relationship}, {dep.age})" for dep in case.dependents) or "None"
        compliance_text = "; ".join(f"{item.name}: {item.value}" for item in case.compliance)
        spouse_text = "None"
        if case.spouse is not None:
            spouse = case.spouse
            spouse_text = f"{spouse.first_name} {spouse.last_name}, SSN {spouse.ssn}, DOB {spouse.date_of_birth}, Occupation {spouse.occupation}"
        lines = [
            f"Case ID: {tp.case_id}",
            f"Tax Year: {tp.tax_year}",
            f"Difficulty Level: {tp.difficulty_level}",
            f"Taxpayer: {tp.first_name} {tp.last_name}",
            f"SSN: {tp.ssn}",
            f"Date of Birth: {tp.date_of_birth}",
            f"Email: {tp.email}",
            f"Phone: {tp.phone}",
            f"Occupation: {tp.occupation}",
            f"Filing Status: {tp.filing_status}",
            f"Spouse: {spouse_text}",
            f"Dependents: {dependent_text}",
            f"Address: {tp.address.street}, {tp.address.city}, {tp.address.state} {tp.address.zip_code}",
            f"Compliance: {compliance_text}",
            "",
            "Intake Answers:",
            *[f"{key}: {value}" for key, value in case.intake_answers.items()],
        ]
        self._render_page(path, "Input Questionnaire", lines)

    def _render_w2(self, case: TaxCase, path: Path) -> None:
        w2 = case.w2
        lines = [
            f"Employer Name: {w2.employer_name}",
            f"Employer EIN: {w2.employer_ein}",
            f"Box 1 Wages: {_currency(w2.wages)}",
            f"Federal Income Tax Withheld: {_currency(w2.federal_withholding)}",
            f"Social Security Wages: {_currency(w2.social_security_wages)}",
            f"Medicare Wages: {_currency(w2.medicare_wages)}",
            f"State: {w2.state}",
            f"State Wages: {_currency(w2.state_wages)}",
            f"State Income Tax Withheld: {_currency(w2.state_withholding)}",
        ]
        self._render_page(path, "Supporting Document - W-2", lines)

    def _render_1099(self, case: TaxCase, path: Path) -> None:
        doc = case.interest_1099
        lines = [
            f"Payer Name: {doc.payer_name}",
            f"Interest Income: {_currency(doc.amount)}",
        ]
        self._render_page(path, "Supporting Document - 1099-INT", lines)

    def _render_additional_supporting_docs(self, case: TaxCase, supporting_dir: Path) -> None:
        for doc in case.income_documents:
            if doc.document_type in {"W-2", "1099-INT"}:
                continue
            filename = self._slug(doc.document_type) + ".pdf"
            amounts = [f"{name}: {_currency(value)}" for name, value in doc.amounts.items()]
            lines = [
                f"Document Type: {doc.document_type}",
                f"Issuer: {doc.issuer_name}",
                f"Summary: {doc.summary}",
                *amounts,
            ]
            self._render_page(supporting_dir / filename, f"Supporting Document - {doc.document_type}", lines)

    def _render_supplemental_supporting_docs(self, case: TaxCase, supporting_dir: Path) -> None:
        for index, doc in enumerate(case.supplemental_documents, start=1):
            filename = f"supplemental_{index:02d}_{self._slug(doc.document_type)}.pdf"
            amounts = [f"{name}: {_currency(value)}" for name, value in doc.amounts.items()]
            lines = [
                f"Document Type: {doc.document_type}",
                f"Issuer: {doc.issuer_name}",
                f"Summary: {doc.summary}",
                *amounts,
            ]
            self._render_page(supporting_dir / filename, f"Supporting Document - {doc.document_type}", lines)

    def _render_federal_summary(self, case: TaxCase, path: Path) -> None:
        tax = case.tax
        docs = ", ".join(doc.document_type for doc in case.income_documents)
        supplemental = ", ".join(doc.document_type for doc in case.supplemental_documents) or "None"
        items = "; ".join(f"{item.description}: {_currency(item.amount)}" for item in case.deductions_and_credits) or "None"
        lines = [
            f"Tax Year: {case.taxpayer.tax_year}",
            f"Planned Forms: {', '.join(case.planned_forms)}",
            f"Income Documents: {docs}",
            f"Supplemental Documents: {supplemental}",
            f"Adjusted Gross Income: {_currency(tax.adjusted_gross_income)}",
            f"Taxable Income: {_currency(tax.taxable_income)}",
            f"Federal Tax: {_currency(tax.federal_tax)}",
            f"Federal Withholding: {_currency(case.w2.federal_withholding)}",
            f"Deductions/Credits/Payments: {items}",
        ]
        self._render_page(path, "Federal Return Summary (1040)", lines)

    def _render_state_summary(self, case: TaxCase, path: Path) -> None:
        tax = case.tax
        state_forms = [form for form in case.planned_forms if "540" in form or "IT-" in form or "IL-1040" in form or "State" in form]
        lines = [
            f"Resident State: {case.taxpayer.address.state}",
            f"State Taxable Income: {_currency(tax.taxable_income)}",
            f"State Tax: {_currency(tax.state_tax)}",
            f"State Withholding: {_currency(case.w2.state_withholding)}",
            f"State Forms: {', '.join(state_forms)}",
        ]
        self._render_page(path, "State Return Summary", lines)

    def _render_executive_summary(self, case: TaxCase, path: Path) -> None:
        tax = case.tax
        result_label = "Refund" if tax.refund_or_amount_due >= 0 else "Amount Due"
        effective_tax_rate = 0.0
        if tax.adjusted_gross_income > 0:
            effective_tax_rate = round(((tax.federal_tax + tax.state_tax) / tax.adjusted_gross_income) * 100, 2)
        lines = [
            f"Taxpayer: {case.taxpayer.first_name} {case.taxpayer.last_name}",
            f"Tax Year / Difficulty: {case.taxpayer.tax_year} / {case.taxpayer.difficulty_level}",
            f"Planned Document Count: {case.document_count}",
            f"Actual Supporting Documents: {len(case.income_documents) + len(case.supplemental_documents)}",
            f"Filing Status: {case.taxpayer.filing_status}",
            f"Federal + State Tax: {_currency(tax.federal_tax + tax.state_tax)}",
            f"Total Withholding: {_currency(tax.total_withholding)}",
            f"{result_label}: {_currency(tax.refund_or_amount_due)}",
            f"Effective Tax Rate: {effective_tax_rate}%",
            "",
            "Notes:",
            *case.notes,
        ]
        self._render_page(path, "Executive Summary", lines)

    def _render_planned_form_packets(self, case: TaxCase, forms_dir: Path) -> None:
        for form_name in case.planned_forms:
            filename = self._slug(form_name) + ".pdf"
            lines = self._planned_form_lines(case, form_name)
            self._render_page(forms_dir / filename, f"Planned Form Packet - {form_name}", lines)

    def _planned_form_lines(self, case: TaxCase, form_name: str) -> list[str]:
        tp = case.taxpayer
        base = [
            f"Case ID: {tp.case_id}",
            f"Tax Year: {tp.tax_year}",
            f"Taxpayer: {tp.first_name} {tp.last_name}",
            f"Filing Status: {tp.filing_status}",
            f"Resident State: {tp.address.state}",
            f"AGI: {_currency(case.tax.adjusted_gross_income)}",
            f"Taxable Income: {_currency(case.tax.taxable_income)}",
        ]

        if form_name == "Form 1040":
            return base + [
                f"Wages: {_currency(case.w2.wages)}",
                f"Interest: {_currency(case.interest_1099.amount)}",
                f"Federal Tax: {_currency(case.tax.federal_tax)}",
                f"Refund / Amount Due: {_currency(case.tax.refund_or_amount_due)}",
            ]
        if form_name in {"Schedule B", "Schedule D", "Schedule A", "Schedule C", "Schedule E", "Schedule SE"}:
            related_docs = [doc for doc in case.income_documents if self._form_matches_doc(form_name, doc.document_type)]
            if not related_docs and form_name == "Schedule A":
                related_docs = [doc for doc in case.supplemental_documents if "1098" in doc.document_type or "Property Tax" in doc.document_type]
            lines = list(base)
            lines.append(f"Related Documents Count: {len(related_docs)}")
            for doc in related_docs:
                lines.append(f"{doc.document_type}: {doc.summary}")
                for key, value in doc.amounts.items():
                    lines.append(f"{key}: {_currency(value)}")
            if len(lines) == len(base) + 1:
                lines.append("No direct line items generated; included for packet completeness.")
            return lines
        if form_name in {"Schedules 1-3", "Form 2441", "Form 8606", "Form 8812", "Form 8863", "Form 8949", "Form 1116", "Form 4562", "Form 8962"}:
            lines = list(base)
            lines.append("Scenario support items:")
            for item in case.deductions_and_credits:
                lines.append(f"{item.description}: {_currency(item.amount)}")
            for doc in case.income_documents:
                if self._form_related(form_name, doc.document_type):
                    lines.append(f"{doc.document_type}: {doc.summary}")
            return lines
        if "540" in form_name or "IT-201" in form_name or "IL-1040" in form_name or "State no-return" in form_name:
            return base + [
                f"State Tax: {_currency(case.tax.state_tax)}",
                f"State Withholding: {_currency(case.w2.state_withholding)}",
                f"State Context: {case.intake_answers.get('state_specific_context', '')}",
            ]
        return base + [
            "Supporting packet placeholder for this planned form.",
            f"Planned forms in case: {', '.join(case.planned_forms)}",
        ]

    def _form_matches_doc(self, form_name: str, document_type: str) -> bool:
        mapping = {
            "Schedule B": {"1099-INT", "1099-DIV"},
            "Schedule D": {"1099-B"},
            "Schedule C": {"1099-NEC", "1099-MISC"},
            "Schedule E": {"Rental Statement", "Schedule K-1"},
            "Schedule SE": {"1099-NEC", "1099-MISC"},
        }
        return document_type in mapping.get(form_name, set())

    def _form_related(self, form_name: str, document_type: str) -> bool:
        related = {
            "Form 2441": set(),
            "Form 8606": {"1099-R"},
            "Form 8812": set(),
            "Form 8863": set(),
            "Form 8949": {"1099-B"},
            "Form 1116": {"Foreign Income Statement"},
            "Form 4562": {"Rental Statement", "1099-NEC", "1099-MISC"},
            "Form 8962": {"1095-A"},
            "Schedules 1-3": {"1099-NEC", "1099-MISC", "1099-R", "Foreign Income Statement"},
        }
        return document_type in related.get(form_name, set())

    def _slug(self, value: str) -> str:
        return value.lower().replace(" ", "_").replace("/", "_")


class TemplateRenderer:
    """Hook for future official template-based PDF filling."""

    def render(self, case: TaxCase, templates_dir: Path, output_dir: Path) -> None:
        raise NotImplementedError(
            "Template-based PDF filling is not configured yet. Add official PDF mappings here."
        )
