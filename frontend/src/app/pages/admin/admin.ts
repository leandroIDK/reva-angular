import { Component } from '@angular/core';

@Component({
  selector: 'app-admin',
  template: `<section class="shell page"><p class="eyebrow">ACCESO PRIVADO</p><h1>Administración REVA</h1><p class="lead">Panel preparado para aprobar publicaciones, gestionar usuarios, revisar reportes y administrar anuncios.</p><div class="admin-grid"><article><h2>Publicaciones</h2><p>Aprobar, rechazar, ocultar o retirar productos.</p></article><article><h2>Usuarios</h2><p>Gestionar compradores, vendedores y permisos.</p></article><article><h2>Reportes</h2><p>Revisar incidencias de la comunidad.</p></article><article><h2>Publicidad</h2><p>Gestionar campañas y espacios patrocinados.</p></article></div><p class="notice">La autenticación y las acciones administrativas se conectarán después de definir la API y la base de datos.</p></section>`,
})
export class Admin {}
