"use client";
import { useEffect, useState, useRef } from "react";

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
  const [isBright, setIsBright] = useState(false);
  const [displayImage, setDisplayImage] = useState(null);
  const onColorExtractedRef = useRef(onColorExtracted);

  useEffect(() => {
    onColorExtractedRef.current = onColorExtracted;
  }, [onColorExtracted]);

  useEffect(() => {
    let cancelled = false;
    const applyFallback = () => {
      if (cancelled) return;
      setDisplayImage(null);
      setColor(FALLBACK_COLOR);
      setIsBright(false);
      onColorExtractedRef.current?.(FALLBACK_COLOR);
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
        const luminance = 0.2126 * boosted.r + 0.7152 * boosted.g + 0.0722 * boosted.b;
        setDisplayImage(albumImage);
        setColor(boosted);
        setIsBright(luminance > 160);
        applyColorToDOM(boosted.r, boosted.g, boosted.b);
        onColorExtractedRef.current?.(boosted);
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
  }, [albumImage]);

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
            className="absolute inset-0 w-full h-full object-cover opacity-[0.35] scale-[1.08] blur-[48px] saturate-[1.5] contrast-[1.2] brightness-[0.9] transition-all duration-1000 ease-in-out animate-fade-in"
            crossOrigin="anonymous"
          />
        )}
        <div className={`absolute inset-0 transition-opacity duration-1000 ${isBright ? 'bg-black/85' : 'bg-black/60'} mix-blend-multiply`} />
        <div
          className="absolute inset-0 transition-colors duration-1000 ease-in-out"
          style={{
            background: `linear-gradient(
              160deg,
              rgba(var(--theme-r),var(--theme-g),var(--theme-b),${isBright ? '0.2' : '0.35'}) 0%,
              rgba(var(--theme-r),var(--theme-g),var(--theme-b),0.15) 30%,
              rgba(10,10,10,0.85) 65%,
              #0a0a0a 100%
            )`,
          }}
        />
      </div>
    </>
  );
}
