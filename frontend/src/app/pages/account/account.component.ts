// Pagina de perfil de usuario: editar cuenta y cambiar contraseña
import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ToastService } from '../../shared/toast/toast.service';

@Component({
  selector: 'app-account',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './account.component.html'
})
export class AccountComponent implements OnInit {
  // Inyeccion de servicios
  auth = inject(AuthService);
  router = inject(Router);
  toast = inject(ToastService);

  // Campos del formulario
  usuario = '';
  email = '';
  avatarUrl = '';
  passwordActual = '';
  passwordNueva = '';
  confirmarPassword = '';

  cargando = signal(false);

  // Flags de validacion: se activan al hacer blur o al enviar
  mostrarErrorUsuario = false;
  mostrarErrorEmail = false;
  mostrarErrorPasswordActual = false;
  mostrarErrorPasswordNueva = false;
  mostrarErrorConfirmar = false;

  // Carga los datos del usuario al entrar en la pagina
  ngOnInit() {
    if (!this.auth.obtenerToken()) { this.router.navigate(['/login']); return; }
    const user = this.auth.obtenerUsuarioGuardado();
    if (user) {
      this.usuario = user.account?.username || '';
      this.email = user.account?.email || '';
      this.avatarUrl = user.account?.avatar_url || '';
    }
  }

  // Validacion: nombre de usuario requerido + minimo 3 caracteres
  get errorUsuario(): string {
    if (!this.mostrarErrorUsuario) return '';
    if (!this.usuario.trim()) return 'El nombre de usuario es requerido';
    if (this.usuario.trim().length < 3) return 'Minimo 3 caracteres';
    return '';
  }

  // Validacion: email requerido + formato valido
  get errorEmail(): string {
    if (!this.mostrarErrorEmail) return '';
    if (!this.email.trim()) return 'El correo es requerido';
    return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(this.email.trim()) ? '' : 'El correo no es valido';
  }

  // Validacion: si se quiere cambiar la password, la actual es obligatoria
  get errorPasswordActual(): string {
    if (!this.mostrarErrorPasswordActual) return '';
    if ((this.passwordNueva || this.confirmarPassword) && !this.passwordActual) return 'Introduce tu contrasena actual';
    return '';
  }

  // Validacion: nueva password minimo 6 caracteres
  get errorPasswordNueva(): string {
    if (!this.mostrarErrorPasswordNueva) return '';
    if (this.passwordNueva && this.passwordNueva.length < 6) return 'Minimo 6 caracteres';
    return '';
  }

  // Validacion: las dos contraseñas deben coincidir
  get errorConfirmar(): string {
    if (!this.mostrarErrorConfirmar) return '';
    if (this.confirmarPassword && this.confirmarPassword !== this.passwordNueva) return 'Las contrasenas no coinciden';
    return '';
  }

  // Envia los cambios al backend
  async enviar() {
    this.mostrarErrorUsuario = true;
    this.mostrarErrorEmail = true;
    this.mostrarErrorPasswordActual = true;
    this.mostrarErrorPasswordNueva = true;
    this.mostrarErrorConfirmar = true;

    if (this.errorUsuario || this.errorEmail || this.errorPasswordActual || this.errorPasswordNueva || this.errorConfirmar) return;

    // Solo envia los campos que han cambiado
    const cambios: any = {};
    cambios['username'] = this.usuario.trim();
    cambios['email'] = this.email.trim();
    cambios['avatar_url'] = this.avatarUrl;

    // Si se ha rellenado la nueva contraseña, la envia junto con la actual
    if (this.passwordNueva) {
      cambios['password'] = this.passwordNueva;
      cambios['current_password'] = this.passwordActual;
    }

    this.cargando.set(true);
    try {
      const user = await this.auth.actualizarCuenta(cambios);
      this.auth.actualizarUsuario(user);
      this.toast.exito('Perfil actualizado');
      // Si cambio la contraseña, cierra sesion para forzar re-login
      if (cambios['password']) {
        this.toast.exito('Contrasena cambiada. Inicia sesion de nuevo.');
        setTimeout(() => this.cerrarSesion(), 2000);
      }
    } catch {
      this.toast.error('Error al actualizar');
    }
    this.cargando.set(false);
  }

  cerrarSesion() {
    this.auth.cerrarSesion();
    this.toast.exito('Sesion cerrada');
    this.router.navigate(['/login']);
  }
}
