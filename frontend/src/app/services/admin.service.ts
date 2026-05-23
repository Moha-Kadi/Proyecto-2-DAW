// Servicio de administracion: endpoints de gestion de usuarios
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { lastValueFrom } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AdminService {
  // Inyeccion del HttpClient para hacer peticiones al backend
  private http = inject(HttpClient);

  // Obtiene la lista de usuarios (sin contraseñas)
  async obtenerUsuarios() {
    return lastValueFrom(this.http.get<any>('/api/admin/usuarios'));
  }

  // Activa o desactiva una cuenta
  async toggleUsuario(id: string) {
    return lastValueFrom(this.http.put<any>(`/api/admin/usuarios/${id}/toggle`, {}));
  }

  // Borra un usuario
  async borrarUsuario(id: string) {
    return lastValueFrom(this.http.delete<any>(`/api/admin/usuarios/${id}`));
  }
}
