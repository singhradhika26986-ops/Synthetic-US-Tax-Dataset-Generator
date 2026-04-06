from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(slots=True)
class Address:
    street: str
    city: str
    state: str
    zip_code: str


@dataclass(slots=True)
class TaxpayerProfile:
    case_id: str
    tax_year: int
    difficulty_level: str
    first_name: str
    last_name: str
    ssn: str
    occupation: str
    email: str
    phone: str
    date_of_birth: str
    address: Address
    filing_status: str = "Single"


@dataclass(slots=True)
class IncomeDocument:
    document_type: str
    issuer_name: str
    summary: str
    amounts: dict[str, float]


@dataclass(slots=True)
class DeductionCreditItem:
    category: str
    description: str
    amount: float


@dataclass(slots=True)
class ComplianceItem:
    name: str
    value: str


@dataclass(slots=True)
class Dependent:
    full_name: str
    relationship: str
    age: int


@dataclass(slots=True)
class SpouseProfile:
    first_name: str
    last_name: str
    ssn: str
    occupation: str
    date_of_birth: str
    email: str
    phone: str


@dataclass(slots=True)
class W2Data(IncomeDocument):
    employer_name: str
    employer_ein: str
    wages: float
    federal_withholding: float
    social_security_wages: float
    medicare_wages: float
    state: str
    state_wages: float
    state_withholding: float


@dataclass(slots=True)
class Interest1099Data(IncomeDocument):
    payer_name: str
    amount: float


@dataclass(slots=True)
class TaxComputation:
    adjusted_gross_income: float
    taxable_income: float
    federal_tax: float
    state_tax: float
    total_withholding: float
    refund_or_amount_due: float


@dataclass(slots=True)
class TaxCase:
    taxpayer: TaxpayerProfile
    spouse: SpouseProfile | None
    w2: W2Data
    interest_1099: Interest1099Data
    dependents: list[Dependent]
    income_documents: list[IncomeDocument]
    supplemental_documents: list[IncomeDocument]
    deductions_and_credits: list[DeductionCreditItem]
    compliance: list[ComplianceItem]
    intake_answers: dict[str, str]
    planned_forms: list[str]
    document_count: int
    tax: TaxComputation
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
