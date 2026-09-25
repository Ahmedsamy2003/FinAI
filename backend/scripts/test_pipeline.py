from backend.app.rag.pipeline import run_rag_pipeline


def main():
    questions = [
        "What is diversification and why is it important?",
        "What is an emergency fund?",
        "What is the relationship between risk and return?",
        "What is compound interest?",
        "If I invest $1000 initially and contribute $500 per month for 10 years at 8% annual return, how much will I have?",
        "What will $500 monthly become after 20 years at 7%?",
        "If I invest $1000 initially and contribute $500 per month for 10 years at 8% annual return, how much will I have?",
        "What will my monthly payment be for a $20,000 loan at 8% for 5 years?",
        "What will my monthly payment be for a $20,000 loan at 8%?",
    ]

    for question in questions:

        print("\n" + "=" * 80)
        print("QUESTION")
        print("=" * 80)
        print(question)

        print("\n" + "-" * 80)
        print("FINAI")
        print("-" * 80)

        answer = run_rag_pipeline(question)

        print(answer)


if __name__ == "__main__":
    main()