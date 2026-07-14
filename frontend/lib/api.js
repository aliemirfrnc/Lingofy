const BASE_URL = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");

// We no longer use localStorage for tokens. Tokens are HttpOnly cookies.

function authHeaders() {
  return {}; // Handled by cookies
}

async function handleResponse(res) {
  if (!res.ok) {
    let detail = "";
    try {
      const data = await res.json();
      detail = data.detail || "";
      if (data.detail && typeof data.detail === "object") {
         detail = data.detail.message || JSON.stringify(data.detail);
      }
    } catch {
      // yanıt JSON değilse sessizce geç
    }
    const err = new Error(detail || `İstek başarısız oldu (${res.status}).`);
    err.status = res.status;
    err.data = detail;
    throw err;
  }
  if (res.status === 204) return null;
  return res.json();
}

const lyricsCache = new Map();

function fetchWithTimeout(url, options, timeout = 10000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  
  if (options.signal) {
    options.signal.addEventListener('abort', () => {
      clearTimeout(id);
      controller.abort(options.signal.reason);
    });
  }

  return fetch(url, { ...options, signal: controller.signal })
    .then((response) => {
      clearTimeout(id);
      return response;
    })
    .catch((error) => {
      clearTimeout(id);
      if (error.name === "AbortError") {
        if (options.signal && options.signal.aborted) {
          throw error;
        }
        const err = new Error("İstek zaman aşımına uğradı.");
        err.name = "TimeoutError";
        err.status = 408;
        throw err;
      }
      // If it's a TypeError (Network error like CORS or offline)
      if (error.name === "TypeError") {
        error.isNetworkError = true;
      }
      throw error;
    });
}

async function request(path, options = {}) {
  if (!BASE_URL) {
    throw new Error(
      "API adresi yapılandırılmamış. NEXT_PUBLIC_API_URL değerini kontrol et.",
    );
  }
  options.credentials = options.credentials || "include";
  try {
    return await fetchWithTimeout(`${BASE_URL}${path}`, options, options.timeout || 10000);
  } catch (error) {
    if (error?.name === "AbortError") throw error;
    if (error?.name === "TimeoutError") throw error;
    if (error?.isNetworkError) {
      const err = new Error("Sunucuya ulaşılamadı (CORS veya Bağlantı Hatası).");
      err.status = 0; // 0 indicates network error
      throw err;
    }
    throw error;
  }
}

let refreshPromise = null;

async function refreshAccessToken() {
  if (!refreshPromise) {
    refreshPromise = request("/auth/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    })
      .then(handleResponse)
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

export async function authFetch(path, options = {}, retried = false) {
  const res = await request(path, options);
  
  if (res.status === 401 && !retried) {
    try {
      await refreshAccessToken();
    } catch {
      throw new Error("Oturum süresi dolmuş, tekrar giriş yap.");
    }
    return authFetch(path, options, true);
  }
  return handleResponse(res);
}

export const api = {
  // ── Auth ──────────────────────────────────────────────────────────────────
  async register(email, password) {
    const res = await request("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    return handleResponse(res);
  },

  async login(email, password) {
    const res = await request("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    return handleResponse(res);
  },

  async me() {
    return authFetch("/auth/me");
  },

  async logout() {
    try {
      await authFetch("/auth/logout", {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
    } catch {
      // oturum zaten geçersiz olabilir
    }
    return { status: "ok" };
  },
  
  async logoutAll() {
    try {
      await authFetch("/auth/logout-all", {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
    } catch {}
    return { status: "ok" };
  },

  // ── Subscriptions ──────────────────────────────────────────────────────────
  async getMyPlan() {
    return authFetch("/api/subscriptions/my-plan");
  },
  
  async upgradePlan(planName) {
    return authFetch("/api/subscriptions/upgrade", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ plan_name: planName }),
    });
  },

  async getLyrics(track, artist = "", options = {}) {
    const key = `${track}::${artist}`.toLowerCase();
    if (lyricsCache.has(key)) {
      return lyricsCache.get(key);
    }
    
    const params = new URLSearchParams({ track, artist });
    
    const fetchAttempt = async (retries = 1) => {
      try {
        const res = await request(`/lyrics?${params}`, { ...options, timeout: 8000 });
        const data = await handleResponse(res);
        if (lyricsCache.size >= 50) {
          const firstKey = lyricsCache.keys().next().value;
          lyricsCache.delete(firstKey);
        }
        lyricsCache.set(key, data);
        return data;
      } catch (err) {
        if (err?.name === "AbortError" || retries === 0) throw err;
        await new Promise((r) => setTimeout(r, 600));
        return fetchAttempt(retries - 1);
      }
    };
    
    return fetchAttempt();
  },

  async translateLine(text, trackId = null, options = {}) {
    return authFetch("/translate-line", {
      ...options,
      method: "POST",
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      body: JSON.stringify({ text, track_id: trackId }),
    });
  },

  async updateSettings(settings) {
    const res = await authFetch("/auth/settings", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settings),
    });
    return res;
  },

  async streamChat(message, retried = false) {
    const res = await request("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    if (res.status === 401 && !retried) {
      try {
        await refreshAccessToken();
      } catch {
        throw new Error("Oturum süresi dolmuş, tekrar giriş yap.");
      }
      return this.streamChat(message, true);
    }
    if (!res.ok) {
      throw new Error(`Sunucu hatası: ${res.status}`);
    }
    return res;
  },

  async translateBatch(lines, trackId = null, options = {}) {
    return authFetch("/translate-batch", {
      ...options,
      method: "POST",
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      body: JSON.stringify({ lines, track_id: trackId }),
    });
  },

  // ── Chat & Word Info ──────────────────────────────────────────────────────
  async chat(message) {
    return authFetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
      timeout: 30000,
    });
  },

  async getWordInfo(word, contextLine = "") {
    return authFetch("/api/word-info", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ word, context_line: contextLine }),
      timeout: 30000,
    });
  },

  // ── Spotify ───────────────────────────────────────────────────────────────
  async spotifyConnectUrl() {
    const data = await authFetch("/spotify/connect-token");
    return `${BASE_URL}/spotify/login?token=${encodeURIComponent(data.connect_token)}`;
  },

  async spotifyStatus() {
    return authFetch("/spotify/status");
  },

  async getCurrentTrack() {
    return authFetch("/spotify/current-track");
  },

  async getQueue() {
    return authFetch("/spotify/queue");
  },

  async spotifyPlay() {
    return authFetch("/spotify/play", { method: "PUT" });
  },

  async spotifyPause() {
    return authFetch("/spotify/pause", { method: "PUT" });
  },

  async spotifyNext() {
    return authFetch("/spotify/next", { method: "POST" });
  },

  async spotifyPrevious() {
    return authFetch("/spotify/previous", { method: "POST" });
  },

  // ── Playlists ─────────────────────────────────────────────────────────────
  async getPlaylists() {
    return authFetch("/spotify/playlists");
  },

  async getPlaylistTracks(playlistId) {
    return authFetch(`/spotify/playlist/${playlistId}`);
  },

  async playTrack(trackUri) {
    return authFetch("/spotify/play-track", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ uri: trackUri }),
    });
  },

  // ── Pronunciation & Progress ──────────────────────────────────────────────
  async analyzePronunciation(audioBlob, expectedText) {
    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.webm");
    formData.append("expected_text", expectedText);

    return authFetch("/api/pronunciation/analyze", {
      method: "POST",
      body: formData,
      timeout: 60000,
    });
  },

  async getProgressStats() {
    return authFetch("/api/progress/stats");
  },
};
