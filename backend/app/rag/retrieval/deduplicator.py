from typing import List, Dict, Any


class Deduplicator:

    def __init__(self):
        pass

    def deduplicate(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        seen = set()
        unique_results = []

        for result in results:
            metadata = result["metadata"]

            content = metadata.get("content", "").strip().lower()

            if not content:
                continue

            if content in seen:
                continue

            seen.add(content)
            unique_results.append(result)

        return unique_results