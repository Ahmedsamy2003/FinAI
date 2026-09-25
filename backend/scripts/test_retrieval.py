from backend.app.rag.retriever import retrieve_documents


def print_results(query: str):
    print("\n" + "=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)

    results = retrieve_documents(
        query=query,
        top_k=4,
    )

    if not results:
        print("No documents retrieved.")
        return

    for result in results:

        print("\n" + "-" * 80)

        print(
            f"RANK: {result['rank']}"
        )

        print(
            f"SOURCE: {result['source']}"
        )

        print(
            f"PAGE: {result['page']}"
        )

        print(
            f"CHUNK ID: {result['chunk_id']}"
        )

        print("\nCONTENT:")

        print(
            result["content"]
        )


def main():

    test_questions = [
        "What is diversification and why is it important?",
        "What is an emergency fund?",
        "What is the relationship between risk and return?",
        "What should someone consider before investing?",
        "What is compound interest?",
    ]

    for question in test_questions:
        print_results(question)


if __name__ == "__main__":
    main()