from app.rag.embeddings.embedder import EmbeddingService
from app.rag.vector_store.faiss_store import FAISSVectorStore
from app.rag.retrieval.reranker import SemanticReranker


VECTOR_STORE_PATH = "data/vector_store"


def main():

    query = "What is Retrieval Augmented Generation and how does it work?"

    embedder = EmbeddingService()

    vector_store = FAISSVectorStore(
        dimension=embedder.get_embedding_dimension()
    )

    vector_store.load(VECTOR_STORE_PATH)

    query_embedding = embedder.embed_text(query)

    retrieved_results = vector_store.search(
        query_embedding,
        top_k=2
    )

    reranker = SemanticReranker()

    reranked_results = reranker.rerank(
        query=query,
        results=retrieved_results,
        top_k=2
    )

    print("\nQUERY:")
    print(query)

    print("\nRERANKED RESULTS:")

    for i, result in enumerate(reranked_results, start=1):

        metadata = result["metadata"]

        print(f"\n--- Result {i} ---")
        print(f"FAISS Score: {result['score']:.4f}")
        print(
            f"Reranker Score: "
            f"{result['reranker_score']:.4f}"
        )
        print(f"Domain: {metadata['domain']}")
        print(f"Topic: {metadata['topic']}")
        print(f"Concept: {metadata['concept']}")
        print(f"Content: {metadata['content']}")


if __name__ == "__main__":
    main()