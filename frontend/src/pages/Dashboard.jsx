import { useNavigate } from "react-router-dom";

function Dashboard() {
  const navigate = useNavigate();

  const user = JSON.parse(
    localStorage.getItem("user") || "{}"
  );

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    navigate("/login");
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f5f7fb",
        padding: "40px",
      }}
    >
      <div
        style={{
          maxWidth: "1100px",
          margin: "0 auto",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <h1>AI Interview Coach</h1>

            <p>
              Welcome back,{" "}
              {user.name || "Candidate"} 👋
            </p>
          </div>

          <button onClick={handleLogout}>
            Logout
          </button>
        </div>

        <div
          style={{
            marginTop: "40px",
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit, minmax(250px, 1fr))",
            gap: "20px",
          }}
        >
          <div
            style={{
              background: "white",
              padding: "25px",
              borderRadius: "16px",
            }}
          >
            <h2>📄 Resume</h2>

            <p>
              Upload and manage your resume.
            </p>

            <button onClick={() => navigate("/resume")}>
              Manage Resume
            </button>
          </div>

          <div
            style={{
              background: "white",
              padding: "25px",
              borderRadius: "16px",
            }}
          >
            <h2>💼 Job Description</h2>

            <p>
              Add the job you're preparing for.
            </p>

            <button>
              Add Job Description
            </button>
          </div>

          <div
            style={{
              background: "white",
              padding: "25px",
              borderRadius: "16px",
            }}
          >
            <h2>🎯 Interview</h2>

            <p>
              Start a personalized mock interview.
            </p>

            <button>
              Start Interview
            </button>
          </div>

          <div
            style={{
              background: "white",
              padding: "25px",
              borderRadius: "16px",
            }}
          >
            <h2>📊 Reports</h2>

            <p>
              Review your interview performance.
            </p>

            <button>
              View Reports
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;