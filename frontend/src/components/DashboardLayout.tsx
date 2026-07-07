import React from "react";
import { Link, useLocation } from "react-router-dom";
import { Shield, LayoutDashboard, GitFork, BookOpen, Activity, AlertTriangle, LogOut } from "lucide-react";
import api from "../services/api";

interface LayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: LayoutProps) {
  const location = useLocation();
  const username = localStorage.getItem("username") || "Guest";
  const role = localStorage.getItem("user_role") || "Viewer";

  const handleLogout = () => {
    api.logout();
  };

  const menuItems = [
    { name: "Overview", path: "/", icon: LayoutDashboard },
    { name: "Run Explorer", path: "/runs", icon: Activity },
    { name: "Risk Heatmap", path: "/heatmap", icon: AlertTriangle },
    { name: "Knowledge Graph", path: "/knowledge", icon: BookOpen },
  ];

  // Helper to color code user roles
  const getRoleBadgeClass = (userRole: string) => {
    switch (userRole) {
      case "Admin": return "bg-red-500/10 border-red-500/30 text-red-400";
      case "QA Engineer": return "bg-indigo-500/10 border-indigo-500/30 text-indigo-400";
      case "Developer": return "bg-blue-500/10 border-blue-500/30 text-blue-400";
      default: return "bg-zinc-500/10 border-zinc-500/30 text-zinc-400";
    }
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border bg-surface flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-border flex items-center gap-3">
          <div className="w-8 h-8 bg-brand-bg rounded flex items-center justify-center text-brand">
            <Shield className="w-5 h-5" />
          </div>
          <span className="font-bold text-lg tracking-tight text-text-primary">QualityOS</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition cursor-pointer ${
                  isActive 
                    ? "bg-brand-bg text-brand" 
                    : "text-text-secondary hover:bg-surface-hover hover:text-text-primary"
                }`}
              >
                <Icon className="w-4 h-4" />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Footer info */}
        <div className="p-4 border-t border-border bg-surface-hover flex items-center gap-3">
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold truncate text-text-primary">{username}</p>
            <span className={`inline-block border text-[10px] font-bold px-1.5 py-0.5 rounded-full mt-1 ${getRoleBadgeClass(role)}`}>
              {role}
            </span>
          </div>
          <button
            onClick={handleLogout}
            className="p-2 hover:bg-surface rounded text-text-secondary hover:text-failure transition cursor-pointer"
            title="Log Out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </aside>

      {/* Main content body */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="h-16 border-b border-border bg-surface flex items-center justify-between px-8">
          <div className="flex items-center gap-2 text-text-secondary text-sm">
            <GitFork className="w-4 h-4" />
            <span>active_branch:</span>
            <span className="font-semibold text-text-primary">main</span>
          </div>
        </header>

        {/* Screen context */}
        <main className="flex-1 overflow-y-auto p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
