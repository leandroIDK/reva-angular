import { Component, inject } from '@angular/core';
import { Api } from './services/api';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <header class="site-header">
      <a class="brand" routerLink="/inicio">REVA<span>.</span></a>
      <nav aria-label="Navegación principal">
        <a routerLink="/inicio" routerLinkActive="active">Inicio</a>
        <a routerLink="/ofertas" routerLinkActive="active">Explorar ofertas</a>
        <a routerLink="/planes" routerLinkActive="active">Planes</a>
        <a routerLink="/subastas" routerLinkActive="active">Subastas</a>
        <a routerLink="/vender" routerLinkActive="active">Vender</a>
        <a routerLink="/crece" routerLinkActive="active">REVA Crece</a>
        <a routerLink="/carrito" routerLinkActive="active">Carrito</a>
        <a routerLink="/cuenta" routerLinkActive="active">{{api.usuario()?'Mi cuenta':'Ingresar'}}</a>
        @if(api.usuario()?.rol==='administrador'){<a routerLink="/admin" routerLinkActive="active">Administración</a>}
        @if(api.usuario()){<button class="secondary" (click)="api.salir()">Salir</button>}
      </nav>
    </header>
    <main><router-outlet /></main>
    <footer>REVA · Oportunidades locales para mover inventario acumulado.</footer>
  `,
})
export class App { api=inject(Api); constructor(){this.api.restaurar();} }
