import React, { useState } from "react";
import { Shield, Key, AlertTriangle } from "lucide-react";

export default function Login() {
  const [isRegistering, setIsRegistering] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("Viewer");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const API_BASE = `http://${window.location.hostname}:8080/api/v1`;

    try {
      if (isRegistering) {
        // Register route
        const res = await fetch(`${API_BASE}/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, email, password, role }),
        });
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "Registration failed");
        }
        // Auto-switch to login flow after successful registration
        setIsRegistering(false);
        setError("Account created. Please log in.");
      } else {
        // Login route
        const params = new URLSearchParams();
        params.append("username", username);
        params.append("password", password);

        const res = await fetch(`${API_BASE}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: params,
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "Invalid credentials");
        }

        const data = await res.json();
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        localStorage.setItem("user_role", data.role);
        localStorage.setItem("username", username);
        
        window.location.href = "/";
      }
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-md bg-surface border border-border rounded-xl p-8 shadow-2xl">
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 bg-brand-bg rounded-lg flex items-center justify-center text-brand mb-4">
            <Shield className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">QualityOS</h1>
          <p className="text-sm text-text-secondary mt-1">Autonomous Quality Engineering Operating System</p>
        </div>

        {error && (
          <div className="flex items-center gap-2 bg-failure-bg border border-failure text-failure text-sm rounded-lg p-3 mb-6">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">Username</label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm text-text-primary focus:outline-none focus:border-brand transition"
              placeholder="e.g. testadmin"
            />
          </div>

          {isRegistering && (
            <div>
              <label className="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">Email Address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm text-text-primary focus:outline-none focus:border-brand transition"
                placeholder="e.g. admin@qualityos.io"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm text-text-primary focus:outline-none focus:border-brand transition"
              placeholder="••••••••"
            />
          </div>

          {isRegistering && (
            <div>
              <label className="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">Role Emulation (RBAC)</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm text-text-primary focus:outline-none focus:border-brand transition"
              >
                <option value="Admin">Admin (Full Control)</option>
                <option value="QA Engineer">QA Engineer (Test Design/Planning)</option>
                <option value="Developer">Developer (Run/View/Repair)</option>
                <option value="Viewer">Viewer (Read-only)</option>
              </select>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-brand hover:bg-brand-hover text-white text-sm font-medium py-3 rounded-lg flex items-center justify-center gap-2 cursor-pointer transition disabled:opacity-50"
          >
            <Key className="w-4 h-4" />
            {loading ? "Processing..." : isRegistering ? "Register Account" : "Access System Gateway"}
          </button>
        </form>

        <div className="text-center mt-6">
          <button
            onClick={() => {
              setIsRegistering(!isRegistering);
              setError("");
            }}
            className="text-xs text-brand hover:underline cursor-pointer"
          >
            {isRegistering ? "Already have an account? Sign In" : "Need to seed a new role? Register here"}
          </button>
        </div>
      </div>
    </div>
  );
}
