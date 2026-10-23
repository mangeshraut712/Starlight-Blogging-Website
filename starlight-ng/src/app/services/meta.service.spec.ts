import { TestBed } from '@angular/core/testing';
import { Meta, Title } from '@angular/platform-browser';
import { MetaService } from './meta.service';

describe('MetaService', () => {
  let service: MetaService;
  let title: Title;
  let meta: Meta;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(MetaService);
    title = TestBed.inject(Title);
    meta = TestBed.inject(Meta);
  });

  it('sets article tags and restores the homepage tags', () => {
    service.setPageMeta({ title: 'My Story', description: 'A short tale', author: 'Ada' });
    expect(title.getTitle()).toBe('My Story | StarLight');
    expect(meta.getTag('property="og:type"')?.content).toBe('article');
    expect(meta.getTag('name="description"')?.content).toBe('A short tale');

    service.resetMeta();
    expect(title.getTitle()).toContain('StarLight');
    expect(meta.getTag('property="og:type"')?.content).toBe('website');
    expect(meta.getTag('property="og:title"')?.content).not.toContain('My Story');
  });
});