import { useState, useEffect, useRef } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { Terminal, Code, HeartHandshake, AlertTriangle, ShieldCheck, Check, Copy, Activity, RefreshCw } from "lucide-react";
import api from "../services/api";
import type { JobRecord, LogRecord, FindingRecord, TraceRecord } from "../services/api";
import LiveExecutionGraph from "../components/LiveExecutionGraph";
import TraceTimeline from "../components/TraceTimeline";

export default function RunExplorer() {
  const [searchParams] = useSearchParams();
  const queryId = searchParams.get("id");

  const [activeRunId, setActiveRunId] = useState<string | null>(queryId);
  const [job, setJob] = useState<JobRecord | null>(null);
  const [logs, setLogs] = useState<LogRecord[]>([]);
  const [findings, setFindings] = useState<FindingRecord[]>([]);
  const [traces, setTraces] = useState<TraceRecord[]>([]);
  const [generatedCode, setGeneratedCode] = useState<Record<string, string>>({});
  
  // Navigation tabs
  const [activeTab, setActiveTab] = useState<"logs" | "code" | "rca">("logs");
  const [selectedFile, setSelectedFile] = useState<string>("");
  const [copied, setCopied] = useState(false);
  const [currentAgent, setCurrentAgent] = useState<string>("RepositoryUnderstanding");
  const [noJobsAvailable, setNoJobsAvailable] = useState(false);
  
  // Patch application simulation states
  const [applyingPatch, setApplyingPatch] = useState(false);
  const [patchApplied, setPatchApplied] = useState(false);

  const socketRef = useRef<WebSocket | null>(null);
  const logsEndRef = useRef<HTMLDivElement | null>(null);

  // Sync active ID with query parameter
  useEffect(() => {
    if (queryId) {
      setActiveRunId(queryId);
    }
  }, [queryId]);

  // Load run details or resolve latest run ID
  useEffect(() => {
    const resolveAndLoad = async () => {
      let targetId = activeRunId;
      setNoJobsAvailable(false);
      
      if (!targetId) {
        try {
          const jobs: JobRecord[] = await api.request("/jobs/");
          if (jobs.length > 0) {
            targetId = jobs[0].id;
            setActiveRunId(targetId);
          } else {
            setNoJobsAvailable(true);
            return;
          }
        } catch (err) {
          console.error("Failed to load latest execution run:", err);
          setNoJobsAvailable(true);
          return;
        }
      }
      
      try {
        const jobData = await api.request(`/jobs/${targetId}`);
        setJob(jobData);
        setCurrentAgent(jobData.status === "COMPLETED" ? "FINISH" : "RepositoryUnderstanding");

        const logsData = await api.request(`/observability/jobs/${targetId}/logs`);
        setLogs(logsData);
        
        const findingsData = await api.request(`/observability/jobs/${targetId}/findings`);
        setFindings(findingsData);

        const tracesData = await api.request(`/observability/jobs/${targetId}/traces`);
        setTraces(tracesData);

        // Fetch mock/generated tests
        const generated: Record<string, string> = {
          "tests/e2e/auth.spec.ts": `import { test, expect } from '@playwright/test';\n\ntest('User login validation', async ({ page }) => {\n  await page.goto('/login');\n  await page.locator('[data-testid="username-input"]').fill('testadmin');\n  await page.locator('[data-testid="password-input"]').fill('AdminSecurePass123!');\n  await page.locator('[data-testid="login-submit"]').click();\n  await expect(page).toHaveURL('/dashboard');\n});`,
          "tests/unit/test_auth.py": `import pytest\nfrom app.infrastructure.auth_provider import auth_provider\n\ndef test_password_hashing():\n  password = "password123"\n  hashed = auth_provider.hash_password(password)\n  assert hashed != password\n  assert auth_provider.verify_password(password, hashed)`,
          "tests/performance/load_login.js": `import http from 'k6/http';\nimport { sleep } from 'k6';\n\nexport default function() {\n  http.post('http://localhost:8080/api/v1/auth/login', {\n    username: 'testadmin',\n    password: 'AdminSecurePass123!'\n  });\n  sleep(1);\n}`
        };
        setGeneratedCode(generated);
        setSelectedFile(Object.keys(generated)[0]);
        
      } catch (err) {
        console.error(err);
      }
    };
    
    resolveAndLoad();
  }, [activeRunId]);

  // Connect WebSockets for active pipeline streams
  useEffect(() => {
    if (!activeRunId || (job && job.status !== "RUNNING" && job.status !== "PENDING")) return;

    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${wsProtocol}//${window.location.hostname}:8080/api/v1/ws/jobs/${activeRunId}`;
    const ws = new WebSocket(wsUrl);
    socketRef.current = ws;

    ws.onmessage = (event) => {
      const data = event.data;
      
      // Parse event structures
      if (data.startsWith("STATUS_UPDATE:")) {
        const nextStatus = data.replace("STATUS_UPDATE:", "");
        setJob((prev) => prev ? { ...prev, status: nextStatus } : null);
        if (nextStatus === "COMPLETED") setCurrentAgent("FINISH");
      } 
      else if (data.startsWith("STEP_COMPLETED:")) {
        const parts = data.split(":");
        const nodeName = parts[1];
        const logMsg = parts.slice(2).join(":");
        
        setCurrentAgent(nodeName);
        setLogs((prev) => [
          ...prev, 
          { 
            agent_name: nodeName, 
            log_message: logMsg, 
            level: "INFO", 
            created_at: new Date().toISOString() 
          }
        ]);
      }
    };

    ws.onerror = (err) => console.error("WebSocket subscription error: ", err);
    ws.onclose = () => console.log("WebSocket disconnected.");

    return () => {
      if (socketRef.current) socketRef.current.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeRunId, job?.status]);

  // Auto-scroll log panels
  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs]);

  const handleCopyCode = () => {
    if (!selectedFile) return;
    navigator.clipboard.writeText(generatedCode[selectedFile]);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleApplyPatch = () => {
    setApplyingPatch(true);
    setTimeout(() => {
      setApplyingPatch(false);
      setPatchApplied(true);
      setLogs((prev) => [
        ...prev,
        {
          agent_name: "COGNITIVE_COPI",
          log_message: "Applied code fix directly to /workspace/app/infrastructure/auth_provider.py successfully.",
          level: "INFO",
          created_at: new Date().toISOString()
        }
      ]);
    }, 1500);
  };

  const simulatedPatch = `diff --git a/backend/app/infrastructure/auth_provider.py b/backend/app/infrastructure/auth_provider.py
index a231f4..c1102e 100644
--- a/backend/app/infrastructure/auth_provider.py
+++ b/backend/app/infrastructure/auth_provider.py
@@ -10,7 +10,7 @@ class AuthenticationProvider(IAuthenticationProvider):
     def decode_token(self, token: str, is_refresh: bool = False) -> Dict[str, Any]:
-        secret = settings.SECRET_KEY
+        secret = settings.REFRESH_SECRET_KEY if is_refresh else settings.SECRET_KEY
         try:
`;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Link to="/" className="text-xs text-indigo-400 font-semibold hover:underline cursor-pointer">
            &larr; Back to Dashboard
          </Link>
          <h1 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-zinc-100 to-indigo-300 mt-2">
            Run Pipeline Detail
          </h1>
          <p className="text-zinc-500 text-xs font-mono mt-1">UUID: {activeRunId}</p>
        </div>
        
        {job && (
          <div className="text-right">
            <span className="text-[10px] text-zinc-500 uppercase tracking-widest block font-bold mb-1">Status</span>
            <span className={`inline-flex items-center gap-1.5 font-semibold px-3 py-1 border rounded-full text-xs ${
              job.status === "COMPLETED" ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : 
              job.status === "FAILED" ? "bg-red-500/10 text-red-400 border-red-500/20" :
              "bg-indigo-500/10 text-indigo-400 border-indigo-500/20 animate-pulse"
            }`}>
              {job.status === "COMPLETED" && <ShieldCheck className="w-3.5 h-3.5" />}
              {job.status === "FAILED" && <AlertTriangle className="w-3.5 h-3.5" />}
              {job.status !== "COMPLETED" && job.status !== "FAILED" && <Activity className="w-3.5 h-3.5" />}
              {job.status}
            </span>
          </div>
        )}
      </div>

      {activeRunId ? (
        <>
          {/* LangGraph execution nodes */}
          <LiveExecutionGraph currentAgent={currentAgent} />

          {/* Core Trace & Findings Details Split */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Tabs Panel */}
            <div className="lg:col-span-2 bg-zinc-950/80 border border-zinc-900 rounded-2xl p-6 flex flex-col h-[520px] shadow-xl">
              {/* Tab Navigation header */}
              <div className="flex border-b border-zinc-900 mb-6">
                <button
                  onClick={() => setActiveTab("logs")}
                  className={`flex items-center gap-2 px-5 py-3 border-b-2 text-sm font-semibold cursor-pointer transition ${
                    activeTab === "logs" ? "border-indigo-500 text-indigo-400" : "border-transparent text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  <Terminal className="w-4 h-4" /> Agent Logs
                </button>
                <button
                  onClick={() => setActiveTab("code")}
                  className={`flex items-center gap-2 px-5 py-3 border-b-2 text-sm font-semibold cursor-pointer transition ${
                    activeTab === "code" ? "border-indigo-500 text-indigo-400" : "border-transparent text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  <Code className="w-4 h-4" /> Test Code
                </button>
                <button
                  onClick={() => setActiveTab("rca")}
                  className={`flex items-center gap-2 px-5 py-3 border-b-2 text-sm font-semibold cursor-pointer transition ${
                    activeTab === "rca" ? "border-indigo-500 text-indigo-400" : "border-transparent text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  <HeartHandshake className="w-4 h-4" /> RCA & Fixes
                </button>
              </div>

              {/* Tab Content contexts */}
              <div className="flex-1 overflow-y-auto min-h-0">
                {activeTab === "logs" && (
                  <div className="bg-zinc-950 border border-zinc-900 rounded-xl p-5 font-mono text-[11px] h-full overflow-y-auto flex flex-col justify-between shadow-inner">
                    <div className="space-y-2.5">
                      {logs.map((log, idx) => (
                        <div key={idx} className="flex gap-4 leading-relaxed">
                          <span className="text-indigo-400 font-bold shrink-0">[{log.agent_name}]</span>
                          <span className="text-zinc-300">{log.log_message}</span>
                        </div>
                      ))}
                      <div ref={logsEndRef} />
                    </div>
                  </div>
                )}

                {activeTab === "code" && (
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 h-full">
                    {/* Left: file selectors */}
                    <div className="border-r border-zinc-900 pr-2 space-y-1 overflow-y-auto">
                      {Object.keys(generatedCode).map((file) => (
                        <button
                          key={file}
                          onClick={() => setSelectedFile(file)}
                          className={`w-full text-left text-[11px] font-mono px-3 py-2 rounded-lg truncate cursor-pointer transition ${
                            selectedFile === file ? "bg-indigo-500/10 text-indigo-400 font-bold border border-indigo-500/20" : "text-zinc-400 hover:bg-zinc-900"
                          }`}
                        >
                          {file}
                        </button>
                      ))}
                    </div>

                    {/* Right: Code Viewer */}
                    <div className="md:col-span-3 bg-zinc-950 border border-zinc-900 rounded-xl p-4 font-mono text-xs relative h-full flex flex-col shadow-inner">
                      <button
                        onClick={handleCopyCode}
                        className="absolute right-4 top-4 p-2 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 rounded-lg text-zinc-400 hover:text-zinc-200 cursor-pointer transition"
                        title="Copy Code"
                      >
                        {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      </button>
                      <pre className="overflow-auto whitespace-pre flex-1 text-[11px] leading-relaxed text-zinc-300">
                        {generatedCode[selectedFile] || "No file selected."}
                      </pre>
                    </div>
                  </div>
                )}

                {activeTab === "rca" && (
                  <div className="space-y-6 h-full overflow-y-auto">
                    {findings.length === 0 ? (
                      <div className="flex flex-col items-center justify-center p-12 bg-emerald-500/5 border border-emerald-500/20 rounded-xl text-emerald-400 h-full">
                        <ShieldCheck className="w-12 h-12 mb-3 opacity-80" />
                        <span className="text-sm font-bold">No Defects Registered</span>
                        <p className="text-xs opacity-75 mt-1 text-center">All autonomous testing cycles passed without failures.</p>
                      </div>
                    ) : (
                      <div className="space-y-6">
                        {findings.map((f) => (
                          <div key={f.id} className="border border-zinc-900 rounded-xl p-5 bg-zinc-950/40 space-y-4 shadow-sm">
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex items-center gap-2">
                                <AlertTriangle className="w-5 h-5 text-red-400 shrink-0" />
                                <div>
                                  <span className="text-[10px] text-zinc-500 block font-mono">Defect identified by {f.agent_name}</span>
                                  <h4 className="font-bold text-sm text-zinc-200 mt-0.5">{f.title}</h4>
                                </div>
                              </div>
                              <span className="text-[10px] font-bold px-2 py-0.5 bg-red-500/10 text-red-400 border border-red-500/20 rounded-md">
                                {f.severity}
                              </span>
                            </div>
                            
                            <p className="text-xs text-zinc-400 leading-relaxed">{f.description}</p>
                            
                            {f.file_path && (
                              <div className="text-xs border border-zinc-900 rounded-xl p-3 bg-zinc-950 font-mono text-zinc-300">
                                <span className="text-zinc-500 block mb-1">Target Source:</span>
                                {f.file_path}:{f.line_number}
                              </div>
                            )}

                            {f.suggestion && (
                              <div className="space-y-4">
                                <div className="space-y-2">
                                  <span className="text-xs font-bold text-indigo-400 block">Suggested Repair Diff:</span>
                                  <pre className="text-[11px] bg-zinc-950 border border-zinc-900 p-3 rounded-xl font-mono overflow-x-auto text-zinc-300 leading-relaxed">
                                    {simulatedPatch}
                                  </pre>
                                </div>
                                <button
                                  type="button"
                                  onClick={handleApplyPatch}
                                  disabled={applyingPatch || patchApplied}
                                  className="w-full bg-emerald-600 hover:bg-emerald-500 disabled:bg-emerald-500/20 disabled:text-emerald-400/50 text-white font-semibold text-xs px-4 py-3 rounded-xl flex items-center justify-center gap-1.5 transition cursor-pointer"
                                >
                                  {applyingPatch ? (
                                    <>
                                      <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Applying patch to source code...
                                    </>
                                  ) : patchApplied ? (
                                    <>
                                      <Check className="w-3.5 h-3.5" /> Patch Applied Successfully!
                                    </>
                                  ) : (
                                    "Apply Fix to Source"
                                  )}
                                </button>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Sidebar Details metrics */}
            <div className="space-y-6">
              <div className="bg-zinc-950/80 border border-zinc-900 rounded-2xl p-6 shadow-xl">
                <h3 className="text-sm font-bold uppercase tracking-wider text-zinc-500 mb-4">Run Parameters</h3>
                <div className="space-y-4 text-xs text-zinc-400">
                  <div>
                    <span className="block font-medium text-zinc-500 mb-1">Repository URL / Path</span>
                    <span className="font-semibold text-zinc-200 truncate block bg-zinc-900 border border-zinc-900 p-2.5 rounded-lg font-mono">{job?.repository_url}</span>
                  </div>
                  <div>
                    <span className="block font-medium text-zinc-500 mb-1">Target Branch</span>
                    <span className="font-semibold text-zinc-200 block font-mono">{job?.branch}</span>
                  </div>
                  <div>
                    <span className="block font-medium text-zinc-500 mb-1">Scan Initiated</span>
                    <span className="font-semibold text-zinc-200 block font-mono">{job?.created_at ? new Date(job.created_at).toLocaleString() : ""}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Jaeger Trace Exporters */}
          <TraceTimeline traces={traces} />
        </>
      ) : (
        <div className="text-center p-12 text-zinc-500 bg-zinc-950/80 border border-zinc-900 rounded-2xl">
          {noJobsAvailable ? (
            <p>No repository runs registered. Please navigate to the <Link to="/" className="text-indigo-400 hover:underline font-bold">Overview Page</Link> and trigger a scan run first.</p>
          ) : (
            <p>
              <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-indigo-500" />
              Resolving active quality run details...
            </p>
          )}
        </div>
      )}
    </div>
  );
}
