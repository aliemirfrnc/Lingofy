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

  async getLyrics(song) {
    const res = await fetch(
      `${BASE_URL}/lyrics?song=${encodeURIComponent(song)}`,
    );
    if (!res.ok) throw new Error(`lyrics failed: ${res.status}`);
    return res.json();
  },
};
