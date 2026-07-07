import { CheckCircle2, Circle } from "lucide-react";

interface LiveExecutionGraphProps {
  currentAgent: string;
}

export default function LiveExecutionGraph({ currentAgent }: LiveExecutionGraphProps) {
  const nodes = [
    "RepositoryUnderstanding",
    "RequirementIntelligence",
    "RiskPrediction",
    "TestStrategy",
    "PlaywrightGenerator",
    "PytestGenerator",
    "APITesting",
    "PerformanceAgent",
    "SecurityAgent",
    "ExploratoryAgent",
    "FailureReproduction",
    "RootCauseAnalysis",
    "DebuggingCopilot",
    "CoverageIntelligence",
    "LearningAgent",
  ];

  const getAgentIndex = (name: string) => nodes.indexOf(name);
  const currentIndex = getAgentIndex(currentAgent);

  const getNodeStatus = (nodeName: string) => {
    const idx = getAgentIndex(nodeName);
    if (currentAgent === "FINISH") return "COMPLETED";
    if (idx < currentIndex) return "COMPLETED";
    if (idx === currentIndex) return "ACTIVE";
    return "PENDING";
  };

  return (
    <div className="bg-surface border border-border rounded-xl p-6">
      <h3 className="text-sm font-bold uppercase tracking-wider text-text-secondary mb-6">
        Multi-Agent Execution Pipeline (LangGraph Workflow)
      </h3>
      
      {/* Node List timeline flow */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {nodes.map((node, i) => {
          const status = getNodeStatus(node);
          return (
            <div 
              key={node} 
              className={`border p-4 rounded-lg flex flex-col justify-between h-28 transition-all ${
                status === "ACTIVE" 
                  ? "bg-brand-bg border-brand text-brand ring-1 ring-brand/35 shadow-[0_0_12px_rgba(99,102,241,0.25)]" 
                  : status === "COMPLETED" 
                  ? "bg-success-bg/15 border-success/30 text-success" 
                  : "bg-background border-border text-text-secondary"
              }`}
            >
              <div className="flex items-start justify-between">
                <span className="text-[10px] font-bold font-mono opacity-60">Node 0{i + 1}</span>
                {status === "COMPLETED" ? (
                  <CheckCircle2 className="w-4 h-4 text-success" />
                ) : status === "ACTIVE" ? (
                  <span className="relative flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-brand"></span>
                  </span>
                ) : (
                  <Circle className="w-4 h-4 text-text-secondary/30" />
                )}
              </div>
              
              <div className="mt-auto">
                <span className="text-xs font-bold font-mono tracking-tight block truncate" title={node}>
                  {node}
                </span>
                <span className="text-[9px] uppercase tracking-wider font-semibold opacity-75 mt-0.5 block">
                  {status === "ACTIVE" ? "Running Node..." : status === "COMPLETED" ? "Finished" : "Planned"}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
