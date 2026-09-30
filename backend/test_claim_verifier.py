from app.evaluation.claim_verifier import (
    verify_claims,
    calculate_technical_accuracy,
)


EVIDENCE = [
    {
        "content": (
            "Retrieval-Augmented Generation combines "
            "information retrieval with language generation. "
            "Relevant information is retrieved from an external "
            "knowledge base and provided to an LLM as context "
            "before generating the answer."
        ),
        "ideal_answer": (
            "RAG retrieves relevant information from an external "
            "knowledge base and provides it to an LLM as context "
            "before generating the final answer."
        ),
        "concept": "Retrieval-Augmented Generation",
        "topic": "Generative AI",
    }
]


TEST_CASES = {
    "CORRECT": (
        "RAG retrieves relevant information from an external "
        "knowledge base and provides it to an LLM as context "
        "before generating the final answer."
    ),

    "PARTIALLY_CORRECT": (
        "RAG retrieves information from a knowledge base "
        "and uses an LLM to generate an answer."
    ),

    "INCORRECT": (
        "RAG is a machine learning algorithm that trains "
        "an LLM on a larger dataset before deployment."
    ),

    "IRRELEVANT": (
        "The STAR method is useful for answering behavioral "
        "interview questions by explaining situation, task, "
        "action, and result."
    ),
}


for name, answer in TEST_CASES.items():

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    result = verify_claims(
        candidate_answer=answer,
        retrieved_evidence=EVIDENCE,
    )

    print("STATUS:")
    print(result["overall_status"])

    print("\nDETECTED CONCEPTS:")
    print(result["detected_concepts"])

    print("\nCLAIMS:")
    for claim in result["claims"]:
        print(
            claim["status"],
            "->",
            claim["claim"]
        )

    print("\nTECHNICAL ACCURACY BASELINE:")
    print(
        calculate_technical_accuracy(result)
    )