from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def match_concepts(
    user_answer: str,
    concepts: list,
    threshold: float = 0.35
):
    if not concepts:
        return [], []

    texts = [user_answer] + concepts

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(texts)

    user_vector = vectors[0]
    concept_vectors = vectors[1:]

    similarities = cosine_similarity(
        user_vector,
        concept_vectors
    )[0]

    covered = []
    missing = []

    for concept, similarity in zip(
        concepts,
        similarities
    ):
        if similarity >= threshold:
            covered.append(concept)
        else:
            missing.append(concept)

    return covered, missing


def concept_coverage_score(
    covered: list,
    missing: list
):
    total_concepts = len(covered) + len(missing)

    if total_concepts == 0:
        return 0

    score = (
        len(covered) / total_concepts
    ) * 100

    return round(score, 2)