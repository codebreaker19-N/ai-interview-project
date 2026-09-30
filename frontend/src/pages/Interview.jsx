import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import axios from "axios";

function Interview() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const sessionId = searchParams.get("session_id");

  const [question, setQuestion] = useState(null);
  const [answer, setAnswer] = useState("");

  const [evaluation, setEvaluation] = useState(null);

  const [loadingQuestion, setLoadingQuestion] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [error, setError] = useState("");

  const token = localStorage.getItem("token");

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }

    if (!sessionId) {
      setError("Interview session not found.");
      setLoadingQuestion(false);
      return;
    }

    loadCurrentQuestion();
  }, [sessionId]);

  const loadCurrentQuestion = async () => {
    try {
      setLoadingQuestion(true);
      setError("");
      setEvaluation(null);
      setAnswer("");

      const response = await axios.get(
        `/interview/session/${sessionId}/question`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setQuestion(response.data);
    } catch (err) {
      console.error("Failed to load question:", err);

      if (err.response?.status === 404) {
        setError(
          err.response?.data?.detail ||
            "No question available for this interview."
        );
      } else {
        setError(
          err.response?.data?.detail ||
            "Failed to load interview question."
        );
      }
    } finally {
      setLoadingQuestion(false);
    }
  };

  const handleSubmitAnswer = async (e) => {
    e.preventDefault();

    if (!answer.trim()) {
      setError("Please enter your answer before submitting.");
      return;
    }

    if (!question) {
      setError("No active question found.");
      return;
    }

    try {
      setSubmitting(true);
      setError("");

      const payload = {
        session_id: Number(sessionId),
        user_answer: answer.trim(),
      };

      if (question.id) {
        if (question.category) {
          payload.session_question_id = question.id;
        } else {
          payload.question_id = question.id;
        }
      }

      const response = await axios.post(
        "/attempts/",
        payload,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const attempt = response.data;

      if (attempt.evaluation) {
        setEvaluation(attempt.evaluation);
      } else {
        try {
          const evaluationResponse = await axios.get(
            `/evaluation/attempt/${attempt.id}`,
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );

          setEvaluation(evaluationResponse.data);
        } catch {
          setEvaluation(null);
        }
      }
    } catch (err) {
      console.error("Failed to submit answer:", err);

      setError(
        err.response?.data?.detail ||
          "Failed to evaluate your answer. Please try again."
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleNextQuestion = async () => {
    try {
      setLoadingQuestion(true);
      setError("");
      setEvaluation(null);
      setAnswer("");

      const response = await axios.get(
        `/interview/session/${sessionId}/next-question`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setQuestion(response.data);
    } catch (err) {
      console.error("Failed to load next question:", err);

      if (
        err.response?.status === 400 &&
        err.response?.data?.detail ===
          "Interview session is completed"
      ) {
        navigate(`/interview/report?session_id=${sessionId}`);
        return;
      }

      setError(
        err.response?.data?.detail ||
          "Failed to load the next question."
      );
    } finally {
      setLoadingQuestion(false);
    }
  };

  const handleFinishInterview = () => {
    navigate(`/interview/report?session_id=${sessionId}`);
  };

  if (loadingQuestion) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center px-6">
        <div className="text-center">
          <div className="text-blue-400 text-lg font-semibold mb-2">
            AI INTERVIEW COACH
          </div>

          <p className="text-slate-400">
            Preparing your interview question...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white px-6 py-10">
      <div className="max-w-4xl mx-auto">

        {/* HEADER */}

        <div className="flex items-center justify-between mb-8">
          <div>
            <p className="text-sm text-blue-400 font-medium mb-2">
              AI INTERVIEW COACH
            </p>

            <h1 className="text-3xl font-bold">
              Interview Session
            </h1>
          </div>

          <button
            type="button"
            onClick={handleFinishInterview}
            className="px-4 py-2 rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800 transition"
          >
            Finish Interview
          </button>
        </div>

        {/* ERROR */}

        {error && (
          <div className="mb-6 bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl px-4 py-3">
            {error}
          </div>
        )}

        {/* QUESTION */}

        {question && !evaluation && (
          <form
            onSubmit={handleSubmitAnswer}
            className="bg-slate-900 border border-slate-800 rounded-2xl p-7"
          >

            {/* QUESTION META */}

            <div className="flex flex-wrap gap-3 mb-6">
              {question.topic && (
                <span className="px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm">
                  {question.topic}
                </span>
              )}

              {question.difficulty && (
                <span className="px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-300 text-sm">
                  {question.difficulty}
                </span>
              )}
            </div>

            {/* QUESTION */}

            <div className="mb-8">
              <p className="text-sm text-slate-400 mb-3">
                Interview Question
              </p>

              <h2 className="text-2xl font-semibold leading-relaxed">
                {question.question}
              </h2>
            </div>

            {/* ANSWER */}

            <div className="mb-6">
              <label className="block text-sm font-medium mb-3">
                Your Answer
              </label>

              <textarea
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Type your answer here..."
                rows={10}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-4 text-white placeholder-slate-500 outline-none focus:border-blue-500 resize-none"
              />
            </div>

            {/* SUBMIT */}

            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl py-3.5 font-semibold transition"
            >
              {submitting
                ? "Evaluating Answer..."
                : "Submit Answer"}
            </button>
          </form>
        )}

        {/* EVALUATION */}

        {evaluation && (
          <div className="space-y-6">

            {/* SCORE */}

            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-7">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <p className="text-sm text-slate-400 mb-1">
                    Overall Score
                  </p>

                  <h2 className="text-5xl font-bold text-blue-400">
                    {evaluation.overall_score ??
                      evaluation.score ??
                      "—"}
                  </h2>
                </div>

                <div className="text-right">
                  <p className="text-sm text-slate-500">
                    Question
                  </p>

                  <p className="text-slate-300 font-medium">
                    {question?.question}
                  </p>
                </div>
              </div>

              {/* METRICS */}

              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">

                <ScoreCard
                  title="Technical Accuracy"
                  value={evaluation.technical_accuracy}
                />

                <ScoreCard
                  title="Semantic Similarity"
                  value={evaluation.semantic_similarity}
                />

                <ScoreCard
                  title="Keyword Coverage"
                  value={evaluation.keyword_coverage}
                />

                <ScoreCard
                  title="Concept Coverage"
                  value={evaluation.concept_coverage}
                />

                <ScoreCard
                  title="Communication"
                  value={evaluation.communication}
                />

                <ScoreCard
                  title="Confidence"
                  value={evaluation.confidence}
                />

              </div>
            </div>

            {/* STRENGTHS */}

            {evaluation.strengths?.length > 0 && (
              <FeedbackCard
                title="Strengths"
                items={evaluation.strengths}
              />
            )}

            {/* WEAKNESSES */}

            {evaluation.weaknesses?.length > 0 && (
              <FeedbackCard
                title="Areas to Improve"
                items={evaluation.weaknesses}
              />
            )}

            {/* MISSING CONCEPTS */}

            {evaluation.missing_concepts?.length > 0 && (
              <FeedbackCard
                title="Missing Concepts"
                items={evaluation.missing_concepts}
              />
            )}

            {/* SUGGESTED ANSWER */}

            {evaluation.suggested_answer && (
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-7">
                <p className="text-sm text-blue-400 font-medium mb-3">
                  Suggested Answer
                </p>

                <p className="text-slate-300 leading-relaxed whitespace-pre-line">
                  {evaluation.suggested_answer}
                </p>
              </div>
            )}

            {/* ACTIONS */}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

              <button
                type="button"
                onClick={handleNextQuestion}
                className="bg-blue-600 hover:bg-blue-500 rounded-xl py-3.5 font-semibold transition"
              >
                Next Question
              </button>

              <button
                type="button"
                onClick={handleFinishInterview}
                className="bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl py-3.5 font-semibold transition"
              >
                View Interview Report
              </button>

            </div>
          </div>
        )}

      </div>
    </div>
  );
}

function ScoreCard({ title, value }) {
  return (
    <div className="bg-slate-800 rounded-xl p-4">
      <p className="text-xs text-slate-400 mb-2">
        {title}
      </p>

      <p className="text-xl font-semibold">
        {value !== null && value !== undefined
          ? Number(value).toFixed(1)
          : "—"}
      </p>
    </div>
  );
}

function FeedbackCard({ title, items }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-7">
      <h3 className="text-lg font-semibold mb-4">
        {title}
      </h3>

      <ul className="space-y-3">
        {items.map((item, index) => (
          <li
            key={index}
            className="text-slate-300 leading-relaxed pl-4 border-l-2 border-slate-700"
          >
            {typeof item === "string"
              ? item
              : JSON.stringify(item)}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Interview;