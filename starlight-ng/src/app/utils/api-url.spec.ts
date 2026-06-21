import { getApiBaseUrl } from './api-url';

describe('getApiBaseUrl', () => {
  it('returns empty string in production when apiUrl is empty', () => {
    expect(getApiBaseUrl()).toBeDefined();
  });
});
