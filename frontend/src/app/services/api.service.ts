import { Injectable, signal } from '@angular/core';

import { environment } from '../../environments/environment';
import { Producto } from '../interfaces/producto.interface';
import { Usuario } from '../interfaces/usuario.interface';

/** Servicio único para la comunicación HTTP, sesión y errores de la API. */
@Injectable({ providedIn: 'root' })
export class Api {
  usuario = signal<Usuario | null>(null);
  private readonly api_url = this.obtenerApiUrl();

  private obtenerApiUrl(): string {
    const url = (globalThis as typeof globalThis & { REVA_API_URL?: string }).REVA_API_URL ?? environment.apiUrl;
    return url.startsWith('https://') ? url.replace(/\/$/, '') : '';
  }

  async llamar<T = any>(ruta: string, method = 'GET', datos?: unknown): Promise<T> {
    const token = sessionStorage.getItem('reva_token');
    const respuesta = await fetch(this.api_url + '/api' + ruta, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: 'Bearer ' + token } : {}),
      },
      ...(datos === undefined ? {} : { body: JSON.stringify(datos) }),
    });

    let cuerpo: any;
    try {
      cuerpo = await respuesta.json();
    } catch {
      throw new Error('El servidor no respondió correctamente. Comprueba que el backend esté iniciado.');
    }

    if (!respuesta.ok) {
      if (respuesta.status === 401) {
        sessionStorage.removeItem('reva_token');
        this.usuario.set(null);
      }
      throw new Error(typeof cuerpo.detail === 'string' ? cuerpo.detail : 'Revisa los datos del formulario.');
    }
    return cuerpo as T;
  }

  async restaurar(): Promise<void> {
    if (!sessionStorage.getItem('reva_token')) return;
    try {
      this.usuario.set(await this.llamar<Usuario>('/yo'));
    } catch {
      this.usuario.set(null);
    }
  }

  async entrar(correo: string, clave: string): Promise<void> {
    const respuesta = await this.llamar<{ token: string; usuario: Usuario }>('/sesion', 'POST', { correo, clave });
    sessionStorage.setItem('reva_token', respuesta.token);
    this.usuario.set(respuesta.usuario);
  }

  async salir(): Promise<void> {
    try {
      await this.llamar('/sesion', 'DELETE');
    } finally {
      sessionStorage.removeItem('reva_token');
      this.usuario.set(null);
    }
  }
}

export type { Producto, Usuario };
