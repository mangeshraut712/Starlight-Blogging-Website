import { environment } from '../../environments/environment';

/** Resolves API base URL: empty string in prod (same-origin /api proxy), localhost in dev. */
export function getApiBaseUrl(): string {
  if (environment.apiUrl !== undefined && environment.apiUrl !== null) {
    return environment.apiUrl;
  }
  return environment.production ? '' : 'http://localhost:8080';
}
