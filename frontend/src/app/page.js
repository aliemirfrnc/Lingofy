"use client";

import dynamic from "next/dynamic";

const LyricsPage = dynamic(() => import("../components/LyricsPage"), {
  ssr: false,
});

export default function Home() {
  return <LyricsPage />;
}
