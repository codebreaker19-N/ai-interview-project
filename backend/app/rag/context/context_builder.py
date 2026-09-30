from typing import List, Dict, Any


class ContextBuilder:

    def build(
        self,
        question: str,
        candidate_answer: str,
        retrieved_results: List[Dict[str, Any]],
        candidate_profile: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:

        evidence = []

        for result in retrieved_results:

            metadata = result["metadata"]

            evidence.append({
                "domain": metadata.get("domain"),
                "topic": metadata.get("topic"),
                "subtopic": metadata.get("subtopic"),
                "concept": metadata.get("concept"),
                "content": metadata.get("content"),
                "ideal_answer": metadata.get("ideal_answer"),
                "keywords": metadata.get("keywords", []),
                "source": metadata.get("source"),
                "reranker_score": result.get("reranker_score")
            })

        return {
            "question": question,
            "candidate_answer": candidate_answer,
            "candidate_profile": candidate_profile or {},
            "retrieved_evidence": evidence
        }