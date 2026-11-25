import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Producto } from '../../interfaces/producto.interface';
import { Api } from '../../services/api.service';

@Component({selector:'app-mercado',imports:[CommonModule,FormsModule,RouterLink],templateUrl:'./mercado.html'})
export class Mercado implements OnInit {
  api=inject(Api); route=inject(ActivatedRoute); vista=this.route.snapshot.data['vista'];
  mensaje=signal(''); error=signal(''); ocupado=signal(false);
  productos=signal<Producto[]>([]); categorias=signal<any[]>([]); planes=signal<any[]>([]); items=signal<any[]>([]); pedidos=signal<any[]>([]); subastas=signal<any[]>([]); usuarios=signal<any[]>([]); reportes=signal<any[]>([]);
  busqueda=''; distrito=''; categoria=0; correo=''; clave=''; nombres=''; registro=false; direccion=''; operacion=crypto.randomUUID(); montos:Record<string,number>={}; seleccion:Record<string,string>={}; motivo='';
  tienda={nombre:'',dni:'',direccion:'',distrito:'Huancayo',consentimiento:false}; identidad='';
  producto={titulo:'',descripcion:'',material:'',condicion:'Nuevo',id_categoria:1,imagen:'',modalidad:'venta',precio_inicial:20,incremento:1,cierre:''};
  variantes=[{talla:'',color:'',precio:20,stock:1}];
  campana={marca:'',video_url:'',destino_url:'',activa:false,vence_en:''}; metricas=signal<any>(null);
  ruc=''; resultadoRuc=signal(''); ubicaciones=signal<any[]>([]);
  consultarRuc(){this.resultadoRuc.set('');this.ejecutar(async()=>{const r=await this.api.llamar('/documentos/ruc/'+this.ruc+'?consentimiento='+this.tienda.consentimiento);this.resultadoRuc.set([r.razonSocial,r.estado,r.direccion].join(' · '));});}
  ubicar(){this.ubicaciones.set([]);this.ejecutar(async()=>{this.ubicaciones.set(await this.api.llamar('/geocodificar?direccion='+encodeURIComponent(this.tienda.direccion)));});}
  crearAnuncio(){this.ejecutar(async()=>{await this.api.llamar('/admin/anuncios','POST',{...this.campana,vence_en:new Date(this.campana.vence_en).toISOString()});this.mensaje.set('Campaña registrada. Si está activa aparecerá en Inicio.');});}
  ngOnInit(){this.cargar();}
  async ejecutar(fn:()=>Promise<void>){if(this.ocupado())return;this.ocupado.set(true);this.error.set('');this.mensaje.set('');try{await fn();}catch(e){this.error.set(e instanceof Error?e.message:'Error inesperado');}finally{this.ocupado.set(false);}}
  async cargar(){await this.ejecutar(async()=>{
    if(['ofertas','vender'].includes(this.vista)){this.categorias.set(await this.api.llamar('/categorias'));this.productos.set(await this.api.llamar(this.vista==='vender'?'/mis-productos':'/productos'));}
    if(this.vista==='planes')this.planes.set(await this.api.llamar('/planes'));
    if(this.vista==='carrito'){this.items.set(await this.api.llamar('/carrito'));this.pedidos.set(await this.api.llamar('/pedidos'));}
    if(this.vista==='subastas')this.subastas.set(await this.api.llamar('/subastas'));
    if(this.vista==='admin'){this.productos.set(await this.api.llamar('/admin/productos'));this.usuarios.set(await this.api.llamar('/admin/usuarios'));this.reportes.set(await this.api.llamar('/admin/reportes'));this.metricas.set(await this.api.llamar('/admin/metricas'));}
  });}
  filtrados(){return this.productos().filter(p=>p.titulo.toLowerCase().includes(this.busqueda.toLowerCase())&&(!this.distrito||p.distrito===this.distrito));}
  autenticar(){this.ejecutar(async()=>{if(this.registro)await this.api.llamar('/registro','POST',{correo:this.correo,clave:this.clave,nombres:this.nombres});await this.api.entrar(this.correo,this.clave);this.clave='';this.mensaje.set('Sesión iniciada. Ya puedes explorar y comprar.');});}
  consultar(){this.identidad='';this.ejecutar(async()=>{const d=await this.api.llamar('/documentos/dni/'+this.tienda.dni+'?consentimiento='+this.tienda.consentimiento);this.identidad=[d.nombres,d.apellidoPaterno,d.apellidoMaterno].join(' ');});}
  guardarTienda(){this.ejecutar(async()=>{await this.api.llamar('/tienda','POST',this.tienda);await this.api.restaurar();this.mensaje.set('Tienda registrada. Puedes enviar tus productos a revisión.');});}
  publicar(){this.ejecutar(async()=>{await this.api.llamar('/productos','POST',{...this.producto,imagen:this.producto.imagen||null,cierre:this.producto.cierre?new Date(this.producto.cierre).toISOString():null,variantes:this.variantes});this.productos.set(await this.api.llamar('/mis-productos'));this.mensaje.set('Publicación enviada al administrador.');});}
  agregar(p:Producto){this.ejecutar(async()=>{const id=this.seleccion[p.id_producto]||p.variantes[0]?.id_variante;await this.api.llamar('/carrito','PUT',{id_variante:id,cantidad:1});this.mensaje.set('Producto añadido al carrito.');});}
  cantidad(i:any,n:number){this.ejecutar(async()=>{await this.api.llamar('/carrito','PUT',{id_variante:i.id_variante,cantidad:n});this.items.set(await this.api.llamar('/carrito'));this.operacion=crypto.randomUUID();});}
  total(){return this.items().reduce((n,i)=>n+Number(i.precio)*i.cantidad,0);}
  comprar(){this.ejecutar(async()=>{await this.api.llamar('/pedidos','POST',{direccion:this.direccion,clave_operacion:this.operacion});this.items.set(await this.api.llamar('/carrito'));this.pedidos.set(await this.api.llamar('/pedidos'));this.operacion=crypto.randomUUID();this.mensaje.set('Pedido de demostración registrado. No se realizó un cobro. Entrega por coordinar con la tienda.');});}
  activar(id:string){this.ejecutar(async()=>{const r=await this.api.llamar('/planes/'+id+'/activar','POST');this.mensaje.set(r.mensaje);});}
  pujar(s:any){this.ejecutar(async()=>{await this.api.llamar('/subastas/'+s.id_subasta+'/pujas','POST',{monto:this.montos[s.id_subasta]});this.subastas.set(await this.api.llamar('/subastas'));this.mensaje.set('Puja registrada.');});}
  minimo(s:any){return s.ultima_puja===null?Number(s.precio_inicial):Number(s.ultima_puja)+Number(s.incremento);}
  vencida(s:any){return new Date(s.cierre).getTime()<=Date.now();}
  moderar(p:Producto,estado:string){this.ejecutar(async()=>{await this.api.llamar('/admin/productos/'+p.id_producto,'PATCH',{estado,motivo:this.motivo});this.productos.set(await this.api.llamar('/admin/productos'));this.mensaje.set('Moderación registrada.');});}
  cuenta(u:any){this.ejecutar(async()=>{await this.api.llamar('/admin/usuarios/'+u.id_usuario,'PATCH',{activo:!u.activo,motivo:this.motivo});this.usuarios.set(await this.api.llamar('/admin/usuarios'));});}
  resolver(id:string){this.ejecutar(async()=>{await this.api.llamar('/admin/reportes/'+id,'PATCH');this.reportes.set(await this.api.llamar('/admin/reportes'));});}
  reportar(p:Producto){this.ejecutar(async()=>{await this.api.llamar('/reportes','POST',{id_producto:p.id_producto,motivo:this.motivo});this.mensaje.set('Reporte enviado.');});}
}
