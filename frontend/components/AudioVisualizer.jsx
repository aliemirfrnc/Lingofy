"use client";

import React, { useEffect, useRef } from "react";

export default function AudioVisualizer({ isRecording, color = "rgba(29, 185, 84, 1)" }) {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    let width = canvas.width;
    let height = canvas.height;

    const drawWaveform = () => {
      ctx.clearRect(0, 0, width, height);

      // Draw a flat line if not recording
      if (!isRecording) {
        ctx.beginPath();
        ctx.moveTo(0, height / 2);
        ctx.lineTo(width, height / 2);
        ctx.strokeStyle = "rgba(255, 255, 255, 0.3)";
        ctx.lineWidth = 2;
        ctx.stroke();
        return;
      }

      // Draw a fake animated waveform
      ctx.beginPath();
      ctx.moveTo(0, height / 2);

      const slices = 40;
      const sliceWidth = width / slices;

      for (let i = 0; i <= slices; i++) {
        // Random amplitude to simulate voice
        const amplitude = Math.random() * (height / 2.5);
        const y = height / 2 + (Math.random() > 0.5 ? amplitude : -amplitude);

        if (i === 0) {
          ctx.moveTo(i * sliceWidth, height / 2);
        } else {
          // Smooth curve using bezier or simple line
          ctx.lineTo(i * sliceWidth, y);
        }
      }

      ctx.lineTo(width, height / 2);
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.stroke();

      // Shadow for premium feel
      ctx.shadowColor = color;
      ctx.shadowBlur = 10;

      if (isRecording) {
        animationRef.current = requestAnimationFrame(drawWaveform);
      }
    };

    if (isRecording) {
      drawWaveform();
    } else {
      drawWaveform(); // Draw flat line once
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isRecording, color]);

  return (
    <canvas
      ref={canvasRef}
      width={300}
      height={100}
      className="w-full h-24 rounded-lg bg-black/20 border border-white/10"
    />
  );
}
