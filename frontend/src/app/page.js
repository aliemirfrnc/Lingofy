"use client";
import { useEffect, useState } from "react";
import { api } from "../../lib/api";

export default function Home() {
  const [lyrics, setLyrics] = useState([]);
  const [translation, setTranslation] = useState({});
  const [selectedLine, setSelectedLine] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .getLyrics("test")
      .then((data) => setLyrics(data.lyrics))
      .catch(() => setError("Şarkı sözleri yüklenemedi."))
      .finally(() => setLoading(false));
  }, []);

  const translateLine = (line) => {
    if (translation[line]) return;
    api
      .translateLine(line)
      .then((data) =>
        setTranslation((prev) => ({ ...prev, [line]: data.translation })),
      )
      .catch(() => {});
  };

  if (loading)
    return (
      <main className="page">
        <p style={{ color: "#fff", margin: "auto" }}>Yükleniyor...</p>
      </main>
    );
  if (error)
    return (
      <main className="page">
        <p style={{ color: "#f55", margin: "auto" }}>{error}</p>
      </main>
    );

  return (
    <main className="page">
      <div className="lyrics-container">
        <h1>Lyringo 🎧</h1>

        {lyrics.map((line, i) => (
          <div className="line-group" key={i}>
            <p
              className={`lyric-line ${selectedLine === i ? "selected" : ""}`}
              onClick={() => {
                setSelectedLine(i);
                translateLine(line);
              }}
            >
              {line}
            </p>
            {translation[line] && (
              <p className="translation">{translation[line]}</p>
            )}
          </div>
        ))}
      </div>

      <style jsx>{`
        .page {
          min-height: 100vh;
          display: flex;
          background: #000;
          color: #fff;
          padding: 0 20px 60px;
        }
        .lyrics-container {
          width: 100%;
          max-width: 600px;
          margin: 100px auto 0;
          text-align: center;
        }
        h1 {
          margin: 0 0 48px;
        }
        .line-group {
          margin-bottom: 30px;
        }
        .lyric-line {
          margin: 0;
          padding: 10px 16px;
          border-radius: 12px;
          color: #777;
          font-size: 16px;
          line-height: 1.6;
          opacity: 0.5;
          cursor: pointer;
          transition:
            background-color 180ms ease,
            color 180ms ease,
            font-size 180ms ease,
            opacity 180ms ease,
            transform 180ms ease;
        }
        .lyric-line:hover {
          color: #bbb;
          opacity: 0.85;
          transform: scale(1.01);
        }
        .lyric-line:active {
          transform: scale(0.99);
        }
        .lyric-line.selected {
          background: rgba(255, 255, 255, 0.08);
          color: #fff;
          font-size: 22px;
          opacity: 1;
        }
        .translation {
          margin: 10px 16px 0;
          color: #aaa;
          font-size: 14px;
          font-style: italic;
          line-height: 1.5;
        }
      `}</style>
    </main>
  );
}
