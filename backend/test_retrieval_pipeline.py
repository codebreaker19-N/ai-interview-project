from app.rag.retrieval.retrieval_pipeline import RetrievalPipeline


VECTOR_STORE_PATH = "data/vector_store"


def main():

    query = "What is Retrieval Augmented Generation and how does it work?"

    pipeline = RetrievalPipeline(
        vector_store_path=VECTOR_STORE_PATH,
        retrieval_top_k=10,
        rerank_top_k=5,
        final_top_k=3,
        relevance_threshold=0.0,
        mmr_lambda=0.7
    )

    results = pipeline.retrieve(query)

    print("\nQUERY:")
    print(query)

    print("\nFINAL RETRIEVAL RESULTS:")

    for i, result in enumerate(results, start=1):

        metadata = result["metadata"]

        print(f"\n--- Result {i} ---")
        print(f"Reranker Score: {result['reranker_score']:.4f}")
        print(f"Domain: {metadata['domain']}")
        print(f"Topic: {metadata['topic']}")
        print(f"Concept: {metadata['concept']}")
        print(f"Content: {metadata['content']}")


if __name__ == "__main__":
    main()