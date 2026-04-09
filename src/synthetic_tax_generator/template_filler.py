from __future__ import annotations

from pathlib import Path

from .models import IncomeDocument, TaxCase
from .pdf_utils import load_pdf_reader


def _safe_currency(value: float) -> str:
    return f"{value:.2f}"


class TemplateFiller:
    """Field filler for the blank tax templates currently available in the workspace.

    The mappings are based on the local template inventory and are designed to
    populate every blank form that has been collected for this project.
    """

    def __init__(self) -> None:
        self.PdfReader = load_pdf_reader()
        from pypdf import PdfWriter

        self.PdfWriter = PdfWriter

    def fill_selected_templates(self, case: TaxCase, templates_dir: Path, output_dir: Path) -> list[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        written: list[Path] = []

        plan = [
            ("federal/blank_1040.pdf", "filled_1040.pdf", self._mapping_1040(case)),
            ("supporting_docs/blank_w2.pdf", "filled_w2.pdf", self._mapping_w2(case)),
            ("supporting_docs/blank_1099_int.pdf", "filled_1099_int.pdf", self._mapping_1099_int(case)),
        ]

        div_doc = self._find_income_doc(case, "1099-DIV")
        if div_doc is not None and (templates_dir / "supporting_docs" / "blank_1099_div.pdf").exists():
            plan.append(("supporting_docs/blank_1099_div.pdf", "filled_1099_div.pdf", self._mapping_1099_div(case, div_doc)))

        b_doc = self._find_income_doc(case, "1099-B")
        if b_doc is not None and (templates_dir / "supporting_docs" / "blank_1099_b.pdf").exists():
            plan.append(("supporting_docs/blank_1099_b.pdf", "filled_1099_b.pdf", self._mapping_1099_b(case, b_doc)))
        r_doc = self._find_income_doc(case, "1099-R")
        if r_doc is not None and (templates_dir / "supporting_docs" / "blank_1099_r.pdf").exists():
            plan.append(("supporting_docs/blank_1099_r.pdf", "filled_1099_r.pdf", self._mapping_1099_r(case, r_doc)))
        if case.taxpayer.address.state == "CA" and (templates_dir / "state" / "blank_ca_540.pdf").exists():
            plan.append(("state/blank_ca_540.pdf", "filled_ca_540.pdf", self._mapping_ca_540(case)))
        if case.taxpayer.address.state == "NY" and (templates_dir / "state" / "blank_ny_it201.pdf").exists():
            plan.append(("state/blank_ny_it201.pdf", "filled_ny_it201.pdf", self._mapping_ny_it201(case)))
        if case.taxpayer.address.state == "IL" and (templates_dir / "state" / "blank_il_1040.pdf").exists():
            plan.append(("state/blank_il_1040.pdf", "filled_il_1040.pdf", self._mapping_il_1040(case)))
        if (templates_dir / "federal" / "blank_schedule_b.pdf").exists():
            plan.append(("federal/blank_schedule_b.pdf", "filled_schedule_b.pdf", self._mapping_schedule_b(case)))
        if self._has_business_income(case) and (templates_dir / "federal" / "blank_schedule_c.pdf").exists():
            plan.append(("federal/blank_schedule_c.pdf", "filled_schedule_c.pdf", self._mapping_schedule_c(case)))
        if self._find_income_doc(case, "1099-B") is not None and (templates_dir / "federal" / "blank_schedule_d.pdf").exists():
            plan.append(("federal/blank_schedule_d.pdf", "filled_schedule_d.pdf", self._mapping_schedule_d(case)))
        if self._has_rental_or_k1(case) and (templates_dir / "federal" / "blank_schedule_e.pdf").exists():
            plan.append(("federal/blank_schedule_e.pdf", "filled_schedule_e.pdf", self._mapping_schedule_e(case)))
        if self._has_business_income(case) and (templates_dir / "federal" / "blank_schedule_se.pdf").exists():
            plan.append(("federal/blank_schedule_se.pdf", "filled_schedule_se.pdf", self._mapping_schedule_se(case)))
        if (templates_dir / "federal" / "blank_schedule_1.pdf").exists():
            plan.append(("federal/blank_schedule_1.pdf", "filled_schedule_1.pdf", self._mapping_schedule_1(case)))
        if (templates_dir / "federal" / "blank_schedule_2.pdf").exists():
            plan.append(("federal/blank_schedule_2.pdf", "filled_schedule_2.pdf", self._mapping_schedule_2(case)))
        if (templates_dir / "federal" / "blank_schedule_3.pdf").exists():
            plan.append(("federal/blank_schedule_3.pdf", "filled_schedule_3.pdf", self._mapping_schedule_3(case)))
        if any(item.category == "deduction" for item in case.deductions_and_credits) and (templates_dir / "federal" / "blank_schedule_a.pdf").exists():
            plan.append(("federal/blank_schedule_a.pdf", "filled_schedule_a.pdf", self._mapping_schedule_a(case)))
        if case.dependents and (templates_dir / "federal" / "blank_2441.pdf").exists():
            plan.append(("federal/blank_2441.pdf", "filled_2441.pdf", self._mapping_2441(case)))
        if case.dependents and (templates_dir / "federal" / "blank_8812.pdf").exists():
            plan.append(("federal/blank_8812.pdf", "filled_8812.pdf", self._mapping_8812(case)))
        if case.dependents and (templates_dir / "federal" / "blank_8863.pdf").exists():
            plan.append(("federal/blank_8863.pdf", "filled_8863.pdf", self._mapping_8863(case)))
        if self._find_income_doc(case, "1099-B") is not None and (templates_dir / "federal" / "blank_8949.pdf").exists():
            plan.append(("federal/blank_8949.pdf", "filled_8949.pdf", self._mapping_8949(case)))
        if case.taxpayer.address.state == "CA" and (templates_dir / "state" / "blank_ca_schedule_ca.pdf").exists():
            plan.append(("state/blank_ca_schedule_ca.pdf", "filled_ca_schedule_ca.pdf", self._mapping_ca_schedule_ca(case)))
        if (templates_dir / "federal" / "blank_1040es.pdf").exists():
            plan.append(("federal/blank_1040es.pdf", "filled_1040es.pdf", self._mapping_1040es(case)))
        if (templates_dir / "federal" / "blank_1040v.pdf").exists():
            plan.append(("federal/blank_1040v.pdf", "filled_1040v.pdf", self._mapping_1040v(case)))
        if any(doc.document_type == "Foreign Income Statement" for doc in case.income_documents) and (templates_dir / "federal" / "blank_1116.pdf").exists():
            plan.append(("federal/blank_1116.pdf", "filled_1116.pdf", self._mapping_1116(case)))
        if self._has_rental_or_k1(case) and (templates_dir / "federal" / "blank_4562.pdf").exists():
            plan.append(("federal/blank_4562.pdf", "filled_4562.pdf", self._mapping_4562(case)))
        if self._find_income_doc(case, "1099-R") is not None and (templates_dir / "federal" / "blank_8606.pdf").exists():
            plan.append(("federal/blank_8606.pdf", "filled_8606.pdf", self._mapping_8606(case)))
        if case.dependents and (templates_dir / "federal" / "blank_8867.pdf").exists():
            plan.append(("federal/blank_8867.pdf", "filled_8867.pdf", self._mapping_8867(case)))
        if self._has_qbi_income(case) and (templates_dir / "federal" / "blank_8995.pdf").exists():
            plan.append(("federal/blank_8995.pdf", "filled_8995.pdf", self._mapping_8995(case)))
        if case.taxpayer.address.state == "CA" and (templates_dir / "state" / "blank_ca_3805v.pdf").exists():
            plan.append(("state/blank_ca_3805v.pdf", "filled_ca_3805v.pdf", self._mapping_ca_3805v(case)))
        if self._find_income_doc(case, "1095-A") is not None and (templates_dir / "supporting_docs" / "blank_1095a.pdf").exists():
            plan.append(("supporting_docs/blank_1095a.pdf", "filled_1095a.pdf", self._mapping_1095a(case)))
        if self._find_supporting_doc(case, "Form 1098") is not None and (templates_dir / "supporting_docs" / "blank_1098.pdf").exists():
            plan.append(("supporting_docs/blank_1098.pdf", "filled_1098.pdf", self._mapping_1098(case)))
        misc_doc = self._find_income_doc(case, "1099-MISC")
        if misc_doc is not None and (templates_dir / "supporting_docs" / "blank_1099_misc.pdf").exists():
            plan.append(("supporting_docs/blank_1099_misc.pdf", "filled_1099_misc.pdf", self._mapping_1099_misc(case, misc_doc)))
        nec_doc = self._find_income_doc(case, "1099-NEC")
        if nec_doc is not None and (templates_dir / "supporting_docs" / "blank_1099_nec.pdf").exists():
            plan.append(("supporting_docs/blank_1099_nec.pdf", "filled_1099_nec.pdf", self._mapping_1099_nec(case, nec_doc)))
        k1_doc = self._find_income_doc(case, "Schedule K-1")
        if k1_doc is not None and (templates_dir / "supporting_docs" / "blank_k1.pdf").exists():
            plan.append(("supporting_docs/blank_k1.pdf", "filled_k1.pdf", self._mapping_k1(case, k1_doc)))

        for rel_template, filename, mapping in plan:
            template_path = templates_dir / rel_template
            if not template_path.exists():
                continue
            out = output_dir / filename
            self._fill_pdf(template_path, out, mapping)
            written.append(out)

        return written

    def _fill_pdf(self, template_path: Path, output_path: Path, mapping: dict[str, str]) -> None:
        reader = self.PdfReader(str(template_path))
        writer = self.PdfWriter()
        writer.clone_document_from_reader(reader)
        self._set_fields_in_tree(writer, mapping)
        for page in writer.pages:
            writer.update_page_form_field_values(page, mapping, auto_regenerate=False)
        with output_path.open("wb") as handle:
            writer.write(handle)

    def _set_fields_in_tree(self, writer, mapping: dict[str, str]) -> None:
        from pypdf.generic import NameObject, TextStringObject

        acro_form = writer._root_object.get("/AcroForm")
        if not acro_form or "/Fields" not in acro_form:
            return

        def walk(obj, prefix: str = ""):
            obj = obj.get_object()
            name = obj.get("/T")
            qualified = f"{prefix}.{name}" if prefix and name else (name or prefix)
            kids = obj.get("/Kids")
            if kids:
                for kid in kids:
                    yield from walk(kid, qualified)
            else:
                yield qualified, obj

        for field_root in acro_form["/Fields"]:
            for qualified_name, obj in walk(field_root):
                if qualified_name in mapping:
                    value = mapping[qualified_name]
                    obj[NameObject("/V")] = TextStringObject(value)
                    obj[NameObject("/DV")] = TextStringObject(value)

    def _mapping_1040(self, case: TaxCase) -> dict[str, str]:
        tp = case.taxpayer
        spouse = case.spouse
        mapping = {
            "topmostSubform[0].Page1[0].f1_01[0]": tp.first_name,
            "topmostSubform[0].Page1[0].f1_02[0]": tp.last_name,
            "topmostSubform[0].Page1[0].f1_03[0]": tp.ssn,
            "topmostSubform[0].Page1[0].f1_04[0]": f"{spouse.first_name} {spouse.last_name}" if spouse else "",
            "topmostSubform[0].Page1[0].f1_05[0]": spouse.ssn if spouse else "",
            "topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_20[0]": tp.address.street,
            "topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_22[0]": tp.address.city,
            "topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_23[0]": tp.address.state,
            "topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_24[0]": tp.address.zip_code,
            "topmostSubform[0].Page1[0].f1_11[0]": _safe_currency(case.w2.wages),
            "topmostSubform[0].Page2[0].f2_01[0]": _safe_currency(case.tax.adjusted_gross_income),
            "topmostSubform[0].Page2[0].f2_03[0]": _safe_currency(case.tax.taxable_income),
            "topmostSubform[0].Page2[0].f2_08[0]": _safe_currency(case.tax.federal_tax),
            "topmostSubform[0].Page2[0].f2_11[0]": _safe_currency(case.tax.total_withholding),
        }

        for idx, dep in enumerate(case.dependents[:4], start=0):
            row_base = 31 + (idx * 4)
            mapping[f"topmostSubform[0].Page1[0].Table_Dependents[0].Row{idx + 1}[0].f1_{row_base:02d}[0]"] = dep.full_name
            mapping[f"topmostSubform[0].Page1[0].Table_Dependents[0].Row{idx + 1}[0].f1_{row_base + 1:02d}[0]"] = "SYNTHETIC"
            mapping[f"topmostSubform[0].Page1[0].Table_Dependents[0].Row{idx + 1}[0].f1_{row_base + 2:02d}[0]"] = dep.relationship
        return {k: v for k, v in mapping.items() if v != ""}

    def _mapping_w2(self, case: TaxCase) -> dict[str, str]:
        tp = case.taxpayer
        w2 = case.w2
        return {
            "topmostSubform[0].CopyA[0].BoxA_ReadOrder[0].f1_01[0]": w2.employer_ein,
            "topmostSubform[0].CopyA[0].Col_Left[0].f1_02[0]": w2.employer_name,
            "topmostSubform[0].CopyA[0].Col_Left[0].FirstName_ReadOrder[0].f1_05[0]": tp.first_name,
            "topmostSubform[0].CopyA[0].Col_Left[0].LastName_ReadOrder[0].f1_06[0]": tp.last_name,
            "topmostSubform[0].CopyA[0].Col_Left[0].f1_07[0]": tp.ssn,
            "topmostSubform[0].CopyA[0].Col_Left[0].f1_08[0]": tp.address.street,
            "topmostSubform[0].CopyA[0].Col_Right[0].Box1_ReadOrder[0].f1_09[0]": _safe_currency(w2.wages),
            "topmostSubform[0].CopyA[0].Col_Right[0].Box3_ReadOrder[0].f1_11[0]": _safe_currency(w2.federal_withholding),
            "topmostSubform[0].CopyA[0].Boxes15_ReadOrder[0].Box15_ReadOrder[0].f1_31[0]": tp.address.state,
            "topmostSubform[0].CopyA[0].Box16_ReadOrder[0].f1_35[0]": _safe_currency(w2.state_wages),
            "topmostSubform[0].CopyA[0].Box17_ReadOrder[0].f1_37[0]": _safe_currency(w2.state_withholding),
        }

    def _mapping_1099_int(self, case: TaxCase) -> dict[str, str]:
        tp = case.taxpayer
        doc = case.interest_1099
        return {
            "topmostSubform[0].CopyA[0].CopyHeader[0].CalendarYear1_1[0]": str(case.taxpayer.tax_year),
            "topmostSubform[0].CopyA[0].LeftColumn[0].f1_1[0]": "12-3456789",
            "topmostSubform[0].CopyA[0].LeftColumn[0].f1_2[0]": doc.payer_name,
            "topmostSubform[0].CopyA[0].LeftColumn[0].f1_5[0]": tp.first_name,
            "topmostSubform[0].CopyA[0].LeftColumn[0].f1_6[0]": tp.last_name,
            "topmostSubform[0].CopyA[0].LeftColumn[0].f1_7[0]": tp.address.street,
            "topmostSubform[0].CopyA[0].LeftColumn[0].f1_8[0]": f"{tp.address.city}, {tp.address.state} {tp.address.zip_code}",
            "topmostSubform[0].CopyA[0].RightColumn[0].Box1[0].f1_9[0]": _safe_currency(doc.amount),
        }

    def _mapping_1099_div(self, case: TaxCase, doc: IncomeDocument) -> dict[str, str]:
        tp = case.taxpayer
        amount = doc.amounts.get("dividends", 0.0)
        return {
            "topmostSubform[0].CopyA[0].CopyHeader[0].CalendarYear[0].f1_1[0]": str(case.taxpayer.tax_year),
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_2[0]": "12-3456789",
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_3[0]": doc.issuer_name,
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_6[0]": tp.first_name,
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_7[0]": tp.last_name,
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_8[0]": tp.address.street,
            "topmostSubform[0].CopyA[0].RghtCol[0].f1_9[0]": _safe_currency(amount),
        }

    def _mapping_1099_b(self, case: TaxCase, doc: IncomeDocument) -> dict[str, str]:
        tp = case.taxpayer
        proceeds = doc.amounts.get("capital_proceeds", 0.0)
        basis = doc.amounts.get("capital_basis", 0.0)
        return {
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_1[0]": "12-3456789",
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_2[0]": doc.issuer_name,
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_5[0]": tp.first_name,
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_6[0]": tp.last_name,
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_7[0]": tp.address.street,
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_8[0]": f"{tp.address.city}, {tp.address.state} {tp.address.zip_code}",
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_9[0]": "SYNTH SALE",
            "topmostSubform[0].CopyA[0].RightCol[0].f1_20[0]": _safe_currency(proceeds),
            "topmostSubform[0].CopyA[0].RightCol[0].f1_22[0]": _safe_currency(basis),
        }

    def _mapping_ca_540(self, case: TaxCase) -> dict[str, str]:
        tp = case.taxpayer
        spouse = case.spouse
        mapping = {
            "540-1002": tp.first_name,
            "540-1003": tp.last_name,
            "540-1004": tp.ssn,
            "540-1008": spouse.first_name if spouse else "",
            "540-1009": spouse.last_name if spouse else "",
            "540-1010": spouse.ssn if spouse else "",
            "540-1014": tp.address.street,
            "540-1015": tp.address.city,
            "540-1016": tp.address.state,
            "540-1017": tp.address.zip_code,
            "540-2001": _safe_currency(case.tax.adjusted_gross_income),
            "540-2007": _safe_currency(case.tax.taxable_income),
            "540-2011": _safe_currency(case.tax.state_tax),
            "540-3022": _safe_currency(case.w2.state_withholding),
            "540-4016": _safe_currency(case.tax.refund_or_amount_due if case.tax.refund_or_amount_due > 0 else 0.0),
            "540-4017": _safe_currency(abs(case.tax.refund_or_amount_due) if case.tax.refund_or_amount_due < 0 else 0.0),
        }
        return {k: v for k, v in mapping.items() if v != ""}

    def _mapping_1099_r(self, case: TaxCase, doc: IncomeDocument) -> dict[str, str]:
        tp = case.taxpayer
        taxable = doc.amounts.get("retirement_income", 0.0)
        withholding = doc.amounts.get("federal_withholding", 0.0)
        return {
            "topmostSubform[0].CopyA[0].LeftCol_ReadOrder[0].f1_01[0]": str(case.taxpayer.tax_year),
            "topmostSubform[0].CopyA[0].LeftCol_ReadOrder[0].PayersTIN[0].f1_02[0]": "12-3456789",
            "topmostSubform[0].CopyA[0].LeftCol_ReadOrder[0].f1_03[0]": doc.issuer_name,
            "topmostSubform[0].CopyA[0].LeftCol_ReadOrder[0].f1_06[0]": tp.first_name,
            "topmostSubform[0].CopyA[0].LeftCol_ReadOrder[0].f1_07[0]": tp.last_name,
            "topmostSubform[0].CopyA[0].f1_08[0]": tp.address.street,
            "topmostSubform[0].CopyA[0].f1_09[0]": f"{tp.address.city}, {tp.address.state} {tp.address.zip_code}",
            "topmostSubform[0].CopyA[0].Box3_ReadOrder[0].f1_10[0]": _safe_currency(taxable),
            "topmostSubform[0].CopyA[0].Box5_ReadOrder[0].f1_12[0]": _safe_currency(taxable),
            "topmostSubform[0].CopyA[0].Box7_ReadOrder[0].f1_14[0]": "7",
            "topmostSubform[0].CopyA[0].Box14_ReadOrder[0].f1_22[0]": _safe_currency(withholding),
        }

    def _mapping_ny_it201(self, case: TaxCase) -> dict[str, str]:
        tp = case.taxpayer
        spouse = case.spouse
        mapping = {
            "TP_first_name": tp.first_name,
            "TP_last_name": tp.last_name,
            "TP_SSN": tp.ssn,
            "TP_DOB": tp.date_of_birth,
            "TP_mail_address": tp.address.street,
            "TP_mail_city": tp.address.city,
            "TP_mail_state": tp.address.state,
            "TP_mail_zip": tp.address.zip_code,
            "Spouse_first_name": spouse.first_name if spouse else "",
            "Spouse_last_name": spouse.last_name if spouse else "",
            "Spouse_SSN": spouse.ssn if spouse else "",
            "Spouse_DOB": spouse.date_of_birth if spouse else "",
            "Line1": _safe_currency(case.w2.wages) if False else "",  # reserved if line naming differs
            "Line2": _safe_currency(case.w2.wages),
            "Line8": _safe_currency(case.tax.adjusted_gross_income),
            "Line33": _safe_currency(case.tax.state_tax),
            "Line46": _safe_currency(case.w2.state_withholding),
            "Line80": _safe_currency(case.tax.refund_or_amount_due if case.tax.refund_or_amount_due > 0 else 0.0),
            "Line81": _safe_currency(abs(case.tax.refund_or_amount_due) if case.tax.refund_or_amount_due < 0 else 0.0),
        }
        for idx, dep in enumerate(case.dependents[:7], start=1):
            mapping[f"H_first{idx}"] = dep.full_name.split()[0]
            mapping[f"H_last{idx}"] = dep.full_name.split()[-1]
            mapping[f"H_relationship{idx}"] = dep.relationship
            mapping[f"H_dependent_ssn{idx}"] = "SYNTHETIC"
        return {k: v for k, v in mapping.items() if v != ""}

    def _mapping_il_1040(self, case: TaxCase) -> dict[str, str]:
        tp = case.taxpayer
        spouse = case.spouse
        return {
            "step1-A-firstnamemi": tp.first_name,
            "step1-A-lastname": tp.last_name,
            "step1-A-ssn": tp.ssn,
            "Step1-A-dob": tp.date_of_birth,
            "step1-A-spousefirstnamemi": spouse.first_name if spouse else "",
            "step1-A-spouselastname": spouse.last_name if spouse else "",
            "step1-A-spousessn": spouse.ssn if spouse else "",
            "step1-A-spousedob": spouse.date_of_birth if spouse else "",
            "step1-A-mailingaddress": tp.address.street,
            "step1-A-city": tp.address.city,
            "step1-A-state": tp.address.state,
            "step1-A-zip": tp.address.zip_code,
            "step1-A-email": tp.email,
            "Federally adjusted income": _safe_currency(case.tax.adjusted_gross_income),
            "Total income": _safe_currency(case.tax.adjusted_gross_income),
            "Illinois base income": _safe_currency(case.tax.taxable_income),
            "Income tax": _safe_currency(case.tax.state_tax),
            "Illinois Income Tax withheld": _safe_currency(case.w2.state_withholding),
            "Total Tax": _safe_currency(case.tax.state_tax),
            "Overpayment amount": _safe_currency(case.tax.refund_or_amount_due if case.tax.refund_or_amount_due > 0 else 0.0),
            "Amount you owe": _safe_currency(abs(case.tax.refund_or_amount_due) if case.tax.refund_or_amount_due < 0 else 0.0),
        }

    def _mapping_schedule_b(self, case: TaxCase) -> dict[str, str]:
        tp = case.taxpayer
        div_doc = self._find_income_doc(case, "1099-DIV")
        dividend_amount = div_doc.amounts.get("dividends", 0.0) if div_doc else 0.0
        total_interest = case.interest_1099.amount
        total_dividends = dividend_amount
        return {
            "topmostSubform[0].Page1[0].f1_01[0]": f"{tp.first_name} {tp.last_name}",
            "topmostSubform[0].Page1[0].f1_02[0]": tp.ssn,
            "topmostSubform[0].Page1[0].Line1_ReadOrder[0].f1_03[0]": case.interest_1099.payer_name,
            "topmostSubform[0].Page1[0].f1_04[0]": _safe_currency(case.interest_1099.amount),
            "topmostSubform[0].Page1[0].f1_05[0]": div_doc.issuer_name if div_doc else "",
            "topmostSubform[0].Page1[0].f1_06[0]": _safe_currency(dividend_amount) if div_doc else "",
            "topmostSubform[0].Page1[0].f1_17[0]": _safe_currency(total_interest),
            "topmostSubform[0].Page1[0].f1_33[0]": _safe_currency(total_dividends),
            "topmostSubform[0].Page1[0].ReadOrderControl[0].f1_34[0]": "No" if total_interest + total_dividends < 1500 else "Yes",
        }

    def _mapping_schedule_c(self, case: TaxCase) -> dict[str, str]:
        tp = case.taxpayer
        nec_doc = self._find_income_doc(case, "1099-NEC")
        misc_doc = self._find_income_doc(case, "1099-MISC")
        gross_receipts = sum(
            doc.amounts.get("business_income", 0.0) + doc.amounts.get("misc_income", 0.0)
            for doc in case.income_documents
        )
        car_truck = round(gross_receipts * 0.04, 2)
        supplies = round(gross_receipts * 0.06, 2)
        office = round(gross_receipts * 0.03, 2)
        rent = round(gross_receipts * 0.05, 2)
        utilities = round(gross_receipts * 0.02, 2)
        wages = round(gross_receipts * 0.08, 2)
        other = round(gross_receipts * 0.04, 2)
        total_expenses = round(car_truck + supplies + office + rent + utilities + wages + other, 2)
        net_profit = round(max(0.0, gross_receipts - total_expenses), 2)
        principal_business = "Independent consulting services"
        return {
            "topmostSubform[0].Page1[0].f1_1[0]": f"{tp.first_name} {tp.last_name}",
            "topmostSubform[0].Page1[0].f1_2[0]": tp.occupation,
            "topmostSubform[0].Page1[0].f1_3[0]": "541611",
            "topmostSubform[0].Page1[0].BComb[0].f1_4[0]": "CONSUL",
            "topmostSubform[0].Page1[0].f1_5[0]": self._find_income_doc(case, "1099-NEC").issuer_name if nec_doc else (misc_doc.issuer_name if misc_doc else "Synthetic Client Services"),
            "topmostSubform[0].Page1[0].DComb[0].f1_6[0]": "987654321",
            "topmostSubform[0].Page1[0].f1_7[0]": tp.address.street,
            "topmostSubform[0].Page1[0].f1_8[0]": f"{tp.address.city}, {tp.address.state} {tp.address.zip_code}",
            "topmostSubform[0].Page1[0].f1_9[0]": principal_business,
            "topmostSubform[0].Page1[0].f1_10[0]": _safe_currency(gross_receipts),
            "topmostSubform[0].Page1[0].f1_11[0]": "0.00",
            "topmostSubform[0].Page1[0].f1_12[0]": _safe_currency(gross_receipts),
            "topmostSubform[0].Page1[0].f1_13[0]": "0.00",
            "topmostSubform[0].Page1[0].f1_14[0]": "0.00",
            "topmostSubform[0].Page1[0].f1_15[0]": "0.00",
            "topmostSubform[0].Page1[0].f1_16[0]": _safe_currency(gross_receipts),
            "topmostSubform[0].Page1[0].Lines8-17[0].f1_17[0]": _safe_currency(car_truck),
            "topmostSubform[0].Page1[0].Lines8-17[0].f1_22[0]": _safe_currency(office),
            "topmostSubform[0].Page1[0].Lines8-17[0].f1_23[0]": _safe_currency(rent),
            "topmostSubform[0].Page1[0].Lines18-27[0].f1_30[0]": _safe_currency(supplies),
            "topmostSubform[0].Page1[0].Lines18-27[0].f1_38[0]": _safe_currency(utilities),
            "topmostSubform[0].Page1[0].Lines18-27[0].f1_39[0]": _safe_currency(wages),
            "topmostSubform[0].Page1[0].f1_41[0]": _safe_currency(other),
            "topmostSubform[0].Page1[0].f1_42[0]": _safe_currency(total_expenses),
            "topmostSubform[0].Page1[0].Line30_ReadOrder[0].f1_43[0]": "0.00",
            "topmostSubform[0].Page1[0].Line30_ReadOrder[0].f1_44[0]": _safe_currency(net_profit),
            "topmostSubform[0].Page1[0].f1_45[0]": _safe_currency(net_profit),
            "topmostSubform[0].Page1[0].f1_46[0]": _safe_currency(net_profit),
            "topmostSubform[0].Page2[0].f2_1[0]": _safe_currency(other),
            "topmostSubform[0].Page2[0].f2_2[0]": "Other miscellaneous business expenses",
            "topmostSubform[0].Page2[0].f2_33[0]": _safe_currency(other),
        }

    def _mapping_schedule_d(self, case: TaxCase) -> dict[str, str]:
        tp = case.taxpayer
        doc = self._find_income_doc(case, "1099-B")
        if doc is None:
            return {}
        proceeds = doc.amounts.get("capital_proceeds", 0.0)
        basis = doc.amounts.get("capital_basis", 0.0)
        gain = round(proceeds - basis, 2)
        return {
            "topmostSubform[0].Page1[0].f1_1[0]": f"{tp.first_name} {tp.last_name}",
            "topmostSubform[0].Page1[0].f1_2[0]": tp.ssn,
            "topmostSubform[0].Page1[0].Table_PartI[0].Row1a[0].f1_3[0]": "Synthetic brokerage sale",
            "topmostSubform[0].Page1[0].Table_PartI[0].Row1a[0].f1_4[0]": _safe_currency(proceeds),
            "topmostSubform[0].Page1[0].Table_PartI[0].Row1a[0].f1_5[0]": _safe_currency(basis),
            "topmostSubform[0].Page1[0].Table_PartI[0].Row1a[0].f1_6[0]": _safe_currency(gain),
            "topmostSubform[0].Page1[0].f1_19[0]": _safe_currency(gain),
            "topmostSubform[0].Page1[0].f1_20[0]": "0.00",
            "topmostSubform[0].Page1[0].f1_21[0]": "0.00",
            "topmostSubform[0].Page1[0].f1_22[0]": _safe_currency(gain),
            "topmostSubform[0].Page1[0].Table_PartII[0].Row8a[0].f1_23[0]": "Synthetic long-term sale",
            "topmostSubform[0].Page1[0].Table_PartII[0].Row8a[0].f1_24[0]": _safe_currency(proceeds),
            "topmostSubform[0].Page1[0].Table_PartII[0].Row8a[0].f1_25[0]": _safe_currency(basis),
            "topmostSubform[0].Page1[0].Table_PartII[0].Row8a[0].f1_26[0]": _safe_currency(gain),
            "topmostSubform[0].Page1[0].f1_39[0]": _safe_currency(gain),
            "topmostSubform[0].Page1[0].f1_40[0]": "0.00",
            "topmostSubform[0].Page1[0].f1_41[0]": "0.00",
            "topmostSubform[0].Page1[0].f1_42[0]": _safe_currency(gain),
            "topmostSubform[0].Page1[0].f1_43[0]": _safe_currency(gain),
            "topmostSubform[0].Page2[0].f2_1[0]": _safe_currency(gain),
        }

    def _mapping_schedule_e(self, case: TaxCase) -> dict[str, str]:
        tp = case.taxpayer
        rental_doc = self._find_income_doc(case, "Rental Statement")
        k1_doc = self._find_income_doc(case, "Schedule K-1")
        rental_income = rental_doc.amounts.get("rental_income", 0.0) if rental_doc else 0.0
        rental_expenses = rental_doc.amounts.get("rental_expenses", 0.0) if rental_doc else 0.0
        net_rental = rental_doc.amounts.get("net_rental_income", 0.0) if rental_doc else 0.0
        k1_income = k1_doc.amounts.get("k1_income", 0.0) if k1_doc else 0.0
        return {
            "topmostSubform[0].Page1[0].f1_1[0]": f"{tp.first_name} {tp.last_name}",
            "topmostSubform[0].Page1[0].f1_2[0]": tp.ssn,
            "topmostSubform[0].Page1[0].Table_Line1a[0].RowA[0].f1_3[0]": rental_doc.issuer_name if rental_doc else "Synthetic rental property",
            "topmostSubform[0].Page1[0].Table_Line1b[0].RowA[0].f1_6[0]": "Single Family Residence" if rental_doc else "",
            "topmostSubform[0].Page1[0].Table_Line2[0].RowA[0].f1_9[0]": "365" if rental_doc else "",
            "topmostSubform[0].Page1[0].Table_Line2[0].RowA[0].f1_10[0]": "320" if rental_doc else "",
            "topmostSubform[0].Page1[0].Table_Income[0].Line3[0].f1_16[0]": _safe_currency(rental_income) if rental_doc else "",
            "topmostSubform[0].Page1[0].Table_Expenses[0].Line5[0].f1_22[0]": _safe_currency(round(rental_expenses * 0.10, 2)) if rental_doc else "",
            "topmostSubform[0].Page1[0].Table_Expenses[0].Line6[0].f1_25[0]": _safe_currency(round(rental_expenses * 0.08, 2)) if rental_doc else "",
            "topmostSubform[0].Page1[0].Table_Expenses[0].Line7[0].f1_28[0]": _safe_currency(round(rental_expenses * 0.12, 2)) if rental_doc else "",
            "topmostSubform[0].Page1[0].Table_Expenses[0].Line9[0].f1_34[0]": _safe_currency(round(rental_expenses * 0.07, 2)) if rental_doc else "",
            "topmostSubform[0].Page1[0].Table_Expenses[0].Line12[0].f1_43[0]": _safe_currency(round(rental_expenses * 0.09, 2)) if rental_doc else "",
            "topmostSubform[0].Page1[0].Table_Expenses[0].Line14[0].f1_49[0]": _safe_currency(round(rental_expenses * 0.18, 2)) if rental_doc else "",
            "topmostSubform[0].Page1[0].Table_Expenses[0].Line19[0].f1_64[0]": _safe_currency(round(rental_expenses * 0.11, 2)) if rental_doc else "",
            "topmostSubform[0].Page1[0].Table_Expenses[0].Line20[0].f1_68[0]": _safe_currency(round(rental_expenses * 0.25, 2)) if rental_doc else "",
            "topmostSubform[0].Page1[0].f1_77[0]": _safe_currency(rental_expenses) if rental_doc else "",
            "topmostSubform[0].Page1[0].f1_80[0]": _safe_currency(net_rental) if rental_doc else "",
            "topmostSubform[0].Page2[0].f2_35[0]": _safe_currency(k1_income) if k1_doc else "",
            "topmostSubform[0].Page2[0].f2_60[0]": _safe_currency(net_rental + k1_income),
        }

    def _mapping_schedule_se(self, case: TaxCase) -> dict[str, str]:
        tp = case.taxpayer
        business_income = round(
            sum(doc.amounts.get("business_income", 0.0) + doc.amounts.get("misc_income", 0.0) for doc in case.income_documents),
            2,
        )
        net_earnings = round(business_income * 0.9235, 2)
        se_tax = round(net_earnings * 0.153, 2)
        deduction = round(se_tax * 0.5, 2)
        return {
            "topmostSubform[0].Page1[0].f1_1[0]": f"{tp.first_name} {tp.last_name}",
            "topmostSubform[0].Page1[0].f1_2[0]": tp.ssn,
            "topmostSubform[0].Page1[0].f1_3[0]": _safe_currency(business_income),
            "topmostSubform[0].Page1[0].f1_4[0]": "0.00",
            "topmostSubform[0].Page1[0].f1_5[0]": _safe_currency(business_income),
            "topmostSubform[0].Page1[0].f1_6[0]": _safe_currency(net_earnings),
            "topmostSubform[0].Page1[0].f1_7[0]": _safe_currency(net_earnings),
            "topmostSubform[0].Page1[0].f1_8[0]": _safe_currency(se_tax),
            "topmostSubform[0].Page1[0].f1_9[0]": _safe_currency(se_tax),
            "topmostSubform[0].Page1[0].Line5a_ReadOrder[0].f1_10[0]": _safe_currency(se_tax),
            "topmostSubform[0].Page1[0].f1_11[0]": _safe_currency(deduction),
            "topmostSubform[0].Page1[0].f1_12[0]": _safe_currency(deduction),
            "topmostSubform[0].Page2[0].f2_1[0]": _safe_currency(business_income),
        }

    def _mapping_schedule_1(self, case: TaxCase) -> dict[str, str]:
        business_income = round(sum(doc.amounts.get("business_income", 0.0) + doc.amounts.get("misc_income", 0.0) for doc in case.income_documents), 2)
        rental_income = round(sum(doc.amounts.get("net_rental_income", 0.0) for doc in case.income_documents), 2)
        unemployment = 0.0
        ira_adj = round(sum(item.amount for item in case.deductions_and_credits if item.description.startswith("Traditional IRA")), 2)
        self_employed_deduction = round(business_income * 0.9235 * 0.153 * 0.5, 2) if business_income else 0.0
        total_income = round(business_income + rental_income + unemployment, 2)
        total_adjustments = round(ira_adj + self_employed_deduction, 2)
        return {
            "topmostSubform[0].Page1[0].f1_01[0]": _safe_currency(unemployment),
            "topmostSubform[0].Page1[0].f1_03[0]": _safe_currency(business_income),
            "topmostSubform[0].Page1[0].f1_06[0]": _safe_currency(rental_income),
            "topmostSubform[0].Page1[0].f1_36[0]": _safe_currency(total_income),
            "topmostSubform[0].Page2[0].f2_05[0]": _safe_currency(ira_adj),
            "topmostSubform[0].Page2[0].f2_09[0]": _safe_currency(self_employed_deduction),
            "topmostSubform[0].Page2[0].f2_28[0]": _safe_currency(total_adjustments),
        }

    def _mapping_schedule_2(self, case: TaxCase) -> dict[str, str]:
        self_employment_tax = round(sum(doc.amounts.get("business_income", 0.0) + doc.amounts.get("misc_income", 0.0) for doc in case.income_documents) * 0.9235 * 0.153, 2)
        penalty = round(sum(item.amount for item in case.deductions_and_credits if item.category == "penalty"), 2)
        total = round(self_employment_tax + penalty, 2)
        return {
            "form1[0].Page1[0].f1_01[0]": _safe_currency(self_employment_tax),
            "form1[0].Page1[0].f1_15[0]": _safe_currency(self_employment_tax),
            "form1[0].Page2[0].f2_20[0]": _safe_currency(penalty),
            "form1[0].Page2[0].f2_24[0]": _safe_currency(total),
        }

    def _mapping_schedule_3(self, case: TaxCase) -> dict[str, str]:
        foreign_tax_credit = round(sum(doc.amounts.get("foreign_tax_paid", 0.0) for doc in case.income_documents), 2)
        dependent_credit = round(sum(item.amount for item in case.deductions_and_credits if item.category == "credit"), 2)
        total = round(foreign_tax_credit + dependent_credit, 2)
        return {
            "topmostSubform[0].Page1[0].f1_01[0]": _safe_currency(dependent_credit),
            "topmostSubform[0].Page1[0].f1_10[0]": _safe_currency(foreign_tax_credit),
            "topmostSubform[0].Page1[0].f1_23[0]": _safe_currency(total),
            "topmostSubform[0].Page1[0].f1_35[0]": _safe_currency(total),
        }

    def _mapping_schedule_a(self, case: TaxCase) -> dict[str, str]:
        mortgage_doc = self._find_supporting_doc(case, "Form 1098")
        property_doc = self._find_supporting_doc(case, "Property Tax Bill")
        mortgage_interest = mortgage_doc.amounts.get("mortgage_interest", 0.0) if mortgage_doc else 0.0
        property_tax = property_doc.amounts.get("property_tax", 0.0) if property_doc else 0.0
        state_tax = case.w2.state_withholding
        salt = round(min(10000.0, property_tax + state_tax), 2)
        gifts = round(case.tax.adjusted_gross_income * 0.01, 2)
        total = round(mortgage_interest + salt + gifts, 2)
        return {
            "form1[0].Page1[0].f1_1[0]": _safe_currency(0.0),
            "form1[0].Page1[0].f1_7[0]": _safe_currency(state_tax),
            "form1[0].Page1[0].f1_8[0]": _safe_currency(property_tax),
            "form1[0].Page1[0].f1_15[0]": _safe_currency(mortgage_interest),
            "form1[0].Page1[0].f1_17[0]": _safe_currency(gifts),
            "form1[0].Page1[0].f1_30[0]": _safe_currency(total),
        }

    def _mapping_2441(self, case: TaxCase) -> dict[str, str]:
        dep = case.dependents[0]
        second_dep = case.dependents[1] if len(case.dependents) > 1 else None
        care_expense = 3000.0 if len(case.dependents) == 1 else 6000.0
        earned_income = case.w2.wages
        credit_rate = 0.20
        credit = round(care_expense * credit_rate, 2)
        return {
            "topmostSubform[0].Page1[0].f1_1[0]": f"{case.taxpayer.first_name} {case.taxpayer.last_name}",
            "topmostSubform[0].Page1[0].f1_2[0]": case.taxpayer.ssn,
            "topmostSubform[0].Page1[0].PartITable[0].BodyRow1[0].f1_3[0]": dep.full_name,
            "topmostSubform[0].Page1[0].PartITable[0].BodyRow1[0].ColB[0].f1_4[0]": "SYNTHETIC",
            "topmostSubform[0].Page1[0].PartITable[0].BodyRow1[0].f1_5[0]": _safe_currency(3000.0),
            "topmostSubform[0].Page1[0].PartITable[0].BodyRow1[0].f1_6[0]": _safe_currency(3000.0),
            "topmostSubform[0].Page1[0].PartITable[0].BodyRow2[0].f1_7[0]": second_dep.full_name if second_dep else "",
            "topmostSubform[0].Page1[0].PartITable[0].BodyRow2[0].ColB[0].f1_8[0]": "SYNTHETIC" if second_dep else "",
            "topmostSubform[0].Page1[0].PartITable[0].BodyRow2[0].f1_9[0]": _safe_currency(3000.0) if second_dep else "",
            "topmostSubform[0].Page1[0].PartITable[0].BodyRow2[0].f1_10[0]": _safe_currency(3000.0) if second_dep else "",
            "topmostSubform[0].Page1[0].f1_27[0]": _safe_currency(care_expense),
            "topmostSubform[0].Page1[0].f1_28[0]": _safe_currency(earned_income),
            "topmostSubform[0].Page1[0].f1_29[0]": _safe_currency(earned_income),
            "topmostSubform[0].Page1[0].f1_30[0]": _safe_currency(care_expense),
            "topmostSubform[0].Page1[0].f1_31[0]": "20",
            "topmostSubform[0].Page1[0].f1_32[0]": _safe_currency(credit),
            "topmostSubform[0].Page1[0].f1_33[0]": _safe_currency(credit),
        }

    def _mapping_8812(self, case: TaxCase) -> dict[str, str]:
        child_count = sum(1 for dep in case.dependents if dep.age < 17)
        other_count = max(0, len(case.dependents) - child_count)
        child_credit = child_count * 2000
        other_credit = other_count * 500
        total = child_credit + other_credit
        return {
            "topmostSubform[0].Page1[0].p1-t1[0]": str(child_count),
            "topmostSubform[0].Page1[0].p1-t4[0]": _safe_currency(child_credit),
            "topmostSubform[0].Page1[0].p1-t5[0]": str(other_count),
            "topmostSubform[0].Page1[0].p1-t6[0]": _safe_currency(other_credit),
            "topmostSubform[0].Page1[0].p1-t7[0]": _safe_currency(total),
            "topmostSubform[0].Page1[0].p1-t14[0]": _safe_currency(case.tax.adjusted_gross_income),
            "topmostSubform[0].Page1[0].p1-t30[0]": _safe_currency(total),
            "topmostSubform[0].Page2[0].Line4aChartTable[0].Line4aChartTableRow5[0].EarnedIncome[0].EarnedIncomeCalc[0].p2-t1[0]": _safe_currency(case.w2.wages),
            "topmostSubform[0].Page2[0].Line4aChartTable[0].Line4aChartTableRow5[0].EarnedIncome[0].p2-t4[0]": _safe_currency(total),
        }

    def _mapping_8863(self, case: TaxCase) -> dict[str, str]:
        student_name = case.dependents[0].full_name if case.dependents else f"{case.taxpayer.first_name} {case.taxpayer.last_name}"
        expenses = 4000.0
        credit = 2500.0
        return {
            "topmostSubform[0].Page1[0].f1_1[0]": f"{case.taxpayer.first_name} {case.taxpayer.last_name}",
            "topmostSubform[0].Page1[0].SocialSecurity[0].f1_2[0]": case.taxpayer.ssn.split("-")[0],
            "topmostSubform[0].Page1[0].SocialSecurity[0].f1_3[0]": case.taxpayer.ssn.split("-")[1],
            "topmostSubform[0].Page1[0].SocialSecurity[0].f1_4[0]": case.taxpayer.ssn.split("-")[2],
            "topmostSubform[0].Page2[0].f2_1[0]": student_name,
            "topmostSubform[0].Page2[0].SSN[0].f2_2[0]": case.taxpayer.ssn.split("-")[0],
            "topmostSubform[0].Page2[0].SSN[0].f2_3[0]": case.taxpayer.ssn.split("-")[1],
            "topmostSubform[0].Page2[0].SSN[0].f2_4[0]": case.taxpayer.ssn.split("-")[2],
            "topmostSubform[0].Page2[0].Line22a[0].f2_9[0]": _safe_currency(expenses),
            "topmostSubform[0].Page2[0].Line22a[0].f2_11[0]": _safe_currency(credit),
            "topmostSubform[0].Page2[0].f2_31[0]": _safe_currency(credit),
            "topmostSubform[0].Page2[0].f2_35[0]": _safe_currency(credit),
        }

    def _mapping_8949(self, case: TaxCase) -> dict[str, str]:
        doc = self._find_income_doc(case, "1099-B")
        if doc is None:
            return {}
        proceeds = doc.amounts.get("capital_proceeds", 0.0)
        basis = doc.amounts.get("capital_basis", 0.0)
        gain = round(proceeds - basis, 2)
        return {
            "topmostSubform[0].Page1[0].f1_1[0]": f"{case.taxpayer.first_name} {case.taxpayer.last_name}",
            "topmostSubform[0].Page1[0].f1_2[0]": case.taxpayer.ssn,
            "topmostSubform[0].Page1[0].SectionBTable[0].Line19a[0].f1_26[0]": "Synthetic brokerage sale",
            "topmostSubform[0].Page1[0].SectionBTable[0].Line19a[0].f1_27[0]": "01/15/2022",
            "topmostSubform[0].Page1[0].SectionBTable[0].Line19a[0].f1_28[0]": "11/20/2022",
            "topmostSubform[0].Page1[0].SectionBTable[0].Line19a[0].f1_29[0]": _safe_currency(proceeds),
            "topmostSubform[0].Page1[0].SectionBTable[0].Line19a[0].f1_30[0]": _safe_currency(basis),
            "topmostSubform[0].Page1[0].SectionBTable[0].Line19a[0].f1_31[0]": _safe_currency(gain),
            "topmostSubform[0].Page2[0].f2_5[0]": _safe_currency(gain),
        }

    def _mapping_ca_schedule_ca(self, case: TaxCase) -> dict[str, str]:
        return {
            "540ca_form - 1002": case.taxpayer.first_name,
            "540ca_form - 1003": case.taxpayer.last_name,
            "540ca_form - 1004": case.taxpayer.ssn,
            "540ca_form - 1014": case.taxpayer.address.street,
            "540ca_form - 1015": case.taxpayer.address.city,
            "540ca_form - 1016": case.taxpayer.address.zip_code,
            "540ca_form - 2001": _safe_currency(case.w2.wages),
            "540ca_form - 2007": _safe_currency(case.tax.adjusted_gross_income),
            "540ca_form - 2011": _safe_currency(case.tax.taxable_income),
            "540ca_form - 2013": _safe_currency(case.tax.state_tax),
            "540ca_form - 2039": _safe_currency(case.w2.state_withholding),
        }

    def _mapping_1095a(self, case: TaxCase) -> dict[str, str]:
        doc = self._find_income_doc(case, "1095-A")
        if doc is None:
            return {}
        return {
            "topmostSubform[0].Page1[0].f1_1[0]": "Marketplace Exchange",
            "topmostSubform[0].Page1[0].f1_2[0]": "12-3456789",
            "topmostSubform[0].Page1[0].f1_7[0]": case.taxpayer.first_name,
            "topmostSubform[0].Page1[0].f1_8[0]": case.taxpayer.last_name,
            "topmostSubform[0].Page1[0].f1_9[0]": case.taxpayer.address.street,
            "topmostSubform[0].Page1[0].f1_10[0]": f"{case.taxpayer.address.city}, {case.taxpayer.address.state} {case.taxpayer.address.zip_code}",
            "topmostSubform[0].Page1[0].Table_PartII[0].Row16[0].f1_16[0]": "1",
            "topmostSubform[0].Page1[0].Table_PartII[0].Row16[0].f1_17[0]": _safe_currency(doc.amounts.get("annual_premium", 0.0)),
            "topmostSubform[0].Page1[0].Table_PartII[0].Row16[0].f1_18[0]": _safe_currency(doc.amounts.get("slcsp", 0.0)),
            "topmostSubform[0].Page1[0].Table_PartII[0].Row16[0].f1_19[0]": _safe_currency(doc.amounts.get("advance_ptc", 0.0)),
        }

    def _mapping_1098(self, case: TaxCase) -> dict[str, str]:
        doc = self._find_supporting_doc(case, "Form 1098")
        if doc is None:
            return {}
        return {
            "topmostSubform[0].CopyA[0].CopyHeader[0].CalendarYear[0].f1_1[0]": str(case.taxpayer.tax_year),
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_2[0]": "12-3456789",
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_3[0]": doc.issuer_name,
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_6[0]": case.taxpayer.first_name,
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_7[0]": case.taxpayer.last_name,
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_10[0]": case.taxpayer.address.street,
            "topmostSubform[0].CopyA[0].RightCol[0].f1_11[0]": _safe_currency(doc.amounts.get("mortgage_interest", 0.0)),
        }

    def _mapping_1099_misc(self, case: TaxCase, doc: IncomeDocument) -> dict[str, str]:
        return {
            "topmostSubform[0].CopyA[0].CopyHeader[0].CalendarYear[0].f1_1[0]": str(case.taxpayer.tax_year),
            "topmostSubform[0].CopyA[0].LeftColumn[0].f1_2[0]": "12-3456789",
            "topmostSubform[0].CopyA[0].LeftColumn[0].f1_3[0]": doc.issuer_name,
            "topmostSubform[0].CopyA[0].LeftColumn[0].f1_6[0]": case.taxpayer.first_name,
            "topmostSubform[0].CopyA[0].LeftColumn[0].f1_7[0]": case.taxpayer.last_name,
            "topmostSubform[0].CopyA[0].LeftColumn[0].f1_8[0]": case.taxpayer.address.street,
            "topmostSubform[0].CopyA[0].RightColumn[0].f1_9[0]": _safe_currency(doc.amounts.get("misc_income", 0.0)),
            "topmostSubform[0].CopyA[0].RightColumn[0].f1_10[0]": "0.00",
        }

    def _mapping_1099_nec(self, case: TaxCase, doc: IncomeDocument) -> dict[str, str]:
        return {
            "topmostSubform[0].CopyA[0].PgHeader[0].CalendarYear[0].f1_1[0]": str(case.taxpayer.tax_year),
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_2[0]": "12-3456789",
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_3[0]": doc.issuer_name,
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_6[0]": case.taxpayer.first_name,
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_7[0]": case.taxpayer.last_name,
            "topmostSubform[0].CopyA[0].LeftCol[0].f1_8[0]": case.taxpayer.address.street,
            "topmostSubform[0].CopyA[0].RightCol[0].f1_9[0]": _safe_currency(doc.amounts.get("business_income", 0.0)),
        }

    def _mapping_k1(self, case: TaxCase, doc: IncomeDocument) -> dict[str, str]:
        income = doc.amounts.get("k1_income", 0.0)
        return {
            "topmostSubform[0].Page1[0].Pg1Header[0].ForCalendarYear[0].f1_1[0]": str(case.taxpayer.tax_year),
            "topmostSubform[0].Page1[0].LeftCol[0].f1_6[0]": "12-3456789",
            "topmostSubform[0].Page1[0].LeftCol[0].f1_7[0]": doc.issuer_name,
            "topmostSubform[0].Page1[0].LeftCol[0].f1_11[0]": case.taxpayer.first_name,
            "topmostSubform[0].Page1[0].LeftCol[0].f1_12[0]": case.taxpayer.last_name,
            "topmostSubform[0].Page1[0].LeftCol[0].f1_13[0]": case.taxpayer.ssn,
            "topmostSubform[0].Page1[0].RightCol[0].RightCol1[0].f1_34[0]": _safe_currency(income),
            "topmostSubform[0].Page1[0].RightCol[0].RightCol1[0].f1_35[0]": "0.00",
        }

    def _mapping_1040es(self, case: TaxCase) -> dict[str, str]:
        quarterly = round(max(0.0, case.tax.federal_tax - case.w2.federal_withholding) / 4, 2)
        tp = case.taxpayer
        return {
            "topmostSubform[0].Page12[0].f12_1[0]": f"{tp.first_name} {tp.last_name}",
            "topmostSubform[0].Page12[0].f12_2[0]": tp.ssn,
            "topmostSubform[0].Page12[0].f12_3[0]": _safe_currency(case.tax.adjusted_gross_income),
            "topmostSubform[0].Page12[0].f12_10[0]": _safe_currency(case.tax.federal_tax),
            "topmostSubform[0].Page12[0].f12_20[0]": _safe_currency(quarterly * 4),
            "topmostSubform[0].Page12[0].f12_21[0]": _safe_currency(quarterly),
            "topmostSubform[0].Page13[0].Pg13Table[0].Line1[0].f13_1[0]": "04/15",
            "topmostSubform[0].Page13[0].Pg13Table[0].Line1[0].f13_2[0]": _safe_currency(quarterly),
            "topmostSubform[0].Page13[0].Pg13Table[0].Line2[0].f13_7[0]": "06/15",
            "topmostSubform[0].Page13[0].Pg13Table[0].Line2[0].f13_8[0]": _safe_currency(quarterly),
            "topmostSubform[0].Page13[0].Pg13Table[0].Line3[0].f13_13[0]": "09/15",
            "topmostSubform[0].Page13[0].Pg13Table[0].Line3[0].f13_14[0]": _safe_currency(quarterly),
            "topmostSubform[0].Page13[0].Pg13Table[0].Line4[0].f13_19[0]": "01/15",
            "topmostSubform[0].Page13[0].Pg13Table[0].Line4[0].f13_20[0]": _safe_currency(quarterly),
            "topmostSubform[0].Page13[0].Total[0].f13_25[0]": _safe_currency(quarterly * 4),
        }

    def _mapping_1040v(self, case: TaxCase) -> dict[str, str]:
        tp = case.taxpayer
        amount_due = abs(case.tax.refund_or_amount_due) if case.tax.refund_or_amount_due < 0 else 0.0
        return {
            "topmostSubform[0].Page1[0].f1_1[0]": tp.first_name,
            "topmostSubform[0].Page1[0].f1_2[0]": tp.last_name,
            "topmostSubform[0].Page1[0].f1_3[0]": tp.ssn,
            "topmostSubform[0].Page1[0].f1_5[0]": tp.address.street,
            "topmostSubform[0].Page1[0].f1_6[0]": tp.address.city,
            "topmostSubform[0].Page1[0].f1_7[0]": tp.address.state,
            "topmostSubform[0].Page1[0].f1_8[0]": tp.address.zip_code,
            "topmostSubform[0].Page1[0].f1_14[0]": _safe_currency(amount_due),
            "topmostSubform[0].Page1[0].f1_15[0]": str(tp.tax_year),
        }

    def _mapping_1116(self, case: TaxCase) -> dict[str, str]:
        doc = self._find_income_doc(case, "Foreign Income Statement")
        foreign_income = doc.amounts.get("foreign_income", 0.0) if doc else 0.0
        foreign_tax = doc.amounts.get("foreign_tax_paid", 0.0) if doc else 0.0
        allowed = round(min(foreign_tax, case.tax.federal_tax * (foreign_income / case.tax.adjusted_gross_income if case.tax.adjusted_gross_income else 0.0)), 2)
        return {
            "topmostSubform[0].Page1[0].f1_01[0]": f"{case.taxpayer.first_name} {case.taxpayer.last_name}",
            "topmostSubform[0].Page1[0].f1_02[0]": case.taxpayer.ssn,
            "topmostSubform[0].Page1[0].f1_03[0]": "Passive category income",
            "topmostSubform[0].Page1[0].Table_Part1_LinesI-1a[0].Line1a[0].Line1a_Text[0].f1_07[0]": "Foreign Employer",
            "topmostSubform[0].Page1[0].Table_Part1_LinesI-1a[0].Line1a[0].ColA[0].f1_10[0]": _safe_currency(foreign_income),
            "topmostSubform[0].Page1[0].Table_Part1_LinesI-1a[0].Line1a[0].ColB[0].f1_11[0]": "0.00",
            "topmostSubform[0].Page1[0].Table_Part1_LinesI-1a[0].Line1a[0].ColC[0].f1_12[0]": _safe_currency(foreign_income),
            "topmostSubform[0].Page1[0].f1_50[0]": _safe_currency(foreign_income),
            "topmostSubform[0].Page1[0].f1_51[0]": _safe_currency(foreign_income),
            "topmostSubform[0].Page2[0].f2_01[0]": _safe_currency(case.tax.federal_tax),
            "topmostSubform[0].Page2[0].f2_07[0]": _safe_currency(foreign_tax),
            "topmostSubform[0].Page2[0].f2_27[0]": _safe_currency(allowed),
        }

    def _mapping_4562(self, case: TaxCase) -> dict[str, str]:
        rental_doc = self._find_income_doc(case, "Rental Statement")
        basis = rental_doc.amounts.get("rental_income", 0.0) * 6 if rental_doc else 25000.0
        depreciation = round(basis / 27.5, 2)
        return {
            "topmostSubform[0].Page1[0].f1_1[0]": f"{case.taxpayer.first_name} {case.taxpayer.last_name}",
            "topmostSubform[0].Page1[0].f1_2[0]": case.taxpayer.ssn,
            "topmostSubform[0].Page1[0].f1_15[0]": _safe_currency(0.0),
            "topmostSubform[0].Page1[0].f1_16[0]": _safe_currency(0.0),
            "topmostSubform[0].Page1[0].f1_17[0]": _safe_currency(0.0),
            "topmostSubform[0].Page2[0].f2_1[0]": "Residential rental property",
            "topmostSubform[0].Page2[0].f2_2[0]": "01/01/2025",
            "topmostSubform[0].Page2[0].f2_3[0]": _safe_currency(basis),
            "topmostSubform[0].Page2[0].f2_4[0]": "27.5 yrs",
            "topmostSubform[0].Page2[0].f2_5[0]": _safe_currency(depreciation),
        }

    def _mapping_8606(self, case: TaxCase) -> dict[str, str]:
        ira_adj = round(sum(item.amount for item in case.deductions_and_credits if item.description.startswith("Traditional IRA")), 2)
        r_doc = self._find_income_doc(case, "1099-R")
        distribution = r_doc.amounts.get("retirement_income", 0.0) if r_doc else 0.0
        return {
            "topmostSubform[0].Page1[0].f1_01[0]": _safe_currency(ira_adj),
            "topmostSubform[0].Page1[0].f1_02[0]": "0.00",
            "topmostSubform[0].Page1[0].f1_03[0]": _safe_currency(ira_adj),
            "topmostSubform[0].Page1[0].f1_14[0]": _safe_currency(distribution),
            "topmostSubform[0].Page1[0].f1_15[0]": "0.00",
            "topmostSubform[0].Page2[0].f2_01[0]": _safe_currency(distribution),
            "topmostSubform[0].Page2[0].f2_02[0]": _safe_currency(distribution),
        }

    def _mapping_8867(self, case: TaxCase) -> dict[str, str]:
        return {
            "topmostSubform[0].Page1[0].PgHeader[0].f1_1[0]": f"{case.taxpayer.first_name} {case.taxpayer.last_name}",
            "topmostSubform[0].Page1[0].f1_2[0]": case.taxpayer.ssn,
            "topmostSubform[0].Page1[0].f1_3[0]": "Synthetic preparer checklist completed",
            "topmostSubform[0].Page1[0].f1_4[0]": str(case.taxpayer.tax_year),
            "topmostSubform[0].Page1[0].Line5Entry[0].f1_6[0]": str(len(case.dependents)),
        }

    def _mapping_8995(self, case: TaxCase) -> dict[str, str]:
        qbi = round(sum(doc.amounts.get("business_income", 0.0) + doc.amounts.get("misc_income", 0.0) + doc.amounts.get("k1_income", 0.0) for doc in case.income_documents), 2)
        deduction = round(qbi * 0.20, 2)
        return {
            "topmostSubform[0].Page1[0].f1_01[0]": f"{case.taxpayer.first_name} {case.taxpayer.last_name}",
            "topmostSubform[0].Page1[0].f1_02[0]": case.taxpayer.ssn,
            "topmostSubform[0].Page1[0].Table[0].Row1i[0].f1_03[0]": "Qualified business income",
            "topmostSubform[0].Page1[0].Table[0].Row1i[0].f1_04[0]": _safe_currency(qbi),
            "topmostSubform[0].Page1[0].Table[0].Row1i[0].f1_05[0]": _safe_currency(deduction),
            "topmostSubform[0].Page1[0].f1_18[0]": _safe_currency(qbi),
            "topmostSubform[0].Page1[0].f1_31[0]": _safe_currency(deduction),
            "topmostSubform[0].Page1[0].f1_33[0]": _safe_currency(deduction),
        }

    def _mapping_ca_3805v(self, case: TaxCase) -> dict[str, str]:
        amount_due = abs(case.tax.refund_or_amount_due) if case.tax.refund_or_amount_due < 0 else 0.0
        return {
            "Names as shown on tax return": f"{case.taxpayer.first_name} {case.taxpayer.last_name}",
            "S S N or I T I N (9 digits)": case.taxpayer.ssn.replace("-", ""),
            "Line 2. Itemized deductions or standard deduction from 2024 Form 540, line 18": _safe_currency(case.tax.taxable_income),
            "Line 5. Adjustments to itemized deductions. See instructions": _safe_currency(case.w2.state_withholding),
            "Line 6. M T I. Combine line 1 through line 5": _safe_currency(case.tax.taxable_income),
            "Line 10. Add line 7 and line 9, (e) Total": _safe_currency(amount_due),
        }

    def _replicate_copies(self, base_mapping: dict[str, str]) -> dict[str, str]:
        mapping: dict[str, str] = {}
        prefixes = [
            "topmostSubform[0].CopyA[0].",
            "topmostSubform[0].Copy1[0].",
            "topmostSubform[0].CopyB[0].",
            "topmostSubform[0].Copy2[0].",
            "topmostSubform[0].CopyC[0].",
            "topmostSubform[0].CopyDforPAYER[0].",
        ]
        for prefix in prefixes:
            for short_name, value in base_mapping.items():
                # Map simple discovered field names into all copies.
                mapping[prefix + short_name] = value
        return mapping

    def _find_income_doc(self, case: TaxCase, document_type: str) -> IncomeDocument | None:
        for doc in case.income_documents:
            if doc.document_type == document_type:
                return doc
        return None

    def _find_supporting_doc(self, case: TaxCase, document_type: str) -> IncomeDocument | None:
        for doc in case.supplemental_documents:
            if doc.document_type == document_type:
                return doc
        return None

    def _has_business_income(self, case: TaxCase) -> bool:
        return any(doc.document_type in {"1099-NEC", "1099-MISC"} for doc in case.income_documents)

    def _has_rental_or_k1(self, case: TaxCase) -> bool:
        return any(doc.document_type in {"Rental Statement", "Schedule K-1"} for doc in case.income_documents)

    def _has_qbi_income(self, case: TaxCase) -> bool:
        return any(doc.document_type in {"1099-NEC", "1099-MISC", "Schedule K-1"} for doc in case.income_documents)
