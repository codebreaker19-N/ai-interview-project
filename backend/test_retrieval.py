from app.rag.embeddings.embedder import EmbeddingService
from app.rag.vector_store.faiss_store import FAISSVectorStore


VECTOR_STORE_PATH = "data/vector_store"


def main():

    embedder = EmbeddingService()

    vector_store = FAISSVectorStore(
        dimension=embedder.get_embedding_dimension()
    )

    vector_store.load(VECTOR_STORE_PATH)

    query = "What is Retrieval Augmented Generation and how does it work?"

    query_embedding = embedder.embed_text(query)

    results = vector_store.search(
        query_embedding,
        top_k=2
    )

    print("\nQUERY:")
    print(query)

    print("\nRETRIEVED RESULTS:")

    for i, result in enumerate(results, start=1):

        metadata = result["metadata"]

        print(f"\n--- Result {i} ---")
        print(f"Score: {result['score']:.4f}")
        print(f"Domain: {metadata['domain']}")
        print(f"Topic: {metadata['topic']}")
        print(f"Concept: {metadata['concept']}")
        print(f"Content: {metadata['content']}")


if __name__ == "__main__":
    main()