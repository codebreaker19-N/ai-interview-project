import { useState } from "react";
import { useNavigate } from "react-router-dom";

const API_BASE_URL = "http://127.0.0.1:8000";

function JobDescription() {
  const navigate = useNavigate();

  const [jobDescription, setJobDescription] = useState("");
  const [profile, setProfile] = useState(null);

  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  // ============================================================
  // GET AUTH TOKEN
  // ============================================================

  const getToken = () => {
    return (
      localStorage.getItem("token") ||
      localStorage.getItem("access_token")
    );
  };

  // ============================================================
  // ANALYZE JOB DESCRIPTION
  // ============================================================

  const handleAnalyze = async () => {
    setErrorMessage("");
    setSuccessMessage("");

    if (!jobDescription.trim()) {
      setErrorMessage(
        "Please paste a job description first."
      );
      return;
    }

    const token = getToken();

    if (!token) {
      navigate("/login");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/job-description/upload`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            job_description: jobDescription.trim(),
          }),
        }
      );

      const data = await response.json().catch(() => null);

      console.log(
        "Job Description Response:",
        response.status,
        data
      );

      // --------------------------------------------------------
      // TOKEN EXPIRED / INVALID
      // --------------------------------------------------------

      if (response.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("access_token");

        navigate("/login");
        return;
      }

      // --------------------------------------------------------
      // BACKEND ERROR
      // --------------------------------------------------------

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            "Job description processing failed."
        );
      }

      // --------------------------------------------------------
      // SUCCESS
      // --------------------------------------------------------

      setProfile(data?.profile || null);

      setSuccessMessage(
        "Job description analyzed and saved successfully!"
      );
    } catch (error) {
      console.error(
        "Job Description Error:",
        error
      );

      setErrorMessage(
        error.message ||
          "Something went wrong while processing the job description."
      );
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // CLEAR JOB DESCRIPTION
  // ============================================================

  const handleClear = () => {
    setJobDescription("");
    setProfile(null);
    setErrorMessage("");
    setSuccessMessage("");
  };

  // ============================================================
  // PROFILE SECTION
  // ============================================================

  const ProfileSection = ({
    title,
    icon,
    items,
  }) => {
    return (
      <div className="profile-card">
        <h3>
          <span className="profile-icon">
            {icon}
          </span>

          {title}
        </h3>

        {!items || items.length === 0 ? (
          <p className="empty-text">
            No information extracted.
          </p>
        ) : (
          <ul>
            {items.map((item, index) => (
              <li key={index}>
                {typeof item === "object"
                  ? JSON.stringify(item)
                  : String(item)}
              </li>
            ))}
          </ul>
        )}
      </div>
    );
  };

  // ============================================================
  // UI
  // ============================================================

  return (
    <div className="jd-page">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <div className="page-header">
        <div>
          <div className="page-label">
            AI INTERVIEW COACH
          </div>

          <h1>Job Description</h1>

          <p>
            Add the job description you're
            preparing for and let AI extract
            the important requirements.
          </p>
        </div>

        <button
          className="back-button"
          onClick={() => navigate("/dashboard")}
        >
          ← Dashboard
        </button>
      </div>

      {/* ======================================================
          MAIN INPUT CARD
      ====================================================== */}

      <div className="jd-card">

        <div className="card-icon">
          💼
        </div>

        <div className="card-heading">
          <h2>
            Add Job Description
          </h2>

          <span className="step-badge">
            Step 2
          </span>
        </div>

        <p className="card-description">
          Paste the complete job description
          below. AI will identify required
          skills, preferred skills,
          responsibilities and qualifications.
        </p>

        {/* TEXTAREA */}

        <div className="textarea-wrapper">
          <textarea
            value={jobDescription}
            onChange={(event) => {
              setJobDescription(
                event.target.value
              );

              setErrorMessage("");
              setSuccessMessage("");
            }}
            placeholder={`Paste the job description here...

Example:

We are looking for a Machine Learning Intern
with experience in Python, Scikit-learn,
Machine Learning, SQL and data analysis...`}
            rows={14}
          />

          <div className="character-count">
            {jobDescription.length} characters
          </div>
        </div>

        {/* BUTTONS */}

        <div className="button-row">

          <button
            className="clear-button"
            onClick={handleClear}
            disabled={
              loading ||
              !jobDescription.trim()
            }
          >
            Clear
          </button>

          <button
            className="analyze-button"
            onClick={handleAnalyze}
            disabled={
              loading ||
              !jobDescription.trim()
            }
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Analyzing...
              </>
            ) : (
              <>
                ✨ Analyze Job Description
              </>
            )}
          </button>

        </div>

        {/* SUCCESS */}

        {successMessage && (
          <div className="success-message">
            <span>✓</span>

            <div>
              <strong>
                Analysis Complete
              </strong>

              <p>
                {successMessage}
              </p>
            </div>
          </div>
        )}

        {/* ERROR */}

        {errorMessage && (
          <div className="error-message">
            <span>⚠</span>

            <div>
              <strong>
                Something went wrong
              </strong>

              <p>
                {errorMessage}
              </p>
            </div>
          </div>
        )}

      </div>

      {/* ======================================================
          EXTRACTED PROFILE
      ====================================================== */}

      {profile && (
        <div className="results-container">

          <div className="results-header">

            <div>
              <div className="section-label">
                AI ANALYSIS
              </div>

              <h2>
                🎯 Extracted Job Profile
              </h2>

              <p>
                These requirements will be used
                later for resume matching and
                personalized interview preparation.
              </p>
            </div>

            <div className="status-badge">
              <span>✓</span>
              Analyzed
            </div>

          </div>

          <div className="profile-grid">

            <ProfileSection
              title="Required Skills"
              icon="🛠️"
              items={
                profile.required_skills
              }
            />

            <ProfileSection
              title="Preferred Skills"
              icon="⭐"
              items={
                profile.preferred_skills
              }
            />

            <ProfileSection
              title="Responsibilities"
              icon="📋"
              items={
                profile.responsibilities
              }
            />

            <ProfileSection
              title="Qualifications"
              icon="🎓"
              items={
                profile.qualifications
              }
            />

          </div>

          {/* NEXT STEP */}

          <div className="next-step-card">

            <div>
              <span className="next-icon">
                🚀
              </span>

              <div>
                <h3>
                  Ready for Resume Matching?
                </h3>

                <p>
                  Compare your resume with
                  this job description to
                  identify skill gaps and
                  matching areas.
                </p>
              </div>
            </div>

            <button
              onClick={() => navigate("/match")}
            >
              Match Resume →
            </button>

          </div>

        </div>
      )}

      {/* ======================================================
          STYLES
      ====================================================== */}

      <style>{`

        .jd-page {
          min-height: 100vh;
          background: #f6f8fc;
          padding: 42px 32px 60px;
          color: #0f172a;
        }

        /* ======================================================
           HEADER
        ====================================================== */

        .page-header {
          max-width: 1100px;
          margin: 0 auto 30px;

          display: flex;
          justify-content: space-between;
          align-items: flex-start;

          gap: 24px;
        }

        .page-label,
        .section-label {
          font-size: 12px;
          font-weight: 700;
          letter-spacing: 0.12em;
          color: #64748b;
          margin-bottom: 8px;
        }

        .page-header h1 {
          margin: 0;
          font-size: 36px;
          line-height: 1.2;
          font-weight: 750;
        }

        .page-header p {
          margin: 10px 0 0;
          color: #64748b;
          font-size: 15px;
          line-height: 1.6;
          max-width: 650px;
        }

        .back-button {
          border: 1px solid #dbe1ea;
          background: white;
          color: #0f172a;

          padding: 11px 18px;
          border-radius: 10px;

          font-size: 14px;
          font-weight: 600;

          cursor: pointer;

          transition: 0.2s;
        }

        .back-button:hover {
          background: #f8fafc;
          border-color: #94a3b8;
        }

        /* ======================================================
           MAIN CARD
        ====================================================== */

        .jd-card {
          max-width: 1100px;
          margin: 0 auto 30px;

          padding: 34px;

          background: white;

          border: 1px solid #e5e7eb;
          border-radius: 20px;

          box-shadow:
            0 10px 35px
            rgba(15, 23, 42, 0.06);
        }

        .card-icon {
          width: 52px;
          height: 52px;

          display: flex;
          align-items: center;
          justify-content: center;

          border-radius: 14px;

          background: #f1f5f9;

          font-size: 25px;

          margin-bottom: 18px;
        }

        .card-heading {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .card-heading h2 {
          margin: 0;
          font-size: 24px;
        }

        .step-badge {
          padding: 5px 10px;

          border-radius: 999px;

          background: #f1f5f9;
          color: #475569;

          font-size: 12px;
          font-weight: 700;
        }

        .card-description {
          color: #64748b;
          line-height: 1.65;

          max-width: 780px;

          margin: 10px 0 22px;
        }

        /* ======================================================
           TEXTAREA
        ====================================================== */

        .textarea-wrapper {
          width: 100%;
        }

        .jd-card textarea {
          width: 100%;

          min-height: 280px;

          padding: 18px;

          border: 1px solid #dbe1ea;
          border-radius: 13px;

          resize: vertical;

          font-family: inherit;
          font-size: 15px;
          line-height: 1.65;

          color: #0f172a;
          background: #ffffff;

          outline: none;

          transition:
            border-color 0.2s,
            box-shadow 0.2s;
        }

        .jd-card textarea::placeholder {
          color: #94a3b8;
        }

        .jd-card textarea:focus {
          border-color: #64748b;

          box-shadow:
            0 0 0 3px
            rgba(100, 116, 139, 0.10);
        }

        .character-count {
          text-align: right;

          margin-top: 7px;

          color: #94a3b8;

          font-size: 12px;
        }

        /* ======================================================
           BUTTONS
        ====================================================== */

        .button-row {
          display: flex;
          justify-content: flex-end;
          align-items: center;

          gap: 12px;

          margin-top: 20px;
        }

        .clear-button {
          padding: 12px 20px;

          border: 1px solid #dbe1ea;
          border-radius: 10px;

          background: white;
          color: #475569;

          font-weight: 600;

          cursor: pointer;
        }

        .clear-button:hover:not(:disabled) {
          background: #f8fafc;
        }

        .clear-button:disabled {
          opacity: 0.45;
          cursor: not-allowed;
        }

        .analyze-button {
          min-width: 220px;

          display: flex;
          align-items: center;
          justify-content: center;

          gap: 9px;

          padding: 13px 22px;

          border: none;
          border-radius: 10px;

          background: #0f172a;
          color: white;

          font-size: 14px;
          font-weight: 650;

          cursor: pointer;

          transition:
            transform 0.15s,
            background 0.2s;
        }

        .analyze-button:hover:not(:disabled) {
          background: #1e293b;
          transform: translateY(-1px);
        }

        .analyze-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
          transform: none;
        }

        /* ======================================================
           SPINNER
        ====================================================== */

        .spinner {
          width: 15px;
          height: 15px;

          border: 2px solid
            rgba(255, 255, 255, 0.35);

          border-top-color: white;

          border-radius: 50%;

          animation: spin 0.7s linear infinite;
        }

        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }

        /* ======================================================
           SUCCESS / ERROR
        ====================================================== */

        .success-message,
        .error-message {
          margin-top: 20px;

          display: flex;
          align-items: flex-start;

          gap: 12px;

          padding: 14px 16px;

          border-radius: 12px;

          font-size: 14px;
        }

        .success-message {
          background: #ecfdf5;
          color: #166534;

          border: 1px solid #bbf7d0;
        }

        .error-message {
          background: #fef2f2;
          color: #b91c1c;

          border: 1px solid #fecaca;
        }

        .success-message > span,
        .error-message > span {
          font-size: 18px;
        }

        .success-message strong,
        .error-message strong {
          display: block;
          margin-bottom: 3px;
        }

        .success-message p,
        .error-message p {
          margin: 0;
          line-height: 1.5;
        }

        /* ======================================================
           RESULTS
        ====================================================== */

        .results-container {
          max-width: 1100px;
          margin: 0 auto;

          padding: 32px;

          background: white;

          border: 1px solid #e5e7eb;
          border-radius: 20px;

          box-shadow:
            0 10px 35px
            rgba(15, 23, 42, 0.05);
        }

        .results-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;

          gap: 20px;

          margin-bottom: 28px;
        }

        .results-header h2 {
          margin: 0;

          font-size: 24px;
        }

        .results-header p {
          margin: 8px 0 0;

          color: #64748b;

          line-height: 1.6;
        }

        .status-badge {
          display: flex;
          align-items: center;
          gap: 6px;

          padding: 8px 13px;

          border-radius: 999px;

          background: #ecfdf5;
          color: #15803d;

          font-size: 13px;
          font-weight: 700;

          white-space: nowrap;
        }

        /* ======================================================
           PROFILE GRID
        ====================================================== */

        .profile-grid {
          display: grid;

          grid-template-columns:
            repeat(
              2,
              minmax(0, 1fr)
            );

          gap: 18px;
        }

        .profile-card {
          padding: 22px;

          border: 1px solid #e5e7eb;
          border-radius: 15px;

          background: #fafbfc;
        }

        .profile-card h3 {
          display: flex;
          align-items: center;

          gap: 9px;

          margin: 0 0 15px;

          font-size: 16px;
        }

        .profile-icon {
          font-size: 19px;
        }

        .profile-card ul {
          margin: 0;
          padding-left: 20px;

          color: #475569;

          line-height: 1.7;
        }

        .profile-card li {
          margin-bottom: 7px;
        }

        .empty-text {
          margin: 0;

          color: #94a3b8;

          font-size: 14px;
        }

        /* ======================================================
           NEXT STEP
        ====================================================== */

        .next-step-card {
          margin-top: 24px;

          padding: 20px 22px;

          display: flex;
          justify-content: space-between;
          align-items: center;

          gap: 20px;

          border: 1px solid #e2e8f0;
          border-radius: 15px;

          background: #f8fafc;
        }

        .next-step-card > div {
          display: flex;
          align-items: flex-start;

          gap: 13px;
        }

        .next-icon {
          font-size: 24px;
        }

        .next-step-card h3 {
          margin: 0 0 5px;

          font-size: 16px;
        }

        .next-step-card p {
          margin: 0;

          color: #64748b;

          font-size: 14px;

          line-height: 1.5;
        }

        .next-step-card button {
          padding: 11px 18px;

          border: none;
          border-radius: 9px;

          background: #0f172a;
          color: white;

          font-weight: 600;

          cursor: pointer;

          white-space: nowrap;
        }

        .next-step-card button:hover {
          background: #1e293b;
        }

        /* ======================================================
           RESPONSIVE
        ====================================================== */

        @media (max-width: 800px) {

          .jd-page {
            padding: 25px 18px 40px;
          }

          .page-header {
            flex-direction: column;
          }

          .back-button {
            align-self: flex-start;
          }

          .jd-card,
          .results-container {
            padding: 23px;
          }

          .profile-grid {
            grid-template-columns: 1fr;
          }

          .results-header {
            flex-direction: column;
          }

          .next-step-card {
            flex-direction: column;
            align-items: flex-start;
          }

          .next-step-card button {
            width: 100%;
          }
        }

        @media (max-width: 500px) {

          .page-header h1 {
            font-size: 29px;
          }

          .button-row {
            flex-direction: column-reverse;
            align-items: stretch;
          }

          .clear-button,
          .analyze-button {
            width: 100%;
          }

        }

      `}</style>
    </div>
  );
}

export default JobDescription;