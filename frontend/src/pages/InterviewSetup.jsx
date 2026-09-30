import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import axios from "axios";

function InterviewReport() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const sessionId = searchParams.get("session_id");

  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const token = localStorage.getItem("token");

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }

    if (!sessionId) {
      setError("Interview session not found.");
      setLoading(false);
      return;
    }

    loadReport();
  }, [sessionId]);

  const loadReport = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await axios.get(
        `/interview/session/${sessionId}/report`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setReport(response.data);
    } catch (err) {
      console.error("Failed to load interview report:", err);

      setError(
        err.response?.data?.detail ||
          "Failed to load interview report."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleBackToSetup = () => {
    navigate("/interview-setup");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-blue-400 font-semibold mb-2">
            AI INTERVIEW COACH
          </p>

          <p className="text-slate-400">
            Preparing your interview report...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-950 text-white px-6 py-10">
        <div className="max-w-3xl mx-auto">
          <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl p-5">
            {error}
          </div>

          <button
            type="button"
            onClick={handleBackToSetup}
            className="mt-6 bg-blue-600 hover:bg-blue-500 px-5 py-3 rounded-xl font-semibold"
          >
            Start New Interview
          </button>
        </div>
      </div>
    );
  }

  if (!report) {
    return null;
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white px-6 py-10">
      <div className="max-w-5xl mx-auto">

        {/* HEADER */}

        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-5 mb-10">
          <div>
            <p className="text-sm text-blue-400 font-medium mb-2">
              AI INTERVIEW COACH
            </p>

            <h1 className="text-4xl font-bold mb-3">
              Interview Report
            </h1>

            <p className="text-slate-400">
              Review your performance and identify areas for improvement.
            </p>
          </div>

          <button
            type="button"
            onClick={handleBackToSetup}
            className="bg-blue-600 hover:bg-blue-500 px-5 py-3 rounded-xl font-semibold transition"
          >
            New Interview
          </button>
        </div>

        {/* SESSION SUMMARY */}

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-7 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-5">

            <SummaryCard
              title="Topic"
              value={report.topic || "—"}
            />

            <SummaryCard
              title="Difficulty"
              value={report.difficulty || "—"}
            />

            <SummaryCard
              title="Questions"
              value={`${report.questions_attempted ?? 0} / ${
                report.total_questions ?? 0
              }`}
            />

            <SummaryCard
              title="Overall Score"
              value={
                report.average_score !== null &&
                report.average_score !== undefined
                  ? `${Number(report.average_score).toFixed(1)}`
                  : "—"
              }
              highlight
            />

          </div>
        </div>

        {/* PERFORMANCE METRICS */}

        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-4">
            Performance Breakdown
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

            <MetricCard
              title="Technical Accuracy"
              value={report.average_technical_accuracy}
            />

            <MetricCard
              title="Semantic Similarity"
              value={report.average_semantic_similarity}
            />

            <MetricCard
              title="Keyword Coverage"
              value={report.average_keyword_coverage}
            />

            <MetricCard
              title="Concept Coverage"
              value={report.average_concept_coverage}
            />

            <MetricCard
              title="Communication"
              value={report.average_communication}
            />

            <MetricCard
              title="Confidence"
              value={report.average_confidence}
            />

          </div>
        </div>

        {/* STRENGTHS */}

        <FeedbackSection
          title="Your Strengths"
          items={report.strengths}
          emptyText="No strengths recorded yet."
        />

        {/* WEAKNESSES */}

        <FeedbackSection
          title="Areas to Improve"
          items={report.weaknesses}
          emptyText="No major weaknesses recorded."
        />

        {/* ACTION */}

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-7 mt-6">
          <h2 className="text-xl font-semibold mb-3">
            Keep Improving
          </h2>

          <p className="text-slate-400 leading-relaxed mb-6">
            Use this report to identify weak areas and practice
            targeted questions in your next interview session.
          </p>

          <button
            type="button"
            onClick={handleBackToSetup}
            className="bg-blue-600 hover:bg-blue-500 px-6 py-3 rounded-xl font-semibold transition"
          >
            Practice Again
          </button>
        </div>

      </div>
    </div>
  );
}

function SummaryCard({
  title,
  value,
  highlight = false,
}) {
  return (
    <div className="bg-slate-800 rounded-xl p-5">
      <p className="text-sm text-slate-400 mb-2">
        {title}
      </p>

      <p
        className={`text-xl font-semibold ${
          highlight ? "text-blue-400 text-3xl" : ""
        }`}
      >
        {value}
      </p>
    </div>
  );
}

function MetricCard({ title, value }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <p className="text-sm text-slate-400 mb-3">
        {title}
      </p>

      <div className="flex items-end justify-between">
        <p className="text-2xl font-bold">
          {value !== null && value !== undefined
            ? Number(value).toFixed(1)
            : "—"}
        </p>

        {value !== null && value !== undefined && (
          <span className="text-xs text-slate-500">
            / 100
          </span>
        )}
      </div>
    </div>
  );
}

function FeedbackSection({
  title,
  items,
  emptyText,
}) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-7 mb-6">
      <h2 className="text-xl font-semibold mb-5">
        {title}
      </h2>

      {!items || items.length === 0 ? (
        <p className="text-slate-500">
          {emptyText}
        </p>
      ) : (
        <ul className="space-y-3">
          {items.map((item, index) => (
            <li
              key={index}
              className="text-slate-300 bg-slate-800 rounded-xl px-4 py-3"
            >
              {typeof item === "string"
                ? item
                : JSON.stringify(item)}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default InterviewReport;