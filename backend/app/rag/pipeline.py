from typing import Any, Dict
import math
from unittest import result
from backend.app.rag.retriever import retrieve_documents
from backend.app.rag.generator import generate_answer
from backend.app.core.memory import conversation_memory
from backend.app.core.financial_tools import run_financial_tool


def save_conversation(
    conversation_id: str,
    question: str,
    answer: str,
) -> None:
    """
    Save the user question and assistant response
    to conversation memory.
    """

    conversation_memory.add_message(
        conversation_id=conversation_id,
        role="user",
        content=question,
    )

    conversation_memory.add_message(
        conversation_id=conversation_id,
        role="assistant",
        content=answer,
    )

def build_investment_chart(
    parameters: Dict[str, Any],
) -> Dict[str, Any]:
    initial = float(parameters["initial_investment"])
    monthly = float(parameters["monthly_contribution"])
    annual_return = float(parameters["annual_return"])
    years = int(parameters["years"])

    monthly_rate = annual_return / 100 / 12
    total_months = years * 12

    data = []

    for year in range(years + 1):
        months = year * 12

        if months == 0:
            balance = initial
        elif monthly_rate == 0:
            balance = initial + monthly * months
        else:
            balance = (
                initial * (1 + monthly_rate) ** months
                + monthly
                * (
                    ((1 + monthly_rate) ** months - 1)
                    / monthly_rate
                )
            )

        data.append(
            {
                "year": "Now" if year == 0 else f"{year}Y",
                "value": round(balance, 2),
            }
        )

    return {
        "type": "area",
        "title": "Investment Growth",
        "eyebrow": "PROJECTION",
        "data": data,
        "xKey": "year",
        "yKey": "value",
        "xLabel": "Years",
        "yLabel": "Projected Balance",
    }


def build_investment_analysis(
    parameters: Dict[str, Any],
    result: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "total_contributed": result["total_contributed"],
        "investment_growth": result["investment_growth"],
        "projected_balance": result["final_balance"],
        "initial_investment": parameters["initial_investment"],
        "monthly_contribution": parameters["monthly_contribution"],
        "annual_return": parameters["annual_return"],
        "period_years": parameters["years"],
    }


def build_loan_chart(
    parameters: Dict[str, Any],
    result: Dict[str, Any],
) -> Dict[str, Any]:
    loan_amount = float(parameters["loan_amount"])
    total_interest = float(result["total_interest"])

    return {
        "type": "bar",
        "title": "Loan Cost Breakdown",
        "eyebrow": "LOAN ANALYSIS",
        "data": [
            {
                "category": "Principal",
                "value": round(loan_amount, 2),
            },
            {
                "category": "Interest",
                "value": round(total_interest, 2),
            },
        ],
        "xKey": "category",
        "yKey": "value",
        "xLabel": "Loan Cost",
        "yLabel": "Amount",
    }

