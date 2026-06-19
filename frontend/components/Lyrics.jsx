import { useState } from "react";
import { api } from "../lib/api";

export default function Lyrics({ lyrics }) {
  const [translations, setTranslations] = useState({});
  const [loading, setLoading] = useState(null);
  const [error, setError] = useState(null);

  async function handleLineClick(line, index) {
    if (translations[index]) return;

    setLoading(index);
    setError(null);

    try {
      const data = await api.translateLine(line);
      setTranslations((prev) => ({ ...prev, [index]: data.translation }));
    } catch (err) {
      setError("Çeviri alınamadı.");
    } finally {
      setLoading(null);
    }
  }

  return (
    <div>
      <ul>
        {lyrics.map((line, index) => (
          <li key={index} onClick={() => handleLineClick(line, index)}>
            <span>{line}</span>
            {loading === index && <span> ...</span>}
            {translations[index] && <span> → {translations[index]}</span>}
          </li>
        ))}
      </ul>
      {error && <p>{error}</p>}
    </div>
  );
}
