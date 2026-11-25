import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Anuncios } from '../../components/anuncios/anuncios';

@Component({
  selector: 'app-home',
  imports: [RouterLink, Anuncios],
  template: `
    <section class="hero shell">
      <div><p class="eyebrow">Hecho para mover oportunidades locales</p><h1>Lo que no vendes, <strong>REVA</strong> lo mueve.</h1><p class="lead">Conectamos a pequeños comerciantes con compradores de Huancayo, El Tambo y Chilca para ayudarles a rotar su mercadería acumulada.</p><a class="button" routerLink="/ofertas">Explorar ofertas</a></div>
      <div class="hero-card"><span>REVA</span><h2>Liquidaciones locales</h2><p>Más visibilidad para tu inventario. Más oportunidades para tu negocio.</p></div>
    </section>
    <app-anuncios />
    <section class="shell value-grid"><article><span>01</span><h2>Vende lo acumulado</h2><p>Publica productos y dales una nueva oportunidad.</p></article><article><span>02</span><h2>Compra cerca</h2><p>Encuentra ofertas locales en un solo espacio.</p></article><article><span>03</span><h2>REVA Crece</h2><p>Accede a orientación gratuita para fortalecer tu negocio.</p></article></section>
  `,
})
export class Home {}
