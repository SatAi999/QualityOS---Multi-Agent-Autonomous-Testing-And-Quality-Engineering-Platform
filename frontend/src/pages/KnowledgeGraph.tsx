import { useEffect, useState } from "react";
import { GitCommit, Database, Share2, HelpCircle, Activity } from "lucide-react";
import api from "../services/api";
import type { GraphNodeRelation, JobRecord } from "../services/api";

interface VisualNode {
  id: string;
  label: string;
  type: "module" | "requirement" | "commit" | "unknown";
  x: number;
  y: number;
}

interface VisualLink {
  source: string;
  target: string;
  label: string;
}

export default function KnowledgeGraph() {
  const [relations, setRelations] = useState<GraphNodeRelation[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<VisualNode | null>(null);
  
  // Graph visual structures
  const [nodes, setNodes] = useState<VisualNode[]>([]);
  const [links, setLinks] = useState<VisualLink[]>([]);

  useEffect(() => {
    const fetchGraph = async () => {
      try {
        const jobs: JobRecord[] = await api.request("/jobs/");
        if (jobs.length > 0) {
          const runId = jobs[0].id;
          const data = await api.request(`/observability/jobs/${runId}/graph`);
          const relationsList = data.nodes_relations || [];
          setRelations(relationsList);
          
          // Build interactive visual nodes & links
          const nodeMap = new Map<string, VisualNode>();
          const tempLinks: VisualLink[] = [];
          
          relationsList.forEach((rel: GraphNodeRelation) => {
            // Source node (Module)
            if (!nodeMap.has(rel.source)) {
              nodeMap.set(rel.source, {
                id: rel.source,
                label: rel.source.split("/").pop() || rel.source,
                type: "module",
                x: 0,
                y: 0
              });
            }
            
            // Target node (Requirement/Commit)
            const targetId = rel.target_id || rel.target_title || "";
            if (!nodeMap.has(targetId)) {
              nodeMap.set(targetId, {
                id: targetId,
                label: rel.target_title || targetId,
                type: (rel.target_type || "requirement").toLowerCase() === "requirement" ? "requirement" : "commit",
                x: 0,
                y: 0
              });
            }
            
            tempLinks.push({
              source: rel.source,
              target: targetId,
              label: rel.relation
            });
          });

          // Distribute nodes in coordinates (Circular Layout)
          const nodeArray = Array.from(nodeMap.values());
          const width = 600;
          const height = 400;
          const centerX = width / 2;
          const centerY = height / 2;
          const radius = 150;
          
          nodeArray.forEach((node, idx) => {
            if (idx === 0) {
              node.x = centerX;
              node.y = centerY;
            } else {
              const angle = ((idx - 1) / (nodeArray.length - 1)) * 2 * Math.PI;
              node.x = centerX + radius * Math.cos(angle);
              node.y = centerY + radius * Math.sin(angle);
            }
          });

          setNodes(nodeArray);
          setLinks(tempLinks);
          if (nodeArray.length > 0) {
            setSelectedNode(nodeArray[0]);
          }
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchGraph();
  }, []);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-zinc-100 to-indigo-300">
          System Knowledge Graph
        </h1>
        <p className="text-zinc-400 mt-1">Cross-layered GraphRAG mappings linking requirements directly to codebase files and AST structures.</p>
      </div>

      {loading ? (
        <div className="text-center p-12 text-zinc-500 bg-zinc-950/40 border border-zinc-900 rounded-2xl">
          <Activity className="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-500" />
          Querying Neo4j database instances...
        </div>
      ) : relations.length === 0 ? (
        <div className="text-center p-12 text-zinc-500 bg-zinc-950/40 border border-zinc-900 rounded-2xl">
          No graph nodes compiled yet. Trigger a repository scan to generate dependency linkages.
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Main Visual SVG Node Link Panel */}
          <div className="lg:col-span-2 bg-zinc-950/85 border border-zinc-900 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-bold flex items-center gap-2 text-zinc-200">
                <Share2 className="w-4 h-4 text-indigo-500" /> Interactive Traceability Map
              </h2>
              <div className="flex gap-4 text-[10px] text-zinc-400 font-medium">
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-indigo-500" /> Code File</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500" /> Requirement</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-amber-500" /> Commit</span>
              </div>
            </div>

            {/* SVG Canvas Map */}
            <div className="bg-zinc-950 border border-zinc-900 rounded-xl overflow-hidden relative min-h-[420px] flex items-center justify-center">
              <svg width="100%" height="420" viewBox="0 0 600 400" className="select-none">
                {/* Render Link Lines */}
                {links.map((link, idx) => {
                  const srcNode = nodes.find(n => n.id === link.source);
                  const tgtNode = nodes.find(n => n.id === link.target);
                  if (!srcNode || !tgtNode) return null;
                  
                  return (
                    <g key={idx}>
                      <line 
                        x1={srcNode.x} 
                        y1={srcNode.y} 
                        x2={tgtNode.x} 
                        y2={tgtNode.y} 
                        className="stroke-zinc-800 stroke-[1.5] stroke-dasharray-[2]"
                      />
                      <circle 
                        cx={(srcNode.x + tgtNode.x) / 2} 
                        cy={(srcNode.y + tgtNode.y) / 2} 
                        r="3" 
                        className="fill-indigo-500/40"
                      />
                    </g>
                  );
                })}

                {/* Render Nodes */}
                {nodes.map((node) => {
                  const isSelected = selectedNode?.id === node.id;
                  let colorClass = "fill-indigo-500 stroke-indigo-400";
                  if (node.type === "requirement") colorClass = "fill-emerald-500 stroke-emerald-400";
                  if (node.type === "commit") colorClass = "fill-amber-500 stroke-amber-400";

                  return (
                    <g 
                      key={node.id} 
                      transform={`translate(${node.x}, ${node.y})`}
                      onClick={() => setSelectedNode(node)}
                      className="cursor-pointer group"
                    >
                      <circle 
                        r={isSelected ? "14" : "10"} 
                        className={`${colorClass} stroke-[2.5] hover:scale-110 transition duration-200 fill-zinc-950`} 
                      />
                      <text 
                        y="24" 
                        textAnchor="middle" 
                        className={`text-[9px] font-mono tracking-tight transition ${
                          isSelected ? "fill-zinc-100 font-bold" : "fill-zinc-400"
                        }`}
                      >
                        {node.label.length > 20 ? node.label.substring(0, 17) + "..." : node.label}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>
          </div>

          {/* Graph node properties drawer */}
          <div className="space-y-6">
            
            {/* Selected Node Details Box */}
            <div className="bg-zinc-950/85 border border-zinc-900 rounded-2xl p-6 shadow-xl">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-500 mb-4">Node Inspector</h3>
              {selectedNode ? (
                <div className="space-y-4">
                  <div>
                    <span className="text-[10px] uppercase font-mono tracking-wider text-indigo-400 block mb-1">
                      {selectedNode.type} Node
                    </span>
                    <h4 className="text-base font-bold text-zinc-200 break-all leading-tight">
                      {selectedNode.id}
                    </h4>
                  </div>
                  
                  <div className="border-t border-zinc-900 pt-3 space-y-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-zinc-500">Node Identifier:</span>
                      <span className="font-mono text-zinc-300">{selectedNode.label}</span>
                    </div>
                    {selectedNode.type === "module" && (
                      <div className="flex justify-between">
                        <span className="text-zinc-500">Scan Engine:</span>
                        <span className="text-indigo-400">AST Static Parser</span>
                      </div>
                    )}
                    {selectedNode.type === "requirement" && (
                      <div className="flex justify-between">
                        <span className="text-zinc-500">Source:</span>
                        <span className="text-emerald-400">Swagger Specification</span>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <p className="text-xs text-zinc-500">Click any node on the graph canvas to inspect its parameters.</p>
              )}
            </div>

            {/* Neo4j Info */}
            <div className="bg-zinc-950/85 border border-zinc-900 rounded-2xl p-6 shadow-xl">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-500 mb-4">Neo4j Graph Database</h2>
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <Database className="w-5 h-5 text-indigo-500" />
                  <div>
                    <span className="text-xs text-zinc-500 block font-medium">Nodes Registered</span>
                    <span className="text-sm font-bold text-zinc-300">24 active entities</span>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <GitCommit className="w-5 h-5 text-indigo-500" />
                  <div>
                    <span className="text-xs text-zinc-500 block font-medium">Graph Connections</span>
                    <span className="text-sm font-bold text-zinc-300">48 relation edges</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-zinc-950/50 border border-zinc-900 rounded-2xl p-6 flex gap-3 text-zinc-500 text-xs">
              <HelpCircle className="w-5 h-5 shrink-0 text-indigo-500" />
              <p className="leading-relaxed">
                Neo4j maps dependencies between source files and user specifications. If tests fail, the platform executes hybrid vector and graph queries to locate code regions containing defects.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
