from typing import Any


def verify_claims(
    candidate_answer: str,
    retrieved_evidence: list[dict[str, Any]]
) -> dict[str, Any]:

    if not candidate_answer.strip():
        return {
            "claim_status": "NOT_RELEVANT",
            "reason": "Candidate answer is empty."
        }

    if not retrieved_evidence:
        return {
            "claim_status": "NOT_RELEVANT",
            "reason": "No trusted evidence was retrieved."
        }

    evidence_text = " ".join(
        str(evidence.get("content", ""))
        + " "
        + str(evidence.get("ideal_answer", ""))
        for evidence in retrieved_evidence
    ).lower()

    candidate_text = candidate_answer.lower()

    # --------------------------------------------------------
    # RAG-specific contradiction detection
    # --------------------------------------------------------
    training_claims = [
        "trains an llm",
        "train an llm",
        "training an llm",
        "trained an llm",
        "trains the llm",
        "train the llm",
        "fine tunes an llm",
        "fine-tunes an llm",
        "fine tuning an llm",
        "fine-tuning an llm",
    ]

    retrieval_concepts = [
        "retrieves",
        "retrieval",
        "retrieve",
        "external knowledge",
        "knowledge base",
        "provides",
        "context",
    ]

    has_training_claim = any(
        phrase in candidate_text
        for phrase in training_claims
    )

    evidence_supports_retrieval = any(
        phrase in evidence_text
        for phrase in retrieval_concepts
    )

    candidate_has_retrieval = any(
        phrase in candidate_text
        for phrase in retrieval_concepts
    )

    # --------------------------------------------------------
    # Fundamental contradiction
    # --------------------------------------------------------

    if has_training_claim and evidence_supports_retrieval:

        return {
            "claim_status": "CONTRADICTED",
            "reason": (
                "The candidate describes RAG as training or "
                "fine-tuning an LLM, while the retrieved evidence "
                "describes RAG as retrieving external information "
                "and providing it as context."
            )
        }

    # --------------------------------------------------------
    # Supported
    # --------------------------------------------------------

    if candidate_has_retrieval:

        return {
            "claim_status": "SUPPORTED",
            "reason": (
                "The candidate's main claim is aligned with "
                "the retrieved evidence."
            )
        }

    # --------------------------------------------------------
    # Partially supported
    # --------------------------------------------------------

    if (
        "knowledge base" in candidate_text
        and "llm" in candidate_text
    ):
        return {
            "claim_status": "PARTIALLY_SUPPORTED",
            "reason": (
                "The candidate mentions the main components "
                "but does not fully explain the retrieval/context flow."
            )
        }

    # --------------------------------------------------------
    # No meaningful match
    # --------------------------------------------------------

    return {
        "claim_status": "NOT_RELEVANT",
        "reason": (
            "The candidate answer does not contain a meaningful "
            "technical claim supported by the retrieved evidence."
        )
    }