def run_rag_pipeline(
    question: str,
    conversation_id: str = "default",
    top_k: int = 4,
) -> Dict[str, Any]:
    """
    Run the complete FinAI pipeline.

    Returns a structured response containing:

        answer
        type
        intent
        parameters
        result

    This allows the frontend to distinguish between:
        - normal RAG answers
        - investment calculations
        - loan calculations
    """

    # ---------------------------------------------------------
    # 1. Retrieve conversation history
    # ---------------------------------------------------------

    history = conversation_memory.get_history(
        conversation_id
    )

    # ---------------------------------------------------------
    # 2. Check whether the question requires a financial tool
    # ---------------------------------------------------------

    financial_tool_result = run_financial_tool(
        question
    )

    # ---------------------------------------------------------
    # 3. Handle financial calculations
    # ---------------------------------------------------------

    if financial_tool_result is not None:

        intent = financial_tool_result["intent"]
        parameters = financial_tool_result["parameters"]

        # -----------------------------------------------------
        # 3A. Missing parameters
        # -----------------------------------------------------

        if financial_tool_result["type"] == "missing_parameters":

            missing_parameters = []

            # ---------------------------------------------
            # Investment growth
            # ---------------------------------------------

            if intent == "investment_growth":

                if parameters["monthly_contribution"] is None:
                    missing_parameters.append(
                        "monthly contribution"
                    )

                if parameters["annual_return"] is None:
                    missing_parameters.append(
                        "expected annual return"
                    )

                if parameters["years"] is None:
                    missing_parameters.append(
                        "investment period"
                    )

            # ---------------------------------------------
            # Loan payment
            # ---------------------------------------------

            elif intent == "loan_payment":

                if parameters["loan_amount"] is None:
                    missing_parameters.append(
                        "loan amount"
                    )

                if parameters["annual_interest_rate"] is None:
                    missing_parameters.append(
                        "annual interest rate"
                    )

                if parameters["years"] is None:
                    missing_parameters.append(
                        "loan term"
                    )

            # ---------------------------------------------
            # Build response
            # ---------------------------------------------

            if len(missing_parameters) == 1:

                answer = (
                    "I can calculate that for you. "
                    f"I just need your {missing_parameters[0]}."
                )

            else:

                missing = ", ".join(
                    missing_parameters[:-1]
                )

                missing += (
                    f" and {missing_parameters[-1]}"
                )

                answer = (
                    "I can calculate that for you. "
                    f"I just need your {missing}."
                )

            save_conversation(
                conversation_id=conversation_id,
                question=question,
                answer=answer,
            )

            return {
                "answer": answer,
                "type": "calculation",
                "intent": intent,
                "parameters": parameters,
                "result": None,
            }

        # -----------------------------------------------------
        # 3B. Successful calculation
        # -----------------------------------------------------

        result = financial_tool_result["result"]

        # -----------------------------------------------------
        # Build chart data for frontend visualization
        # -----------------------------------------------------

        if intent == "investment_growth":
            initial = parameters["initial_investment"]
            monthly = parameters["monthly_contribution"]
            annual_rate = parameters["annual_return"] / 100
            years = int(parameters["years"])

            monthly_rate = annual_rate / 12

            chart = []

            for year in range(0, years + 1):
                months = year * 12

                if months == 0:
                    balance = initial
                elif monthly_rate == 0:
                    balance = initial + (monthly * months)
                else:
                    balance = (
                        initial * ((1 + monthly_rate) ** months)
                        + monthly
                        * (((1 + monthly_rate) ** months - 1) / monthly_rate)
                    )

                chart.append(
                    {
                        "year": "Now" if year == 0 else f"{year}Y",
                        "value": round(balance, 2),
                    }
                )

            result["chart"] = chart

        # -----------------------------------------------------
        # Investment growth
        # -----------------------------------------------------

        if intent == "investment_growth":

            calculation_context = f"""
The user asked for an investment growth calculation.

The calculation was performed by FinAI's deterministic
financial calculator.

INPUTS:
Initial investment: ${parameters["initial_investment"]:,.2f}
Monthly contribution: ${parameters["monthly_contribution"]:,.2f}
Assumed annual return: {parameters["annual_return"]:.2f}%
Investment period: {parameters["years"]} years

CALCULATED RESULTS:
Total contributed: ${result["total_contributed"]:,.2f}
Investment growth: ${result["investment_growth"]:,.2f}
Projected final balance: ${result["final_balance"]:,.2f}

IMPORTANT:
These are mathematical projections based on the assumptions
provided by the user. They are NOT guaranteed investment
returns.

Explain the result naturally and clearly.
Do not invent additional financial facts.
"""

        # -----------------------------------------------------
        # Loan payment
        # -----------------------------------------------------

        elif intent == "loan_payment":

            calculation_context = f"""
The user asked for a loan payment calculation.

The calculation was performed by FinAI's deterministic
financial calculator.

INPUTS:
Loan amount: ${parameters["loan_amount"]:,.2f}
Annual interest rate: {parameters["annual_interest_rate"]:.2f}%
Loan term: {parameters["years"]:.0f} years

CALCULATED RESULTS:
Monthly payment: ${result["monthly_payment"]:,.2f}
Total paid: ${result["total_paid"]:,.2f}
Total interest: ${result["total_interest"]:,.2f}

IMPORTANT:
These are mathematical loan-payment calculations based on
the assumptions provided by the user.

The calculated payment is not a financial recommendation.
Explain the result naturally and clearly.
Do not invent additional financial facts.
"""

        else:

            calculation_context = (
                "The financial calculator returned a result. "
                "Explain the result clearly using only the "
                "provided calculation data."
            )

        # -----------------------------------------------------
        # Generate natural-language explanation
        # -----------------------------------------------------

        answer = generate_answer(
            question=question,
            context=calculation_context,
            conversation_history=history,
        )

        # -----------------------------------------------------
        # Save conversation
        # -----------------------------------------------------

        save_conversation(
            conversation_id=conversation_id,
            question=question,
            answer=answer,
        )

        # -----------------------------------------------------
        # Return structured calculation response
        # -----------------------------------------------------

        # ---------------------------------------------------------
        # Build visualization data for the frontend
        # ---------------------------------------------------------

        chart = None
        analysis = None

        if intent == "investment_growth":

            chart = build_investment_chart(
                parameters
            )

            analysis = build_investment_analysis(
                parameters,
                result,
            )

        elif intent == "loan_payment":

            chart = build_loan_chart(
                parameters,
                result,
            )


        # ---------------------------------------------------------
        # Return structured calculation response
        # ---------------------------------------------------------

        return {
            "answer": answer,
            "type": "calculation",
            "intent": intent,
            "parameters": parameters,
            "result": result,
            "chart": chart,
            "analysis": analysis,
        }

    # ---------------------------------------------------------
    # 4. Normal RAG knowledge question
    # ---------------------------------------------------------

    documents = retrieve_documents(
        query=question,
        top_k=top_k,
    )

    # ---------------------------------------------------------
    # 5. Handle no retrieval results
    # ---------------------------------------------------------

    if not documents:

        answer = (
            "I couldn't find enough information in my financial "
            "knowledge base to answer that question reliably."
        )

        save_conversation(
            conversation_id=conversation_id,
            question=question,
            answer=answer,
        )

        return {
            "answer": answer,
            "type": "rag",
            "intent": None,
            "parameters": None,
            "result": None,
        }

    # ---------------------------------------------------------
    # 6. Build RAG context
    # ---------------------------------------------------------

    context_parts = []

    for document in documents:
        context_parts.append(
            document["content"]
        )

    context = "\n\n---\n\n".join(
        context_parts
    )

    # ---------------------------------------------------------
    # 7. Generate grounded RAG answer
    # ---------------------------------------------------------

    answer = generate_answer(
        question=question,
        context=context,
        conversation_history=history,
    )

    # ---------------------------------------------------------
    # 8. Save conversation
    # ---------------------------------------------------------

    save_conversation(
        conversation_id=conversation_id,
        question=question,
        answer=answer,
    )

    # ---------------------------------------------------------
    # 9. Return structured RAG response
    # ---------------------------------------------------------

    return {
        "answer": answer,
        "type": "rag",
        "intent": None,
        "parameters": None,
        "result": None,
    }