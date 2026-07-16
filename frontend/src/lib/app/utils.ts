import { clsx, type ClassValue } from 'clsx';

/**
 * Merges class names safely.
 * Since Tailwind is forbidden in the Customer UI, we only need clsx, not tailwind-merge.
 */
export function cx(...inputs: ClassValue[]) {
  return clsx(inputs);
}
