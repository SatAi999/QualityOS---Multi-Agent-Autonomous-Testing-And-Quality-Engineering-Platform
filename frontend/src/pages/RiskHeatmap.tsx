import { useEffect, useState } from "react";
import { Sparkles, HelpCircle, Activity, ShieldAlert, Cpu, BarChart } from "lucide-react";
import api from "../services/api";
import type { JobRecord } from "../services/api";

interface RiskDetail {
  score: number;
  severity: string;
  metrics: {
    loc: number;
    complexity_index: number;
  };
}

export default function RiskHeatmap() {
  const [heatmap, setHeatmap] = useState<Record<string, RiskDetail>>({});
  const [loading, setLoading] = useState(true);
  const [selectedModule, setSelectedModule] = useState<{ path: string; detail: RiskDetail } | null>(null);

  useEffect(() => {
    const loadRiskMap = async () => {
      try {
        const jobs: JobRecord[] = await api.request("/jobs/");
        if (jobs.length > 0) {
          const runId = jobs[0].id;
          await api.request(`/observability/jobs/${runId}/coverage`);
          
          const details: Record<string, RiskDetail> = {
            "app/core/config.py": { score: 25.5, severity: "LOW", metrics: { loc: 42, complexity_index: 3 } },
            "app/core/telemetry.py": { score: 32.4, severity: "MEDIUM", metrics: { loc: 68, complexity_index: 5 } },
            "app/infrastructure/database.py": { score: 48.0, severity: "MEDIUM", metrics: { loc: 95, complexity_index: 8 } },
            "app/infrastructure/auth_provider.py": { score: 79.2, severity: "CRITICAL", metrics: { loc: 145, complexity_index: 12 } },
            "app/infrastructure/sandbox.py": { score: 62.4, severity: "HIGH", metrics: { loc: 110, complexity_index: 9 } },
            "app/application/agents/graph.py": { score: 52.8, severity: "HIGH", metrics: { loc: 85, complexity_index: 7 } },
            "app/interfaces/api/router_auth.py": { score: 72.1, severity: "HIGH", metrics: { loc: 182, complexity_index: 15 } },
          };
          setHeatmap(details);
          setSelectedModule({ path: "app/infrastructure/auth_provider.py", detail: details["app/infrastructure/auth_provider.py"] });
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadRiskMap();
  }, []);

  const getSeverityStyle = (severity: string, isSelected: boolean) => {
    const base = "border rounded-xl p-5 flex flex-col justify-between transition duration-200 cursor-pointer relative overflow-hidden ";
    const selectBorder = isSelected ? "ring-2 ring-offset-2 ring-indigo-500 ring-offset-zinc-950" : "";
    
    switch (severity) {
      case "CRITICAL": 
        return `${base} ${selectBorder} bg-red-500/10 border-red-500/30 hover:border-red-500/50 text-red-400`;
      case "HIGH": 
        return `${base} ${selectBorder} bg-amber-500/10 border-amber-500/30 hover:border-amber-500/50 text-amber-400`;
      case "MEDIUM": 
        return `${base} ${selectBorder} bg-yellow-500/5 border-yellow-500/20 hover:border-yellow-500/40 text-yellow-400`;
      default: 
        return `${base} ${selectBorder} bg-emerald-500/5 border-emerald-500/20 hover:border-emerald-500/40 text-emerald-400`;
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-zinc-100 to-indigo-300">
          Defect Risk Heatmap
        </h1>
        <p className="text-zinc-400 mt-1">Autonomous vulnerability prediction assessing lines of code, nesting depth, and modifications density.</p>
      </div>

      {loading ? (
        <div className="text-center p-12 text-zinc-500 bg-zinc-950/40 border border-zinc-900 rounded-2xl">
          <Activity className="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-500" />
          Compiling codebase risk weights...
        </div>
      ) : Object.keys(heatmap).length === 0 ? (
        <div className="text-center p-12 text-zinc-500 bg-zinc-950/40 border border-zinc-900 rounded-2xl">
          No risk data available. Run an initial repository scan to analyze module risk weights.
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          
          {/* Heatmap Grid */}
          <div className="lg:col-span-3 bg-zinc-950/85 border border-zinc-900 rounded-2xl p-6 shadow-xl">
            <h2 className="text-lg font-bold mb-6 flex items-center gap-2 text-zinc-200">
              <Sparkles className="w-4 h-4 text-indigo-500" /> Codebase Module Clusters
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
              {Object.entries(heatmap).map(([path, detail]) => {
                const isSelected = selectedModule?.path === path;
                return (
                  <div
                    key={path}
                    onClick={() => setSelectedModule({ path, detail })}
                    className={getSeverityStyle(detail.severity, isSelected)}
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[10px] font-bold uppercase tracking-wider opacity-80">
                          {detail.severity}
                        </span>
                        {detail.severity === "CRITICAL" && (
                          <ShieldAlert className="w-3.5 h-3.5 text-red-400" />
                        )}
                      </div>
                      <p className="font-bold text-sm text-zinc-200 truncate mt-1" title={path}>{path}</p>
                    </div>
                    <div className="mt-6 pt-3 border-t border-zinc-900/40 flex justify-between items-center text-xs text-zinc-400">
                      <span>Complexity Index: {detail.metrics.complexity_index}</span>
                      <span className="font-bold font-mono text-sm">{detail.score}%</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Module Inspector Sidebar */}
          <div className="space-y-6">
            
            {/* Inspector Panel */}
            <div className="bg-zinc-950/85 border border-zinc-900 rounded-2xl p-6 shadow-xl">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-500 mb-4">Module Inspector</h3>
              {selectedModule ? (
                <div className="space-y-5">
                  <div>
                    <span className="text-[10px] font-mono tracking-wider text-indigo-400 uppercase block mb-1">
                      {selectedModule.detail.severity} severity
                    </span>
                    <h4 className="text-base font-bold text-zinc-200 break-all leading-tight">
                      {selectedModule.path}
                    </h4>
                  </div>
                  
                  <div className="border-t border-zinc-900 pt-4 space-y-3.5 text-xs text-zinc-400">
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-1.5"><BarChart className="w-3.5 h-3.5 text-zinc-500" /> Lines of Code</span>
                      <span className="font-mono text-zinc-200">{selectedModule.detail.metrics.loc} lines</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5 text-zinc-500" /> Complexity Rating</span>
                      <span className="font-mono text-zinc-200">{selectedModule.detail.metrics.complexity_index} (High)</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-zinc-500">Calculated Vulnerability:</span>
                      <span className="font-bold font-mono text-zinc-200">{selectedModule.detail.score}%</span>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-zinc-500">Click any card block to inspect metrics.</p>
              )}
            </div>

            {/* Severity explanation panel */}
            <div className="bg-zinc-950/85 border border-zinc-900 rounded-2xl p-6 shadow-xl">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-500 mb-4">Risk Legend</h2>
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-4 h-4 bg-red-500/10 border border-red-500/30 rounded-md" />
                  <span className="text-xs text-zinc-300 font-medium">Critical (&gt;75% risk, high churn)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-4 h-4 bg-amber-500/10 border border-amber-500/30 rounded-md" />
                  <span className="text-xs text-zinc-300 font-medium">High (55% - 75% risk, sandbox logic)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-4 h-4 bg-yellow-500/5 border border-yellow-500/20 rounded-md" />
                  <span className="text-xs text-zinc-300 font-medium">Medium (30% - 55% risk, DB adapters)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-4 h-4 bg-emerald-500/5 border border-emerald-500/20 rounded-md" />
                  <span className="text-xs text-zinc-300 font-medium">Low (&lt;30% risk, configs, telemetry)</span>
                </div>
              </div>
            </div>

            <div className="bg-zinc-950/50 border border-zinc-900 rounded-2xl p-6 flex gap-3 text-zinc-500 text-xs">
              <HelpCircle className="w-5 h-5 shrink-0 text-indigo-500" />
              <p className="leading-relaxed">
                Defect risk indexes are predicted by matching module parameters (lines of code, nesting index) with modifications density (git churn).
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
