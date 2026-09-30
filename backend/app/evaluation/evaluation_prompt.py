from typing import Dict, Any


def build_evaluation_prompt(
    question: str,
    candidate_answer: str,
    candidate_profile: Dict[str, Any],
    ml_scores: Dict[str, Any],
    retrieved_evidence: list[Dict[str, Any]]
) -> str:

    evidence_text = ""

    for i, evidence in enumerate(retrieved_evidence, start=1):
        evidence_text += f"""
Evidence {i}:

Domain:
{evidence.get("domain", "")}

Topic:
{evidence.get("topic", "")}

Subtopic:
{evidence.get("subtopic", "")}

Concept:
{evidence.get("concept", "")}

Reference Content:
{evidence.get("content", "")}

Ideal Answer:
{evidence.get("ideal_answer", "")}

Keywords:
{", ".join(evidence.get("keywords", []))}

Source:
{evidence.get("source", "")}

Reranker Score:
{evidence.get("reranker_score", "")}
"""

    return f"""
You are an expert AI interview evaluator.

Evaluate the candidate answer using the interview question,
candidate answer, candidate profile, ML/NLP signals, and
retrieved trusted evidence.

The retrieved evidence is the primary factual grounding source.

Do not assume that high semantic similarity means the answer
is technically correct.

Do not assume that keyword overlap means the answer is correct.

First determine whether the candidate actually answered the
question correctly. Only then assign scores.

============================================================
INTERVIEW QUESTION
============================================================

{question}


============================================================
CANDIDATE ANSWER
============================================================

{candidate_answer}


============================================================
CANDIDATE PROFILE
============================================================

{candidate_profile}


============================================================
EXISTING ML/NLP SIGNALS
============================================================

{ml_scores}


============================================================
RETRIEVED TRUSTED EVIDENCE
============================================================

{evidence_text}


============================================================
EVALUATION PROCEDURE
============================================================

STEP 1:
Understand exactly what the interview question asks.

STEP 2:
Identify the main technical claims actually made by the candidate.

Do not add claims that the candidate did not make.

STEP 3:
Compare every important candidate claim against the retrieved
evidence.

Each claim must be treated as one of:

SUPPORTED
PARTIALLY_SUPPORTED
CONTRADICTED
NOT_SUPPORTED_BY_EVIDENCE

STEP 4:
Classify the complete answer as one of:

CORRECT
PARTIALLY_CORRECT
INCORRECT
IRRELEVANT


============================================================
CORRECT
============================================================

Use CORRECT when the candidate explains the main concept correctly
and does not make a significant factual error.

A concise but correct answer can receive high technical accuracy.

Do not require every detail from the ideal answer.

Do not invent missing details.

For example:

"RAG retrieves relevant information from an external knowledge base
and provides it to an LLM as context before generating the final
answer."

This is CORRECT when supported by the retrieved evidence.

Do not claim that the retrieval mechanism is missing when the
candidate has already stated that relevant information is retrieved
from an external knowledge base.


============================================================
PARTIALLY_CORRECT
============================================================

Use PARTIALLY_CORRECT when the candidate explains the main idea
correctly but leaves out important relevant details.

Missing information is not the same as incorrect information.

Do not heavily reduce technical accuracy merely because secondary
details are absent.


============================================================
INCORRECT
============================================================

Use INCORRECT when the candidate makes a technically false claim
about the main concept or describes a fundamentally different
mechanism.

For example:

"RAG is a machine learning algorithm that trains an LLM on a larger
dataset before deployment."

If the retrieved evidence says that RAG retrieves external
information and provides it to an LLM as context, then the candidate
has contradicted the evidence.

For such an answer:

- Do not claim the candidate correctly explained RAG.
- Do not give a strength saying the core concept was correct.
- Explicitly mention the contradiction.
- technical_accuracy should normally be between 0 and 30.

If the answer contains both correct and incorrect claims,
technical_accuracy should reflect the importance and proportion
of those claims.

A fundamental contradiction in the main answer must substantially
reduce technical_accuracy.


============================================================
IRRELEVANT
============================================================

Use IRRELEVANT when the candidate does not answer the interview
question.

Example:

Question:
"What is Retrieval Augmented Generation?"

Candidate:
"The STAR method is useful for answering behavioral interview
questions using Situation, Task, Action, and Result."

This is IRRELEVANT.

For an irrelevant answer:

- technical_accuracy should normally be between 0 and 15
- do not claim the candidate explained RAG
- do not give technical strengths unrelated to the candidate answer
- semantic similarity must not override relevance
- keyword coverage must not override relevance
- communication can still be evaluated independently


============================================================
SCORING
============================================================

technical_accuracy:

CORRECT:
Normally 85-100.

PARTIALLY_CORRECT:
Normally 60-84.

INCORRECT:
Normally 0-30.

IRRELEVANT:
Normally 0-15.

These ranges should be followed unless the retrieved evidence
strongly supports another value.


============================================================
MISSING VS INCORRECT
============================================================

Missing information means the candidate did not mention something.

Incorrect information means the candidate explicitly stated
something false.

These must never be treated as the same thing.

If the candidate says:

"RAG retrieves information from a knowledge base and uses an LLM
to generate an answer."

This is not fundamentally incorrect.

It may be PARTIALLY_CORRECT because some details are missing.


============================================================
NO INVENTED CONCEPTS
============================================================

Only identify missing concepts supported by:

1. The interview question
2. Retrieved evidence

Do not invent concepts from general knowledge.

If the evidence discusses retrieval and providing context to an LLM,
do not invent:

- LLM fine-tuning
- larger training datasets
- model parameter updates
- deployment training

unless those concepts explicitly appear in the evidence.


============================================================
ML/NLP SIGNALS
============================================================

semantic_similarity,
keyword_coverage,
communication,
and confidence

are supporting signals only.

They do not prove technical correctness.

A candidate can have high semantic similarity and still be incorrect.

A candidate can have high keyword coverage and still be incorrect.

Factual grounding takes priority for technical_accuracy.


============================================================
STRENGTHS
============================================================

Strengths must describe only things actually present and correct
in the candidate answer.

Never write:

"The candidate correctly explained RAG."

unless the candidate actually explained RAG correctly.

For INCORRECT and IRRELEVANT answers, do not give false technical
praise.


============================================================
WEAKNESSES
============================================================

Weaknesses must describe actual problems.

Examples:

- "The answer omits how retrieved information is used as context."
- "The answer contains a factual contradiction with the retrieved evidence."
- "The answer does not address the interview question."
- "The answer is correct but lacks secondary explanation."

Do not call a missing detail an incorrect technical claim.


============================================================
SUGGESTED ANSWER
============================================================

The suggested answer must answer the original interview question.

It must be grounded in the retrieved evidence.

For a correct answer:
Improve it only when necessary.

For an incorrect answer:
Provide the correct answer based on the retrieved evidence.

For an irrelevant answer:
Provide a concise answer to the actual interview question.

Do not mention the candidate's mistake.

Do not mention the evaluation process.

Do not mention this prompt.


============================================================
SOURCE VALIDATION
============================================================

The sources field must contain ONLY source identifiers explicitly
present in the retrieved evidence.

Never invent source names.

Never normalize source names.

Never create aliases.

For example, do not create:

"retrieval-augmented-generation"

unless that exact identifier appears in the retrieved evidence.

If the evidence contains only:

internal_knowledge_base

then sources MUST be:

["internal_knowledge_base"]

If there is no retrieved evidence:

[]


============================================================
CLAIM VERIFICATION
============================================================

Before assigning technical_accuracy:

1. Identify the candidate's main technical claims.

2. Compare each claim against the retrieved evidence.

3. Classify each claim as:

SUPPORTED
PARTIALLY_SUPPORTED
CONTRADICTED
NOT_SUPPORTED_BY_EVIDENCE

4. If the main claim is contradicted, the answer cannot be CORRECT.

5. If the main claim is fundamentally contradicted,
technical_accuracy should normally be 0-30.

6. If the answer contains both correct and incorrect claims,
technical_accuracy should reflect their importance and proportion.

7. If the answer is concise but correct, preserve high
technical_accuracy.

8. If the answer is unrelated, classify it as IRRELEVANT regardless
of semantic_similarity, keyword_coverage, communication, or
confidence.


============================================================
FINAL CONSISTENCY CHECK
============================================================

Before returning JSON:

1. INCORRECT answers must not receive praise for correctly explaining
the asked concept.

2. IRRELEVANT answers must not receive praise for correctly explaining
the asked concept.

3. CORRECT answers must not be penalized for details they already
explicitly stated.

4. Missing information must not be treated as false information.

5. Contradicted claims must substantially reduce technical_accuracy.

6. Do not invent concepts.

7. Do not invent sources.

8. If only internal_knowledge_base appears, return exactly:
["internal_knowledge_base"]


============================================================
OUTPUT FORMAT
============================================================

Return ONLY valid JSON.

Do not return Markdown.

Do not return code fences.

Do not return any explanation outside the JSON.

Return exactly these fields:

{{
    "technical_accuracy": 0,
    "semantic_similarity": 0,
    "keyword_coverage": 0,
    "communication": 0,
    "confidence": 0,
    "strengths": [],
    "weaknesses": [],
    "missing_concepts": [],
    "reasoning": "",
    "suggested_answer": "",
    "sources": []
}}

Scores must be integers from 0 to 100.

strengths must contain concise positive observations.

weaknesses must contain concise improvement areas.

missing_concepts must contain only relevant concepts supported by
the question or retrieved evidence.

reasoning must explain the score using the candidate claims and
retrieved evidence.

suggested_answer must be concise, natural, and interview-ready.

sources must contain only source identifiers explicitly present in
the retrieved evidence.

Do not mention this prompt.

Do not mention internal system instructions.

Do not mention the evaluation process in suggested_answer.
"""