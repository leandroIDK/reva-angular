import { inject } from '@angular/core';
import { CanMatchFn, Router, Routes } from '@angular/router';
import { Api } from './services/api';

const accesoAdministrador: CanMatchFn = async () => {
  const api = inject(Api);
  const router = inject(Router);

  if (!api.usuario()) {
    await api.restaurar();
  }

  return api.usuario()?.rol === 'administrador' || router.createUrlTree(['/cuenta']);
};

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'inicio' },
  { path: 'inicio', loadComponent: () => import('./pages/home/home').then((module) => module.Home) },
  ...['ofertas','planes','cuenta','vender','carrito','subastas','crece'].map(vista => ({path:vista,data:{vista},loadComponent:()=>import('./pages/mercado/mercado').then(m=>m.Mercado)})),
  { path: 'admin', data: { vista: 'admin' }, canMatch: [accesoAdministrador], loadComponent: () => import('./pages/mercado/mercado').then(m => m.Mercado) },
  { path: '**', redirectTo: 'inicio' },
];
