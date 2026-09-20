"use client";

import { useState, useEffect } from "react";
import { X } from "lucide-react";

export function DevelopmentNoticePopup() {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    // Check if user has seen the popup before
    const hasSeenPopup = localStorage.getItem("hasSeenDevelopmentNotice");
    if (!hasSeenPopup) {
      // Small delay to ensure smooth animation
      setTimeout(() => {
        setIsOpen(true);
      }, 500);
    }
  }, []);

  const handleClose = () => {
    setIsOpen(false);
    localStorage.setItem("hasSeenDevelopmentNotice", "true");
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="relative w-full max-w-4xl bg-transparent rounded-2xl overflow-hidden shadow-2xl">
        {/* Close Button */}
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 z-10 w-8 h-8 rounded-full bg-white/90 hover:bg-white flex items-center justify-center transition-colors shadow-lg"
          aria-label="Close"
        >
          <X className="w-5 h-5 text-slate-700" />
        </button>

        {/* Two Panel Layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-0">
          {/* Left Panel - Light Theme */}
          <div className="bg-white rounded-l-2xl md:rounded-r-none p-6 md:p-8 flex flex-col justify-between">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-slate-800 mb-4">
                Shaped by Your Choices, Driven by Your Vision
              </h2>
              <p className="text-base md:text-lg text-slate-600 mb-6">
                We will use that context when making future suggestions.
              </p>

              {/* Feature Tags */}
              <div className="flex flex-wrap gap-3 mb-6">
                <span className="px-4 py-2 bg-slate-100 text-slate-700 rounded-full text-sm font-medium">
                  Performance
                </span>
                <span className="px-4 py-2 bg-slate-100 text-slate-700 rounded-full text-sm font-medium">
                  Availability
                </span>
                <span className="px-4 py-2 bg-slate-100 text-slate-700 rounded-full text-sm font-medium">
                  Cost
                </span>
                <span className="px-4 py-2 bg-slate-100 text-slate-700 rounded-full text-sm font-medium">
                  Revenue
                </span>
              </div>
            </div>

            {/* Explore Demo Button */}
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-lime-400"></div>
              <button
                onClick={handleClose}
                className="px-6 py-3 bg-black text-white rounded-lg font-medium hover:bg-slate-900 transition-colors"
              >
                Explore Demo
              </button>
            </div>
          </div>

          {/* Right Panel - Dark Theme */}
          <div className="bg-black rounded-r-2xl md:rounded-l-none p-6 md:p-8 flex flex-col justify-between">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                Platform Under Development
              </h2>
              <p className="text-base md:text-lg text-slate-300 mb-6">
                Our AI-powered trading platform is currently in active development. We're building an intelligent system that analyzes markets in real-time, makes automated trading decisions, and manages positions 24/7. We focus on reducing latency and keeping the UI consistently responsive, even under heavy traffic loads.
              </p>

              {/* Radar Chart Visualization */}
              <div className="relative w-full h-48 flex items-center justify-center">
                <svg
                  viewBox="0 0 200 200"
                  className="w-full h-full"
                  style={{ maxWidth: "300px" }}
                >
                  {/* Grid Lines */}
                  <defs>
                    <linearGradient id="radarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.3" />
                      <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.1" />
                    </linearGradient>
                  </defs>

                  {/* Grid Circles */}
                  <circle cx="100" cy="100" r="60" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                  <circle cx="100" cy="100" r="40" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                  <circle cx="100" cy="100" r="20" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />

                  {/* Grid Lines */}
                  <line x1="100" y1="100" x2="100" y2="20" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                  <line x1="100" y1="100" x2="40" y2="160" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                  <line x1="100" y1="100" x2="160" y2="160" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />

                  {/* Radar Area - Performance, Availability, Cost */}
                  <polygon
                    points="100,40 60,140 140,140"
                    fill="url(#radarGradient)"
                    stroke="#3b82f6"
                    strokeWidth="2"
                    opacity="0.6"
                  />

                  {/* Data Points */}
                  <circle cx="100" cy="40" r="4" fill="#3b82f6" />
                  <circle cx="60" cy="140" r="4" fill="#3b82f6" />
                  <circle cx="140" cy="140" r="4" fill="#3b82f6" />

                  {/* Labels */}
                  <text x="100" y="15" textAnchor="middle" fill="white" fontSize="10" fontWeight="500">
                    Performance
                  </text>
                  <text x="35" y="145" textAnchor="middle" fill="white" fontSize="10" fontWeight="500">
                    Availability
                  </text>
                  <text x="165" y="145" textAnchor="middle" fill="white" fontSize="10" fontWeight="500">
                    Cost
                  </text>
                </svg>
              </div>
            </div>

            {/* Status Indicator */}
            <div className="flex items-center gap-2 text-slate-400 text-sm">
              <div className="w-2 h-2 rounded-full bg-lime-400 animate-pulse"></div>
              <span>Development in progress</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
