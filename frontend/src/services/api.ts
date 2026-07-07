const API_BASE = `http://${window.location.hostname}:8080/api/v1`;

export interface UserInfo {
  username: string;
  role: string;
}

export interface JobRecord {
  id: string;
  repository_url: string;
  branch: string;
  status: string;
  created_at: string;
}

export interface LogRecord {
  agent_name: string;
  log_message: string;
  level: string;
  created_at: string;
}

export interface FindingRecord {
  id: number;
  agent_name: string;
  title: string;
  severity: string;
  description: string;
  file_path?: string;
  line_number?: number;
  suggestion?: string;
  created_at: string;
}

export interface TraceRecord {
  agent_name: string;
  duration_seconds: number;
  start_time: string;
  status: string;
}

export interface GraphNodeRelation {
  source: string;
  relation: string;
  target_type: string;
  target_id: string;
  target_title?: string;
}

export interface CoverageRecord {
  requirement_coverage: number;
  risk_coverage: number;
  api_coverage: number;
  scenario_coverage: number;
  flaky_tests_count: number;
  total_assertions_checked: number;
}

class ApiService {
  private getHeaders(): HeadersInit {
    const token = localStorage.getItem("access_token");
    return {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
  }

  async request(path: string, options: RequestInit = {}): Promise<any> {
    const url = `${API_BASE}${path}`;
    const headers = { ...this.getHeaders(), ...options.headers };
    
    let response = await fetch(url, { ...options, headers });
    
    if (response.status === 401 && localStorage.getItem("refresh_token")) {
      // Try refresh
      const refreshed = await this.refreshToken();
      if (refreshed) {
        // Retry request
        const retryHeaders = { ...this.getHeaders(), ...options.headers };
        response = await fetch(url, { ...options, headers: retryHeaders });
      }
    }

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: "Network error" }));
      throw new Error(err.detail || "Request failed");
    }

    return response.json();
  }

  async refreshToken(): Promise<boolean> {
    const refresh_token = localStorage.getItem("refresh_token");
    if (!refresh_token) return false;

    try {
      const res = await fetch(`${API_BASE}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token }),
      });

      if (!res.ok) throw new Error("Session expired");

      const data = await res.json();
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      localStorage.setItem("user_role", data.role);
      return true;
    } catch {
      this.logout();
      return false;
    }
  }

  logout() {
    const refresh_token = localStorage.getItem("refresh_token");
    if (refresh_token) {
      fetch(`${API_BASE}/auth/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token }),
      }).catch(() => {});
    }
    localStorage.clear();
    window.location.href = "/login";
  }
}

export const api = new ApiService();
export default api;
