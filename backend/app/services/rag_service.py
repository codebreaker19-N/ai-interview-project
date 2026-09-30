from typing import List, Dict

from app.services.tavily_service import search_technical_context


def retrieve_interview_context(
    question: str,
    missing_concepts: List[str],
    max_results: int = 5
) -> Dict:

    if not question:
        return {
            "query": "",
            "context": "",
            "sources": []
        }

    concepts = [
        concept.strip()
        for concept in missing_concepts
        if concept and concept.strip()
    ]

    if concepts:
        query = (
            f"{question}. "
            f"Focus on: {', '.join(concepts)}"
        )
    else:
        query = question

    search_result = search_technical_context(query)

    results = search_result.get("results", [])

    results = results[:max_results]

    context_parts = []
    sources = []

    for result in results:

        title = result.get("title", "")
        url = result.get("url", "")
        content = result.get("content", "")

        if content:
            context_parts.append(
                f"Source: {title}\n"
                f"Content: {content}"
            )

        if url:
            sources.append({
                "title": title,
                "url": url
            })

    context = "\n\n".join(context_parts)

    return {
        "query": query,
        "context": context,
        "sources": sources
    }