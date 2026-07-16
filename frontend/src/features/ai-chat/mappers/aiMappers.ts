import { Message, StreamingChunk } from '../models/aiModels';

export const mapChunkToDomain = (chunkRaw: string): StreamingChunk => {
  return {
    id: crypto.randomUUID(),
    chunk: chunkRaw,
    createdAt: new Date(),
  };
};

export const mapToMessage = (role: 'user' | 'assistant' | 'system', content: string): Message => {
  return {
    id: crypto.randomUUID(),
    role,
    content,
    createdAt: new Date(),
  };
};
