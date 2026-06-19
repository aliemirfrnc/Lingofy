const BASE_URL = process.env.NEXT_PUBLIC_API_URL;

export const api = {
  async translateLine(text) {
    const res = await fetch(`${BASE_URL}/translate-line`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) throw new Error(`translate failed: ${res.status}`);
    return res.json();
  },

  async chat(message) {
    const res = await fetch(`${BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    if (!res.ok) throw new Error(`chat failed: ${res.status}`);
    return res.json();
  },

  async getLyrics(track, artist = "") {
    const params = new URLSearchParams({ track, artist });
    const res = await fetch(`${BASE_URL}/lyrics?${params}`);
    if (!res.ok) throw new Error(`lyrics failed: ${res.status}`);
    return res.json();
  },

  spotifyLoginUrl() {
    return `${BASE_URL}/spotify/login`;
  },

  async getCurrentTrack(sessionId) {
    const res = await fetch(
      `${BASE_URL}/spotify/current-track?session_id=${sessionId}`,
    );
    if (!res.ok) throw new Error(`current-track failed: ${res.status}`);
    return res.json();
  },

  async spotifyPlay(sessionId) {
    const res = await fetch(
      `${BASE_URL}/spotify/play?session_id=${sessionId}`,
      {
        method: "PUT",
      },
    );
    if (!res.ok) throw new Error(`play failed: ${res.status}`);
    return res.json();
  },

  async spotifyPause(sessionId) {
    const res = await fetch(
      `${BASE_URL}/spotify/pause?session_id=${sessionId}`,
      {
        method: "PUT",
      },
    );
    if (!res.ok) throw new Error(`pause failed: ${res.status}`);
    return res.json();
  },

  async spotifyNext(sessionId) {
    const res = await fetch(
      `${BASE_URL}/spotify/next?session_id=${sessionId}`,
      {
        method: "POST",
      },
    );
    if (!res.ok) throw new Error(`next failed: ${res.status}`);
    return res.json();
  },

  async spotifyPrevious(sessionId) {
    const res = await fetch(
      `${BASE_URL}/spotify/previous?session_id=${sessionId}`,
      {
        method: "POST",
      },
    );
    if (!res.ok) throw new Error(`previous failed: ${res.status}`);
    return res.json();
  },
};
