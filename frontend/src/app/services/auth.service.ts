// Servicio de autenticacion: login, registro, perfil y sesion
import { Injectable, signal, computed, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { lastValueFrom } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AuthService {
  // Inyecta el HttpClient para hacer peticiones al backend
  private http = inject(HttpClient);
  // URL base para los endpoints de autenticacion
  private readonly api = '/api/auth';

  // Estado reactivo del usuario
  usuarioActual = signal<any>(null);

  // True si el usuario esta logueado y su cuenta esta activa
  sesionActiva = computed(() => {
    const usuario = this.usuarioActual();
    return !!usuario && usuario.account?.is_active !== false;
  });

  constructor() {
    this.usuarioActual.set(this.obtenerUsuarioGuardado());
  }

  // Verifica el token guardado contra el backend
  async verificarToken() {
    const token = this.obtenerToken();
    if (!token) { this.cerrarSesion(); return false; }
    try {
      const usuario = await lastValueFrom(this.http.get<any>(`${this.api}/perfil`));
      this.actualizarUsuario(usuario);
      return usuario.account?.is_active !== false;
    } catch {
      this.cerrarSesion();
      return false;
    }
  }

  // Endpoints
  async registrar(datos: any) {
    return lastValueFrom(this.http.post<any>(`${this.api}/registro`, datos));
  }

  async iniciarSesion(datos: any) {
    return lastValueFrom(this.http.post<any>(`${this.api}/login`, datos));
  }

  async actualizarCuenta(cambios: any) {
    return lastValueFrom(this.http.put<any>(`${this.api}/perfil`, cambios));
  }

  // Manejo de sesion en localStorage
  guardarSesion(token: string, usuario?: any) {
    localStorage.setItem('access_token', token);
    if (usuario) {
      localStorage.setItem('user', JSON.stringify(usuario));
      this.usuarioActual.set(usuario);
    }
  }

  actualizarUsuario(usuario: any) {
    localStorage.setItem('user', JSON.stringify(usuario));
    this.usuarioActual.set({ ...usuario });
  }

  obtenerUsuarioGuardado() {
    const json = localStorage.getItem('user');
    if (json) { try { return JSON.parse(json); } catch { return null; } }
    return null;
  }

  obtenerToken() {
    return localStorage.getItem('access_token');
  }

  cerrarSesion() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    this.usuarioActual.set(null);
  }
}
