from backend.app.core.financial_tools import (
    detect_financial_intent,
    extract_investment_parameters,
    run_financial_tool,
)


def main():

    questions = [
    "What is diversification and why is it important?",

    "If I invest $1000 initially and contribute $500 per month for 10 years at 8% annual return, how much will I have?",

    "What will $500 monthly become after 20 years at 7%?",

    "If I take a $20,000 loan at 8% for 5 years, what is my monthly payment?",
]

    for question in questions:

        print("=" * 80)
        print("QUESTION")
        print(question)

        print("\nINTENT")
        print(detect_financial_intent(question))

        print("\nPARAMETERS")
        print(extract_investment_parameters(question))

        print("\nTOOL RESULT")
        print(run_financial_tool(question))


if __name__ == "__main__":
    main()