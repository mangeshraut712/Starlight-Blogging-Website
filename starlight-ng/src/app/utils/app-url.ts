/** Allow only in-app paths so login cannot redirect to another origin. */
export function safeReturnUrl(value: unknown, fallback = '/explore'): string {
  if (typeof value !== 'string') {
    return fallback;
  }
  const url = value.trim();
  if (!url.startsWith('/') || url.startsWith('//') || url.startsWith('/\\')) {
    return fallback;
  }
  if (url.includes('://') || url.includes('\\') || url.includes('\0')) {
    return fallback;
  }
  return url;
}

/** Resolve a router path against the document base href (GitHub Pages subpath). */
export function absoluteAppUrl(path: string): string {
  const baseHref = document.querySelector('base')?.href || `${window.location.origin}/`;
  return new URL(path.replace(/^\//, ''), baseHref).href;
}

/** TinyMCE asset prefix, including the production base href. */
export function tinymceBaseUrl(): string {
  const href = document.querySelector('base')?.getAttribute('href') || '/';
  const normalized = href.endsWith('/') ? href : `${href}/`;
  return `${normalized}tinymce`;
}
