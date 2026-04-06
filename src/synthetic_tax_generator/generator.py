from __future__ import annotations

import json
import random
from pathlib import Path

from .models import (
    Address,
    ComplianceItem,
    DeductionCreditItem,
    Dependent,
    IncomeDocument,
    Interest1099Data,
    SpouseProfile,
    TaxCase,
    TaxComputation,
    TaxpayerProfile,
    W2Data,
)
from .pdf_renderer import PdfBundleRenderer
from .tax_logic import (
    compute_federal_tax,
    compute_refund,
    compute_state_tax,
    get_standard_deduction_single,
    round_currency,
)


LEVEL_CONFIG = {
    "Level 1": {
        "filing_statuses": ["Single", "Head of Household"],
        "doc_target": (4, 6),
        "income_types": ["W-2", "1099-INT", "1099-DIV"],
        "optional_docs": ["1098", "Property Tax Statement"],
        "extra_forms": ["Form 1040", "Schedule B"],
    },
    "Level 2": {
        "filing_statuses": ["Single", "Married Filing Jointly", "Head of Household"],
        "doc_target": (7, 10),
        "income_types": ["W-2", "1099-INT", "1099-DIV", "1099-B", "1099-NEC", "1099-R"],
        "optional_docs": ["1095-A", "1098", "HSA Contribution Statement", "IRA Contribution Statement"],
        "extra_forms": ["Form 1040", "Schedules 1-3", "Schedule B", "Schedule D", "Form 8949", "Form 2441", "Form 8863", "Form 8812"],
    },
    "Level 3": {
        "filing_statuses": ["Single", "Married Filing Jointly", "Head of Household"],
        "doc_target": (11, 15),
        "income_types": ["W-2", "1099-INT", "1099-DIV", "1099-B", "1099-NEC", "1099-MISC", "1099-R", "K-1", "Rental", "Foreign Income", "1095-A"],
        "optional_docs": ["1098", "Property Tax Statement", "Brokerage Statement", "Rental Expense Summary", "Business Expense Receipts", "Bank Statement", "HSA Contribution Statement", "IRA Contribution Statement"],
        "extra_forms": ["Form 1040", "Schedules 1-3", "Schedule A", "Schedule B", "Schedule C", "Schedule D", "Schedule E", "Schedule SE", "Form 4562", "Form 8949", "Form 8606", "Form 2441", "Form 8863", "Form 8812", "Form 1116"],
    },
}

STATE_NAMES = {
    "CA": "California",
    "TX": "Texas",
    "NY": "New York",
    "IL": "Illinois",
    "FL": "Florida",
}

STATE_RULE_NOTES = {
    "CA": ["Consider CalEITC/YCTC eligibility", "Track California SDI on W-2", "Apply Schedule CA adjustments"],
    "TX": ["No state income tax return in most cases", "Include franchise/no-state-tax note"],
    "NY": ["Consider renter and household credit scenarios", "Apply New York additions/subtractions"],
    "IL": ["Apply flat state income tax treatment", "Consider property tax credit scenarios"],
    "FL": ["No state income tax return in most cases", "Retain state residency evidence only"],
}


