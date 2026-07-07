import { Clock } from "lucide-react";
import type { TraceRecord } from "../services/api";

interface TraceTimelineProps {
  traces: TraceRecord[];
}

export default function TraceTimeline({ traces }: TraceTimelineProps) {
  if (traces.length === 0) return null;

  // Find max duration to calibrate width scaling
  const maxDuration = Math.max(...traces.map((t) => t.duration_seconds), 1);

  return (
    <div className="bg-surface border border-border rounded-xl p-6 space-y-5">
      <h3 className="text-sm font-bold uppercase tracking-wider text-text-secondary flex items-center gap-2">
        <Clock className="w-4 h-4 text-brand" /> OpenTelemetry Agent Traces (Jaeger timelines)
      </h3>
      
      <div className="space-y-4">
        {traces.map((trace) => {
          // Calculate percentage width of the trace duration
          const percentage = (trace.duration_seconds / maxDuration) * 100;
          return (
            <div key={trace.agent_name} className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-6 text-sm">
              {/* Agent Title */}
              <div className="w-52 shrink-0">
                <span className="font-mono font-bold text-xs text-text-primary block truncate">
                  {trace.agent_name}
                </span>
                <span className="text-[10px] text-text-secondary">
                  Duration: {trace.duration_seconds}s
                </span>
              </div>
              
              {/* Gantt Bar */}
              <div className="flex-1 bg-background rounded-full h-3.5 overflow-hidden flex items-center">
                <div 
                  className="bg-brand hover:bg-brand-hover h-full rounded-full transition-all"
                  style={{ width: `${Math.max(percentage, 5)}%` }}
                  title={`${trace.agent_name}: ${trace.duration_seconds}s`}
                />
              </div>

              {/* Status */}
              <div className="w-16 text-right shrink-0 text-xs font-semibold text-success font-mono">
                {trace.status}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
