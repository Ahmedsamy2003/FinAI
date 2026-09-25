import re
from typing import Optional, Dict, Any

from backend.app.core.financial_calculators import (
    calculate_investment_growth,
    calculate_loan_payment,
)


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_financial_intent(question: str) -> str:
    """
    Detect the financial operation required by the user.

    Returns:
        - "investment_growth"
        - "loan_payment"
        - "knowledge"
    """

    text = question.lower().strip()

    # ---------------------------------------------------------
    # Loan payment detection
    # ---------------------------------------------------------

    loan_phrases = [
        "loan payment",
        "loan payments",
        "monthly loan payment",
        "monthly payment",
        "mortgage payment",
        "car loan",
        "loan",
        "borrow",
        "borrowing",
        "repay",
        "repayment",
    ]

    has_loan_language = any(
        phrase in text
        for phrase in loan_phrases
    )

    has_calculation_language = any(
        phrase in text
        for phrase in [
            "calculate",
            "how much",
            "how much will i pay",
            "how much would i pay",
            "what will i pay",
            "what would i pay",
            "what is my payment",
            "what would my payment be",
            "monthly payment",
            "total interest",
        ]
    )

    if has_loan_language and (
        has_calculation_language
        or bool(
            re.search(
                r"\$?\s*\d[\d,]*(?:\.\d+)?",
                text,
            )
        )
    ):
        return "loan_payment"

    # ---------------------------------------------------------
    # Investment calculation detection
    # ---------------------------------------------------------

    investment_calculation_phrases = [
        "calculate",
        "how much will i have",
        "how much would i have",
        "what will i have",
        "what would i have",
        "how much will it grow",
        "how much would it grow",
        "what will it grow to",
        "what would it grow to",
        "future value",
        "investment growth",
        "calculate my investment",
        "calculate the investment",
    ]

    has_investment_calculation_language = any(
        phrase in text
        for phrase in investment_calculation_phrases
    )

    # ---------------------------------------------------------
    # Numerical investment information
    # ---------------------------------------------------------

    has_money_amount = bool(
        re.search(
            r"\$?\s*\d[\d,]*(?:\.\d+)?",
            text,
        )
    )

    has_time_period = bool(
        re.search(
            r"\d+\s*(?:years?|yrs?|months?)",
            text,
        )
    )

    has_percentage = bool(
        re.search(
            r"\d+(?:\.\d+)?\s*%",
            text,
        )
    )

    has_contribution_language = any(
        phrase in text
        for phrase in [
            "per month",
            "monthly",
            "every month",
            "each month",
            "contribute",
        ]
    )

    # ---------------------------------------------------------
    # Explicit investment calculation
    # ---------------------------------------------------------

    if has_investment_calculation_language:
        return "investment_growth"

    # ---------------------------------------------------------
    # Concrete investment scenario
    # ---------------------------------------------------------

    if (
        has_money_amount
        and has_time_period
        and (
            has_percentage
            or has_contribution_language
        )
    ):
        return "investment_growth"

    # ---------------------------------------------------------
    # General financial knowledge
    # ---------------------------------------------------------

    return "knowledge"


# ============================================================
# NUMBER EXTRACTION
# ============================================================

def extract_number(
    pattern: str,
    text: str,
) -> Optional[float]:
    """
    Extract the first numeric value matching a regex pattern.
    """

    match = re.search(
        pattern,
        text,
        re.IGNORECASE,
    )

    if not match:
        return None

    return float(
        match.group(1).replace(",", "")
    )


# ============================================================
# INVESTMENT GROWTH PARAMETERS
# ============================================================

def extract_investment_parameters(
    question: str,
) -> Dict[str, Any]:
    """
    Extract parameters for an investment-growth calculation.

    Supported parameters:
    - initial investment
    - monthly contribution
    - annual return
    - years

    Initial investment is optional and defaults to $0
    during tool execution.
    """

    text = question.lower()

    # ---------------------------------------------------------
    # Initial investment
    # ---------------------------------------------------------

    initial_investment = extract_number(
        r"\$?\s*([\d,]+(?:\.\d+)?)\s*"
        r"(?:initially|initial investment|"
        r"upfront|to start|as an initial investment)",
        text,
    )

    if initial_investment is None:
        initial_investment = extract_number(
            r"(?:start(?:ing)? with|begin(?:ning)? with)"
            r"\s*\$?\s*([\d,]+(?:\.\d+)?)",
            text,
        )

    # "invest $5,000"
    if initial_investment is None:
        initial_investment = extract_number(
            r"(?:invest|investing)\s+"
            r"\$?\s*([\d,]+(?:\.\d+)?)",
            text,
        )

    # ---------------------------------------------------------
    # Monthly contribution
    # ---------------------------------------------------------

    monthly_contribution = extract_number(
        r"\$?\s*([\d,]+(?:\.\d+)?)\s*"
        r"(?:per month|monthly)",
        text,
    )

    if monthly_contribution is None:
        monthly_contribution = extract_number(
            r"(?:contribute|save|invest|put)\s+"
            r"\$?\s*([\d,]+(?:\.\d+)?)\s*"
            r"(?:every month|each month|monthly)",
            text,
        )

    # ---------------------------------------------------------
    # Annual return
    # ---------------------------------------------------------

    annual_return = extract_number(
        r"([\d.]+)\s*%\s*"
        r"(?:annual|per year|return)?",
        text,
    )

    # ---------------------------------------------------------
    # Investment period
    # ---------------------------------------------------------

    years = extract_number(
        r"(\d+)\s*(?:years?|yrs?)",
        text,
    )

    return {
        "initial_investment": initial_investment,
        "monthly_contribution": monthly_contribution,
        "annual_return": annual_return,
        "years": int(years) if years is not None else None,
    }


