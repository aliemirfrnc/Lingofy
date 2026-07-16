import { memo } from "react";

export const LyricLine = memo(function LyricLine({
  line,
  lineIndex,
  isActive,
  lyricOpacity,
  scale,
  lineTranslation,
  onLineClick,
  onWordClick,
  onCoachClick,
  lineRef
}) {
  return (
    <div className={`mb-6 transition-all duration-500 ${isActive ? 'my-8' : ''}`}>
      <p
        ref={lineRef}
        onClick={() => onLineClick(lineIndex)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onLineClick(lineIndex);
          }
        }}
        tabIndex={0}
        role="button"
        aria-label={`Satırı seç: ${line}`}
        className={`m-0 py-1.5 leading-snug tracking-tight transition-all duration-500 select-none cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-theme focus-visible:rounded-lg ${isActive ? 'drop-shadow-2xl' : ''}`}
        style={{
          opacity: lyricOpacity,
          transform: `scale(${scale})`,
          color: isActive ? "#ffffff" : "rgba(255,255,255,0.75)",
          fontWeight: isActive ? 900 : 700,
          textShadow: isActive
            ? `0 0 60px rgba(var(--theme-r),var(--theme-g),var(--theme-b),0.8), 0 4px 12px rgba(0,0,0,0.9)`
            : "0 2px 4px rgba(0,0,0,0.5)",
          fontSize: isActive ? 32 : 20,
        }}
      >
        {line.split(/(\s+)/).map((token, ti) =>
          /^\s+$/.test(token) ? (
            token
          ) : (
            <span
              key={ti}
              onClick={(e) => {
                e.stopPropagation();
                onWordClick(token, line, lineIndex);
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  e.stopPropagation();
                  onWordClick(token, line, lineIndex);
                }
              }}
              tabIndex={0}
              role="button"
              aria-label={`${token} kelimesini seç`}
              className="cursor-pointer rounded-md px-[2px] transition-colors hover:bg-white/20 hover:text-theme-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-theme"
            >
              {token}
            </span>
          )
        )}
      </p>

      {isActive && (
        <div className="mt-4 mb-2 min-h-[30px] flex flex-col items-center justify-center gap-3 relative z-20 animate-slide-up" style={{opacity: 1}}>
          {lineTranslation === null ? (
            <span className="text-[13px] text-white/30 bg-black/40 px-3 py-1 rounded-full">
              Çeviri alınamadı
            </span>
          ) : lineTranslation ? (
            <span 
              className="glass-panel text-center tracking-wide shadow-2xl"
              style={{
                backgroundColor: 'rgba(0,0,0,0.35)',
                border: '1px solid rgba(255,255,255,0.08)',
                padding: '12px 24px',
                borderRadius: '16px',
                color: '#E8E8E8',
                opacity: 1,
                fontSize: '18px',
                fontWeight: '700'
              }}
            >
              {lineTranslation}
            </span>
          ) : (
            <span className="text-[13px] text-white/30 animate-pulse bg-white/5 px-3 py-1 rounded-full">
              Çeviri yükleniyor...
            </span>
          )}
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              onCoachClick(line);
            }}
            className="mt-2 bg-gradient-to-r from-red-500/20 to-orange-500/20 border border-red-500/30 text-red-300 rounded-full px-4 py-1.5 text-[13px] font-bold cursor-pointer hover:scale-105 transition-transform flex items-center gap-2 shadow-glow"
          >
            🎤 Telaffuzunu Test Et
          </button>
        </div>
      )}
    </div>
  );
});