class SyntheticTaxDatasetGenerator:
    def __init__(self, seed: int | None = None) -> None:
        self.random = random.Random(seed)
        self.first_names = [
            "Ava", "Liam", "Noah", "Emma", "Olivia", "Mason", "Sophia", "Isabella",
            "James", "Mia", "Lucas", "Amelia", "Harper", "Ethan", "Charlotte", "Elijah",
        ]
        self.last_names = [
            "Carter", "Nguyen", "Patel", "Johnson", "Garcia", "Brown", "Wilson", "Taylor",
            "Anderson", "Thomas", "Martin", "Jackson", "White", "Harris", "Clark", "Lewis",
        ]
        self.jobs = [
            "Software Analyst", "Retail Manager", "Dental Assistant", "Warehouse Supervisor",
            "Project Coordinator", "Graphic Designer", "Sales Associate", "Bookkeeper",
            "Mechanical Technician", "Teacher", "Business Analyst", "Operations Specialist",
        ]
        self.streets = ["Oak", "Maple", "Cedar", "Pine", "Lake", "Hill", "River", "Sunset"]
        self.street_types = ["St", "Ave", "Blvd", "Rd", "Ln", "Way", "Dr"]
        self.cities = {
            "CA": ["Los Angeles", "San Diego", "Sacramento", "San Jose"],
            "NY": ["Albany", "Buffalo", "Rochester", "Syracuse"],
            "TX": ["Austin", "Dallas", "Plano", "Houston"],
            "FL": ["Miami", "Orlando", "Tampa", "Jacksonville"],
            "IL": ["Chicago", "Naperville", "Springfield", "Peoria"],
        }
        self.email_domains = ["examplemail.com", "maildemo.net", "syntheticdata.org"]
        self.company_prefixes = ["North", "Blue", "Silver", "Summit", "Golden", "Prime"]
        self.company_suffixes = ["Labs", "Services", "Holdings", "Logistics", "Retail", "Systems"]
        self.tax_years = [2020, 2021, 2022, 2023, 2024, 2025]
        self.states = ["CA", "TX", "NY", "IL", "FL"]
        self.levels = list(LEVEL_CONFIG.keys())

    def generate_batch(self, count: int, output_dir: Path) -> list[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        renderer = PdfBundleRenderer()
        written_cases: list[Path] = []
        cases: list[TaxCase] = []

        for index in range(1, count + 1):
            case = self.generate_case(index)
            case_dir = output_dir / case.taxpayer.case_id
            case_dir.mkdir(parents=True, exist_ok=True)
            self._write_json(case, case_dir / "case_data.json")
            renderer.render_case_bundle(case, case_dir)
            written_cases.append(case_dir)
            cases.append(case)

        self._write_batch_manifest(cases, output_dir / "batch_manifest.json")

        return written_cases

    def generate_case(self, index: int) -> TaxCase:
        tax_year = self.tax_years[(index - 1) % len(self.tax_years)]
        state = self.states[(index - 1) % len(self.states)]
        difficulty_level = self.levels[(index - 1) % len(self.levels)]
        level_config = LEVEL_CONFIG[difficulty_level]

        profile = self._build_profile(index, state, tax_year, difficulty_level, level_config["filing_statuses"])
        spouse = self._build_spouse(profile) if profile.filing_status == "Married Filing Jointly" else None
        w2 = self._build_w2(state, tax_year)
        interest = self._build_1099_interest()

        dependents = self._build_dependents(profile.filing_status, difficulty_level)
        income_documents = [w2, interest]
        income_documents.extend(self._build_additional_income_documents(difficulty_level, state))

        deductions_and_credits = self._build_deduction_credit_items(profile, difficulty_level, state, tax_year, dependents)
        compliance = self._build_compliance_items(tax_year)
        intake_answers = self._build_intake_answers(profile, spouse, state, difficulty_level, income_documents, dependents, deductions_and_credits)
        planned_forms = self._build_planned_forms(difficulty_level, state, profile, income_documents, deductions_and_credits)

        total_income = round_currency(sum(self._document_total(doc) for doc in income_documents))
        adjustments = round_currency(sum(item.amount for item in deductions_and_credits if item.category == "adjustment"))
        deductions = round_currency(sum(item.amount for item in deductions_and_credits if item.category == "deduction"))
        credits = round_currency(sum(item.amount for item in deductions_and_credits if item.category == "credit"))

        agi = round_currency(total_income - adjustments)
        standard_deduction = get_standard_deduction_single(tax_year)
        deduction_used = max(standard_deduction, deductions) if profile.filing_status != "Married Filing Separately" else standard_deduction
        taxable_income = max(0.0, round_currency(agi - deduction_used))
        federal_tax_before_credits = compute_federal_tax(taxable_income, tax_year)
        federal_tax = max(0.0, round_currency(federal_tax_before_credits - credits))
        state_tax = compute_state_tax(state, taxable_income)
        total_withholding = round_currency(
            sum(doc.amounts.get("federal_withholding", 0.0) + doc.amounts.get("state_withholding", 0.0) for doc in income_documents)
            + sum(item.amount for item in deductions_and_credits if item.category == "payment")
        )
        penalties = round_currency(sum(item.amount for item in deductions_and_credits if item.category == "penalty"))
        refund = compute_refund(total_withholding, federal_tax + state_tax + penalties)

        tax = TaxComputation(
            adjusted_gross_income=agi,
            taxable_income=taxable_income,
            federal_tax=federal_tax,
            state_tax=state_tax,
            total_withholding=total_withholding,
            refund_or_amount_due=refund,
        )

        target_min, target_max = level_config["doc_target"]
        document_count = min(target_max, max(target_min, len(income_documents) + max(1, len(deductions_and_credits) // 2)))
        supplemental_documents = self._build_supplemental_documents(
            difficulty_level=difficulty_level,
            state=state,
            target_count=document_count,
            current_count=len(income_documents),
        )
        document_count = len(income_documents) + len(supplemental_documents)

        notes = [
            "Synthetic taxpayer profile generated with deterministic random data.",
            f"Scenario covers tax year {tax_year} for {STATE_NAMES[state]} at {difficulty_level}.",
            "Tax values are simplified for dataset generation and still require final sample/template alignment.",
            *STATE_RULE_NOTES[state],
        ]

        return TaxCase(
            taxpayer=profile,
            spouse=spouse,
            w2=w2,
            interest_1099=interest,
            dependents=dependents,
            income_documents=income_documents,
            supplemental_documents=supplemental_documents,
            deductions_and_credits=deductions_and_credits,
            compliance=compliance,
            intake_answers=intake_answers,
            planned_forms=planned_forms,
            document_count=document_count,
            tax=tax,
            notes=notes,
        )

    def _build_profile(self, index: int, state: str, tax_year: int, difficulty_level: str, filing_statuses: list[str]) -> TaxpayerProfile:
        first_name = self.random.choice(self.first_names)
        last_name = self.random.choice(self.last_names)
        filing_status = self.random.choice(filing_statuses)
        address = Address(
            street=f"{self.random.randint(100, 9999)} {self.random.choice(self.streets)} {self.random.choice(self.street_types)}",
            city=self.random.choice(self.cities[state]),
            state=state,
            zip_code=f"{self.random.randint(10000, 99999)}",
        )
        ssn = self._fake_ssn()
        return TaxpayerProfile(
            case_id=f"case_{index:04d}",
            tax_year=tax_year,
            difficulty_level=difficulty_level,
            first_name=first_name,
            last_name=last_name,
            ssn=ssn,
            occupation=self.random.choice(self.jobs),
            email=self._fake_email(first_name, last_name),
            phone=self._fake_phone(),
            date_of_birth=self._fake_dob(),
            address=address,
            filing_status=filing_status,
        )

    def _build_w2(self, state: str, tax_year: int) -> W2Data:
        wages = round_currency(self.random.uniform(28_000, 145_000))
        bonus = round_currency(self.random.uniform(0, 18_000))
        total_wages = round_currency(wages + bonus)
        federal_withholding = round_currency(total_wages * self.random.uniform(0.08, 0.18))
        state_withholding_rate = {
            "CA": self.random.uniform(0.03, 0.07),
            "NY": self.random.uniform(0.03, 0.06),
            "IL": self.random.uniform(0.03, 0.05),
            "TX": 0.0,
            "FL": 0.0,
        }[state]
        state_withholding = round_currency(total_wages * state_withholding_rate)

        return W2Data(
            document_type="W-2",
            issuer_name=self._fake_company_name(),
            summary=f"Primary employment income for tax year {tax_year}",
            amounts={
                "wages": total_wages,
                "federal_withholding": federal_withholding,
                "state_withholding": state_withholding,
            },
            employer_name=self._fake_company_name(),
            employer_ein=self._fake_ein(),
            wages=total_wages,
            federal_withholding=federal_withholding,
            social_security_wages=total_wages,
            medicare_wages=total_wages,
            state=state,
            state_wages=total_wages,
            state_withholding=state_withholding,
        )

    def _build_1099_interest(self) -> Interest1099Data:
        amount = round_currency(self.random.uniform(0, 1_800))
        return Interest1099Data(
            document_type="1099-INT",
            issuer_name=f"{self._fake_company_name()} Bank",
            summary="Taxable bank interest income",
            amounts={"interest_income": amount},
            payer_name=f"{self._fake_company_name()} Bank",
            amount=amount,
        )

    def _build_dependents(self, filing_status: str, difficulty_level: str) -> list[Dependent]:
        if filing_status == "Single":
            return []

        max_dependents = {"Level 1": 1, "Level 2": 2, "Level 3": 3}[difficulty_level]
        dependent_count = self.random.randint(0, max_dependents)
        dependents = []
        for _ in range(dependent_count):
            dependents.append(
                Dependent(
                    full_name=f"{self.random.choice(self.first_names)} {self.random.choice(self.last_names)}",
                    relationship=self.random.choice(["Son", "Daughter", "Parent", "Niece"]),
                    age=self.random.randint(3, 22),
                )
            )
        return dependents

    def _build_spouse(self, profile: TaxpayerProfile) -> SpouseProfile:
        first_name = self.random.choice(self.first_names)
        last_name = profile.last_name
        return SpouseProfile(
            first_name=first_name,
            last_name=last_name,
            ssn=self._fake_ssn(),
            occupation=self.random.choice(self.jobs),
            date_of_birth=self._fake_dob(),
            email=self._fake_email(first_name, last_name),
            phone=self._fake_phone(),
        )

    def _build_additional_income_documents(self, difficulty_level: str, state: str) -> list[IncomeDocument]:
        chosen = []
        available = [kind for kind in LEVEL_CONFIG[difficulty_level]["income_types"] if kind not in {"W-2", "1099-INT"}]
        minimum = {"Level 1": 1, "Level 2": 3, "Level 3": 6}[difficulty_level]
        self.random.shuffle(available)
        for income_type in available[:minimum]:
            chosen.append(self._build_income_document(income_type, state))
        return chosen

    def _build_income_document(self, income_type: str, state: str) -> IncomeDocument:
        amount = round_currency(self.random.uniform(400, 28_000))
        if income_type == "1099-DIV":
            return IncomeDocument("1099-DIV", f"{self._fake_company_name()} Brokerage", "Ordinary and qualified dividends", {"dividends": amount})
        if income_type == "1099-B":
            proceeds = round_currency(amount * self.random.uniform(1.1, 1.8))
            basis = round_currency(proceeds * self.random.uniform(0.65, 0.95))
            return IncomeDocument("1099-B", f"{self._fake_company_name()} Brokerage", "Brokerage sales activity", {"capital_proceeds": proceeds, "capital_basis": basis, "capital_gain": round_currency(proceeds - basis)})
        if income_type == "1099-NEC":
            return IncomeDocument("1099-NEC", self._fake_company_name(), "Nonemployee compensation", {"business_income": amount})
        if income_type == "1099-MISC":
            return IncomeDocument("1099-MISC", self._fake_company_name(), "Miscellaneous income", {"misc_income": amount})
        if income_type == "1099-R":
            taxable = round_currency(amount * self.random.uniform(0.7, 1.0))
            withholding = round_currency(taxable * self.random.uniform(0.05, 0.15))
            return IncomeDocument("1099-R", f"{self._fake_company_name()} Retirement Services", "Retirement distribution", {"retirement_income": taxable, "federal_withholding": withholding})
        if income_type == "K-1":
            return IncomeDocument("Schedule K-1", self._fake_company_name(), "Pass-through entity income", {"k1_income": amount})
        if income_type == "Rental":
            rents = round_currency(amount * self.random.uniform(1.2, 1.8))
            expenses = round_currency(rents * self.random.uniform(0.35, 0.7))
            return IncomeDocument("Rental Statement", f"{self.random.randint(100, 9999)} Rental Property", "Rental income and expense summary", {"rental_income": rents, "rental_expenses": expenses, "net_rental_income": round_currency(rents - expenses)})
        if income_type == "Foreign Income":
            foreign_tax = round_currency(amount * self.random.uniform(0.05, 0.18))
            return IncomeDocument("Foreign Income Statement", "Foreign Employer", "Foreign earned income with taxes paid", {"foreign_income": amount, "foreign_tax_paid": foreign_tax})
        if income_type == "1095-A":
            premium = round_currency(amount * self.random.uniform(0.4, 0.8))
            slcsp = round_currency(premium * self.random.uniform(0.8, 1.1))
            advance = round_currency(premium * self.random.uniform(0.5, 0.9))
            return IncomeDocument("1095-A", "Marketplace Exchange", "ACA marketplace coverage statement", {"annual_premium": premium, "slcsp": slcsp, "advance_ptc": advance})
        return IncomeDocument("State Income Statement", STATE_NAMES[state], "General supplemental income", {"other_income": amount})

    def _build_deduction_credit_items(
        self,
        profile: TaxpayerProfile,
        difficulty_level: str,
        state: str,
        tax_year: int,
        dependents: list[Dependent],
    ) -> list[DeductionCreditItem]:
        items: list[DeductionCreditItem] = []
        if difficulty_level in {"Level 2", "Level 3"}:
            items.append(DeductionCreditItem("payment", "Estimated tax payments", round_currency(self.random.uniform(0, 4_000))))
        if difficulty_level == "Level 3":
            items.append(DeductionCreditItem("adjustment", "Traditional IRA deduction", round_currency(self.random.uniform(0, 3_000))))
            items.append(DeductionCreditItem("deduction", "Itemized deductions total", round_currency(self.random.uniform(14_500, 32_000))))
            items.append(DeductionCreditItem("penalty", "Underpayment penalty", round_currency(self.random.uniform(0, 250))))
        if dependents:
            items.append(DeductionCreditItem("credit", "Child tax or dependent credit", round_currency(500 * len(dependents) + self.random.uniform(0, 1_500))))
        if state == "CA":
            items.append(DeductionCreditItem("credit", "California renter and family credits", round_currency(self.random.uniform(100, 900))))
        if state == "NY":
            items.append(DeductionCreditItem("credit", "New York household credit", round_currency(self.random.uniform(75, 450))))
        if state == "IL":
            items.append(DeductionCreditItem("credit", "Illinois property tax credit", round_currency(self.random.uniform(100, 500))))
        if tax_year >= 2025:
            items.append(DeductionCreditItem("payment", "Extension payment for relevance set", round_currency(self.random.uniform(0, 2_500))))
        return [item for item in items if item.amount > 0]

    def _build_supplemental_documents(
        self,
        difficulty_level: str,
        state: str,
        target_count: int,
        current_count: int,
    ) -> list[IncomeDocument]:
        needed = max(0, target_count - current_count)
        available = list(LEVEL_CONFIG[difficulty_level]["optional_docs"])
        self.random.shuffle(available)
        selected = available[:needed]
        docs: list[IncomeDocument] = []
        for name in selected:
            docs.append(self._build_supporting_document(name, state))
        return docs

    def _build_supporting_document(self, name: str, state: str) -> IncomeDocument:
        if name == "1098":
            mortgage_interest = round_currency(self.random.uniform(2_000, 14_000))
            return IncomeDocument("Form 1098", "Mortgage Servicer", "Mortgage interest statement", {"mortgage_interest": mortgage_interest})
        if name == "Property Tax Statement":
            property_tax = round_currency(self.random.uniform(1_200, 7_500))
            return IncomeDocument("Property Tax Bill", f"{STATE_NAMES[state]} County", "Property tax bill for itemized deduction support", {"property_tax": property_tax})
        if name == "1095-A":
            premium = round_currency(self.random.uniform(1_800, 9_000))
            return IncomeDocument("1095-A", "Marketplace Exchange", "ACA policy statement", {"annual_premium": premium})
        if name == "HSA Contribution Statement":
            amount = round_currency(self.random.uniform(500, 4_150))
            return IncomeDocument("HSA Contribution Statement", "Plan Administrator", "Health savings account contributions", {"hsa_contributions": amount})
        if name == "IRA Contribution Statement":
            amount = round_currency(self.random.uniform(500, 6_500))
            return IncomeDocument("IRA Contribution Statement", "Retirement Custodian", "IRA contribution support", {"ira_contributions": amount})
        if name == "Brokerage Statement":
            amount = round_currency(self.random.uniform(5_000, 45_000))
            return IncomeDocument("Brokerage Statement", "Brokerage Firm", "Year-end brokerage statement", {"ending_balance": amount})
        if name == "Rental Expense Summary":
            amount = round_currency(self.random.uniform(2_000, 18_000))
            return IncomeDocument("Rental Expense Summary", "Property Manager", "Rental receipts and repairs support", {"rental_expenses": amount})
        if name == "Business Expense Receipts":
            amount = round_currency(self.random.uniform(800, 9_500))
            return IncomeDocument("Business Expense Receipts", "Small Business Activity", "Deductible business expense support", {"business_expenses": amount})
        if name == "Bank Statement":
            amount = round_currency(self.random.uniform(1_000, 25_000))
            return IncomeDocument("Bank Statement", "Bank", "Monthly bank statement support", {"average_balance": amount})
        return IncomeDocument(name, "Supporting Issuer", "General supporting document", {"reference_amount": round_currency(self.random.uniform(100, 3_000))})

    def _build_compliance_items(self, tax_year: int) -> list[ComplianceItem]:
        return [
            ComplianceItem("Prior-year filing status", self.random.choice(["Timely filed", "Extension filed", "First-time filer"])),
            ComplianceItem("Estimated payments behavior", self.random.choice(["Quarterly estimates made", "No estimates made", "One catch-up estimate made"])),
            ComplianceItem("E-file preference", self.random.choice(["Electronic filing", "Paper filing simulation"])),
            ComplianceItem("Tax year coverage", str(tax_year)),
        ]

    def _build_intake_answers(
        self,
        profile: TaxpayerProfile,
        spouse: SpouseProfile | None,
        state: str,
        difficulty_level: str,
        income_documents: list[IncomeDocument],
        dependents: list[Dependent],
        deductions_and_credits: list[DeductionCreditItem],
    ) -> dict[str, str]:
        income_types = ", ".join(doc.document_type for doc in income_documents)
        dependent_text = "; ".join(f"{dep.full_name} ({dep.relationship}, age {dep.age})" for dep in dependents) or "No dependents"
        credit_text = ", ".join(item.description for item in deductions_and_credits if item.category == "credit") or "No credits claimed"
        spouse_text = "No spouse on return"
        if spouse is not None:
            spouse_text = f"{spouse.first_name} {spouse.last_name}, DOB {spouse.date_of_birth}, occupation {spouse.occupation}"
        return {
            "filing_status": profile.filing_status,
            "spouse_details": spouse_text,
            "dependent_information": dependent_text,
            "income_sources": income_types,
            "itemized_or_standard": "Itemized" if any(item.category == "deduction" for item in deductions_and_credits) else "Standard",
            "credits_claimed": credit_text,
            "state_specific_context": "; ".join(STATE_RULE_NOTES[state]),
            "complexity_tier": difficulty_level,
        }

    def _build_planned_forms(
        self,
        difficulty_level: str,
        state: str,
        profile: TaxpayerProfile,
        income_documents: list[IncomeDocument],
        deductions_and_credits: list[DeductionCreditItem],
    ) -> list[str]:
        forms = list(LEVEL_CONFIG[difficulty_level]["extra_forms"])
        if any(doc.document_type in {"1099-NEC", "1099-MISC"} for doc in income_documents):
            forms.extend(["Schedule C", "Schedule SE"])
        if any(doc.document_type == "Rental Statement" for doc in income_documents):
            forms.extend(["Schedule E", "Form 4562"])
        if any(doc.document_type == "Foreign Income Statement" for doc in income_documents):
            forms.append("Form 1116")
        if any(doc.document_type == "1095-A" for doc in income_documents):
            forms.append("Form 8962")
        if any(doc.document_type == "1099-R" for doc in income_documents):
            forms.append("Form 8606")
        if any(item.description.startswith("Itemized") for item in deductions_and_credits):
            forms.append("Schedule A")
        state_form = {
            "CA": "Form 540 + Schedule CA + Form 3805V",
            "NY": "IT-201 equivalent + credit schedules",
            "IL": "IL-1040 equivalent + property tax credit schedule",
            "TX": "State no-return residency note",
            "FL": "State no-return residency note",
        }[state]
        forms.append(state_form)
        if profile.filing_status == "Head of Household":
            forms.append("Filing status support worksheet")
        return sorted(set(forms))

    def _document_total(self, doc: IncomeDocument) -> float:
        keys = [
            "wages",
            "interest_income",
            "dividends",
            "capital_gain",
            "business_income",
            "misc_income",
            "retirement_income",
            "k1_income",
            "net_rental_income",
            "foreign_income",
            "other_income",
        ]
        return round_currency(sum(doc.amounts.get(key, 0.0) for key in keys))

    def _fake_ssn(self) -> str:
        return f"{self.random.randint(100, 899):03d}-{self.random.randint(10, 99):02d}-{self.random.randint(1000, 9999):04d}"

    def _fake_ein(self) -> str:
        return f"{self.random.randint(10, 99):02d}-{self.random.randint(1000000, 9999999):07d}"

    def _fake_phone(self) -> str:
        return f"({self.random.randint(200, 989)}) {self.random.randint(200, 989)}-{self.random.randint(1000, 9999)}"

    def _fake_email(self, first_name: str, last_name: str) -> str:
        token = self.random.randint(10, 999)
        domain = self.random.choice(self.email_domains)
        return f"{first_name.lower()}.{last_name.lower()}{token}@{domain}"

    def _fake_dob(self) -> str:
        year = self.random.randint(1958, 2002)
        month = self.random.randint(1, 12)
        day = self.random.randint(1, 28)
        return f"{year:04d}-{month:02d}-{day:02d}"

    def _fake_company_name(self) -> str:
        return f"{self.random.choice(self.company_prefixes)} {self.random.choice(self.company_suffixes)}"

    def _write_json(self, case: TaxCase, target: Path) -> None:
        target.write_text(json.dumps(case.to_dict(), indent=2), encoding="utf-8")

    def _write_batch_manifest(self, cases: list[TaxCase], target: Path) -> None:
        by_state: dict[str, int] = {}
        by_year: dict[str, int] = {}
        by_level: dict[str, int] = {}
        for case in cases:
            by_state[case.taxpayer.address.state] = by_state.get(case.taxpayer.address.state, 0) + 1
            by_year[str(case.taxpayer.tax_year)] = by_year.get(str(case.taxpayer.tax_year), 0) + 1
            by_level[case.taxpayer.difficulty_level] = by_level.get(case.taxpayer.difficulty_level, 0) + 1

        manifest = {
            "total_cases": len(cases),
            "distribution": {
                "by_state": by_state,
                "by_tax_year": by_year,
                "by_difficulty_level": by_level,
            },
            "requirements_alignment": {
                "states": self.states,
                "tax_years": self.tax_years,
                "difficulty_levels": self.levels,
                "tax_year_2025_target_note": "Project asks for about 100 tax-year-2025 cases, around 20 per state.",
            },
            "cases": [
                {
                    "case_id": case.taxpayer.case_id,
                    "tax_year": case.taxpayer.tax_year,
                    "state": case.taxpayer.address.state,
                    "difficulty_level": case.taxpayer.difficulty_level,
                    "document_count": case.document_count,
                    "planned_forms": case.planned_forms,
                }
                for case in cases
            ],
        }
        target.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
