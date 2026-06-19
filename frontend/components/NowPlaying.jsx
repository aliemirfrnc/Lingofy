import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../lib/api";

export default function NowPlaying({ onTrackChange, onProgress }) {
  const [sessionId, setSessionId] = useState(null);
  const [track, setTrack] = useState(null);
  const [error, setError] = useState(null);
  const lastTrackKey = useRef(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const fromUrl = params.get("spotify_session");
    if (fromUrl) {
      localStorage.setItem("spotify_session", fromUrl);
      window.history.replaceState({}, "", window.location.pathname);
    }
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setSessionId(fromUrl || localStorage.getItem("spotify_session"));
  }, []);

  const fetchTrack = useCallback(() => {
    if (!sessionId) return;
    api
      .getCurrentTrack(sessionId)
      .then((data) => {
        setTrack(data);
        setError(null);

        if (data.is_playing && data.track_name) {
          const key = `${data.track_name}::${data.artist}`;
          if (key !== lastTrackKey.current) {
            lastTrackKey.current = key;
            onTrackChange?.(data.track_name, data.artist);
          }
        }

        onProgress?.(data.progress_ms, data.duration_ms, data.is_playing);
      })
      .catch((err) => {
        if (err.message.includes("401")) {
          localStorage.removeItem("spotify_session");
          setSessionId(null);
          setTrack(null);
        } else {
          setError("Spotify verisi alınamadı.");
        }
      });
  }, [sessionId, onTrackChange, onProgress]);

  useEffect(() => {
    if (!sessionId) return;
    fetchTrack();
    const interval = setInterval(fetchTrack, 2000);
    return () => clearInterval(interval);
  }, [sessionId, fetchTrack]);

  const handleConnect = () => {
    window.location.href = api.spotifyLoginUrl();
  };

  const handlePlayPause = () => {
    const action = track?.is_playing ? api.spotifyPause : api.spotifyPlay;
    action(sessionId)
      .then(fetchTrack)
      .catch(() =>
        setError("Komut gönderilemedi. Aktif bir Spotify cihazı açık mı?"),
      );
  };

  const handleNext = () => {
    api
      .spotifyNext(sessionId)
      .then(() => setTimeout(fetchTrack, 500))
      .catch(() => setError("Sıradaki şarkıya geçilemedi."));
  };

  const handlePrevious = () => {
    api
      .spotifyPrevious(sessionId)
      .then(() => setTimeout(fetchTrack, 500))
      .catch(() => setError("Önceki şarkıya geçilemedi."));
  };

  if (!sessionId) {
    return (
      <div style={cardStyle}>
        <p
          style={{
            color: "#4A1B0C",
            fontSize: 14,
            margin: "0 0 10px",
            fontFamily: "var(--font-serif, serif)",
          }}
        >
          Spotify hesabını bağla
        </p>
        <button onClick={handleConnect} style={connectBtnStyle}>
          Spotify’a bağlan
        </button>
      </div>
    );
  }

  const progressPct =
    track?.progress_ms && track?.duration_ms
      ? Math.min(100, (track.progress_ms / track.duration_ms) * 100)
      : 0;

  return (
    <div style={cardStyle}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          marginBottom: 10,
        }}
      >
        <div style={coverStyle}>
          {track?.album_image ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={track.album_image}
              alt=""
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                borderRadius: 6,
              }}
            />
          ) : (
            <span style={{ fontSize: 18, color: "#b0a89a" }}>♪</span>
          )}
        </div>
        <div style={{ minWidth: 0 }}>
          <p style={titleStyle}>
            {track?.track_name ||
              (error ? "Veri alınamadı" : "Bir şey çalmıyor")}
          </p>
          <p style={subtitleStyle}>{track?.artist || "—"}</p>
        </div>
      </div>

      <div
        style={{
          height: 3,
          background: "#e8ddc8",
          borderRadius: 2,
          overflow: "hidden",
          marginBottom: 10,
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${progressPct}%`,
            background: "#D85A30",
          }}
        />
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 20,
        }}
      >
        <button onClick={handlePrevious} style={iconBtnStyle}>
          ⏮
        </button>
        <button onClick={handlePlayPause} style={playBtnStyle}>
          {track?.is_playing ? "⏸" : "▶"}
        </button>
        <button onClick={handleNext} style={iconBtnStyle}>
          ⏭
        </button>
      </div>

      {error && (
        <p
          style={{
            color: "#D85A30",
            fontSize: 11,
            textAlign: "center",
            marginTop: 8,
          }}
        >
          {error}
        </p>
      )}
    </div>
  );
}

const cardStyle = {
  background: "#fff",
  border: "0.5px solid #e8ddc8",
  borderRadius: 12,
  padding: 14,
  marginBottom: 32,
  textAlign: "center",
};

const coverStyle = {
  width: 44,
  height: 44,
  borderRadius: 6,
  background: "#f0e6d2",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  flexShrink: 0,
  overflow: "hidden",
};

const titleStyle = {
  color: "#4A1B0C",
  fontSize: 14,
  fontWeight: 500,
  margin: 0,
  fontFamily: "var(--font-serif, serif)",
  whiteSpace: "nowrap",
  overflow: "hidden",
  textOverflow: "ellipsis",
  textAlign: "left",
};

const subtitleStyle = {
  color: "#9c8f7a",
  fontSize: 12,
  margin: 0,
  textAlign: "left",
};

const connectBtnStyle = {
  padding: "10px 20px",
  borderRadius: 8,
  border: "none",
  background: "#D85A30",
  color: "#fff",
  cursor: "pointer",
  fontWeight: 500,
  fontSize: 14,
};

const iconBtnStyle = {
  background: "none",
  border: "none",
  color: "#9c8f7a",
  fontSize: 16,
  cursor: "pointer",
  padding: 0,
};

const playBtnStyle = {
  width: 30,
  height: 30,
  borderRadius: "50%",
  background: "#D85A30",
  border: "none",
  color: "#fff",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  cursor: "pointer",
};
