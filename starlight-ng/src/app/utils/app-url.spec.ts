import { absoluteAppUrl, safeReturnUrl, tinymceBaseUrl } from './app-url';

describe('safeReturnUrl', () => {
  it('keeps internal paths', () => {
    expect(safeReturnUrl('/post/hello-world')).toBe('/post/hello-world');
  });

  it('rejects external and protocol-relative targets', () => {
    expect(safeReturnUrl('https://evil.example')).toBe('/explore');
    expect(safeReturnUrl('//evil.example')).toBe('/explore');
    expect(safeReturnUrl('/\\evil.example')).toBe('/explore');
    expect(safeReturnUrl(null)).toBe('/explore');
  });
});

describe('app urls', () => {
  afterEach(() => {
    document.head.querySelector('base')?.remove();
  });

  it('prefixes TinyMCE with the base href', () => {
    const base = document.createElement('base');
    base.setAttribute('href', '/Starlight-Blogging-Website/');
    document.head.appendChild(base);
    expect(tinymceBaseUrl()).toBe('/Starlight-Blogging-Website/tinymce');
  });

  it('builds share links under the base href', () => {
    const base = document.createElement('base');
    base.setAttribute('href', '/Starlight-Blogging-Website/');
    document.head.appendChild(base);
    expect(absoluteAppUrl('/post/my-story')).toContain('/Starlight-Blogging-Website/post/my-story');
  });
});
