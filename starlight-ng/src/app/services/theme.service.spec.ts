import { TestBed } from '@angular/core/testing';

import { ThemeService } from './theme.service';

describe('ThemeService', () => {
  const STORAGE_KEY = 'starlight_theme';

  function stubSystemPreference(prefersDark: boolean): void {
    spyOn(window, 'matchMedia').and.returnValue({ matches: prefersDark } as MediaQueryList);
  }

  beforeEach(() => {
    localStorage.removeItem(STORAGE_KEY);
    document.documentElement.removeAttribute('data-theme');
  });

  it('uses the system preference when no theme is stored', () => {
    stubSystemPreference(true);
    const service = TestBed.inject(ThemeService);
    expect(service.currentTheme).toBe('dark');
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });

  it('falls back to the system preference when the stored value is invalid', () => {
    localStorage.setItem(STORAGE_KEY, 'blue');
    stubSystemPreference(false);
    const service = TestBed.inject(ThemeService);
    expect(service.currentTheme).toBe('light');
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
  });

  it('prefers a valid stored theme over the system preference', () => {
    localStorage.setItem(STORAGE_KEY, 'dark');
    stubSystemPreference(false);
    const service = TestBed.inject(ThemeService);
    expect(service.currentTheme).toBe('dark');
  });

  it('toggleTheme flips the theme, persists it and applies it to the document', () => {
    stubSystemPreference(false);
    const service = TestBed.inject(ThemeService);
    service.toggleTheme();
    expect(service.currentTheme).toBe('dark');
    expect(localStorage.getItem(STORAGE_KEY)).toBe('dark');
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });
});
