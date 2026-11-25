import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'inicio' },
  { path: 'inicio', loadComponent: () => import('./pages/home/home').then((module) => module.Home) },
  ...['ofertas','planes','admin','cuenta','vender','carrito','subastas','crece'].map(vista => ({path:vista,data:{vista},loadComponent:()=>import('./pages/mercado/mercado').then(m=>m.Mercado)})),
  { path: '**', redirectTo: 'inicio' },
];
