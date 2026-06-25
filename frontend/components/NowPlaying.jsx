"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../lib/api";
import { Play, Pause, SkipBack, SkipForward, Music } from "lucide-react";
import { Button } from "./ui/Button";

export default function NowPlaying({
  onTrackChange,
  onProgress,
  onTrackData,
}) {
  const [connected, setConnected] = useState(null);
  const [track, setTrack] = useState(null);
  const [error, setError] = useState(null);
  const lastTrackKey = useRef(null);
  const fetchInFlightRef = useRef(false);

  const checkStatus = useCallback(() => {
    api
      .spotifyStatus()
      .then((data) => setConnected(data.connected))
      .catch(() => setConnected(false));
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("spotify_connected")) {
      window.history.replaceState({}, "", window.location.pathname);
    }
    checkStatus();
  }, [checkStatus]);

  const prefetchNext = useCallback(() => {
    api
      .getQueue()
      .then((q) => {
        if (q.track_name)
          api.getLyrics(q.track_name, q.artist || "").catch(() => {});
      })
      .catch(() => {});
  }, []);

  const fetchTrack = useCallback(() => {
    if (!connected || fetchInFlightRef.current) return;
    fetchInFlightRef.current = true;
    api
      .getCurrentTrack()
      .then((data) => {
        setTrack(data);
        setError(null);
        onTrackData?.(data);
        if (data?.track_name) {
          const key = `${data.track_name}::${data.artist}`;
          if (key !== lastTrackKey.current) {
            lastTrackKey.current = key;
            onTrackChange?.(data.track_name, data.artist);
            prefetchNext();
          }
        }
        onProgress?.(data?.progress_ms, data?.duration_ms, data?.is_playing);
      })
      .catch((err) => {
        if (err.status === 401 || err.status === 404) {
          setConnected(false);
          setTrack(null);
          onTrackData?.(null);
        } else {
          setError(err.message || "Spotify verisi alınamadı.");
        }
      })
      .finally(() => {
        fetchInFlightRef.current = false;
      });
  }, [connected, onTrackChange, onProgress, onTrackData, prefetchNext]);

  useEffect(() => {
    if (!connected) return;
    fetchTrack();
    const interval = setInterval(fetchTrack, 2000);
    return () => clearInterval(interval);
  }, [connected, fetchTrack]);

  const handleConnect = () => {
    api
      .spotifyConnectUrl()
      .then((url) => {
        window.location.href = url;
      })
      .catch((err) => setError(err.message || "Bağlantı başlatılamadı."));
  };

  const handlePlayPause = () => {
    const action = track?.is_playing ? api.spotifyPause : api.spotifyPlay;
    action()
      .then(fetchTrack)
      .catch((err) => setError(err.message || "Komut başarısız."));
  };

  const handleNext = () => {
    api
      .spotifyNext()
      .then(() => setTimeout(fetchTrack, 500))
      .catch((err) => setError(err.message || "Sıradaki şarkıya geçilemedi."));
  };

  const handlePrevious = () => {
    api
      .spotifyPrevious()
      .then(() => setTimeout(fetchTrack, 500))
      .catch((err) => setError(err.message || "Önceki şarkıya geçilemedi."));
  };

  if (connected === null) return <div className="h-20 shrink-0" />;

  if (!connected) {
    return (
      <div className="bg-white/5 border border-white/10 rounded-2xl p-5 text-center mb-4 shrink-0 animate-fade-in shadow-sm">
        <p className="text-white/60 text-[13px] mb-3">Spotify ile bağlan</p>
        <Button onClick={handleConnect} variant="primary" className="rounded-full shadow-glow">
          Bağlan
        </Button>
        {error && <p className="text-red-400 text-[11px] text-center mt-2">{error}</p>}
      </div>
    );
  }

  const progressPct =
    track?.progress_ms && track?.duration_ms
      ? Math.min(100, (track.progress_ms / track.duration_ms) * 100)
      : 0;

  return (
    <div className="glass-panel p-3 mb-4 shrink-0 animate-fade-in overflow-hidden">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-11 h-11 rounded-lg bg-white/10 flex items-center justify-center shrink-0 overflow-hidden shadow-sm">
          {track?.album_image ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={track.album_image}
              alt=""
              className="w-full h-full object-cover"
              crossOrigin="anonymous"
            />
          ) : (
            <Music className="text-white/30" size={20} />
          )}
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-[14px] font-semibold text-white m-0 truncate">
            {track?.track_name || "—"}
          </p>
          <p className="text-[12px] text-white/50 m-0 mt-0.5 truncate">
            {track?.artist || "—"}
          </p>
        </div>
      </div>

      <div className="h-1 bg-white/10 rounded-full mb-3 overflow-hidden">
        <div
          className="h-full rounded-full bg-theme transition-all duration-1000 ease-linear shadow-glow"
          style={{ width: `${progressPct}%` }}
        />
      </div>

      <div className="flex items-center justify-center gap-5">
        <button onClick={handlePrevious} className="text-white/60 hover:text-white transition-colors">
          <SkipBack size={20} className="fill-current" />
        </button>
        <button
          onClick={handlePlayPause}
          className="w-9 h-9 rounded-full bg-white text-black flex items-center justify-center hover:scale-105 transition-transform shadow-lg"
        >
          {track?.is_playing ? <Pause size={18} className="fill-current" /> : <Play size={18} className="fill-current ml-1" />}
        </button>
        <button onClick={handleNext} className="text-white/60 hover:text-white transition-colors">
          <SkipForward size={20} className="fill-current" />
        </button>
      </div>

      {error && <p className="text-red-400/80 text-[11px] text-center mt-2 m-0">{error}</p>}
    </div>
  );
}
