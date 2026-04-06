from __future__ import annotations


STANDARD_DEDUCTION_SINGLE_BY_YEAR = {
    2020: 12400.0,
    2021: 12550.0,
    2022: 12950.0,
    2023: 13850.0,
    2024: 14600.0,
    2025: 15000.0,
}


def round_currency(value: float) -> float:
    return round(value, 2)


def get_standard_deduction_single(tax_year: int) -> float:
    return STANDARD_DEDUCTION_SINGLE_BY_YEAR.get(tax_year, STANDARD_DEDUCTION_SINGLE_BY_YEAR[2025])


def compute_federal_tax(taxable_income: float, tax_year: int) -> float:
    if taxable_income <= 0:
        return 0.0

    brackets_by_year = {
        2020: [(9_875, 0.10), (40_125, 0.12), (85_525, 0.22), (163_300, 0.24)],
        2021: [(9_950, 0.10), (40_525, 0.12), (86_375, 0.22), (164_925, 0.24)],
        2022: [(10_275, 0.10), (41_775, 0.12), (89_075, 0.22), (170_050, 0.24)],
        2023: [(11_000, 0.10), (44_725, 0.12), (95_375, 0.22), (182_100, 0.24)],
        2024: [(11_600, 0.10), (47_150, 0.12), (100_525, 0.22), (191_950, 0.24)],
        2025: [(11_950, 0.10), (48_600, 0.12), (103_000, 0.22), (196_000, 0.24)],
    }
    brackets = brackets_by_year.get(tax_year, brackets_by_year[2025])

    remaining = taxable_income
    previous_cap = 0.0
    tax = 0.0

    for cap, rate in brackets:
        span = cap - previous_cap
        amount = min(remaining, span)
        if amount > 0:
            tax += amount * rate
            remaining -= amount
        previous_cap = cap
        if remaining <= 0:
            break

    if remaining > 0:
        tax += remaining * 0.32

    return round_currency(tax)


def compute_state_tax(state: str, taxable_income: float) -> float:
    if taxable_income <= 0:
        return 0.0

    state = state.upper()
    flat_rates = {
        "CA": 0.06,
        "NY": 0.058,
        "IL": 0.0495,
        "TX": 0.0,
        "FL": 0.0,
    }
    return round_currency(taxable_income * flat_rates.get(state, 0.04))


def compute_refund(total_withholding: float, total_tax: float) -> float:
    return round_currency(total_withholding - total_tax)
