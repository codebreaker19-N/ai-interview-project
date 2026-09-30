from app.rag.retrieval.retrieval_pipeline import RetrievalPipeline
from app.rag.context.context_builder import ContextBuilder


VECTOR_STORE_PATH = "data/vector_store"


def main():

    question = "What is Retrieval Augmented Generation and how does it work?"

    candidate_answer = (
        "RAG retrieves relevant information from a knowledge base "
        "and gives that information to an LLM before generating an answer."
    )

    pipeline = RetrievalPipeline(
        vector_store_path=VECTOR_STORE_PATH,
        retrieval_top_k=10,
        rerank_top_k=5,
        final_top_k=3,
        relevance_threshold=0.0,
        mmr_lambda=0.7
    )

    results = pipeline.retrieve(question)

    builder = ContextBuilder()

    context = builder.build(
        question=question,
        candidate_answer=candidate_answer,
        retrieved_results=results,
        candidate_profile={
            "role": "AI Engineer",
            "skills": ["Python", "Machine Learning", "RAG"]
        }
    )

    print("\nQUESTION:")
    print(context["question"])

    print("\nCANDIDATE ANSWER:")
    print(context["candidate_answer"])

    print("\nCANDIDATE PROFILE:")
    print(context["candidate_profile"])

    print("\nRETRIEVED EVIDENCE:")

    for evidence in context["retrieved_evidence"]:
        print("\n--- Evidence ---")
        print(f"Topic: {evidence['topic']}")
        print(f"Concept: {evidence['concept']}")
        print(f"Content: {evidence['content']}")
        print(f"Ideal Answer: {evidence['ideal_answer']}")
        print(f"Keywords: {evidence['keywords']}")


if __name__ == "__main__":
    main()