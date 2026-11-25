import { Injectable, signal } from '@angular/core';
export interface Usuario { id_usuario:string; correo:string; nombres:string; rol:string; }
export interface Variante { id_variante:string; precio:number; stock:number; talla:string; color:string; }
export interface Producto { id_producto:string; titulo:string; descripcion:string; condicion:string; material:string; distrito:string; tienda:string; modalidad:string; estado:string; motivo:string; variantes:Variante[]; imagenes:{url:string}[]; }
@Injectable({providedIn:'root'})
export class Api {
  usuario=signal<Usuario|null>(null);
  async llamar<T=any>(ruta:string,method='GET',datos?:unknown):Promise<T> {
    const token=sessionStorage.getItem('reva_token');
    const r=await fetch('/api'+ruta,{method,headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{})},...(datos===undefined?{}:{body:JSON.stringify(datos)})});
    let body:any;
    try { body=await r.json(); } catch { throw new Error('El servidor no respondió correctamente. Comprueba que el backend esté iniciado.'); }
    if(!r.ok){ if(r.status===401){sessionStorage.removeItem('reva_token');this.usuario.set(null);} throw new Error(typeof body.detail==='string'?body.detail:'Revisa los datos del formulario.'); }
    return body;
  }
  async restaurar(){if(sessionStorage.getItem('reva_token')){try {this.usuario.set(await this.llamar('/yo'));}catch {this.usuario.set(null);}}}
  async entrar(correo:string,clave:string){const r=await this.llamar('/sesion','POST',{correo,clave});sessionStorage.setItem('reva_token',r.token);this.usuario.set(r.usuario);}
  async salir(){try {await this.llamar('/sesion','DELETE');}finally{sessionStorage.removeItem('reva_token');this.usuario.set(null);}}
}
