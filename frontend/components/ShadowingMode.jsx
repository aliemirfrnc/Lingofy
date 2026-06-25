"use client";

import React, { useState } from "react";
import PronunciationCoach from "./PronunciationCoach";
import { Mic, X, ChevronLeft, ChevronRight, Play } from "lucide-react";
import { Button } from "./ui/Button";
import { Badge } from "./ui/Badge";

export default function ShadowingMode({ lyrics, onClose }) {
  const [currentLineIndex, setCurrentLineIndex] = useState(0);
  const [isPracticing, setIsPracticing] = useState(false);
  
  // A premium feature for step-by-step line reading
  const lines = lyrics
    .split("\n")
    .filter((l) => l.trim().length > 0)
    .filter((l) => !l.startsWith("[")); // filter out tags like [Chorus]

  const handleNext = () => {
    if (currentLineIndex < lines.length - 1) {
      setCurrentLineIndex((prev) => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentLineIndex > 0) {
      setCurrentLineIndex((prev) => prev - 1);
    }
  };

  return (
    <div className="fixed inset-0 z-40 bg-black flex flex-col animate-fade-in">
      {/* Header */}
      <div className="flex justify-between items-center p-6 bg-gradient-to-b from-theme-900/40 to-black shrink-0">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-theme-400 to-purple-500 flex items-center justify-center shadow-glow shrink-0">
            <Mic className="w-5 h-5 text-black" fill="currentColor" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2 m-0 leading-none mb-1.5">
              Shadowing Mode 
              <Badge variant="warning" className="ml-1 uppercase">Premium</Badge>
            </h2>
            <p className="text-white/50 text-xs font-semibold m-0">Adım adım tekrarla ve mükemmelleştir</p>
          </div>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} className="rounded-full w-10 h-10 text-white/50 hover:text-white">
          <X className="w-6 h-6" />
        </Button>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center p-8 max-w-4xl mx-auto w-full relative z-10 min-h-0">
        
        {/* Progress */}
        <div className="w-full flex items-center justify-between mb-16 text-xs text-white/30 font-bold tabular-nums">
          <span>{currentLineIndex + 1}</span>
          <div className="flex-1 mx-4 h-1 bg-white/10 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-theme-500 to-theme-300 transition-all duration-300 shadow-glow"
              style={{ width: `${((currentLineIndex + 1) / lines.length) * 100}%` }}
            ></div>
          </div>
          <span>{lines.length}</span>
        </div>

        {/* Current Line Focus */}
        <div className="text-center space-y-8 w-full flex-1 flex flex-col justify-center min-h-0">
          {currentLineIndex > 0 && (
            <p className="text-lg text-white/20 blur-[1px] select-none m-0 font-medium truncate px-4">{lines[currentLineIndex - 1]}</p>
          )}
          
          <div className="glass-panel p-8 md:p-12 relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-r from-theme-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <p className="text-3xl md:text-5xl font-black text-white leading-tight drop-shadow-lg relative z-10 m-0 tracking-tight">
              {lines[currentLineIndex]}
            </p>
          </div>
          
          {currentLineIndex < lines.length - 1 && (
            <p className="text-lg text-white/20 blur-[1px] select-none m-0 font-medium truncate px-4">{lines[currentLineIndex + 1]}</p>
          )}
        </div>

        {/* Actions */}
        <div className="mt-16 flex items-center gap-6 md:gap-8 shrink-0 pb-10">
          <Button 
            variant="secondary"
            size="icon"
            onClick={handlePrev}
            disabled={currentLineIndex === 0}
            className="w-14 h-14 rounded-full disabled:opacity-30"
          >
            <ChevronLeft className="w-8 h-8" />
          </Button>

          <Button 
            onClick={() => setIsPracticing(true)}
            className="group relative flex items-center gap-3 bg-white text-black hover:bg-white px-8 py-6 rounded-full font-bold text-lg hover:scale-105 transition-all shadow-glow"
          >
            <div className="absolute inset-0 rounded-full bg-white opacity-20 blur-xl group-hover:opacity-40 transition-opacity"></div>
            <Mic className="w-6 h-6 text-black" fill="currentColor" />
            Sıra Sende
          </Button>

          <Button 
            variant="secondary"
            size="icon"
            onClick={handleNext}
            disabled={currentLineIndex === lines.length - 1}
            className="w-14 h-14 rounded-full disabled:opacity-30"
          >
            <ChevronRight className="w-8 h-8" />
          </Button>
        </div>

      </div>

      {isPracticing && (
        <PronunciationCoach 
          expectedText={lines[currentLineIndex]} 
          onClose={() => setIsPracticing(false)} 
        />
      )}
    </div>
  );
}
