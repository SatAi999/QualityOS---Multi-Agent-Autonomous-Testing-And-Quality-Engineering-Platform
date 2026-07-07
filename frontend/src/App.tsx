import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import DashboardLayout from "./components/DashboardLayout";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import RunExplorer from "./pages/RunExplorer";
import RiskHeatmap from "./pages/RiskHeatmap";
import KnowledgeGraph from "./pages/KnowledgeGraph";

// Route protection wrapper checking access token existence
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem("access_token");
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <DashboardLayout>{children}</DashboardLayout>;
}

export default function App() {
  return (
    <Router>
      <Routes>
        {/* Auth routes */}
        <Route path="/login" element={<Login />} />
        
        {/* Protected Dashboard Contexts */}
        <Route 
          path="/" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/runs" 
          element={
            <ProtectedRoute>
              <RunExplorer />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/heatmap" 
          element={
            <ProtectedRoute>
              <RiskHeatmap />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/knowledge" 
          element={
            <ProtectedRoute>
              <KnowledgeGraph />
            </ProtectedRoute>
          } 
        />

        {/* Fallback route */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}
