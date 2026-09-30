from typing import List, Dict, Any

from sentence_transformers import CrossEncoder


class SemanticReranker:

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:

        if not results:
            return []

        pairs = []

        for result in results:
            content = result["metadata"].get("content", "")
            pairs.append([query, content])

        scores = self.model.predict(pairs)

        reranked_results = []

        for result, score in zip(results, scores):
            reranked_result = result.copy()
            reranked_result["reranker_score"] = float(score)

            reranked_results.append(reranked_result)

        reranked_results.sort(
            key=lambda x: x["reranker_score"],
            reverse=True
        )

        return reranked_results[:top_k]