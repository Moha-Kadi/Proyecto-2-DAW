// Panel de administracion: tabla de usuarios con toggle y borrado
import { Component, signal, inject, OnInit } from '@angular/core';
import { AdminService } from '../../services/admin.service';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [],
  templateUrl: './admin.component.html',
})
export class AdminComponent implements OnInit {
  adminService = inject(AdminService);

  // Lista de usuarios (sin el admin principal)
  usuarios = signal<any[]>([]);
  cargando = signal(true);
  error = signal('');

  ngOnInit() {
    this.cargarUsuarios();
  }

  // Obtiene la lista de usuarios del backend
  async cargarUsuarios() {
    this.cargando.set(true);
    try {
      const res = await this.adminService.obtenerUsuarios();
      // Filtra al admin principal para que no aparezca en la tabla
      this.usuarios.set(res.filter((u: any) => u.account.username !== 'admin'));
    } catch {
      this.error.set('Error al cargar usuarios');
    }
    this.cargando.set(false);
  }

  // Activa o desactiva un usuario
  async toggleUsuario(id: string) {
    try {
      await this.adminService.toggleUsuario(id);
      this.cargarUsuarios();
    } catch {
      this.error.set('Error al cambiar estado');
    }
  }

  // Borra un usuario con confirmacion previa
  async borrarUsuario(id: string) {
    if (!confirm('Seguro que quieres eliminar este usuario?')) return;
    try {
      await this.adminService.borrarUsuario(id);
      this.cargarUsuarios();
    } catch {
      this.error.set('Error al eliminar');
    }
  }
}
