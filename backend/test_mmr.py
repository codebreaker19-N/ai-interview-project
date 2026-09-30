from app.rag.embeddings.embedder import EmbeddingService
from app.rag.vector_store.faiss_store import FAISSVectorStore
from app.rag.retrieval.mmr import MMRRetriever


VECTOR_STORE_PATH = "data/vector_store"


def main():

    query = "What is Retrieval Augmented Generation and how does it work?"

    embedder = EmbeddingService()

    vector_store = FAISSVectorStore(
        dimension=embedder.get_embedding_dimension()
    )

    vector_store.load(VECTOR_STORE_PATH)

    query_embedding = embedder.embed_text(query)

    results = vector_store.search(
        query_embedding,
        top_k=2
    )

    mmr = MMRRetriever(
        lambda_param=0.7
    )

    selected_results = mmr.select(
        query_embedding=query_embedding,
        results=results,
        top_k=2
    )

    print("\nQUERY:")
    print(query)

    print("\nMMR RESULTS:")

    for i, result in enumerate(selected_results, start=1):

        metadata = result["metadata"]

        print(f"\n--- Result {i} ---")
        print(f"FAISS Score: {result['score']:.4f}")
        print(f"Topic: {metadata['topic']}")
        print(f"Concept: {metadata['concept']}")


if __name__ == "__main__":
    main()