"use client";
import { memo, useEffect, useRef, useState } from "react";
import { api } from "../lib/api";
import { Home, Library, TrendingUp, Mic, Lock, Music } from "lucide-react";
import { Button } from "./ui/Button";

export default memo(function Sidebar({
  selectedPlaylistId,
  onPlaylistSelect,
  onHomeClick,
  onProgressClick,
  planName,
}) {
  const [playlists, setPlaylists] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [view, setView] = useState("library"); // "home" | "library" | "progress"
  const fetchedRef = useRef(false);

  useEffect(() => {
    if (fetchedRef.current) return;
    fetchedRef.current = true;
    setLoading(true);

    api
      .getPlaylists()
      .then((data) => setPlaylists(Array.isArray(data?.playlists) ? data.playlists : []))
      .catch((err) => setError(err.message || "Playlistler yüklenemedi."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <aside className="w-60 flex-shrink-0 h-screen bg-surface backdrop-blur-xl border-r border-border shadow-[4px_0_24px_rgba(0,0,0,0.2)] flex flex-col overflow-hidden transition-all">
      {/* Logo */}
      <div className="pt-6 pb-2 px-5 shrink-0">
        <span className="text-xl font-extrabold tracking-tight text-theme">
          Lingofy
        </span>
      </div>

      {/* Nav */}
      <nav className="p-3 flex flex-col gap-1 shrink-0">
        <button
          className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13px] font-semibold transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-theme
            ${view === "home" ? "bg-white/10 text-white" : "text-white/55 hover:text-white hover:bg-white/5"}`}
          onClick={() => {
            setView("home");
            onHomeClick?.();
          }}
          aria-current={view === "home" ? "page" : undefined}
        >
          <Home size={18} />
          Ana Sayfa
        </button>
        <button
          className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13px] font-semibold transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-theme
            ${view === "library" ? "bg-white/10 text-white" : "text-white/55 hover:text-white hover:bg-white/5"}`}
          onClick={() => setView("library")}
          aria-current={view === "library" ? "page" : undefined}
        >
          <Library size={18} />
          Kütüphane
        </button>

        <button
          className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13px] font-semibold transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-theme
            ${view === "progress" ? "bg-white/10 text-white" : "text-white/55 hover:text-white hover:bg-white/5"}`}
          onClick={() => {
            setView("progress");
            onProgressClick?.();
          }}
          aria-current={view === "progress" ? "page" : undefined}
        >
          <TrendingUp size={18} />
          Telaffuz Gelişimi
        </button>

        {/* Shadowing Mode - Premium Lock Example */}
        <button
          className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13px] font-semibold text-white/55 hover:text-white hover:bg-white/5 transition-all duration-200"
          onClick={() => {
            if (planName === "FREE") {
              window.location.href = "/pricing";
            } else {
              // Shadowing mode trigger if exists
            }
          }}
        >
          <Mic size={18} />
          <div className="flex items-center justify-between w-full">
            <span>Shadowing Mode</span>
            {planName === "FREE" && <Lock size={12} className="text-white/30" />}
          </div>
        </button>
      </nav>

      <div className="h-px bg-white/5 mx-4 my-2 shrink-0" />

      {/* Playlists */}
      <div className="px-5 py-2 shrink-0">
        <span className="text-[10px] font-bold text-white/30 uppercase tracking-[0.1em]">Playlistler</span>
      </div>

      <div className="flex-1 overflow-y-auto px-3 pb-4 custom-scrollbar">
        {loading && (
          <div className="flex justify-center py-6">
            <div className="w-5 h-5 border-2 border-white/10 border-t-theme rounded-full animate-spin" />
          </div>
        )}

        {error && !loading && <p className="text-xs text-red-400/80 px-2 m-0">{error}</p>}

        {!loading && !error && playlists.length === 0 && (
          <p className="text-xs text-white/30 px-2 m-0">Playlist bulunamadı.</p>
        )}

        {playlists.map((pl) => {
          const isActive = pl.id === selectedPlaylistId;
          return (
            <button
              key={pl.id}
              onClick={() => onPlaylistSelect?.(pl)}
              className={`flex items-center gap-3 w-full p-2 rounded-xl text-left transition-all duration-200 border-l-[3px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-theme
                ${isActive 
                  ? "bg-theme-100/10 border-theme text-white" 
                  : "border-transparent text-white/70 hover:bg-white/5 hover:text-white"
                }`}
              aria-current={isActive ? "page" : undefined}
              aria-label={`${pl.name} listesini aç`}
            >
              <div className="w-9 h-9 rounded-lg bg-white/10 flex items-center justify-center shrink-0 overflow-hidden shadow-sm">
                {pl.image ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={pl.image}
                    alt=""
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <Music size={16} className="text-white/30" />
                )}
              </div>
              <div className="min-w-0">
                <p className="m-0 text-[13px] font-medium truncate">
                  {pl.name}
                </p>
                <p className="m-0 mt-0.5 text-[11px] text-white/40">
                  {pl.track_count} şarkı
                </p>
              </div>
            </button>
          );
        })}
      </div>

      {/* PREMIUM CTA */}
      {(!planName || planName === "FREE") && (
        <div className="p-4 mt-auto shrink-0">
          <div 
            className="group relative bg-gradient-to-br from-theme-500/10 to-purple-500/10 border border-theme-500/20 rounded-2xl p-4 cursor-pointer hover:border-theme-500/40 transition-all duration-300 overflow-hidden"
            onClick={() => window.location.href = "/pricing"}
          >
            <div className="absolute inset-0 bg-theme-500/5 group-hover:bg-theme-500/10 transition-colors" />
            <div className="relative z-10">
              <div className="text-theme font-bold text-sm mb-1 flex items-center gap-1.5">
                Lingofy Premium
              </div>
              <div className="text-white/50 text-xs mb-3 leading-relaxed">
                Sınırsız öğrenme deneyimi için planını yükselt.
              </div>
              <Button variant="premium" size="sm" className="w-full font-bold shadow-glow">
                Yükselt
              </Button>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
});
