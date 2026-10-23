import { Injectable } from '@angular/core';
import { Meta, Title } from '@angular/platform-browser';

const DEFAULT_TITLE = 'StarLight — Professional Publishing Platform';
const DEFAULT_DESCRIPTION = 'Write and share your stories with the universe. Join the community of writers and readers.';

@Injectable({ providedIn: 'root' })
export class MetaService {
  constructor(private title: Title, private meta: Meta) {}

  setPageMeta(options: {
    title: string;
    description?: string;
    author?: string;
    image?: string;
    type?: 'article' | 'website';
  }): void {
    const fullTitle = `${options.title} | StarLight`;
    const description = options.description || 'Read stories on StarLight';
    this.title.setTitle(fullTitle);
    this.meta.updateTag({ name: 'description', content: description });
    this.meta.updateTag({ property: 'og:title', content: fullTitle });
    this.meta.updateTag({ property: 'og:description', content: description });
    this.meta.updateTag({ property: 'og:type', content: options.type || 'article' });
    this.meta.updateTag({ name: 'twitter:card', content: 'summary_large_image' });
    this.meta.updateTag({ name: 'twitter:title', content: fullTitle });
    this.meta.updateTag({ name: 'twitter:description', content: description });
    if (options.author) {
      this.meta.updateTag({ name: 'author', content: options.author });
    }
    if (options.image) {
      this.meta.updateTag({ property: 'og:image', content: options.image });
    }
    this.updateCanonical(window.location.href.split('#')[0]);
  }

  resetMeta(): void {
    this.title.setTitle(DEFAULT_TITLE);
    this.meta.updateTag({ name: 'description', content: DEFAULT_DESCRIPTION });
    this.meta.updateTag({ property: 'og:title', content: 'StarLight - Share Your Stories with the Universe' });
    this.meta.updateTag({ property: 'og:description', content: DEFAULT_DESCRIPTION });
    this.meta.updateTag({ property: 'og:type', content: 'website' });
    this.meta.updateTag({ name: 'twitter:title', content: DEFAULT_TITLE });
    this.meta.updateTag({ name: 'twitter:description', content: DEFAULT_DESCRIPTION });
    const base = document.querySelector('base')?.href || window.location.origin;
    this.updateCanonical(base);
  }

  private updateCanonical(url: string): void {
    this.meta.updateTag({ property: 'og:url', content: url });
    document.querySelector("link[rel='canonical']")?.setAttribute('href', url);
  }
}
