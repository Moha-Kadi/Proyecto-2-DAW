import { Injectable, signal, computed, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { lastValueFrom } from 'rxjs';

export interface DatosRegistro {
  account: {
    username: string;
    email: string;
    password: string;
  };
}

export interface DatosLogin {
  email: string;
  password: string;
}

export interface RespuestaLogin {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    account: {
      username: string;
      email: string;
      avatar_url: string;
      is_active: boolean;
      rol: string;
    };
    favorites: {
      teams: number[];
      players: number[];
    };
  };
}

// Tipo usuario
export type Usuario = RespuestaLogin['user'];

// Injectanble para que Angular pueda inyectar este servicio en componentes, guards, etc.
@Injectable({ providedIn: 'root' })
export class AuthService {
  // Utiliza httpClient para hacer peticiones al backend, api es la ruta base de los endpoints de autenticacion.
  private http = inject(HttpClient);
  private readonly api = '/api/auth';

  // Estado reactivo del usuario
  usuarioActual = signal<Usuario | null>(null);
  
  // Devuelve booleano indicando si hay sesion activa (usuario logueado y activo)
  sesionActiva = computed(() => {
    const usuario = this.usuarioActual();
    return !!usuario && usuario.account?.is_active !== false;
  });

  constructor() {
    // Recupera la sesion guardada en localStorage al iniciar
    this.usuarioActual.set(this.obtenerUsuarioGuardado());
  }

  // Verifica el token con el backend. Si es valido, actualiza el usuario actual. Si no, cierra sesion.
  async verificarToken(): Promise<boolean> {
    const token = this.obtenerToken();
    if (!token) {
      this.cerrarSesion();
      return false;
    }

    try {
      const usuario = await lastValueFrom(this.http.get<Usuario>(`${this.api}/perfil`));
      this.actualizarUsuario(usuario);
      return usuario.account?.is_active !== false;
    } catch {
      this.cerrarSesion();
      return false;
    }
  }

  // Peticiones al backend para registro, login y actualizacion de cuenta.
  async registrar(datos: DatosRegistro): Promise<Usuario> {
    return lastValueFrom(this.http.post<Usuario>(`${this.api}/registro`, datos));
  }

  async iniciarSesion(datos: DatosLogin): Promise<RespuestaLogin> {
    return lastValueFrom(this.http.post<RespuestaLogin>(`${this.api}/login`, datos));
  }

  async actualizarCuenta(cambios: any): Promise<Usuario> {
    return lastValueFrom(this.http.put<Usuario>(`${this.api}/perfil`, cambios));
  }

  // Funciones para manejar la sesion en localStorage y actualizar el signal usuarioActual.
  guardarSesion(token: string, usuario?: Usuario): void {
    localStorage.setItem('access_token', token);
    if (usuario) {
      localStorage.setItem('user', JSON.stringify(usuario));
      // Actualiza el signal para que la UI reaccione inmediatamente
      this.usuarioActual.set(usuario);
    }
  }

  actualizarUsuario(usuario: Usuario): void {
    localStorage.setItem('user', JSON.stringify(usuario));
    // Se usa spread ({...usuario}) para crear una nueva referencia y que
    // Angular detecte el cambio en el signal
    this.usuarioActual.set({ ...usuario });
  }

  obtenerUsuarioGuardado(): Usuario | null {
    const json = localStorage.getItem('user');
    if (json) {
      try { return JSON.parse(json); } catch { return null; }
    }
    return null;
  }

  obtenerToken(): string | null {
    return localStorage.getItem('access_token');
  }

  cerrarSesion(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    this.usuarioActual.set(null);
  }
}
