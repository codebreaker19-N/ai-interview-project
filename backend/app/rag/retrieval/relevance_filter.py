from typing import List, Dict, Any


class RelevanceFilter:

    def __init__(
        self,
        minimum_score: float = 0.0
    ):
        self.minimum_score = minimum_score

    def filter(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        filtered_results = []

        for result in results:

            score = result.get("reranker_score")

            if score is None:
                continue

            if score >= self.minimum_score:
                filtered_results.append(result)

        return filtered_results