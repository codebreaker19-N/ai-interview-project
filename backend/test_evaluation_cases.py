from app.evaluation.evaluation_prompt import build_evaluation_prompt
from app.evaluation.evaluation_schema import EvaluationResult

from app.services.llm import generate_evaluation


QUESTION = (
    "What is Retrieval Augmented Generation "
    "and how does it work?"
)


CANDIDATE_PROFILE = {
    "role": "AI Engineer",
    "skills": [
        "Python",
        "Machine Learning",
        "RAG"
    ]
}


ML_SCORES = {
    "semantic_similarity": 91,
    "keyword_coverage": 80,
    "communication": 88,
    "confidence": 84
}


RETRIEVED_EVIDENCE = [
    {
        "domain": "Technology",
        "topic": "Generative AI",
        "subtopic": "RAG",
        "concept": "Retrieval-Augmented Generation",
        "content": (
            "Retrieval-Augmented Generation combines "
            "information retrieval with language generation. "
            "Relevant external knowledge is retrieved before "
            "the language model generates an answer."
        ),
        "ideal_answer": (
            "RAG is a technique where relevant information "
            "is retrieved from an external knowledge base "
            "and provided to an LLM as context before "
            "generating the response."
        ),
        "keywords": [
            "RAG",
            "retrieval",
            "knowledge base",
            "LLM",
            "context"
        ],
        "source": "internal_knowledge_base",
        "reranker_score": 8.1036
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
    )
}


def run_case(name, candidate_answer):

    prompt = build_evaluation_prompt(
        question=QUESTION,
        candidate_answer=candidate_answer,
        candidate_profile=CANDIDATE_PROFILE,
        ml_scores=ML_SCORES,
        retrieved_evidence=RETRIEVED_EVIDENCE
    )

    print("\n" + "=" * 70)
    print(f"TEST CASE: {name}")
    print("=" * 70)

    print("\nCandidate Answer:")
    print(candidate_answer)

    evaluation = generate_evaluation(prompt)

    if isinstance(evaluation, EvaluationResult):
        data = evaluation.model_dump()
    else:
        data = evaluation

    print("\nEvaluation:")

    print(
        "Technical Accuracy:",
        data["technical_accuracy"]
    )

    print(
        "Semantic Similarity:",
        data["semantic_similarity"]
    )

    print(
        "Keyword Coverage:",
        data["keyword_coverage"]
    )

    print(
        "Communication:",
        data["communication"]
    )

    print(
        "Confidence:",
        data["confidence"]
    )

    print(
        "Strengths:",
        data["strengths"]
    )

    print(
        "Weaknesses:",
        data["weaknesses"]
    )

    print(
        "Missing Concepts:",
        data["missing_concepts"]
    )

    print(
        "Reasoning:",
        data["reasoning"]
    )

    print(
        "Suggested Answer:",
        data["suggested_answer"]
    )

    print(
        "Sources:",
        data["sources"]
    )


def main():

    for name, answer in TEST_CASES.items():

        run_case(
            name,
            answer
        )


if __name__ == "__main__":
    main()