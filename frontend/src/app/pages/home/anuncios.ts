import {Component,inject,signal} from '@angular/core';
import {Api} from '../../services/api';
@Component({selector:'app-anuncios',template:`@if(anuncios().length){<section class="shell"><p class="eyebrow">Espacio publicitario</p><div class="cards">@for(a of anuncios();track a.video_url){<article><small>Publicidad · {{a.marca}}</small><video controls muted playsinline preload="none" style="width:100%;border-radius:12px" [src]="a.video_url">Tu navegador no reproduce este video.</video><a [href]="a.destino_url" target="_blank" rel="noopener noreferrer sponsored">Conocer más</a></article>}</div></section>}`})
export class Anuncios {
  anuncios=signal<any[]>([]);api=inject(Api);
  constructor(){this.api.llamar<any[]>('/anuncios').then(a=>this.anuncios.set(a)).catch(()=>{});}
}
