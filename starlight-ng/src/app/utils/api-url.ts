import { environment } from '../../environments/environment';

/** Resolves API base URL: Render origin in prod, localhost in dev. */
export function getApiBaseUrl(): string {
  if (environment.apiUrl !== undefined && environment.apiUrl !== null) {
    return environment.apiUrl;
  }
  return environment.production ? '' : 'http://localhost:8080';
}
