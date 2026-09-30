from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def semantic_skill_match(
    resume_skills: list,
    jd_skills: list,
    threshold: float = 0.72
):
    if not resume_skills or not jd_skills:
        return [], jd_skills

    resume_embeddings = model.encode(
        resume_skills
    )

    jd_embeddings = model.encode(
        jd_skills
    )

    similarities = cosine_similarity(
        jd_embeddings,
        resume_embeddings
    )

    matched = []
    missing = []

    for jd_index, jd_skill in enumerate(jd_skills):

        best_score = similarities[jd_index].max()
        best_index = similarities[jd_index].argmax()

        if best_score >= threshold:
            matched.append({
                "skill": jd_skill,
                "matched_with": resume_skills[best_index],
                "similarity": round(
                    float(best_score) * 100,
                    2
                )
            })
        else:
            missing.append(jd_skill)

    return matched, missing