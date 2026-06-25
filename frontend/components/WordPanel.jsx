"use client";
import { X, Loader2 } from "lucide-react";
import ErrorBanner from "./ErrorBanner";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/Card";
import { Badge } from "./ui/Badge";
import { Button } from "./ui/Button";

export default function WordPanel({
  selectedWord,
  wordInfo,
  wordLoading,
  wordError,
  onRetry,
  onClose,
}) {
  if (!selectedWord) return null;

  return (
    <Card className="flex flex-col h-full border-white/5 animate-slide-up shadow-glass">
      <CardHeader className="flex flex-row items-start justify-between pb-2 px-5 pt-5">
        <CardTitle className="text-2xl font-bold tracking-tight text-white m-0">
          {selectedWord}
        </CardTitle>
        <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8 rounded-full -mr-2 text-white/50 hover:bg-white/10 hover:text-white">
          <X size={18} />
          <span className="sr-only">Kapat</span>
        </Button>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto px-5 pb-5 custom-scrollbar">
        {wordLoading && (
          <div className="flex justify-center items-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-theme" />
          </div>
        )}

        {wordError && !wordLoading && (
          <ErrorBanner message={wordError} onRetry={onRetry} />
        )}

        {wordInfo && !wordLoading && !wordError && (
          <div className="space-y-6 mt-2 animate-fade-in">
            {/* Meta tags (POS, pron) */}
            <div className="flex items-center gap-3">
              {wordInfo.part_of_speech && (
                <Badge variant="default" className="uppercase text-[10px] tracking-wider px-3">
                  {wordInfo.part_of_speech}
                </Badge>
              )}
              {wordInfo.pronunciation && (
                <span className="text-sm italic text-white/40">/{wordInfo.pronunciation}/</span>
              )}
            </div>

            <div>
              <p className="text-xl font-bold text-theme mb-1">{wordInfo.translation}</p>
              <p className="text-[13px] leading-relaxed text-white/60">{wordInfo.definition}</p>
            </div>

            {(wordInfo.register || wordInfo.frequency) && (
              <div className="flex flex-wrap gap-2">
                {wordInfo.register && <Badge variant="secondary">{wordInfo.register}</Badge>}
                {wordInfo.frequency && <Badge variant="secondary">{wordInfo.frequency}</Badge>}
              </div>
            )}

            {wordInfo.contextual_meaning && (
              <div className="bg-theme-50 border border-theme-200 rounded-xl p-4">
                <p className="text-[10px] uppercase tracking-[0.1em] text-theme-600 font-bold mb-1.5">Bu satırda</p>
                <p className="text-[13px] leading-relaxed text-theme-50">{wordInfo.contextual_meaning}</p>
              </div>
            )}

            {wordInfo.grammar_note && (
              <div>
                <p className="text-[10px] uppercase tracking-widest text-white/30 font-bold mb-1.5">Gramer notu</p>
                <p className="text-[13px] leading-relaxed text-white/70">{wordInfo.grammar_note}</p>
              </div>
            )}

            {Array.isArray(wordInfo.synonyms) && wordInfo.synonyms.length > 0 && (
              <div>
                <p className="text-[10px] uppercase tracking-widest text-white/30 font-bold mb-1.5">Eş anlamlılar</p>
                <div className="flex flex-wrap gap-1.5">
                  {wordInfo.synonyms.map(syn => (
                     <Badge key={syn} variant="outline" className="text-xs bg-black/20 text-white/70">{syn}</Badge>
                  ))}
                </div>
              </div>
            )}

            {Array.isArray(wordInfo.antonyms) && wordInfo.antonyms.length > 0 && (
              <div>
                <p className="text-[10px] uppercase tracking-widest text-white/30 font-bold mb-1.5">Zıt anlamlılar</p>
                <div className="flex flex-wrap gap-1.5">
                  {wordInfo.antonyms.map(ant => (
                     <Badge key={ant} variant="outline" className="text-xs bg-black/20 text-white/70">{ant}</Badge>
                  ))}
                </div>
              </div>
            )}

            {Array.isArray(wordInfo.examples) && wordInfo.examples.length > 0 && (
              <div>
                <p className="text-[10px] uppercase tracking-widest text-white/30 font-bold mb-1.5">Örnek cümleler</p>
                <div className="space-y-3 bg-white/5 border border-white/5 rounded-xl p-4">
                  {wordInfo.examples.map((ex, i) => (
                    <p key={i} className="text-[13px] italic text-white/80 leading-relaxed">
                      "{ex}"
                    </p>
                  ))}
                </div>
              </div>
            )}

            {wordInfo.usage_note && (
              <div>
                <p className="text-[10px] uppercase tracking-widest text-white/30 font-bold mb-1.5">Kullanım notu</p>
                <p className="text-[13px] leading-relaxed text-white/70">{wordInfo.usage_note}</p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
