import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const API_BASE_URL = "http://127.0.0.1:8000";

function Match() {
  const navigate = useNavigate();

  const [resume, setResume] = useState(null);
  const [jobDescriptions, setJobDescriptions] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState("");

  const [loading, setLoading] = useState(true);
  const [matching, setMatching] = useState(false);

  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  const getToken = () => {
    return (
      localStorage.getItem("token") ||
      localStorage.getItem("access_token")
    );
  };

  const getAuthHeaders = () => {
    const token = getToken();

    return {
      Authorization: `Bearer ${token}`,
    };
  };

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    const token = getToken();

    if (!token) {
      navigate("/login");
      return;
    }

    setLoading(true);
    setErrorMessage("");

    try {
      const [resumeResponse, jobResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/resume/profile`, {
          headers: getAuthHeaders(),
        }),

        fetch(`${API_BASE_URL}/job-description`, {
          headers: getAuthHeaders(),
        }),
      ]);

      if (
        resumeResponse.status === 401 ||
        jobResponse.status === 401
      ) {
        localStorage.removeItem("token");
        localStorage.removeItem("access_token");
        navigate("/login");
        return;
      }

      const resumeData = await resumeResponse.json();
      const jobData = await jobResponse.json();

      if (!resumeResponse.ok) {
        throw new Error(
          resumeData?.detail || "Unable to load resume."
        );
      }

      if (!jobResponse.ok) {
        throw new Error(
          jobData?.detail ||
            "Unable to load job descriptions."
        );
      }

      setResume(resumeData);

      if (Array.isArray(jobData)) {
        setJobDescriptions(jobData);
      } else if (Array.isArray(jobData?.job_descriptions)) {
        setJobDescriptions(jobData.job_descriptions);
      } else if (jobData?.id) {
        setJobDescriptions([jobData]);
      } else {
        setJobDescriptions([]);
      }
    } catch (error) {
      console.error("Load data error:", error);

      setErrorMessage(
        error.message || "Failed to load matching data."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleMatch = async () => {
    if (!resume?.resume_id) {
      setErrorMessage(
        "Please upload your resume first."
      );
      return;
    }

    if (!selectedJobId) {
      setErrorMessage(
        "Please select a job description."
      );
      return;
    }

    setMatching(true);
    setErrorMessage("");
    setResult(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/matching/resume-jd?resume_id=${resume.resume_id}&job_description_id=${selectedJobId}`,
        {
          method: "GET",
          headers: getAuthHeaders(),
        }
      );

      const data = await response.json();

      console.log("MATCH RESPONSE:", data);

      if (response.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("access_token");
        navigate("/login");
        return;
      }

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            "Resume-JD matching failed."
        );
      }

      setResult(data);
    } catch (error) {
      console.error("Matching error:", error);

      setErrorMessage(
        error.message ||
          "Something went wrong while matching."
      );
    } finally {
      setMatching(false);
    }
  };

  const renderSkillList = (items) => {
    if (!Array.isArray(items) || items.length === 0) {
      return (
        <p className="empty">
          No information available.
        </p>
      );
    }

    return (
      <div className="skill-list">
        {items.map((item, index) => {
          if (typeof item === "object" && item !== null) {
            return (
              <div
                className="skill-item"
                key={index}
              >
                <div className="skill-name">
                  {item.skill || "Skill"}
                </div>

                {item.matched_with && (
                  <div className="matched-with">
                    Matched with:{" "}
                    <strong>
                      {item.matched_with}
                    </strong>
                  </div>
                )}

                {item.similarity !== undefined && (
                  <div className="similarity">
                    {item.similarity}% similarity
                  </div>
                )}
              </div>
            );
          }

          return (
            <div
              className="skill-item simple"
              key={index}
            >
              {String(item)}
            </div>
          );
        })}
      </div>
    );
  };

  const match = result?.match || {};

  const score =
    match.match_score ??
    match.overall_match ??
    match.score ??
    match.match_percentage ??
    null;

  return (
    <div className="match-page">

      {/* HEADER */}

      <div className="page-header">
        <div>
          <div className="eyebrow">
            AI INTERVIEW COACH
          </div>

          <h1>Resume–Job Match</h1>

          <p>
            Understand how well your resume aligns
            with your target role.
          </p>
        </div>

        <button
          className="back-button"
          onClick={() => navigate("/dashboard")}
        >
          ← Dashboard
        </button>
      </div>

      {/* LOADING */}

      {loading && (
        <div className="state-card">
          <div className="loader"></div>

          <p>
            Loading your resume and job descriptions...
          </p>
        </div>
      )}

      {/* ERROR */}

      {!loading && errorMessage && (
        <div className="error-card">
          ⚠️ {errorMessage}
        </div>
      )}

      {/* NO RESUME */}

      {!loading && !resume?.resume_id && (
        <div className="state-card">
          <div className="state-icon">
            📄
          </div>

          <h2>
            Upload your resume first
          </h2>

          <p>
            We need your resume before calculating
            your job match.
          </p>

          <button
            className="primary-button"
            onClick={() => navigate("/resume")}
          >
            Upload Resume
          </button>
        </div>
      )}

      {/* NO JOB DESCRIPTION */}

      {!loading &&
        resume?.resume_id &&
        jobDescriptions.length === 0 && (
          <div className="state-card">
            <div className="state-icon">
              💼
            </div>

            <h2>
              Add a job description
            </h2>

            <p>
              Add a target job description before
              running the matching analysis.
            </p>

            <button
              className="primary-button"
              onClick={() =>
                navigate("/job-description")
              }
            >
              Add Job Description
            </button>
          </div>
        )}

      {/* MATCHING UI */}

      {!loading &&
        resume?.resume_id &&
        jobDescriptions.length > 0 && (
          <div className="match-container">

            {/* SELECTION CARD */}

            <div className="selection-card">

              <div className="card-heading">

                <div className="heading-icon">
                  🎯
                </div>

                <div>
                  <h2>
                    Analyze Your Job Fit
                  </h2>

                  <p>
                    Select a target job description
                    to compare it with your resume.
                  </p>
                </div>

              </div>

              {/* RESUME */}

              <div className="resume-preview">

                <div className="file-icon">
                  📄
                </div>

                <div>
                  <span>
                    Your Resume
                  </span>

                  <strong>
                    Resume #{resume.resume_id}
                  </strong>
                </div>

                <div className="verified">
                  ✓ Ready
                </div>

              </div>

              {/* JOB SELECT */}

              <label>
                Target Job Description
              </label>

              <select
                value={selectedJobId}
                onChange={(event) =>
                  setSelectedJobId(
                    event.target.value
                  )
                }
              >
                <option value="">
                  Select a job description
                </option>

                {jobDescriptions.map((job) => (
                  <option
                    key={job.id}
                    value={job.id}
                  >
                    {job.title ||
                      job.role ||
                      `Job Description #${job.id}`}
                  </option>
                ))}
              </select>

              <button
                className="primary-button full"
                onClick={handleMatch}
                disabled={matching}
              >
                {matching
                  ? "Analyzing..."
                  : "Analyze Match →"}
              </button>

            </div>

            {/* RESULTS */}

            {result && (
              <div className="results-section">

                {/* RESULT HEADER */}

                <div className="result-header">

                  <div>
                    <div className="eyebrow">
                      ANALYSIS COMPLETE
                    </div>

                    <h2>
                      Your Match Analysis
                    </h2>

                    <p>
                      Resume #{result.resume_id}
                      {" "}vs Job Description #
                      {result.job_description_id}
                    </p>
                  </div>

                  {score !== null && (
                    <div className="score-card">

                      <span>
                        Match Score
                      </span>

                      <strong>
                        {Number(score).toFixed(2)}%
                      </strong>

                    </div>
                  )}

                </div>

                {/* REQUIRED SKILLS */}

                <div className="section-title">
                  <h3>
                    Required Skills
                  </h3>

                  <p>
                    Skills explicitly required
                    by the job description.
                  </p>
                </div>

                <div className="result-grid">

                  <div className="result-card matched-card">

                    <h3>
                      ✓ Required Matched
                    </h3>

                    {renderSkillList(
                      match.required_matched
                    )}

                  </div>

                  <div className="result-card missing-card">

                    <h3>
                      ⚠ Required Missing
                    </h3>

                    {renderSkillList(
                      match.required_missing
                    )}

                  </div>

                </div>

                {/* PREFERRED SKILLS */}

                <div className="section-title preferred-title">
                  <h3>
                    Preferred Skills
                  </h3>

                  <p>
                    Additional skills that can
                    strengthen your profile.
                  </p>
                </div>

                <div className="result-grid">

                  <div className="result-card preferred-card">

                    <h3>
                      ⭐ Preferred Matched
                    </h3>

                    {renderSkillList(
                      match.preferred_matched
                    )}

                  </div>

                  <div className="result-card missing-card">

                    <h3>
                      ⚠ Preferred Missing
                    </h3>

                    {renderSkillList(
                      match.preferred_missing
                    )}

                  </div>

                </div>

                {/* SCORE BREAKDOWN */}

                <div className="section-title">
                  <h3>
                    📊 Match Breakdown
                  </h3>

                  <p>
                    Detailed skill alignment between
                    your resume and the target role.
                  </p>
                </div>

                <div className="breakdown-grid">

                  <div className="breakdown-card">

                    <span>
                      Overall Match
                    </span>

                    <strong>
                      {score !== null
                        ? `${Number(score).toFixed(2)}%`
                        : "N/A"}
                    </strong>

                  </div>

                  <div className="breakdown-card">

                    <span>
                      Required Skill Match
                    </span>

                    <strong>
                      {match.required_skill_match !==
                        undefined
                        ? `${Number(
                            match.required_skill_match
                          ).toFixed(2)}%`
                        : "N/A"}
                    </strong>

                  </div>

                  <div className="breakdown-card">

                    <span>
                      Preferred Skill Match
                    </span>

                    <strong>
                      {match.preferred_skill_match !==
                        undefined
                        ? `${Number(
                            match.preferred_skill_match
                          ).toFixed(2)}%`
                        : "N/A"}
                    </strong>

                  </div>

                </div>

              </div>
            )}

          </div>
        )}

      <style>{`

        * {
          box-sizing: border-box;
        }

        .match-page {
          min-height: 100vh;
          background: #f6f8fc;
          padding: 42px;
          color: #111827;
        }

        .page-header {
          max-width: 1120px;
          margin: 0 auto 32px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 20px;
        }

        .eyebrow {
          font-size: 12px;
          font-weight: 700;
          letter-spacing: 1.5px;
          color: #64748b;
          margin-bottom: 8px;
        }

        .page-header h1 {
          margin: 0;
          font-size: 36px;
          letter-spacing: -1px;
        }

        .page-header p {
          color: #64748b;
          margin: 8px 0 0;
        }

        .back-button {
          background: white;
          border: 1px solid #dbe1ea;
          padding: 11px 18px;
          border-radius: 10px;
          cursor: pointer;
          font-weight: 600;
        }

        .match-container {
          max-width: 1120px;
          margin: auto;
        }

        .selection-card,
        .results-section,
        .state-card {
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 20px;
          padding: 30px;
          box-shadow:
            0 10px 35px
            rgba(15, 23, 42, 0.05);
          margin-bottom: 25px;
        }

        .card-heading {
          display: flex;
          gap: 15px;
          align-items: center;
          margin-bottom: 25px;
        }

        .heading-icon {
          font-size: 35px;
        }

        .card-heading h2 {
          margin: 0;
        }

        .card-heading p {
          color: #64748b;
          margin: 5px 0 0;
        }

        .resume-preview {
          display: flex;
          align-items: center;
          gap: 15px;
          background: #f8fafc;
          border: 1px solid #e5e7eb;
          border-radius: 14px;
          padding: 17px;
          margin-bottom: 24px;
        }

        .file-icon {
          font-size: 28px;
        }

        .resume-preview span {
          display: block;
          font-size: 12px;
          color: #64748b;
        }

        .resume-preview strong {
          display: block;
          margin-top: 3px;
        }

        .verified {
          margin-left: auto;
          color: #15803d;
          font-size: 13px;
          font-weight: 700;
        }

        label {
          display: block;
          margin-bottom: 8px;
          font-weight: 700;
        }

        select {
          width: 100%;
          padding: 14px;
          border: 1px solid #dbe1ea;
          border-radius: 10px;
          background: white;
          font-size: 15px;
          outline: none;
        }

        select:focus {
          border-color: #64748b;
        }

        .primary-button {
          margin-top: 20px;
          padding: 13px 22px;
          background: #111827;
          color: white;
          border: none;
          border-radius: 10px;
          cursor: pointer;
          font-weight: 700;
        }

        .primary-button:hover {
          opacity: 0.9;
        }

        .primary-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .primary-button.full {
          width: 100%;
        }

        .result-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 20px;
          margin-bottom: 30px;
        }

        .result-header h2 {
          margin: 0;
          font-size: 28px;
        }

        .result-header p {
          color: #64748b;
        }

        .score-card {
          min-width: 180px;
          padding: 20px 25px;
          border-radius: 16px;
          background: #f8fafc;
          text-align: center;
          border: 1px solid #e5e7eb;
        }

        .score-card span {
          display: block;
          color: #64748b;
          font-size: 13px;
        }

        .score-card strong {
          display: block;
          font-size: 34px;
          margin-top: 5px;
        }

        .section-title {
          margin: 30px 0 15px;
        }

        .section-title h3 {
          margin: 0;
          font-size: 20px;
        }

        .section-title p {
          margin: 5px 0 0;
          color: #64748b;
          font-size: 14px;
        }

        .preferred-title {
          margin-top: 35px;
        }

        .result-grid {
          display: grid;
          grid-template-columns:
            repeat(2, minmax(0, 1fr));
          gap: 18px;
        }

        .result-card {
          border: 1px solid #e5e7eb;
          border-radius: 15px;
          padding: 22px;
          background: #fafbfc;
        }

        .result-card h3 {
          margin-top: 0;
          margin-bottom: 18px;
        }

        .matched-card {
          border-left: 4px solid #22c55e;
        }

        .missing-card {
          border-left: 4px solid #f59e0b;
        }

        .preferred-card {
          border-left: 4px solid #6366f1;
        }

        .skill-list {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .skill-item {
          padding: 12px 14px;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 10px;
        }

        .skill-item.simple {
          font-weight: 600;
        }

        .skill-name {
          font-weight: 700;
        }

        .matched-with {
          margin-top: 5px;
          font-size: 13px;
          color: #64748b;
        }

        .similarity {
          margin-top: 5px;
          font-size: 12px;
          color: #15803d;
          font-weight: 700;
        }

        .empty {
          color: #94a3b8;
        }

        .breakdown-grid {
          display: grid;
          grid-template-columns:
            repeat(3, minmax(0, 1fr));
          gap: 18px;
        }

        .breakdown-card {
          padding: 22px;
          border: 1px solid #e5e7eb;
          border-radius: 15px;
          background: #fafbfc;
        }

        .breakdown-card span {
          display: block;
          color: #64748b;
          font-size: 14px;
        }

        .breakdown-card strong {
          display: block;
          margin-top: 8px;
          font-size: 28px;
        }

        .state-card {
          max-width: 1120px;
          margin: auto;
          text-align: center;
          padding: 60px 30px;
        }

        .state-icon {
          font-size: 48px;
        }

        .state-card p {
          color: #64748b;
        }

        .error-card {
          max-width: 1120px;
          margin: 0 auto 20px;
          padding: 15px 18px;
          background: #fef2f2;
          color: #b91c1c;
          border: 1px solid #fecaca;
          border-radius: 12px;
        }

        .loader {
          width: 28px;
          height: 28px;
          border: 3px solid #e5e7eb;
          border-top-color: #111827;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
          margin: auto;
        }

        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }

        @media (max-width: 700px) {

          .match-page {
            padding: 20px;
          }

          .page-header {
            flex-direction: column;
            align-items: flex-start;
          }

          .result-header {
            flex-direction: column;
            align-items: flex-start;
          }

          .result-grid {
            grid-template-columns: 1fr;
          }

          .breakdown-grid {
            grid-template-columns: 1fr;
          }

          .verified {
            display: none;
          }
        }

      `}</style>

    </div>
  );
}

export default Match;