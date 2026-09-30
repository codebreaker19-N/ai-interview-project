from app.rag.ingestion.loader import KnowledgeBaseLoader
from app.rag.ingestion.chunker import KnowledgeChunker
from app.rag.embeddings.embedder import EmbeddingService
from app.rag.vector_store.faiss_store import FAISSVectorStore


KNOWLEDGE_BASE_PATH = "data/knowledge_base"
VECTOR_STORE_PATH = "data/vector_store"


def main():

    loader = KnowledgeBaseLoader(KNOWLEDGE_BASE_PATH)
    documents = loader.load_all()

    chunker = KnowledgeChunker()
    chunks = chunker.create_chunks(documents)

    embedder = EmbeddingService()
    embeddings = embedder.embed_documents(chunks)

    metadata = []

    for document in documents:
        metadata.append({
            "domain": document.domain,
            "role": document.role,
            "interview_type": document.interview_type,
            "topic": document.topic,
            "subtopic": document.subtopic,
            "concept": document.concept,
            "content": document.content,
            "ideal_answer": document.ideal_answer,
            "keywords": document.keywords,
            "difficulty": document.difficulty,
            "source_type": document.source_type,
            "source": document.source
        })

    vector_store = FAISSVectorStore(
        dimension=embedder.get_embedding_dimension()
    )

    vector_store.add(
        embeddings,
        metadata
    )

    vector_store.save(VECTOR_STORE_PATH)

    print(f"Documents indexed: {len(documents)}")
    print(f"Vector store size: {vector_store.size()}")
    print(f"Saved to: {VECTOR_STORE_PATH}")


if __name__ == "__main__":
    main()