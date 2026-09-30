import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";

import Login from "./pages/Login";
import Resume from "./pages/Resume";
import JobDescription from "./pages/JobDescription";
import Match from "./pages/match";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        <Route
          path="/"
          element={<Navigate to="/login" replace />}
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
         path="/dashboard"
         element={<Dashboard />}
        />

        <Route
         path="/resume"
         element={<Resume />}
        />

        <Route
         path="/job-description"
         element={<JobDescription />}
        />

        <Route path="/match" element={<Match />} />


      </Routes>
    </BrowserRouter>
  );
}

export default App;