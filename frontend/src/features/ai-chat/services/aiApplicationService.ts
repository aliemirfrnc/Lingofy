import { sendChatRequest } from './aiApiService';
import { AIError, AIErrorType } from '../models/aiModels';

export const handleStreamResponse = async function* (
  message: string,
  signal?: AbortSignal
): AsyncGenerator<string, void, unknown> {
  let response: Response;
  try {
    response = await sendChatRequest({ message }, signal);
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw error;
    }
    throw new AIError('Ağ bağlantısı kurulamadı. Lütfen internet bağlantınızı kontrol edin.', 'Offline');
  }

  if (!response.ok) {
    let errorMessage = 'Bir hata oluştu.';
    let type: AIErrorType = 'Unknown';
    let status = response.status;
    let retryAfter = undefined;

    try {
      const errorData = await response.json();
      if (errorData.detail) errorMessage = errorData.detail;
      if (errorData.title) errorMessage = errorData.detail || errorData.title;
      if (errorData.extensions?.retry_after) retryAfter = errorData.extensions.retry_after;
    } catch {
      errorMessage = response.statusText;
    }

    if (status === 400 || status === 422) type = 'Validation';
    else if (status === 401) type = 'Unauthorized';
    else if (status === 403) type = 'Forbidden';
    else if (status === 429) type = 'LimitExceeded';
    else if (status === 503) type = 'Maintenance';

    throw new AIError(errorMessage, type, status, retryAfter);
  }

  if (!response.body) {
    throw new AIError('Sunucudan beklenen veri akışı alınamadı.', 'Unknown');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  try {
    while (true) {
      const { value, done } = await reader.read();
      if (value) {
        const chunk = decoder.decode(value, { stream: !done });
        if (chunk) {
          yield chunk;
        }
      }
      if (done) break;
    }

    const remaining = decoder.decode();
    if (remaining) {
      yield remaining;
    }
  } finally {
    reader.releaseLock();
  }
};
