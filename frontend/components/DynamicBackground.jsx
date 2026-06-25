"use client";
import { useEffect, useState } from "react";

const FALLBACK_COLOR = { r: 60, g: 60, b: 100 };

function getAverageColor(img) {
  const canvas = document.createElement("canvas");
  canvas.width = 8;
  canvas.height = 8;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(img, 0, 0, 8, 8);
  const data = ctx.getImageData(0, 0, 8, 8).data;
  let r = 0,
    g = 0,
    b = 0,
    count = 0;
  for (let i = 0; i < data.length; i += 4) {
    const brightness = (data[i] + data[i + 1] + data[i + 2]) / 3;
    if (brightness < 20 || brightness > 235) continue;
    r += data[i];
    g += data[i + 1];
    b += data[i + 2];
    count++;
  }
  if (count === 0) return { r: 80, g: 80, b: 120 };
  return {
    r: Math.round(r / count),
    g: Math.round(g / count),
    b: Math.round(b / count),
  };
}

function saturate(color, factor = 1.4) {
  const max = Math.max(color.r, color.g, color.b);
  const min = Math.min(color.r, color.g, color.b);
  if (max === min) return color;
  return {
    r: Math.max(0, Math.min(255, Math.round(color.r + (color.r - 128) * (factor - 1)))),
    g: Math.max(0, Math.min(255, Math.round(color.g + (color.g - 128) * (factor - 1)))),
    b: Math.max(0, Math.min(255, Math.round(color.b + (color.b - 128) * (factor - 1)))),
  };
}

export default function DynamicBackground({ albumImage, onColorExtracted }) {
  const [color, setColor] = useState(FALLBACK_COLOR);
  const [displayImage, setDisplayImage] = useState(null);

  useEffect(() => {
    let cancelled = false;
    const applyFallback = () => {
      if (cancelled) return;
      setDisplayImage(null);
      setColor(FALLBACK_COLOR);
      onColorExtracted?.(FALLBACK_COLOR);
    };

    const applyColorToDOM = (r, g, b) => {
      document.documentElement.style.setProperty("--theme-r", r);
      document.documentElement.style.setProperty("--theme-g", g);
      document.documentElement.style.setProperty("--theme-b", b);
    };

    if (!albumImage) {
      applyFallback();
      applyColorToDOM(FALLBACK_COLOR.r, FALLBACK_COLOR.g, FALLBACK_COLOR.b);
      return () => {
        cancelled = true;
      };
    }

    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      if (cancelled) return;
      try {
        const raw = getAverageColor(img);
        const boosted = saturate(raw, 1.6);
        setDisplayImage(albumImage);
        setColor(boosted);
        applyColorToDOM(boosted.r, boosted.g, boosted.b);
        onColorExtracted?.(boosted);
      } catch {
        applyFallback();
        applyColorToDOM(FALLBACK_COLOR.r, FALLBACK_COLOR.g, FALLBACK_COLOR.b);
      }
    };
    img.onerror = () => {
      applyFallback();
      applyColorToDOM(FALLBACK_COLOR.r, FALLBACK_COLOR.g, FALLBACK_COLOR.b);
    };
    img.src = albumImage;

    return () => {
      cancelled = true;
      img.onload = null;
      img.onerror = null;
    };
  }, [albumImage, onColorExtracted]);

  const { r, g, b } = color;

  return (
    <>
      <div
        aria-hidden="true"
        className="fixed inset-0 z-0 overflow-hidden bg-background"
      >
        {displayImage && (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={displayImage}
            alt=""
            className="absolute inset-0 w-full h-full object-cover opacity-[0.18] scale-[1.08] blur-[48px] saturate-[1.4] transition-all duration-1000 ease-in-out animate-fade-in"
            crossOrigin="anonymous"
          />
        )}
        <div
          className="absolute inset-0 transition-colors duration-1000 ease-in-out"
          style={{
            background: `linear-gradient(
              160deg,
              rgba(var(--theme-r),var(--theme-g),var(--theme-b),0.28) 0%,
              rgba(var(--theme-r),var(--theme-g),var(--theme-b),0.10) 30%,
              rgba(10,10,10,0.85) 65%,
              #0a0a0a 100%
            )`,
          }}
        />
      </div>
    </>
  );
}
