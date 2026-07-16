import { User, AuthSuccess } from '../models/authModels';
import { AuthResponseDTO, MeResponseDTO } from '../services/authService';

// The backend AuthResponse is { status: string, email: string, message: string }
// The backend MeResponse is { email: string }

export const mapAuthResponseToDomain = (data: AuthResponseDTO): AuthSuccess => {
  return {
    status: data.status,
    email: data.email,
    message: data.message,
  };
};

export const mapMeResponseToUser = (data: MeResponseDTO): User => {
  return {
    email: data.email,
  };
};
