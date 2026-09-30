from app.rag.retrieval.deduplicator import Deduplicator


def main():

    results = [
        {
            "score": 0.90,
            "metadata": {
                "content": "RAG combines retrieval with generation."
            }
        },
        {
            "score": 0.85,
            "metadata": {
                "content": "RAG combines retrieval with generation."
            }
        },
        {
            "score": 0.70,
            "metadata": {
                "content": "The STAR method structures behavioral answers."
            }
        }
    ]

    deduplicator = Deduplicator()

    unique_results = deduplicator.deduplicate(results)

    print(f"Before: {len(results)}")
    print(f"After: {len(unique_results)}")

    for result in unique_results:
        print(result["metadata"]["content"])


if __name__ == "__main__":
    main()