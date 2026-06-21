import { Injectable } from '@angular/core';
import { Title, Meta } from '@angular/platform-browser';

@Injectable({ providedIn: 'root' })
export class MetaService {
  constructor(private title: Title, private meta: Meta) {}

  setPageMeta(options: {
    title: string;
    description?: string;
    author?: string;
    image?: string;
  }): void {
    const fullTitle = `${options.title} | StarLight`;
    this.title.setTitle(fullTitle);

    this.meta.updateTag({ name: 'description', content: options.description || 'Read stories on StarLight' });
    this.meta.updateTag({ property: 'og:title', content: fullTitle });
    this.meta.updateTag({ property: 'og:description', content: options.description || '' });
    this.meta.updateTag({ property: 'og:type', content: 'article' });
    if (options.author) {
      this.meta.updateTag({ name: 'author', content: options.author });
    }
    if (options.image) {
      this.meta.updateTag({ property: 'og:image', content: options.image });
    }
  }

  resetMeta(): void {
    this.title.setTitle('StarLight — Where Stories Become Stars');
    this.meta.updateTag({ name: 'description', content: 'A professional publishing platform for writers and readers.' });
  }
}
