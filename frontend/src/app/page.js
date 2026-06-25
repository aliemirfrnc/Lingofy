"use client";
import { useCallback, useEffect, useRef, useState, useMemo } from "react";
import Chat from "../../components/Chat";
import DynamicBackground from "../../components/DynamicBackground";
import LandingPage from "../../components/LandingPage";
import LyricsPlayer from "../../components/LyricsPlayer";
import NowPlaying from "../../components/NowPlaying";
import PlaylistView from "../../components/PlaylistView";
import ProgressDashboard from "../../components/ProgressDashboard";
import Sidebar from "../../components/Sidebar";
import WordPanel from "../../components/WordPanel";
import { api } from "../../lib/api";

export default function Home() {
  const [authChecked, setAuthChecked] = useState(false);
  const [authEmail, setAuthEmail] = useState(null);
  const [planStatus, setPlanStatus] = useState(null);

  const [accentColor, setAccentColor] = useState({ r: 60, g: 60, b: 100 });
  const [albumImage, setAlbumImage] = useState(null);

  // Playlist state
  const [selectedPlaylist, setSelectedPlaylist] = useState(null);
  const [selectedTrack, setSelectedTrack] = useState(null);
  const [centerView, setCenterView] = useState("lyrics"); // "lyrics" | "playlist" | "progress"

  // NowPlaying state
  const [currentTrackName, setCurrentTrackName] = useState(null);
  const [currentArtist, setCurrentArtist] = useState(null);

  // Word panel state
  const [selectedWord, setSelectedWord] = useState(null);
  const [wordInfo, setWordInfo] = useState(null);
  const [wordLoading, setWordLoading] = useState(false);
  const [wordError, setWordError] = useState(null);
  const [lastContextLine, setLastContextLine] = useState("");
  const wordRequestRef = useRef(0);

  // Topbar Dropdown
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  // LyricsPlayer callbacks
  const trackChangeCallbackRef = useRef(null);
  const progressCallbackRef = useRef(null);
  const registerTrackChange = useCallback((cb) => {
    trackChangeCallbackRef.current = cb;
  }, []);
  const registerProgress = useCallback((cb) => {
    progressCallbackRef.current = cb;
  }, []);

  // Auth check & Plan fetch
  useEffect(() => {
    api.me()
      .then(async (data) => {
        if (data) {
          setAuthEmail(data.email);
          try {
            const planData = await api.getMyPlan();
            setPlanStatus(planData);
          } catch (e) {}
        }
      })
      .catch(() => {})
      .finally(() => setAuthChecked(true));
  }, []);

  const handleLogout = useCallback(() => {
    api.logout().catch(() => {});
    setAuthEmail(null);
    setPlanStatus(null);
  }, []);

  // Spotify → LyricsPlayer bridge
  const handleTrackChange = useCallback((trackName, artist) => {
    setCurrentTrackName(trackName);
    setCurrentArtist(artist);
    trackChangeCallbackRef.current?.(trackName, artist);
  }, []);

  const handleProgress = useCallback((progressMs, dur, isPlaying) => {
    progressCallbackRef.current?.(progressMs, dur, isPlaying);
  }, []);

  const handleTrackData = useCallback((trackData) => {
    setAlbumImage(trackData?.album_image ?? null);
  }, []);

  // Playlist → şarkı seç
  const handlePlaylistSelect = useCallback((playlist) => {
    setSelectedPlaylist(playlist);
    setCenterView("playlist");
    setSelectedTrack(null);
  }, []);

  const handleTrackSelect = useCallback((track) => {
    setSelectedTrack(track);
    setAlbumImage(track.album_image ?? null);
    trackChangeCallbackRef.current?.(track.name, track.artist);
    
    const uriToPlay = track.uri || `spotify:track:${track.id}`;
    api.playTrack(uriToPlay).catch(() => {});
    
    setCenterView("lyrics");
  }, []);

  // Word panel
  const handleWordClose = useCallback(() => {
    wordRequestRef.current += 1;
    setSelectedWord(null);
    setWordLoading(false);
  }, []);

  const handleWordClick = useCallback((rawWord, contextLine) => {
    const cleaned = rawWord.replace(/^[.,!?;:"'()[\]{}…—-]+|[.,!?;:"'()[\]{}…—-]+$/g, "");
    if (!cleaned) return;
    const reqId = ++wordRequestRef.current;

    setSelectedWord(cleaned);
    setLastContextLine(contextLine);
    setWordInfo(null);
    setWordError(null);
    setWordLoading(true);

    api.getWordInfo(cleaned, contextLine)
      .then((data) => {
        if (reqId === wordRequestRef.current) setWordInfo(data);
      })
      .catch((err) => {
        if (reqId === wordRequestRef.current) {
          if (err.status === 403) {
            setWordError("Günlük kelime sınırınıza ulaştınız. Sınırsız arama için Lingofy Premium'a geçin!");
          } else {
            setWordError(err.message || "Kelime bilgisi alınamadı.");
          }
        }
      })
      .finally(() => {
        if (reqId === wordRequestRef.current) setWordLoading(false);
      });
  }, []);

  // Derived Info
  const planName = planStatus?.plan?.name || "FREE";
  const planColor = planName === "MASTER" ? "text-purple-400" : planName === "PRO" ? "text-green-400" : "text-zinc-400";
  const planBadge = planName === "MASTER" ? "🟣 Master" : planName === "PRO" ? "🔵 Pro" : "🟢 Free";
  const avatarBadge = planName === "MASTER" ? "👑" : planName === "PRO" ? "PRO" : "";

  if (!authChecked) return <div style={{ minHeight: "100vh", background: "#0a0a0a" }} />;
  if (!authEmail) return <LandingPage onAuthenticated={(email) => {
    setAuthEmail(email);
    api.getMyPlan().then(setPlanStatus).catch(()=>{});
  }} />;

  return (
    <main className="relative min-h-screen overflow-hidden">
      <DynamicBackground albumImage={albumImage} onColorExtracted={setAccentColor} />

      <div className="relative z-10 flex h-screen">
        {/* SOL: Sidebar */}
        <Sidebar
          selectedPlaylistId={selectedPlaylist?.id}
          onPlaylistSelect={handlePlaylistSelect}
          onHomeClick={() => setCenterView("lyrics")}
          onProgressClick={() => setCenterView("progress")}
          planName={planName}
        />

        {/* ORTA: Lyrics veya Playlist */}
        <div className="flex-1 flex flex-col h-screen overflow-hidden pt-4 pr-3 pl-4 min-w-0">
          
          {/* TOPBAR */}
          <div className="flex items-center justify-between mb-4 flex-shrink-0 px-2">
            <span className="text-[15px] font-bold tracking-tight whitespace-nowrap text-theme shadow-glow">
              {centerView === "progress" 
                ? "Lingofy AI Coach"
                : centerView === "playlist" && selectedPlaylist
                ? selectedPlaylist.name
                : currentTrackName
                  ? `${currentTrackName}${currentArtist ? ` — ${currentArtist}` : ""}`
                  : "Lingofy"}
            </span>
            
            <div className="relative">
              <button 
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="flex items-center gap-3 hover:bg-white/10 p-1.5 pr-4 rounded-full transition-colors border border-transparent hover:border-white/5"
              >
                <div className="relative">
                  <div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center font-bold text-sm text-white">
                    {authEmail[0].toUpperCase()}
                  </div>
                  {avatarBadge && (
                    <div className="absolute -bottom-1 -right-1 bg-black text-[10px] px-1 py-0.5 rounded-md font-black shadow-md border border-white/10 z-10 text-white">
                      {avatarBadge}
                    </div>
                  )}
                </div>
                <div className="text-left hidden sm:block">
                  <div className="text-sm font-bold text-white leading-tight">{authEmail.split('@')[0]}</div>
                  <div className={`text-xs font-semibold ${planColor} leading-tight`}>{planBadge}</div>
                </div>
                <svg className={`w-4 h-4 text-zinc-400 transition-transform ${isDropdownOpen ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* DROPDOWN */}
              {isDropdownOpen && (
                <>
                  <div className="fixed inset-0 z-40" onClick={() => setIsDropdownOpen(false)}></div>
                  <div className="absolute right-0 mt-2 w-64 bg-zinc-900 border border-zinc-800 rounded-2xl shadow-2xl z-50 overflow-hidden animate-fade-in">
                    <div className="p-4 border-b border-zinc-800">
                      <div className="text-sm font-bold text-white mb-1">Mevcut Planınız</div>
                      <div className={`text-xl font-black ${planColor}`}>{planName}</div>
                      {planName === "FREE" && (
                        <div className="mt-2 text-xs text-zinc-400">Limitlere takılmadan devam etmek için yükseltin.</div>
                      )}
                    </div>
                    
                    <div className="p-2">
                      {planName === "FREE" && (
                        <button onClick={() => window.location.href = "/pricing"} className="w-full text-left px-4 py-2 hover:bg-zinc-800 rounded-xl text-sm font-bold text-green-400 flex items-center gap-2">
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z"/></svg>
                          Planı Yükselt
                        </button>
                      )}
                      <button onClick={() => window.location.href = "/account"} className="w-full text-left px-4 py-2 hover:bg-zinc-800 rounded-xl text-sm text-zinc-200">
                        Hesabım (Faturalar & Haklar)
                      </button>
                      <button className="w-full text-left px-4 py-2 hover:bg-zinc-800 rounded-xl text-sm text-zinc-200">
                        Ayarlar
                      </button>
                      <div className="h-px bg-zinc-800 my-2"></div>
                      <button onClick={handleLogout} className="w-full text-left px-4 py-2 hover:bg-red-500/10 text-red-400 rounded-xl text-sm">
                        Çıkış Yap
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>

          <NowPlaying
            onTrackChange={handleTrackChange}
            onProgress={handleProgress}
            onTrackData={handleTrackData}
          />

          <div className="flex-1 min-h-0 relative">
            {centerView === "progress" ? (
              <ProgressDashboard onClose={() => setCenterView("lyrics")} />
            ) : centerView === "playlist" && selectedPlaylist ? (
              <PlaylistView
                playlist={selectedPlaylist}
                onTrackSelect={handleTrackSelect}
                selectedTrackId={selectedTrack?.id}
                onClose={() => setCenterView("lyrics")}
              />
            ) : (
              <LyricsPlayer
                onWordClick={handleWordClick}
                onTrackChange={registerTrackChange}
                onProgress={registerProgress}
              />
            )}
          </div>
        </div>

        {/* SAĞ: Word panel veya Chat */}
        <div className="w-[300px] shrink-0 flex flex-col h-screen pt-4 pr-4 pb-5 pl-1 gap-0 overflow-hidden">
          {selectedWord ? (
            <>
              <WordPanel
                selectedWord={selectedWord}
                wordInfo={wordInfo}
                wordLoading={wordLoading}
                wordError={wordError}
                onRetry={() => handleWordClick(selectedWord, lastContextLine)}
                onClose={handleWordClose}
              />
              <div className="mt-3 flex-1 min-h-0">
                <Chat />
              </div>
            </>
          ) : (
            <Chat />
          )}
        </div>
      </div>
    </main>
  );
}
