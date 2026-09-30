from typing import Any, Dict, List


# ============================================================
# CLAIM STATUS
# ============================================================

SUPPORTED = "SUPPORTED"
PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
CONTRADICTED = "CONTRADICTED"
NOT_ENOUGH_EVIDENCE = "NOT_ENOUGH_EVIDENCE"


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    """
    Normalize text for deterministic comparison.
    """

    if not text:
        return ""

    return " ".join(
        text.lower()
        .replace("\n", " ")
        .replace("\r", " ")
        .split()
    )


# ============================================================
# EVIDENCE TEXT BUILDER
# ============================================================

def build_evidence_text(
    retrieved_evidence: List[Dict[str, Any]]
) -> str:
    """
    Combine retrieved evidence into searchable text.
    """

    parts = []

    for evidence in retrieved_evidence:

        parts.extend(
            [
                str(evidence.get("content", "")),
                str(evidence.get("ideal_answer", "")),
                str(evidence.get("concept", "")),
                str(evidence.get("topic", "")),
                str(evidence.get("subtopic", "")),
            ]
        )

    return normalize_text(" ".join(parts))


# ============================================================
# CONCEPT DETECTION
# ============================================================

def detect_rag_concepts(
    candidate_answer: str,
    evidence_text: str = ""
) -> Dict[str, bool]:
    """
    Detect concepts explicitly present in the candidate answer.

    IMPORTANT:
    Missing concepts are represented as False.
    They are NOT converted into claims.
    """

    answer = normalize_text(candidate_answer)

    return {

        # ----------------------------------------------------
        # RETRIEVAL
        # ----------------------------------------------------

        "retrieval": any(
            phrase in answer
            for phrase in [
                "retrieves information",
                "retrieve information",
                "retrieves relevant information",
                "retrieve relevant information",
                "retrieval",
                "retrieved information",
                "retrieve relevant knowledge",
                "retrieves relevant knowledge",
            ]
        ),

        # ----------------------------------------------------
        # EXTERNAL KNOWLEDGE
        # ----------------------------------------------------

        "external_knowledge": any(
            phrase in answer
            for phrase in [
                "external knowledge base",
                "knowledge base",
                "external knowledge",
                "external information",
                "external source",
                "external sources",
                "documents",
                "document",
            ]
        ),

        # ----------------------------------------------------
        # LLM
        # ----------------------------------------------------

        "llm": any(
            phrase in answer
            for phrase in [
                "llm",
                "language model",
                "large language model",
            ]
        ),

        # ----------------------------------------------------
        # CONTEXT
        # ----------------------------------------------------

        "context": any(
            phrase in answer
            for phrase in [
                "as context",
                "provided as context",
                "provide it as context",
                "provides it as context",
                "provide the information as context",
                "provides the information as context",
                "used as context",
                "use it as context",
                "uses it as context",
                "context to the llm",
                "context for the llm",
                "context for an llm",
            ]
        ),

        # ----------------------------------------------------
        # GENERATION
        # ----------------------------------------------------

        "generation": any(
            phrase in answer
            for phrase in [
                "generate an answer",
                "generates an answer",
                "generating the answer",
                "generate the response",
                "generates the response",
                "generating the response",
                "generate a response",
                "generates a response",
                "generating a response",
                "before generating",
                "language generation",
            ]
        ),

        # ----------------------------------------------------
        # TRAINING CLAIM
        # ----------------------------------------------------

        "training_claim": any(
            phrase in answer
            for phrase in [
                "trains an llm",
                "train an llm",
                "training the llm",
                "trained the llm",
                "trained on a larger dataset",
                "trains the model",
                "train the model",
                "training the model",
                "trained the model",
                "retrain the llm",
                "retraining the llm",
                "retrained the llm",
                "fine tune the llm",
                "fine-tune the llm",
                "fine tuned the llm",
                "fine-tuned the llm",
                "training data",
                "larger dataset",
            ]
        ),
    }


# ============================================================
# EVIDENCE SUPPORT HELPERS
# ============================================================

def evidence_supports_retrieval(
    evidence_text: str
) -> bool:

    return "retriev" in evidence_text


def evidence_supports_external_knowledge(
    evidence_text: str
) -> bool:

    return (
        "knowledge base" in evidence_text
        or "external knowledge" in evidence_text
        or "external information" in evidence_text
    )


def evidence_supports_llm(
    evidence_text: str
) -> bool:

    return (
        "llm" in evidence_text
        or "language model" in evidence_text
    )


