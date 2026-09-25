from backend.app.rag.generator import generate_answer


def main():
    context = """
    Diversification means spreading money among different investments
    that have different risk and return characteristics. Diversification
    can help reduce the risk of losing money because poor performance
    from one investment may be offset by better performance from others.

    Investors should also consider their goals, time horizon, and ability
    and willingness to take risk when making investment decisions.
    """

    question = "What is diversification and why is it important?"

    answer = generate_answer(
        question=question,
        context=context
    )

    print("=" * 80)
    print("QUESTION")
    print("=" * 80)
    print(question)

    print("\n" + "=" * 80)
    print("FINAI ANSWER")
    print("=" * 80)
    print(answer)


if __name__ == "__main__":
    main()