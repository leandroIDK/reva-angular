import { Component, inject, signal } from '@angular/core';

import { Api } from '../../services/api.service';

/** Bloque reutilizable de campañas publicitarias activas en la página de inicio. */
@Component({
  selector: 'app-anuncios',
  template: `
    @if (anuncios().length) {
      <section class="shell">
        <p class="eyebrow">Espacio publicitario</p>
        <div class="cards">
          @for (anuncio of anuncios(); track anuncio.video_url) {
            <article>
              <small>Publicidad · {{ anuncio.marca }}</small>
              <video controls muted playsinline preload="none" style="width:100%;border-radius:12px" [src]="anuncio.video_url">
                Tu navegador no reproduce este video.
              </video>
              <a [href]="anuncio.destino_url" target="_blank" rel="noopener noreferrer sponsored">Conocer más</a>
            </article>
          }
        </div>
      </section>
    }
  `,
})
export class Anuncios {
  anuncios = signal<any[]>([]);
  private readonly api = inject(Api);

  constructor() {
    this.api.llamar<any[]>('/anuncios').then(anuncios => this.anuncios.set(anuncios)).catch(() => {});
  }
}