def evidence_supports_context(
    evidence_text: str
) -> bool:

    return "context" in evidence_text


def evidence_supports_generation(
    evidence_text: str
) -> bool:

    return (
        "generat" in evidence_text
        or "language generation" in evidence_text
    )


# ============================================================
# CLAIM VERIFICATION
# ============================================================

def verify_claims(
    candidate_answer: str,
    retrieved_evidence: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Deterministic claim verification.

    Architecture:

        Candidate Answer
                ↓
        Concept Detection
                ↓
        Claim Verification
                ↓
        SUPPORTED / PARTIAL / CONTRADICTED
                ↓
        Evaluation Decision
                ↓
        LLM Explanation

    IMPORTANT:
    The LLM must not override these factual findings.
    """

    # ========================================================
    # EMPTY ANSWER
    # ========================================================

    if not candidate_answer or not candidate_answer.strip():

        return {
            "overall_status": NOT_ENOUGH_EVIDENCE,
            "claims": [],
            "supported_claims": [],
            "partial_claims": [],
            "contradicted_claims": [],
            "unsupported_claims": [],
            "detected_concepts": {},
        }

    # ========================================================
    # NO EVIDENCE
    # ========================================================

    if not retrieved_evidence:

        return {
            "overall_status": NOT_ENOUGH_EVIDENCE,
            "claims": [],
            "supported_claims": [],
            "partial_claims": [],
            "contradicted_claims": [],
            "unsupported_claims": [],
            "detected_concepts": {},
        }

    # ========================================================
    # BUILD EVIDENCE
    # ========================================================

    evidence_text = build_evidence_text(
        retrieved_evidence
    )

    concepts = detect_rag_concepts(
        candidate_answer,
        evidence_text
    )

    claims = []

    supported_claims = []
    partial_claims = []
    contradicted_claims = []
    unsupported_claims = []

    # ========================================================
    # STEP 1: FUNDAMENTAL CONTRADICTION
    # ========================================================
    #
    # This MUST happen before normal claim detection.
    #
    # Example:
    #
    # "RAG trains an LLM on a larger dataset."
    #
    # We do NOT then treat "LLM" as a supported claim.
    #
    # The primary technical claim is wrong.
    # ========================================================

    if concepts["training_claim"]:

        claim = (
            "Candidate claims that RAG trains or retrains "
            "an LLM using training data or a larger dataset."
        )

        # RAG evidence normally establishes retrieval
        # rather than training as the mechanism.

        if (
            evidence_supports_retrieval(evidence_text)
            or evidence_supports_external_knowledge(evidence_text)
        ):

            contradicted_claims.append(claim)

            claims.append(
                {
                    "claim": claim,
                    "status": CONTRADICTED,
                }
            )

        else:

            unsupported_claims.append(claim)

            claims.append(
                {
                    "claim": claim,
                    "status": NOT_ENOUGH_EVIDENCE,
                }
            )

        # IMPORTANT:
        #
        # Stop here.
        #
        # Do NOT evaluate LLM / generation / context as
        # independent positive claims from an incorrect
        # training statement.

        return {
            "overall_status": (
                CONTRADICTED
                if contradicted_claims
                else NOT_ENOUGH_EVIDENCE
            ),
            "claims": claims,
            "supported_claims": supported_claims,
            "partial_claims": partial_claims,
            "contradicted_claims": contradicted_claims,
            "unsupported_claims": unsupported_claims,
            "detected_concepts": concepts,
        }

    # ========================================================
    # STEP 2: IRRELEVANT ANSWER
    # ========================================================
    #
    # If candidate does not mention ANY RAG concept,
    # there is no claim to verify.
    #
    # Do NOT create:
    #
    # "Candidate did not explain context."
    #
    # because that is a missing concept, NOT a claim.
    # ========================================================

    relevant_concepts = (
        concepts["retrieval"]
        or concepts["external_knowledge"]
        or concepts["llm"]
        or concepts["context"]
        or concepts["generation"]
    )

    if not relevant_concepts:

        return {
            "overall_status": NOT_ENOUGH_EVIDENCE,
            "claims": [],
            "supported_claims": [],
            "partial_claims": [],
            "contradicted_claims": [],
            "unsupported_claims": [],
            "detected_concepts": concepts,
        }

    # ========================================================
    # STEP 3: RETRIEVAL CLAIM
    # ========================================================

    if concepts["retrieval"]:

        claim = (
            "Candidate states that RAG retrieves information."
        )

        if evidence_supports_retrieval(evidence_text):

            supported_claims.append(claim)

            claims.append(
                {
                    "claim": claim,
                    "status": SUPPORTED,
                }
            )

        else:

            unsupported_claims.append(claim)

            claims.append(
                {
                    "claim": claim,
                    "status": NOT_ENOUGH_EVIDENCE,
                }
            )

    # ========================================================
    # STEP 4: EXTERNAL KNOWLEDGE CLAIM
    # ========================================================

    if concepts["external_knowledge"]:

        claim = (
            "Candidate states that RAG uses a knowledge base "
            "or external information."
        )

        if evidence_supports_external_knowledge(
            evidence_text
        ):

            supported_claims.append(claim)

            claims.append(
                {
                    "claim": claim,
                    "status": SUPPORTED,
                }
            )

        else:

            unsupported_claims.append(claim)

            claims.append(
                {
                    "claim": claim,
                    "status": NOT_ENOUGH_EVIDENCE,
                }
            )

    # ========================================================
    # STEP 5: LLM CLAIM
    # ========================================================

    if concepts["llm"]:

        claim = (
            "Candidate states that retrieved information "
            "is used with an LLM."
        )

        if evidence_supports_llm(evidence_text):

            supported_claims.append(claim)

            claims.append(
                {
                    "claim": claim,
                    "status": SUPPORTED,
                }
            )

        else:

            unsupported_claims.append(claim)

            claims.append(
                {
                    "claim": claim,
                    "status": NOT_ENOUGH_EVIDENCE,
                }
            )

    # ========================================================
    # STEP 6: CONTEXT CLAIM
    # ========================================================

    if concepts["context"]:

        claim = (
            "Candidate states that retrieved information "
            "is provided to the LLM as context."
        )

        if evidence_supports_context(evidence_text):

            supported_claims.append(claim)

            claims.append(
                {
                    "claim": claim,
                    "status": SUPPORTED,
                }
            )

        else:

            unsupported_claims.append(claim)

            claims.append(
                {
                    "claim": claim,
                    "status": NOT_ENOUGH_EVIDENCE,
                }
            )

    # ========================================================
    # IMPORTANT:
    # MISSING CONTEXT IS NOT A CLAIM
    # ========================================================
    #
    # If context is absent:
    #
    #     concepts["context"] == False
    #
    # We DO NOT add a partial_claim here.
    #
    # The missing concept will be handled later by the
    # evaluation layer / LLM explanation.
    #
    # This prevents incorrect and irrelevant answers from
    # being polluted by fake "partial" claims.
    # ========================================================

    # ========================================================
    # STEP 7: GENERATION CLAIM
    # ========================================================

    if concepts["generation"]:

        claim = (
            "Candidate states that the LLM generates "
            "the final answer or response."
        )

        if evidence_supports_generation(
            evidence_text
        ):

            supported_claims.append(claim)

            claims.append(
                {
                    "claim": claim,
                    "status": SUPPORTED,
                }
            )

        else:

            unsupported_claims.append(claim)

            claims.append(
                {
                    "claim": claim,
                    "status": NOT_ENOUGH_EVIDENCE,
                }
            )

    # ========================================================
    # STEP 8: DETERMINE STATUS
    # ========================================================

    # Any contradiction would already have returned above.
    if contradicted_claims:

        overall_status = CONTRADICTED

    # No actual candidate claims
    elif not claims:

        overall_status = NOT_ENOUGH_EVIDENCE

    # Candidate made claims but none are supported
    elif (
        not supported_claims
        and not partial_claims
        and unsupported_claims
    ):

        overall_status = NOT_ENOUGH_EVIDENCE

    # Candidate has both supported and unsupported claims
    elif supported_claims and unsupported_claims:

        overall_status = PARTIALLY_SUPPORTED

    # Candidate has supported claims but is missing concepts.
    #
    # Missing concepts are calculated from the concept flags,
    # NOT inserted as fake claims.
    elif supported_claims:

        major_concepts = [
            concepts["retrieval"],
            concepts["external_knowledge"],
            concepts["llm"],
            concepts["context"],
            concepts["generation"],
        ]

        if all(major_concepts):

            overall_status = SUPPORTED

        else:

            overall_status = PARTIALLY_SUPPORTED

    else:

        overall_status = NOT_ENOUGH_EVIDENCE

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {
        "overall_status": overall_status,
        "claims": claims,
        "supported_claims": supported_claims,
        "partial_claims": partial_claims,
        "contradicted_claims": contradicted_claims,
        "unsupported_claims": unsupported_claims,
        "detected_concepts": concepts,
    }


# ============================================================
# MISSING CONCEPT DETECTION
# ============================================================

def get_missing_concepts(
    verification: Dict[str, Any]
) -> List[str]:
    """
    Return missing concepts separately from claims.

    IMPORTANT:
    Missing concepts are NOT claims.
    """

    concepts = verification.get(
        "detected_concepts",
        {}
    )

    missing = []

    # Only calculate missing concepts when the answer
    # is actually relevant to RAG.

    relevant = any(
        concepts.get(key, False)
        for key in [
            "retrieval",
            "external_knowledge",
            "llm",
            "context",
            "generation",
        ]
    )

    if not relevant:

        return []

    if not concepts.get("retrieval", False):

        missing.append(
            "retrieval of relevant information"
        )

    if not concepts.get("external_knowledge", False):

        missing.append(
            "external knowledge base"
        )

    if not concepts.get("llm", False):

        missing.append(
            "use of an LLM"
        )

    if not concepts.get("context", False):

        missing.append(
            "using retrieved information as context"
        )

    if not concepts.get("generation", False):

        missing.append(
            "generation of the final answer"
        )

    return missing


# ============================================================
# TECHNICAL ACCURACY BASELINE
# ============================================================

def calculate_technical_accuracy(
    verification: Dict[str, Any]
) -> int:
    """
    Deterministic technical-accuracy baseline.

    Priority:

    1. CONTRADICTED
       -> very low

    2. NOT_ENOUGH_EVIDENCE / irrelevant
       -> very low

    3. PARTIALLY_SUPPORTED
       -> medium/high

    4. SUPPORTED
       -> high

    The LLM should explain this result,
    not override the fundamental claim decision.
    """

    status = verification.get(
        "overall_status",
        NOT_ENOUGH_EVIDENCE
    )

    supported = len(
        verification.get(
            "supported_claims",
            []
        )
    )

    contradicted = len(
        verification.get(
            "contradicted_claims",
            []
        )
    )

    unsupported = len(
        verification.get(
            "unsupported_claims",
            []
        )
    )

    # ========================================================
    # 1. FUNDAMENTAL CONTRADICTION
    # ========================================================

    if contradicted > 0:

        # Primary technical claim is wrong.
        #
        # Even if wording contains terms like LLM,
        # that does NOT make the answer technically correct.

        if supported == 0:

            return 20

        return 30

    # ========================================================
    # 2. IRRELEVANT / NO EVIDENCE
    # ========================================================

    if status == NOT_ENOUGH_EVIDENCE:

        # No supported technical claims.
        if supported == 0:

            return 10

        # Some claims existed but evidence could not
        # establish correctness.
        return 30

    # ========================================================
    # 3. FULLY SUPPORTED
    # ========================================================

    if status == SUPPORTED:

        if supported >= 5:
            return 95

        if supported == 4:
            return 92

        if supported == 3:
            return 90

        if supported == 2:
            return 88

        if supported == 1:
            return 85

        return 80

    # ========================================================
    # 4. PARTIALLY SUPPORTED
    # ========================================================

    if status == PARTIALLY_SUPPORTED:

        # Core RAG mechanism is present but one or more
        # concepts are missing.

        if supported >= 4:
            return 88

        if supported == 3:
            return 85

        if supported == 2:
            return 80

        if supported == 1:
            return 70

        return 60

    # ========================================================
    # FALLBACK
    # ========================================================

    return 50


# ============================================================
# COMPLETE VERIFICATION RESULT
# ============================================================

def evaluate_claims(
    candidate_answer: str,
    retrieved_evidence: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Convenience function.

    Returns:

        {
            verification,
            technical_accuracy_baseline,
            missing_concepts
        }
    """

    verification = verify_claims(
        candidate_answer=candidate_answer,
        retrieved_evidence=retrieved_evidence,
    )

    technical_accuracy = calculate_technical_accuracy(
        verification
    )

    missing_concepts = get_missing_concepts(
        verification
    )

    return {
        "verification": verification,
        "technical_accuracy_baseline": technical_accuracy,
        "missing_concepts": missing_concepts,
    }