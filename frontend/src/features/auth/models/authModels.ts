import { z } from 'zod';
import { loginSchema, registerSchema } from '../validation/authSchemas';

// Frontend request types inferred from validation schemas
export type LoginRequest = z.infer<typeof loginSchema>;
export type RegisterRequest = z.infer<typeof registerSchema>;

// Frontend Domain Models
export interface User {
  email: string;
}

export interface AuthSuccess {
  status: string;
  email: string;
  message: string;
}
