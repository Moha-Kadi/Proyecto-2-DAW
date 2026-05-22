// Pagina de inicio de sesion
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ToastService } from '../../shared/toast/toast.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './login.component.html'
})
export class LoginComponent {
  private auth = inject(AuthService);
  private router = inject(Router);
  private toast = inject(ToastService);

  // Campos del formulario
  email = '';
  password = '';
  // Signal que controla el estado de carga del boton
  cargando = signal(false);

  // Flags: se activan al hacer blur o al enviar para mostrar errores
  mostrarErrorEmail = false;
  mostrarErrorPassword = false;

  // Validacion del email: requerido y formato valido
  get errorEmail(): string {
    if (!this.mostrarErrorEmail) return '';
    if (!this.email) return 'El correo es requerido';
    return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(this.email) ? '' : 'El correo no es valido';
  }

  // Validacion de la password: requerido
  get errorPassword(): string {
    if (!this.mostrarErrorPassword) return '';
    return this.password ? '' : 'La contrasena es requerida';
  }

  // Envia el formulario: valida, llama al backend, guarda sesion y redirige
  async enviar() {
    // Activar validacion visual en todos los campos
    this.mostrarErrorEmail = true;
    this.mostrarErrorPassword = true;
    if (this.errorEmail || this.errorPassword || this.cargando()) return;

    this.cargando.set(true);

    try {
      const resp = await this.auth.iniciarSesion({ email: this.email, password: this.password });
      this.cargando.set(false);
      // Guarda el token y los datos del usuario en localStorage y el signal
      this.auth.guardarSesion(resp.access_token, resp.user);
      this.toast.exito(`Bienvenido, ${resp.user.account.username}`);
      this.router.navigate(['/']);
    } catch (err: any) {
      this.cargando.set(false);
      // 403 = cuenta desactivada, cualquier otro error = credenciales incorrectas
      if (err?.status === 403) {
        this.toast.error('Cuenta desactivada. Contacta con el administrador.');
      } else {
        this.toast.error('Credenciales incorrectas. Verifica tu email y contrasena.');
      }
    }
  }
}
