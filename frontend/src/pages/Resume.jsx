import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

const API_BASE_URL = "http://127.0.0.1:8000";

function Resume() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [profile, setProfile] = useState(null);

  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  // =========================================================
  // TOKEN
  // =========================================================

  const getToken = () => {
    return (
      localStorage.getItem("token") ||
      localStorage.getItem("access_token")
    );
  };

  // =========================================================
  // LOAD EXISTING PROFILE
  // =========================================================

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    const token = getToken();

    if (!token) {
      navigate("/login");
      return;
    }

    setLoading(true);
    setErrorMessage("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/resume/profile`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("access_token");
        navigate("/login");
        return;
      }

      if (response.status === 404) {
        setProfile(null);
        return;
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail ||
            "Unable to load resume profile."
        );
      }

      const data = await response.json();

      setProfile(data);
    } catch (error) {
      console.error("Profile loading error:", error);

      setErrorMessage(
        error.message || "Unable to load resume profile."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // SELECT FILE
  // =========================================================

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    setSuccessMessage("");
    setErrorMessage("");

    if (!file) {
      setSelectedFile(null);
      return;
    }

    // Check PDF
    const isPDF =
      file.type === "application/pdf" ||
      file.name.toLowerCase().endsWith(".pdf");

    if (!isPDF) {
      setSelectedFile(null);

      setErrorMessage(
        "Please select a PDF resume only."
      );

      event.target.value = "";
      return;
    }

    setSelectedFile(file);
  };

  // =========================================================
  // UPLOAD
  // =========================================================

  const handleUpload = async () => {
    setSuccessMessage("");
    setErrorMessage("");

    if (!selectedFile) {
      setErrorMessage(
        "Please select a PDF resume first."
      );
      return;
    }

    const token = getToken();

    if (!token) {
      navigate("/login");
      return;
    }

    setUploading(true);

    try {
      // IMPORTANT:
      // FastAPI expects field name exactly "file"

      const formData = new FormData();

      formData.append("file", selectedFile);

      const response = await fetch(
        `${API_BASE_URL}/resume/upload`,
        {
          method: "POST",

          headers: {
            Authorization: `Bearer ${token}`,
          },

          // DO NOT manually set Content-Type.
          // Browser automatically sets multipart/form-data
          // with the correct boundary.

          body: formData,
        }
      );

      const data = await response.json().catch(() => null);

      console.log("Resume upload status:", response.status);
      console.log("Resume upload response:", data);

      // =====================================================
      // AUTH ERROR
      // =====================================================

      if (response.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("access_token");

        navigate("/login");
        return;
      }

      // =====================================================
      // VALIDATION ERROR
      // =====================================================

      if (response.status === 422) {
        console.error(
          "FastAPI validation error:",
          data
        );

        throw new Error(
          data?.detail
            ? JSON.stringify(data.detail)
            : "Invalid resume upload request."
        );
      }

      // =====================================================
      // OTHER ERROR
      // =====================================================

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            "Resume upload failed."
        );
      }

      // =====================================================
      // SUCCESS
      // =====================================================

      setProfile({
        resume_id: data.resume_id,
        user_id: data.user_id,
        ...data.profile,
      });

      setSuccessMessage(
        "Resume uploaded and profile generated successfully!"
      );

      setSelectedFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      console.error("Resume upload error:", error);

      setErrorMessage(
        error.message ||
          "Something went wrong while uploading the resume."
      );
    } finally {
      setUploading(false);
    }
  };

  // =========================================================
  // PROFILE SECTION
  // =========================================================

  const ProfileSection = ({
    title,
    icon,
    data,
  }) => {
    const items = Array.isArray(data)
      ? data
      : data
      ? [data]
      : [];

    return (
      <div className="profile-card">
        <h3>
          <span>{icon}</span>
          {title}
        </h3>

        {items.length === 0 ? (
          <p className="empty-text">
            No information available
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

  // =========================================================
  // UI
  // =========================================================

  return (
    <div className="resume-page">

      {/* HEADER */}

      <div className="resume-header">
        <div>
          <h1>Resume Profile</h1>

          <p>
            Upload your resume and let AI build
            your personalized interview profile.
          </p>
        </div>

        <button
          className="back-button"
          onClick={() => navigate("/dashboard")}
        >
          ← Dashboard
        </button>
      </div>

      {/* UPLOAD CARD */}

      <div className="upload-card">

        <div className="upload-icon">
          📄
        </div>

        <h2>Upload Your Resume</h2>

        <p>
          Upload your latest resume in PDF format.
          We will extract your skills, projects,
          education and experience.
        </p>

        <input
          ref={fileInputRef}
          id="resume-file"
          type="file"
          accept="application/pdf,.pdf"
          onChange={handleFileChange}
        />

        {selectedFile && (
          <div className="selected-file">
            <span>📎</span>

            <div>
              <strong>
                {selectedFile.name}
              </strong>

              <small>
                {(selectedFile.size / 1024).toFixed(1)} KB
              </small>
            </div>
          </div>
        )}

        <button
          className="upload-button"
          onClick={handleUpload}
          disabled={uploading || !selectedFile}
        >
          {uploading
            ? "Analyzing Resume..."
            : "Upload & Analyze Resume"}
        </button>

        {successMessage && (
          <div className="success-message">
            ✓ {successMessage}
          </div>
        )}

        {errorMessage && (
          <div className="error-message">
            ⚠ {errorMessage}
          </div>
        )}
      </div>

      {/* PROFILE */}

      <div className="profile-container">

        <div className="profile-heading">
          <div>
            <h2>🧠 Your Resume Intelligence</h2>

            <p>
              Information extracted from your resume
              will be used to personalize your
              interview experience.
            </p>
          </div>

          {profile && (
            <span className="profile-status">
              ✓ Profile Ready
            </span>
          )}
        </div>

        {loading ? (
          <div className="loading">
            Loading your resume profile...
          </div>
        ) : !profile ? (
          <div className="empty-profile">
            <div className="empty-icon">
              📋
            </div>

            <h3>
              No Resume Profile Yet
            </h3>

            <p>
              Upload your resume above to generate
              your personalized profile.
            </p>
          </div>
        ) : (
          <div className="profile-grid">

            <ProfileSection
              title="Skills"
              icon="💻"
              data={profile.skills}
            />

            <ProfileSection
              title="Projects"
              icon="🚀"
              data={profile.projects}
            />

            <ProfileSection
              title="Experience"
              icon="💼"
              data={profile.experience}
            />

            <ProfileSection
              title="Education"
              icon="🎓"
              data={profile.education}
            />

            <ProfileSection
              title="Achievements"
              icon="🏆"
              data={profile.achievements}
            />

            <ProfileSection
              title="Leadership"
              icon="👑"
              data={profile.leadership}
            />

            <ProfileSection
              title="Certifications"
              icon="📜"
              data={profile.certifications}
            />

          </div>
        )}
      </div>

      {/* STYLES */}

      <style>{`

        * {
          box-sizing: border-box;
        }

        .resume-page {
          min-height: 100vh;
          background: #f6f8fc;
          padding: 40px;
          color: #111827;
        }

        .resume-header {
          max-width: 1100px;
          margin: 0 auto 30px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 20px;
        }

        .resume-header h1 {
          margin: 0;
          font-size: 34px;
          font-weight: 700;
        }

        .resume-header p {
          margin-top: 8px;
          color: #64748b;
          font-size: 16px;
        }

        .back-button {
          border: 1px solid #dbe1ea;
          background: white;
          padding: 11px 18px;
          border-radius: 10px;
          cursor: pointer;
          font-size: 14px;
        }

        .back-button:hover {
          background: #f8fafc;
        }

        .upload-card {
          max-width: 1100px;
          margin: 0 auto 30px;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 20px;
          padding: 35px;
          text-align: center;
          box-shadow: 0 8px 30px rgba(15, 23, 42, 0.05);
        }

        .upload-icon {
          font-size: 45px;
          margin-bottom: 10px;
        }

        .upload-card h2 {
          margin: 5px 0 8px;
          font-size: 24px;
        }

        .upload-card > p {
          max-width: 600px;
          margin: 0 auto 25px;
          color: #64748b;
          line-height: 1.6;
        }

        .upload-card input[type="file"] {
          display: block;
          margin: 0 auto;
          max-width: 100%;
        }

        .selected-file {
          max-width: 500px;
          margin: 20px auto 0;
          display: flex;
          align-items: center;
          gap: 12px;
          text-align: left;
          padding: 14px;
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 12px;
        }

        .selected-file span {
          font-size: 25px;
        }

        .selected-file div {
          display: flex;
          flex-direction: column;
          gap: 3px;
        }

        .selected-file small {
          color: #64748b;
        }

        .upload-button {
          margin-top: 22px;
          border: none;
          border-radius: 11px;
          padding: 13px 25px;
          background: #111827;
          color: white;
          font-size: 15px;
          font-weight: 600;
          cursor: pointer;
        }

        .upload-button:hover:not(:disabled) {
          background: #1f2937;
        }

        .upload-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .success-message {
          margin: 18px auto 0;
          max-width: 650px;
          padding: 12px;
          border-radius: 10px;
          background: #ecfdf5;
          color: #15803d;
          border: 1px solid #bbf7d0;
        }

        .error-message {
          margin: 18px auto 0;
          max-width: 650px;
          padding: 12px;
          border-radius: 10px;
          background: #fef2f2;
          color: #dc2626;
          border: 1px solid #fecaca;
          word-break: break-word;
        }

        .profile-container {
          max-width: 1100px;
          margin: 0 auto;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 20px;
          padding: 30px;
          box-shadow: 0 8px 30px rgba(15, 23, 42, 0.05);
        }

        .profile-heading {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 20px;
          margin-bottom: 25px;
        }

        .profile-heading h2 {
          margin: 0;
          font-size: 24px;
        }

        .profile-heading p {
          color: #64748b;
          margin: 7px 0 0;
        }

        .profile-status {
          white-space: nowrap;
          padding: 8px 13px;
          border-radius: 999px;
          background: #ecfdf5;
          color: #15803d;
          font-size: 13px;
          font-weight: 600;
        }

        .profile-grid {
          display: grid;
          grid-template-columns: repeat(
            auto-fit,
            minmax(300px, 1fr)
          );
          gap: 18px;
        }

        .profile-card {
          border: 1px solid #e5e7eb;
          border-radius: 15px;
          padding: 20px;
          background: #fafbfc;
        }

        .profile-card h3 {
          margin: 0 0 14px;
          display: flex;
          gap: 8px;
          align-items: center;
          font-size: 17px;
        }

        .profile-card ul {
          margin: 0;
          padding-left: 20px;
          color: #475569;
          line-height: 1.7;
        }

        .profile-card li {
          margin-bottom: 5px;
          word-break: break-word;
        }

        .empty-text {
          color: #94a3b8;
          margin: 0;
        }

        .loading {
          text-align: center;
          padding: 50px;
          color: #64748b;
        }

        .empty-profile {
          text-align: center;
          padding: 50px 20px;
          background: #f8fafc;
          border-radius: 15px;
        }

        .empty-icon {
          font-size: 45px;
          margin-bottom: 10px;
        }

        .empty-profile h3 {
          margin: 0 0 8px;
        }

        .empty-profile p {
          color: #64748b;
          margin: 0;
        }

        @media (max-width: 700px) {

          .resume-page {
            padding: 20px;
          }

          .resume-header {
            align-items: flex-start;
            flex-direction: column;
          }

          .resume-header h1 {
            font-size: 28px;
          }

          .profile-heading {
            align-items: flex-start;
            flex-direction: column;
          }

          .upload-card,
          .profile-container {
            padding: 22px;
          }

        }

      `}</style>
    </div>
  );
}

export default Resume;