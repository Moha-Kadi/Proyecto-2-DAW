// Pagina de registro de nuevo usuario
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ToastService } from '../../shared/toast/toast.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './register.component.html'
})
export class RegisterComponent {
  private auth = inject(AuthService);
  private router = inject(Router);
  private toast = inject(ToastService);

  // Campos del formulario
  usuario = '';
  email = '';
  password = '';
  confirmarPassword = '';
  cargando = signal(false);

  // Flags: se activan al hacer blur o al enviar
  mostrarErrorUsuario = false;
  mostrarErrorEmail = false;
  mostrarErrorPassword = false;
  mostrarErrorConfirmar = false;

  // Validacion del usuario: requerido + minimo 3 caracteres
  get errorUsuario(): string {
    if (!this.mostrarErrorUsuario) return '';
    if (!this.usuario) return 'El nombre de usuario es requerido';
    if (this.usuario.length < 3) return 'Minimo 3 caracteres';
    return '';
  }

  // Validacion del email: requerido + formato
  get errorEmail(): string {
    if (!this.mostrarErrorEmail) return '';
    if (!this.email) return 'El correo es requerido';
    return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(this.email) ? '' : 'El correo no es valido';
  }

  // Validacion de la password: requerido + minimo 6 caracteres + letras y numeros
  get errorPassword(): string {
    if (!this.mostrarErrorPassword) return '';
    if (!this.password) return 'La contrasena es requerida';
    if (this.password.length < 6) return 'Minimo 6 caracteres';
    return /^(?=.*[A-Za-z])(?=.*\d)/.test(this.password) ? '' : 'Debe contener letras y numeros';
  }

  // Validacion de confirmacion: requerido + debe coincidir con password
  get errorConfirmar(): string {
    if (!this.mostrarErrorConfirmar) return '';
    if (!this.confirmarPassword) return 'Debes confirmar la contrasena';
    if (this.confirmarPassword !== this.password) return 'Las contrasenas no coinciden';
    return '';
  }

  // Envia el formulario: valida, registra, redirige al login
  async enviar() {
    // Activar validacion visual en todos los campos
    this.mostrarErrorUsuario = true;
    this.mostrarErrorEmail = true;
    this.mostrarErrorPassword = true;
    this.mostrarErrorConfirmar = true;

    if (this.errorUsuario || this.errorEmail || this.errorPassword || this.errorConfirmar || this.cargando()) return;

    this.cargando.set(true);

    try {
      await this.auth.registrar({
        account: { username: this.usuario, email: this.email, password: this.password }
      });
      this.toast.exito('Cuenta creada. Redirigiendo al login...');
      setTimeout(() => this.router.navigate(['/login']), 1500);
    } catch {
      this.toast.error('Error al registrar');
    }
    this.cargando.set(false);
  }
}
