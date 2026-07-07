import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { 
  Activity, 
  ShieldAlert, 
  CheckCircle2, 
  Play, 
  GitBranch, 
  ArrowRight, 
  Clock, 
  Sparkles, 
  Database, 
  Cpu, 
  Layers, 
  RefreshCw 
} from "lucide-react";
import api from "../services/api";
import type { JobRecord } from "../services/api";

export default function Dashboard() {
  const [jobs, setJobs] = useState<JobRecord[]>([]);
  const [repoUrl, setRepoUrl] = useState("https://github.com/SatAi999/DataEng-Smart-Data-Engineering-Platform.git");
  const [branch, setBranch] = useState("main");
  const [loading, setLoading] = useState(false);
  const [triggering, setTriggering] = useState(false);
  const [error, setError] = useState("");

  const fetchJobs = async () => {
    try {
      const data = await api.request("/jobs/");
      setJobs(data);
    } catch (err: any) {
      setError(err.message || "Failed to load scans history");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchJobs();
  }, []);

  const handleTrigger = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setTriggering(true);
    setError("");

    try {
      await api.request("/jobs/trigger", {
        method: "POST",
        body: JSON.stringify({ repository_url: repoUrl, branch }),
      });
      await fetchJobs();
    } catch (err: any) {
      setError(err.message || "Unauthorized or trigger failed");
    } finally {
      setTriggering(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "COMPLETED":
        return (
          <span className="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5" /> Completed
          </span>
        );
      case "FAILED":
        return (
          <span className="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20">
            <ShieldAlert className="w-3.5 h-3.5" /> Failed
          </span>
        );
      case "RUNNING":
        return (
          <span className="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 animate-pulse">
            <Activity className="w-3.5 h-3.5" /> Running
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-zinc-500/10 text-zinc-400 border border-zinc-500/20">
            <Clock className="w-3.5 h-3.5" /> Pending
          </span>
        );
    }
  };

  return (
    <div className="space-y-10 max-w-7xl mx-auto">
      {/* Header Banner Section */}
      <div className="relative overflow-hidden rounded-2xl border border-zinc-800/80 bg-gradient-to-r from-zinc-950 via-zinc-900 to-indigo-950/20 p-8 md:p-10 shadow-2xl">
        <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-500/5 blur-[100px] rounded-full pointer-events-none" />
        <div className="relative z-10 space-y-4 max-w-2xl">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Sparkles className="w-3.5 h-3.5" /> QualityOS Orchestrator Engine v1.2
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-zinc-100 via-zinc-200 to-indigo-200">
            Autonomous Quality Engineering
          </h1>
          <p className="text-zinc-400 text-sm md:text-base leading-relaxed">
            Configure unit test suites, check requirements connectivity, predict codebase vulnerabilities, and isolate and debug failures automatically.
          </p>
        </div>
      </div>

      {/* Grid: Form & Global Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Trigger form panel */}
        <div className="lg:col-span-2 bg-zinc-950/80 border border-zinc-900 rounded-2xl p-6 md:p-8 shadow-md">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold flex items-center gap-2 text-zinc-100">
              <Play className="w-4 h-4 text-indigo-500 fill-indigo-500" /> Start Scan Run
            </h2>
            <span className="text-[10px] text-zinc-500 font-mono tracking-wider">SECURE SANDBOX ACTIVE</span>
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-xl p-4 mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleTrigger} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-2">
                <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2">Repository URL / Local Path</label>
                <input
                  type="text"
                  required
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  placeholder="e.g. /workspace or https://github.com/..."
                  className="w-full bg-zinc-900/40 border border-zinc-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-zinc-100 placeholder-zinc-600 transition"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2">Branch</label>
                <input
                  type="text"
                  required
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                  placeholder="main"
                  className="w-full bg-zinc-900/40 border border-zinc-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-zinc-100 placeholder-zinc-600 transition"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={triggering}
              className="bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold px-6 py-3 rounded-xl cursor-pointer transition flex items-center gap-2 disabled:opacity-50 shadow-lg shadow-indigo-600/10"
            >
              <Activity className="w-4 h-4" />
              {triggering ? "Spawning Agent Stack..." : "Start Quality Run"}
            </button>
          </form>
        </div>

        {/* Global Quality Stats */}
        <div className="bg-zinc-950/80 border border-zinc-900 rounded-2xl p-6 md:p-8 flex flex-col justify-between shadow-md">
          <div className="space-y-6">
            <h2 className="text-lg font-bold text-zinc-100">Overall Agent Metrics</h2>
            <div className="space-y-4">
              <div className="p-3 bg-zinc-900/30 border border-zinc-900 rounded-xl flex items-center justify-between">
                <span className="text-sm text-zinc-400 flex items-center gap-2">
                  <Database className="w-4 h-4 text-emerald-400" /> Coverage Rating
                </span>
                <span className="text-sm font-bold text-emerald-400 font-mono">100% Verified</span>
              </div>
              <div className="p-3 bg-zinc-900/30 border border-zinc-900 rounded-xl flex items-center justify-between">
                <span className="text-sm text-zinc-400 flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-indigo-400" /> Sandboxed Runs
                </span>
                <span className="text-sm font-bold text-indigo-400 font-mono">Clean Sandbox</span>
              </div>
              <div className="p-3 bg-zinc-900/30 border border-zinc-900 rounded-xl flex items-center justify-between">
                <span className="text-sm text-zinc-400 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-amber-400" /> Self-Heals
                </span>
                <span className="text-sm font-bold text-amber-400 font-mono">92% Resolved</span>
              </div>
            </div>
          </div>
          <div className="border-t border-zinc-900 pt-4 mt-6">
            <Link to="/heatmap" className="text-xs text-indigo-400 font-semibold hover:underline flex items-center gap-1.5 cursor-pointer">
              Explore Codebase Risk Heatmap <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Scan History list */}
      <div className="bg-zinc-950/80 border border-zinc-900 rounded-2xl overflow-hidden shadow-md">
        <div className="px-6 py-5 border-b border-zinc-900 flex items-center justify-between">
          <h2 className="text-lg font-bold text-zinc-100 flex items-center gap-2">
            Execution Log Registry
          </h2>
          <button 
            onClick={fetchJobs} 
            className="text-xs text-indigo-400 font-semibold hover:underline flex items-center gap-1 cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Refresh Records
          </button>
        </div>

        {loading ? (
          <div className="p-12 text-center text-zinc-500">
            <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-indigo-500" />
            Loading execution records...
          </div>
        ) : jobs.length === 0 ? (
          <div className="p-12 text-center text-zinc-500">
            No repository runs registered. Insert repository URL and run a scan above.
          </div>
        ) : (
          <div className="divide-y divide-zinc-900">
            {jobs.map((job) => (
              <div key={job.id} className="px-6 py-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 hover:bg-zinc-900/25 transition">
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-zinc-200 text-sm truncate max-w-xs sm:max-w-md font-mono">
                      {job.repository_url}
                    </span>
                    <span className="flex items-center gap-1 text-[10px] bg-zinc-900 text-zinc-400 border border-zinc-800 px-1.5 py-0.5 rounded-md">
                      <GitBranch className="w-3 h-3" /> {job.branch}
                    </span>
                  </div>
                  <p className="text-xs text-zinc-500 font-mono">ID: {job.id}</p>
                </div>
                <div className="flex items-center gap-4">
                  {getStatusBadge(job.status)}
                  <Link
                    to={`/runs?id=${job.id}`}
                    className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1 cursor-pointer bg-indigo-500/5 hover:bg-indigo-500/10 border border-indigo-500/10 px-3 py-1.5 rounded-lg transition"
                  >
                    Explore Traces & Logs <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
