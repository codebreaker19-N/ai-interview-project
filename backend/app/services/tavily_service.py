import os

from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()


def get_tavily_client():
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise ValueError(
            "TAVILY_API_KEY is not configured"
        )

    return TavilyClient(api_key=api_key)


def search_technical_context(
    query: str,
    max_results: int = 5
):
    client = get_tavily_client()

    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=True
    )

    results = []

    for item in response.get("results", []):

        results.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "content": item.get("content")
        })

    return {
        "answer": response.get("answer"),
        "results": results
    }