from app.evaluation.evaluation_prompt import build_evaluation_prompt


def main():

    question = (
        "What is Retrieval Augmented Generation "
        "and how does it work?"
    )

    candidate_answer = (
        "RAG retrieves relevant information from a "
        "knowledge base and gives that information "
        "to an LLM before generating an answer."
    )

    candidate_profile = {
        "role": "AI Engineer",
        "skills": [
            "Python",
            "Machine Learning",
            "RAG"
        ]
    }

    ml_scores = {
        "semantic_similarity": 91,
        "keyword_coverage": 80,
        "communication": 88,
        "confidence": 84
    }

    retrieved_evidence = [
        {
            "domain": "Technology",
            "topic": "Generative AI",
            "subtopic": "RAG",
            "concept": "Retrieval-Augmented Generation",
            "content": (
                "Retrieval-Augmented Generation combines "
                "information retrieval with language generation."
            ),
            "ideal_answer": (
                "RAG retrieves relevant information from "
                "an external knowledge base and provides "
                "it to an LLM as context."
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

    prompt = build_evaluation_prompt(
        question=question,
        candidate_answer=candidate_answer,
        candidate_profile=candidate_profile,
        ml_scores=ml_scores,
        retrieved_evidence=retrieved_evidence
    )

    print("\n================ PROMPT ================\n")
    print(prompt)


if __name__ == "__main__":
    main()