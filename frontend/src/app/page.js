"use client";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Chat from "../../components/Chat";
import NowPlaying from "../../components/NowPlaying";
import { api } from "../../lib/api";

export default function Home() {
  const [lyrics, setLyrics] = useState([]);
  const [synced, setSynced] = useState(null);
  const [translation, setTranslation] = useState({});
  const [selectedLine, setSelectedLine] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [playback, setPlayback] = useState({ progressMs: 0, isPlaying: false });

  const lineRefs = useRef([]);

  const loadLyrics = useCallback((track, artist = "") => {
    setLoading(true);
    setError(null);
    setTranslation({});
    setSelectedLine(null);
    setSynced(null);

    api
      .getLyrics(track, artist)
      .then((data) => {
        setLyrics(data.lyrics);
        setSynced(data.synced && data.synced.length > 0 ? data.synced : null);
      })
      .catch(() => setError("Şarkı sözleri yüklenemedi."))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadLyrics("test");
  }, [loadLyrics]);

  const handleTrackChange = useCallback(
    (trackName, artist) => {
      setPlayback({ progressMs: 0, isPlaying: false });
      loadLyrics(trackName, artist);
    },
    [loadLyrics],
  );

  const handleProgress = useCallback((progressMs, durationMs, isPlaying) => {
    setPlayback({ progressMs: progressMs ?? 0, isPlaying: !!isPlaying });
  }, []);

  // Spotify her 2 saniyede bir gerçek progress veriyor; aradaki saniyeleri yerel olarak ilerletiyoruz.
  useEffect(() => {
    if (!playback.isPlaying) return;
    const id = setInterval(() => {
      setPlayback((p) => ({ ...p, progressMs: p.progressMs + 1000 }));
    }, 1000);
    return () => clearInterval(id);
  }, [playback.isPlaying]);

  const currentLineIndex = useMemo(() => {
    if (!synced || synced.length === 0) return null;
    const progressSec = playback.progressMs / 1000;
    let idx = -1;
    for (let i = 0; i < synced.length; i++) {
      if (synced[i].time <= progressSec) idx = i;
      else break;
    }
    return idx >= 0 ? idx : null;
  }, [synced, playback.progressMs]);

  useEffect(() => {
    if (currentLineIndex === null) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setSelectedLine((prev) =>
      prev === currentLineIndex ? prev : currentLineIndex,
    );
  }, [currentLineIndex]);

  const translateLine = useCallback((line) => {
    if (!line) return;
    setTranslation((prev) => {
      if (prev[line]) return prev;
      api
        .translateLine(line)
        .then((data) =>
          setTranslation((p) => ({ ...p, [line]: data.translation })),
        )
        .catch(() => {});
      return prev;
    });
  }, []);

  // Mevcut satırı çevir, bir sonraki satırı da arka planda önceden çek —
  // satır değiştiğinde çeviri zaten hazır olsun.
  useEffect(() => {
    if (selectedLine === null) return;

    const line = lyrics[selectedLine];
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (line) translateLine(line);

    const nextLine = lyrics[selectedLine + 1];
     
    if (nextLine) translateLine(nextLine);

    const el = lineRefs.current[selectedLine];
    if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
  }, [selectedLine, lyrics, translateLine]);

  return (
    <main className="page">
      <div className="content">
        <h1>Lingofy 🎧</h1>

        <NowPlaying
          onTrackChange={handleTrackChange}
          onProgress={handleProgress}
        />

        {loading ? (
          <p style={{ color: "#4A1B0C", textAlign: "center" }}>Yükleniyor...</p>
        ) : error ? (
          <p style={{ color: "#D85A30", textAlign: "center" }}>{error}</p>
        ) : (
          <div className="lyrics-container">
            {lyrics.map((line, i) => (
              <div className="line-group" key={i}>
                <p
                  ref={(el) => (lineRefs.current[i] = el)}
                  className={`lyric-line ${selectedLine === i ? "selected" : ""}`}
                  onClick={() => setSelectedLine(i)}
                >
                  {line}
                </p>
                {translation[line] && (
                  <p className="translation">{translation[line]}</p>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="chat-container">
          <Chat />
        </div>
      </div>

      <style jsx>{`
        .page {
          min-height: 100vh;
          display: flex;
          background: #faf6ee;
          padding: 0 20px 60px;
        }
        .content {
          width: 100%;
          max-width: 560px;
          margin: 60px auto 0;
        }
        h1 {
          margin: 0 0 24px;
          text-align: center;
          color: #4a1b0c;
          font-family: var(--font-serif, serif);
          font-weight: 500;
        }
        .lyrics-container {
          text-align: center;
          margin-bottom: 40px;
        }
        .line-group {
          margin-bottom: 24px;
        }
        .lyric-line {
          margin: 0;
          padding: 10px 16px;
          border-radius: 10px;
          color: #b0a89a;
          font-size: 16px;
          line-height: 1.6;
          font-family: var(--font-serif, serif);
          cursor: pointer;
          transition:
            background-color 180ms ease,
            color 180ms ease,
            font-size 180ms ease,
            transform 180ms ease;
        }
        .lyric-line:hover {
          color: #8a7c63;
          transform: scale(1.01);
        }
        .lyric-line:active {
          transform: scale(0.99);
        }
        .lyric-line.selected {
          background: #f5c4b3;
          color: #4a1b0c;
          font-size: 22px;
        }
        .translation {
          margin: 8px 16px 0;
          color: #712b13;
          font-size: 14px;
          font-style: italic;
          line-height: 1.5;
        }
      `}</style>
    </main>
  );
}
