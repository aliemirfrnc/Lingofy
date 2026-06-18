"use client";
import { useEffect, useState } from "react";

export default function LyricsPage() {
  const [lyrics, setLyrics] = useState([]);
  const [translation, setTranslation] = useState({});
  const [selectedLine, setSelectedLine] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/lyrics?song=test")
      .then((res) => res.json())
      .then((data) => setLyrics(data.lyrics));
  }, []);

  const translateLine = (line) => {
    setSelectedLine(line);

    fetch("http://127.0.0.1:8000/translate-line", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: line }),
    })
      .then((res) => res.json())
      .then((data) =>
        setTranslation((prev) => ({
          ...prev,
          [line]: data.translation,
        })),
      );
  };

  return (
    <div
      style={{
        maxWidth: 600,
        margin: "100px auto",
        textAlign: "center",
        color: "white",
      }}
    >
      <h1>Lyringo 🎧</h1>

      {lyrics.map((line, i) => {
        const isActive = selectedLine === line;

        return (
          <div key={i} style={{ marginBottom: 30 }}>
            <p
              onClick={() => translateLine(line)}
              style={{
                cursor: "pointer",
                fontSize: isActive ? 22 : 16,
                color: isActive ? "white" : "#777",
                transition: "all 0.2s ease",
              }}
            >
              {line}
            </p>

            {translation[line] && (
              <p
                style={{
                  fontSize: 14,
                  color: "#aaa",
                  fontStyle: "italic",
                }}
              >
                {translation[line]}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}
