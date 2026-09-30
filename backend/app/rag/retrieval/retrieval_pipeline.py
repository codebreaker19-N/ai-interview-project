from typing import List, Dict, Any

from app.rag.embeddings.embedder import EmbeddingService
from app.rag.vector_store.faiss_store import FAISSVectorStore
from app.rag.retrieval.deduplicator import Deduplicator
from app.rag.retrieval.reranker import SemanticReranker
from app.rag.retrieval.relevance_filter import RelevanceFilter
from app.rag.retrieval.mmr import MMRRetriever


class RetrievalPipeline:

    def __init__(
        self,
        vector_store_path: str,
        retrieval_top_k: int = 10,
        rerank_top_k: int = 5,
        final_top_k: int = 3,
        relevance_threshold: float = 0.0,
        mmr_lambda: float = 0.7,
    ):
        self.retrieval_top_k = retrieval_top_k
        self.rerank_top_k = rerank_top_k
        self.final_top_k = final_top_k

        # Embedding service
        self.embedder = EmbeddingService()

        embedding_dimension = (
            self.embedder.get_embedding_dimension()
        )

        # FAISS vector store
        self.vector_store = FAISSVectorStore(
            dimension=embedding_dimension
        )

        self.vector_store.load(
            vector_store_path
        )

        # Retrieval components
        self.deduplicator = Deduplicator()

        self.reranker = SemanticReranker()

        self.relevance_filter = RelevanceFilter(
            minimum_score=relevance_threshold
        )

        self.mmr = MMRRetriever(
            lambda_param=mmr_lambda
        )

    def retrieve(
        self,
        query: str
    ) -> List[Dict[str, Any]]:

        # ----------------------------------------------------
        # Validate query
        # ----------------------------------------------------

        if not query or not query.strip():
            return []

        query = query.strip()

        # ----------------------------------------------------
        # 1. Query Embedding
        # ----------------------------------------------------

        query_embedding = self.embedder.embed_text(
            query
        )

        if not query_embedding:
            return []

        # ----------------------------------------------------
        # 2. Vector Retrieval
        # ----------------------------------------------------

        results = self.vector_store.search(
            query_embedding,
            top_k=self.retrieval_top_k
        )

        if not results:
            return []

        # ----------------------------------------------------
        # 3. Deduplication
        # ----------------------------------------------------

        results = self.deduplicator.deduplicate(
            results
        )

        if not results:
            return []

        # ----------------------------------------------------
        # 4. Semantic Reranking
        # ----------------------------------------------------

        results = self.reranker.rerank(
            query=query,
            results=results,
            top_k=self.rerank_top_k
        )

        if not results:
            return []

        # ----------------------------------------------------
        # 5. Relevance Filtering
        # ----------------------------------------------------

        results = self.relevance_filter.filter(
            results
        )

        if not results:
            return []

        # ----------------------------------------------------
        # 6. MMR Diversity Selection
        # ----------------------------------------------------

        results = self.mmr.select(
            query_embedding=query_embedding,
            results=results,
            top_k=self.final_top_k
        )

        return results