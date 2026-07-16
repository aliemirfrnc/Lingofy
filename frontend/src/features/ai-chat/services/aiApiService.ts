import { ChatRequestDTO } from '../types';

export const sendChatRequest = async (dto: ChatRequestDTO, signal?: AbortSignal): Promise<Response> => {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || '/api'}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(dto),
    signal,
  });

  return response;
};
