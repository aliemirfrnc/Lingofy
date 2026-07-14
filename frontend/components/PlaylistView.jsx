"use client";
import { memo, useEffect, useRef, useState } from "react";
import { api } from "../lib/api";
import { ArrowLeft, Play, Music, Disc3 } from "lucide-react";

function msToMin(ms) {
  const m = Math.floor(ms / 60000);
  const s = Math.floor((ms % 60000) / 1000);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export default memo(function PlaylistView({
  playlist,
  onTrackSelect,
  selectedTrackId,
  onClose,
}) {
  const [tracks, setTracks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [playlistName, setPlaylistName] = useState(playlist?.name || "");
  const [hoveredTrackId, setHoveredTrackId] = useState(null);
  const loadedIdRef = useRef(null);

  useEffect(() => {
    if (!playlist?.id || playlist.id === loadedIdRef.current) return;
    loadedIdRef.current = playlist.id;
    setLoading(true);
    setError(null);
    setTracks([]);

    api
      .getPlaylistTracks(playlist.id)
      .then((data) => {
        setPlaylistName(playlist.name);
        setTracks(Array.isArray(data?.tracks) ? data.tracks : []);
      })
      .catch((err) => setError(err.message || "Şarkılar yüklenemedi."))
      .finally(() => setLoading(false));
  }, [playlist]);

  return (
    <div className="h-full flex flex-col overflow-hidden animate-slide-up">
      {/* Header */}
      <div className="p-5 pb-4 shrink-0 flex items-center gap-4">
        <button 
          className="w-8 h-8 rounded-full bg-white/5 border border-white/10 text-white/70 flex items-center justify-center hover:bg-white/10 transition-colors cursor-pointer shrink-0" 
          onClick={onClose} 
          aria-label="Geri"
        >
          <ArrowLeft size={16} />
        </button>
        <div className="flex items-center gap-3 min-w-0">
          {playlist?.image && (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={playlist.image}
              alt=""
              className="w-12 h-12 rounded-lg object-cover shrink-0 shadow-md"
            />
          )}
          <div className="min-w-0">
            <p className="m-0 text-[10px] text-white/40 font-bold tracking-widest uppercase mb-0.5">
              PLAYLIST
            </p>
            <p className="m-0 text-lg font-bold text-white truncate shadow-glow">
              {playlistName}
            </p>
          </div>
        </div>
      </div>

      <div className="h-px mx-5 mb-2 shrink-0 bg-theme-500/20" />

      {/* Track listesi */}
      {loading && (
        <div className="flex-1 overflow-y-auto px-3 pb-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="flex items-center gap-3 w-full p-2 rounded-xl mb-1">
              <div className="w-6 shrink-0 flex items-center justify-center">
                <span className="text-xs text-white/20 tabular-nums">{i + 1}</span>
              </div>
              <div className="w-10 h-10 rounded-md bg-white/5 animate-pulse shrink-0" />
              <div className="flex-1 flex flex-col gap-2 pl-1">
                <div className="h-2.5 w-1/2 bg-white/10 rounded animate-pulse" />
                <div className="h-2 w-1/3 bg-white/5 rounded animate-pulse" />
              </div>
            </div>
          ))}
        </div>
      )}

      {error && !loading && (
        <div className="flex justify-center py-10">
          <p className="text-xs text-red-400/80 m-0">{error}</p>
        </div>
      )}

      {!loading && !error && (
        <div className="flex-1 overflow-y-auto px-3 pb-4 custom-scrollbar">
          {tracks.map((track, i) => {
            const isActive = track.id === selectedTrackId;
            const isHovered = hoveredTrackId === track.id;
            
            return (
              <button
                key={track.id}
                onMouseEnter={() => setHoveredTrackId(track.id)}
                onMouseLeave={() => setHoveredTrackId(null)}
                className={`flex items-center gap-3 w-full p-2 rounded-xl text-left transition-all duration-200 group mb-1
                  ${isActive ? "bg-theme-100/15" : isHovered ? "bg-white/5" : "bg-transparent"}
                `}
                onClick={() => onTrackSelect?.(track)}
              >
                {/* Numara / aktif gösterge */}
                <div className="w-6 shrink-0 flex items-center justify-center">
                  {isActive ? (
                    <Play size={12} className="text-theme fill-theme" />
                  ) : isHovered ? (
                    <Play size={12} className="text-white/70 fill-white/70" />
                  ) : (
                    <span className={`text-xs tabular-nums ${isActive ? "text-theme" : "text-white/30"}`}>
                      {i + 1}
                    </span>
                  )}
                </div>

                {/* Albüm kapak */}
                <div className="w-10 h-10 rounded-md bg-white/5 flex items-center justify-center shrink-0 overflow-hidden shadow-sm">
                  {track.album_image ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={track.album_image}
                      alt=""
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <Music size={16} className="text-white/20" />
                  )}
                </div>

                {/* Şarkı bilgisi */}
                <div className="flex-1 min-w-0 pr-2">
                  <p className={`m-0 text-[13px] font-medium truncate transition-colors duration-200
                    ${isActive ? "text-theme-100" : "text-white group-hover:text-white"}`}
                  >
                    {track.name}
                  </p>
                  <p className="m-0 mt-0.5 text-[11px] text-white/40 truncate group-hover:text-white/60 transition-colors">
                    {track.artist}
                  </p>
                </div>

                {/* Süre */}
                <span className="text-[11px] text-white/30 shrink-0 pr-2 font-medium tabular-nums group-hover:text-white/50 transition-colors">
                  {msToMin(track.duration_ms)}
                </span>
              </button>
            );
          })}

          {tracks.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 px-5 opacity-80">
              <Disc3 size={48} className="text-white/20 mb-4" />
              <p className="m-0 mb-2 text-base font-semibold text-white">Bu playlist boş</p>
              <p className="m-0 text-[13px] text-white/50 text-center">Şu anda görüntülenecek şarkı bulunmuyor.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
});

