import re


def extract_concepts(ideal_answer: str):
    sentences = re.split(r"[.!?]", ideal_answer)

    concepts = []

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        words = re.findall(r"\b[a-zA-Z][a-zA-Z-]*\b", sentence.lower())

        if len(words) >= 2:
            concepts.append(sentence.lower())

    return concepts