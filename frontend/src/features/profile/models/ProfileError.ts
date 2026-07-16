export type ProfileErrorType =
  | 'Validation'
  | 'Unauthorized'
  | 'Forbidden'
  | 'Offline'
  | 'Maintenance'
  | 'Unknown';

export class ProfileError extends Error {
  public type: ProfileErrorType;
  public fieldErrors?: Record<string, string[]>;
  public status?: number;

  constructor(
    message: string,
    type: ProfileErrorType = 'Unknown',
    fieldErrors?: Record<string, string[]>,
    status?: number
  ) {
    super(message);
    this.name = 'ProfileError';
    this.type = type;
    this.fieldErrors = fieldErrors;
    this.status = status;
  }
}