# ============================================================
# LOAN PAYMENT PARAMETERS
# ============================================================

def extract_loan_parameters(
    question: str,
) -> Dict[str, Any]:
    """
    Extract parameters for a loan-payment calculation.

    Supported parameters:
    - loan amount
    - annual interest rate
    - loan term in years
    """

    text = question.lower()

    # ---------------------------------------------------------
    # Loan amount
    # ---------------------------------------------------------

    loan_amount = extract_number(
        r"(?:loan|borrow|borrowed|amount)\s*"
        r"(?:amount)?\s*(?:of)?\s*"
        r"\$?\s*([\d,]+(?:\.\d+)?)",
        text,
    )

    # Alternative:
    # "$20,000 loan"
    if loan_amount is None:
        loan_amount = extract_number(
            r"\$?\s*([\d,]+(?:\.\d+)?)\s*"
            r"(?:loan|mortgage)",
            text,
        )

    # Alternative:
    # "borrow $20,000"
    if loan_amount is None:
        loan_amount = extract_number(
            r"(?:borrow|borrowed)\s+"
            r"\$?\s*([\d,]+(?:\.\d+)?)",
            text,
        )

    # ---------------------------------------------------------
    # Annual interest rate
    # ---------------------------------------------------------

    annual_interest_rate = extract_number(
        r"([\d.]+)\s*%\s*"
        r"(?:annual|per year|interest|apr)?",
        text,
    )

    # ---------------------------------------------------------
    # Loan term
    # ---------------------------------------------------------

    years = extract_number(
        r"(\d+)\s*(?:years?|yrs?)",
        text,
    )

    # ---------------------------------------------------------
    # Months as loan term
    # ---------------------------------------------------------

    months = extract_number(
        r"(\d+)\s*(?:months?|mos?)",
        text,
    )

    if years is None and months is not None:
        years = months / 12

    return {
        "loan_amount": loan_amount,
        "annual_interest_rate": annual_interest_rate,
        "years": years,
    }


# ============================================================
# FINANCIAL TOOL EXECUTION
# ============================================================

def run_financial_tool(
    question: str,
) -> Optional[Dict[str, Any]]:
    """
    Detect and execute the appropriate financial calculator.

    Supported tools:
    - Investment growth
    - Loan payment

    Returns:
        Calculator result,
        missing-parameter information,
        or None for knowledge questions.
    """

    intent = detect_financial_intent(question)

    # =========================================================
    # LOAN PAYMENT
    # =========================================================

    if intent == "loan_payment":

        parameters = extract_loan_parameters(
            question
        )

        required = [
            "loan_amount",
            "annual_interest_rate",
            "years",
        ]

        if not all(
            parameters[key] is not None
            for key in required
        ):
            return {
                "type": "missing_parameters",
                "intent": intent,
                "parameters": parameters,
            }

        result = calculate_loan_payment(
            loan_amount=parameters["loan_amount"],
            annual_interest_rate=parameters[
                "annual_interest_rate"
            ],
            years=parameters["years"],
        )

        return {
            "type": "calculation",
            "intent": intent,
            "parameters": parameters,
            "result": result,
        }

    # =========================================================
    # INVESTMENT GROWTH
    # =========================================================

    if intent == "investment_growth":

        parameters = extract_investment_parameters(
            question
        )

        # Initial investment is optional.
        # If the user does not provide one,
        # assume $0 initial investment.

        if parameters["initial_investment"] is None:
            parameters["initial_investment"] = 0.0

        required = [
            "monthly_contribution",
            "annual_return",
            "years",
        ]

        if not all(
            parameters[key] is not None
            for key in required
        ):
            return {
                "type": "missing_parameters",
                "intent": intent,
                "parameters": parameters,
            }

        result = calculate_investment_growth(
            initial_investment=parameters[
                "initial_investment"
            ],
            monthly_contribution=parameters[
                "monthly_contribution"
            ],
            annual_return=parameters[
                "annual_return"
            ],
            years=parameters["years"],
        )

        return {
            "type": "calculation",
            "intent": intent,
            "parameters": parameters,
            "result": result,
        }

    # =========================================================
    # KNOWLEDGE QUESTION
    # =========================================================

    return None