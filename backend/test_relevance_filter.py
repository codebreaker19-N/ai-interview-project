from app.rag.retrieval.relevance_filter import RelevanceFilter


def main():

    results = [
        {
            "reranker_score": 8.1036,
            "metadata": {
                "concept": "Retrieval-Augmented Generation"
            }
        },
        {
            "reranker_score": -11.1465,
            "metadata": {
                "concept": "STAR Method"
            }
        }
    ]

    relevance_filter = RelevanceFilter(
        minimum_score=0.0
    )

    filtered_results = relevance_filter.filter(results)

    print(f"Before filtering: {len(results)}")
    print(f"After filtering: {len(filtered_results)}")

    for result in filtered_results:
        print(
            result["metadata"]["concept"],
            "→",
            result["reranker_score"]
        )


if __name__ == "__main__":
    main()