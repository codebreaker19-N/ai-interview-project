from typing import List, Dict, Any

import numpy as np


class MMRRetriever:

    def __init__(
        self,
        lambda_param: float = 0.7
    ):
        self.lambda_param = lambda_param

    def _cosine_similarity(
        self,
        vector_a: np.ndarray,
        vector_b: np.ndarray
    ) -> float:

        denominator = (
            np.linalg.norm(vector_a) *
            np.linalg.norm(vector_b)
        )

        if denominator == 0:
            return 0.0

        return float(
            np.dot(vector_a, vector_b) / denominator
        )

    def select(
        self,
        query_embedding: List[float],
        results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:

        if not results:
            return []

        query_vector = np.asarray(
            query_embedding,
            dtype="float32"
        )

        selected = []
        remaining = list(results)

        while remaining and len(selected) < top_k:

            best_result = None
            best_score = float("-inf")

            for result in remaining:

                embedding = result.get("embedding")

                if embedding is None:
                    continue

                document_vector = np.asarray(
                    embedding,
                    dtype="float32"
                )

                relevance = self._cosine_similarity(
                    query_vector,
                    document_vector
                )

                if selected:

                    diversity_penalty = max(
                        self._cosine_similarity(
                            document_vector,
                            np.asarray(
                                selected_result["embedding"],
                                dtype="float32"
                            )
                        )
                        for selected_result in selected
                    )

                else:
                    diversity_penalty = 0.0

                mmr_score = (
                    self.lambda_param * relevance
                    -
                    (1 - self.lambda_param) * diversity_penalty
                )

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_result = result

            if best_result is None:
                break

            selected.append(best_result)
            remaining.remove(best_result)

        return selected