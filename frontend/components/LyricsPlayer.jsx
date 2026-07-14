"use client";
import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { api } from "../lib/api";
import ErrorBanner from "./ErrorBanner";
import PronunciationCoach from "./PronunciationCoach";
import ShadowingMode from "./ShadowingMode";
import { useTranslationQueue } from "../hooks/useTranslationQueue";
import { LyricLine } from "./LyricLine";

export default memo(function LyricsPlayer({
  accentColor,
  onWordClick,
  onTrackChange,
  onProgress,
}) {
  const [lyrics, setLyrics] = useState([]);
  const [synced, setSynced] = useState(null);
  
  const { translation, setTranslation, translateLineQueue, resetQueue, lastTrackRef } = useTranslationQueue();

  const [selectedLine, setSelectedLine] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [errorStatus, setErrorStatus] = useState(null);
  const [playback, setPlayback] = useState({ progressMs: 0, isPlaying: false });
  const [syncOffsetMs, setSyncOffsetMs] = useState(() => {
    if (typeof window === "undefined") return 0;
    return Number.parseInt(localStorage.getItem("lingofy_sync_offset"), 10) || 0;
  });
  const [autoFollow, setAutoFollow] = useState(true);
  const [translatingAll, setTranslatingAll] = useState(false);
  const [translateAllError, setTranslateAllError] = useState(null);
  const [showFullTranslation, setShowFullTranslation] = useState(false);
  const [coachLine, setCoachLine] = useState(null);
  const [showShadowing, setShowShadowing] = useState(false);

  const lineRefs = useRef([]);
  const containerRef = useRef(null);
  const idleTimerRef = useRef(null);
  const programmaticScrollUntil = useRef(0);
  const lastArtistRef = useRef(null);
  const lyricsRequestRef = useRef(0);
  const lyricsAbortRef = useRef(null);

  const { r = 120, g = 80, b = 200 } = accentColor || {};

  const adjustOffset = useCallback((deltaMs) => {
    setSyncOffsetMs((prev) => {
      const next = prev + deltaMs;
      localStorage.setItem("lingofy_sync_offset", String(next));
      return next;
    });
  }, []);

  const pauseAutoFollow = useCallback(() => {
    setAutoFollow(false);
    if (idleTimerRef.current) clearTimeout(idleTimerRef.current);
    idleTimerRef.current = setTimeout(() => setAutoFollow(true), 6000);
  }, []);

  const resumeAutoFollow = useCallback(() => {
    if (idleTimerRef.current) clearTimeout(idleTimerRef.current);
    setAutoFollow(true);
  }, []);

  const handleLineClick = useCallback((index) => {
    pauseAutoFollow();
    setSelectedLine(index);
  }, [pauseAutoFollow]);

  const handleWordClick = useCallback((token, line, index) => {
    pauseAutoFollow();
    setSelectedLine(index);
    onWordClick?.(token, line);
  }, [pauseAutoFollow, onWordClick]);

  const handleCoachClick = useCallback((line) => {
    setCoachLine(line);
  }, []);

  const loadLyrics = useCallback((track, artist = "") => {
    const requestId = lyricsRequestRef.current + 1;
    lyricsRequestRef.current = requestId;
    lyricsAbortRef.current?.abort();
    const controller = new AbortController();
    lyricsAbortRef.current = controller;
    
    resetQueue(track);

    lastArtistRef.current = artist;

    setLoading(true);
    setError(null);
    setErrorStatus(null);
    setSelectedLine(null);
    setSynced(null);
    setAutoFollow(true);
    setTranslateAllError(null);
    setShowFullTranslation(false);

    api
      .getLyrics(track, artist, { signal: controller.signal })
      .then((data) => {
        if (requestId !== lyricsRequestRef.current) return;
        setLyrics(data.lyrics ?? []);
        setSynced(data.synced?.length > 0 ? data.synced : null);
      })
      .catch((err) => {
        if (err.name === "AbortError" || requestId !== lyricsRequestRef.current) return;
        setLyrics([]);
        setError(err.message || "Şarkı sözleri yüklenemedi.");
        setErrorStatus(err.status ?? null);
      })
      .finally(() => {
        if (requestId === lyricsRequestRef.current) setLoading(false);
      });
  }, [resetQueue]);

  useEffect(
    () => () => {
      lyricsAbortRef.current?.abort();
      if (idleTimerRef.current) clearTimeout(idleTimerRef.current);
    },
    [],
  );

  // Dışarıdan gelen şarkı değişikliği
  useEffect(() => {
    onTrackChange?.((trackName, artist) => {
      setPlayback({ progressMs: 0, isPlaying: false });
      loadLyrics(trackName, artist);
    });
  }, [onTrackChange, loadLyrics]);

  // Progress güncellemesi
  useEffect(() => {
    onProgress?.((progressMs, _dur, isPlaying) => {
      setPlayback({ progressMs: progressMs ?? 0, isPlaying: !!isPlaying });
    });
  }, [onProgress]);

  useEffect(() => {
    if (!playback.isPlaying) return;
    const id = setInterval(() => {
      setPlayback((p) => ({ ...p, progressMs: p.progressMs + 1000 }));
    }, 1000);
    return () => clearInterval(id);
  }, [playback.isPlaying]);

  const currentLineIndex = useMemo(() => {
    if (!synced?.length) return null;
    const progressSec = (playback.progressMs + syncOffsetMs) / 1000;
    let idx = -1;
    for (let i = 0; i < synced.length; i++) {
      if (synced[i].time <= progressSec) idx = i;
      else break;
    }
    return idx >= 0 ? idx : null;
  }, [synced, playback.progressMs, syncOffsetMs]);

  const activeLineIndex =
    autoFollow && currentLineIndex !== null ? currentLineIndex : selectedLine;

  useEffect(() => {
    if (!autoFollow || activeLineIndex === null) return;
    const el = lineRefs.current[activeLineIndex];
    if (el) {
      programmaticScrollUntil.current = Date.now() + 800;
      el.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [activeLineIndex, autoFollow]);

  useEffect(() => {
    if (activeLineIndex === null || !lyrics.length) return;
    // Prefetch logic: Active line + 5 previous + 5 next lines
    const start = Math.max(0, activeLineIndex - 5);
    const end = Math.min(lyrics.length - 1, activeLineIndex + 5);
    for (let i = start; i <= end; i++) {
      const line = lyrics[i];
      if (line && translation[line] === undefined) {
        translateLineQueue(line);
      }
    }
  }, [activeLineIndex, lyrics, translateLineQueue, translation]);

  useEffect(() => {
    function handleScroll() {
      if (Date.now() < programmaticScrollUntil.current) return;
      pauseAutoFollow();
    }
    const el = containerRef.current;
    if (el) el.addEventListener("scroll", handleScroll, { passive: true });
    return () => el?.removeEventListener("scroll", handleScroll);
  }, [pauseAutoFollow]);

  const handleTranslateAll = useCallback(() => {
    const pending = [...new Set(lyrics)].filter(
      (line) => line.trim() && translation[line] === undefined,
    );
    if (pending.length === 0) {
      setShowFullTranslation(true);
      return;
    }

    setTranslatingAll(true);
    setTranslateAllError(null);
    const requestId = lyricsRequestRef.current;

    api
      .translateBatch(pending, lastTrackRef.current)
      .then((data) => {
        if (requestId !== lyricsRequestRef.current) return;
        setTranslation((prev) => {
          const next = { ...prev, ...data.translations };
          (data.failed || []).forEach((l) => {
            next[l] = null;
          });
          return next;
        });
        if (data.failed?.length) {
          setTranslateAllError(`${data.failed.length} satır çevrilemedi.`);
        }
        setShowFullTranslation(true);
      })
      .catch((err) => {
        if (requestId === lyricsRequestRef.current) {
          setTranslateAllError(err.message || "Çeviri başarısız.");
        }
      })
      .finally(() => {
        if (requestId === lyricsRequestRef.current) setTranslatingAll(false);
      });
  }, [lastTrackRef, lyrics, setTranslation, translation]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-3 relative z-10">
        <div className="flex flex-col gap-4 items-center w-full max-w-lg">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="h-[18px] rounded-lg bg-theme/30 animate-pulse"
              style={{
                width: `${Math.random() * 40 + 30}%`,
                opacity: Math.max(0.1, 1 - i * 0.15),
                animationDelay: `${i * 0.1}s`,
              }}
            />
          ))}
        </div>
      </div>
    );
  }

  if (error && !lyrics.length) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-3 relative z-10">
        <ErrorBanner
          message={error}
          onRetry={
            errorStatus !== 404
              ? () => loadLyrics(lastTrackRef.current, lastArtistRef.current)
              : undefined
          }
        />
        <p className="text-white/40 text-[13px] mt-4">
          Spotify&apos;da bir şarkı çal — sözler otomatik yüklenecek
        </p>
      </div>
    );
  }

  if (!lyrics.length) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-3 relative z-10">
        <p className="text-white/30 text-[15px]">Spotify&apos;da bir şarkı çal</p>
      </div>
    );
  }

  return (
    <div className="relative h-full flex flex-col z-10">
      {/* Senkron kontrol + tümünü çevir */}
      <div className="flex items-center justify-between px-6 py-4 shrink-0">
        {synced && (
          <div className="flex items-center gap-2">
            <button className="bg-white/5 border border-white/10 text-white/70 rounded-md px-2.5 py-1 text-xs cursor-pointer hover:bg-white/10 transition-colors" onClick={() => adjustOffset(-500)}>
              −0.5s
            </button>
            <span className="text-white/40 text-[11px] min-w-[52px] text-center">
              {syncOffsetMs > 0 ? "+" : ""}
              {(syncOffsetMs / 1000).toFixed(1)}s
            </span>
            <button className="bg-white/5 border border-white/10 text-white/70 rounded-md px-2.5 py-1 text-xs cursor-pointer hover:bg-white/10 transition-colors" onClick={() => adjustOffset(500)}>
              +0.5s
            </button>
          </div>
        )}
        {lyrics.length > 0 && (
          <div className="flex gap-2">
            <button
              className="bg-yellow-500/15 border border-yellow-500/35 text-yellow-500/90 rounded-full px-4 py-1.5 text-xs font-medium cursor-pointer hover:bg-yellow-500/25 transition-colors flex items-center gap-1.5"
              onClick={() => setShowShadowing(true)}
            >
              <span className="text-sm">🎤</span> Shadowing Mode
            </button>
            <button
              className="bg-theme-100 border border-theme-300 text-white/90 rounded-full px-4 py-1.5 text-xs font-medium cursor-pointer hover:bg-theme-200 transition-colors disabled:opacity-50"
              onClick={handleTranslateAll}
              disabled={translatingAll}
            >
              {translatingAll ? "Çevriliyor..." : "Tümünü çevir"}
            </button>
          </div>
        )}
      </div>

      {translateAllError && (
        <div className="px-6">
          <ErrorBanner
            message={translateAllError}
            onRetry={handleTranslateAll}
          />
        </div>
      )}

      {/* Lyrics listesi */}
      <div ref={containerRef} className="flex-1 overflow-y-auto custom-scrollbar">
        <div className="max-w-[640px] mx-auto px-8 text-center relative z-10">
          {/* Üst dolgu */}
          <div className="h-[35vh]" />

          {lyrics.map((line, i) => {
            const isActive = i === activeLineIndex;
            const dist = Math.abs((activeLineIndex ?? 0) - i);
            const lyricOpacity = isActive ? 1 : Math.max(0.25, 0.60 - dist * 0.1); 
            const scale = isActive ? 1.05 : 0.98;
            const lineTranslation = translation[line];

            return (
              <LyricLine
                key={i}
                line={line}
                lineIndex={i}
                isActive={isActive}
                lyricOpacity={lyricOpacity}
                scale={scale}
                lineTranslation={lineTranslation}
                onLineClick={handleLineClick}
                onWordClick={handleWordClick}
                onCoachClick={handleCoachClick}
                lineRef={(el) => (lineRefs.current[i] = el)}
              />
            );
          })}

          {/* Alt dolgu */}
          <div className="h-[45vh]" />
        </div>
      </div>

      {/* Tam çeviri paneli (overlay) */}
      {showFullTranslation && (
        <div className="absolute inset-0 bg-black/60 backdrop-blur-xl flex items-center justify-center z-50 animate-fade-in">
          <div className="glass-panel w-[90%] max-w-[500px] max-h-[78vh] flex flex-col overflow-hidden">
            <div className="flex justify-between items-center px-5 py-4 border-b border-white/5 shrink-0">
              <span className="text-white font-semibold">Tam çeviri</span>
              <button
                className="text-white/50 text-xl cursor-pointer hover:text-white transition-colors"
                onClick={() => setShowFullTranslation(false)}
              >
                ×
              </button>
            </div>
            <div className="overflow-y-auto px-5 py-3 custom-scrollbar">
              {lyrics.map((line, i) => {
                if (!line.trim()) return null;
                const t = translation[line];
                return (
                  <div key={i} className="pb-3 mb-3 border-b border-white/5 last:border-0">
                    <p className="m-0 mb-1 text-[13px] text-white/45 leading-relaxed">{line}</p>
                    <p
                      className={`m-0 text-[14px] italic leading-relaxed ${
                        t ? "text-theme-100/85" : "text-white/25"
                      }`}
                    >
                      {t === null ? "Çeviri alınamadı" : t || "•••"}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Şimdiki satıra dön */}
      {synced && !autoFollow && (
        <button
          className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-theme border-none text-white rounded-full px-5 py-2.5 text-[13px] font-medium cursor-pointer shadow-glow z-40 hover:scale-105 transition-transform flex items-center gap-2 animate-slide-up"
          onClick={resumeAutoFollow}
        >
          ↓ Şimdiki satıra dön
        </button>
      )}

      {coachLine && (
        <PronunciationCoach
          expectedText={coachLine}
          onClose={() => setCoachLine(null)}
        />
      )}

      {showShadowing && (
        <ShadowingMode
          lyrics={lyrics.join("\n")}
          onClose={() => setShowShadowing(false)}
        />
      )}
    </div>
  );
});
