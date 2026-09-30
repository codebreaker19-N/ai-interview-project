from app.evaluation.evaluation_schema import EvaluationResult


def main():

    result = EvaluationResult(
        technical_accuracy=86,
        semantic_similarity=91,
        keyword_coverage=80,
        communication=88,
        confidence=84,
        strengths=[
            "Clearly explained the main concept."
        ],
        weaknesses=[
            "Could provide a more detailed explanation."
        ],
        missing_concepts=[
            "Context usage"
        ],
        reasoning=(
            "The answer is technically correct but "
            "could include more detail."
        ),
        suggested_answer=(
            "RAG retrieves relevant information from "
            "an external knowledge base and provides "
            "it to an LLM as context."
        ),
        sources=[
            "internal_knowledge_base"
        ]
    )

    print("\nVALIDATION SUCCESSFUL\n")
    print(result)


if __name__ == "__main__":
    main()