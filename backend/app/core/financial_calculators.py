from typing import Dict


def calculate_investment_growth(
    initial_investment: float,
    monthly_contribution: float,
    annual_return: float,
    years: int,
) -> Dict[str, float]:
    """
    Calculate the future value of an investment with
    an initial investment and regular monthly contributions.

    Assumptions:
    - Contributions are made at the end of each month.
    - Annual return is converted to a monthly rate.
    - Compounding occurs monthly.

    Returns:
        Dictionary containing:
        - total_contributed
        - investment_growth
        - final_balance
    """

    if initial_investment < 0:
        raise ValueError(
            "Initial investment cannot be negative."
        )

    if monthly_contribution < 0:
        raise ValueError(
            "Monthly contribution cannot be negative."
        )

    if annual_return < 0:
        raise ValueError(
            "Annual return cannot be negative."
        )

    if years <= 0:
        raise ValueError(
            "Investment period must be greater than zero."
        )

    monthly_rate = annual_return / 100 / 12
    number_of_months = years * 12

    initial_growth = (
        initial_investment
        * (1 + monthly_rate) ** number_of_months
    )

    if monthly_rate == 0:
        contributions_growth = (
            monthly_contribution
            * number_of_months
        )
    else:
        contributions_growth = (
            monthly_contribution
            * (
                ((1 + monthly_rate) ** number_of_months - 1)
                / monthly_rate
            )
        )

    final_balance = (
        initial_growth
        + contributions_growth
    )

    total_contributed = (
        initial_investment
        + monthly_contribution * number_of_months
    )

    investment_growth = (
        final_balance
        - total_contributed
    )

    return {
        "total_contributed": round(
            total_contributed,
            2,
        ),
        "investment_growth": round(
            investment_growth,
            2,
        ),
        "final_balance": round(
            final_balance,
            2,
        ),
    }


def calculate_loan_payment(
    loan_amount: float,
    annual_interest_rate: float,
    years: int,
) -> Dict[str, float]:
    """
    Calculate the monthly payment and total cost of a loan.

    Assumptions:
    - Fixed interest rate.
    - Monthly payments.
    - Standard amortizing loan.
    - No additional fees or penalties.

    Returns:
        Dictionary containing:
        - loan_amount
        - monthly_payment
        - total_paid
        - total_interest
    """

    if loan_amount <= 0:
        raise ValueError(
            "Loan amount must be greater than zero."
        )

    if annual_interest_rate < 0:
        raise ValueError(
            "Annual interest rate cannot be negative."
        )

    if years <= 0:
        raise ValueError(
            "Loan period must be greater than zero."
        )

    monthly_rate = annual_interest_rate / 100 / 12
    number_of_months = years * 12

    # ---------------------------------------------------------
    # Zero-interest loan
    # ---------------------------------------------------------

    if monthly_rate == 0:
        monthly_payment = (
            loan_amount / number_of_months
        )

    # ---------------------------------------------------------
    # Standard amortizing loan
    # ---------------------------------------------------------

    else:
        monthly_payment = (
            loan_amount
            * (
                monthly_rate
                * (1 + monthly_rate) ** number_of_months
            )
            / (
                (1 + monthly_rate) ** number_of_months
                - 1
            )
        )

    total_paid = (
        monthly_payment
        * number_of_months
    )

    total_interest = (
        total_paid
        - loan_amount
    )

    return {
        "loan_amount": round(
            loan_amount,
            2,
        ),
        "monthly_payment": round(
            monthly_payment,
            2,
        ),
        "total_paid": round(
            total_paid,
            2,
        ),
        "total_interest": round(
            total_interest,
            2,
        ),
    }