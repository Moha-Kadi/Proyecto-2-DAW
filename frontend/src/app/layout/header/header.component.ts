import { Component, computed, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ToastService } from '../../shared/toast/toast.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './header.component.html'
})
export class HeaderComponent {
  private auth = inject(AuthService);
  private router = inject(Router);
  private toast = inject(ToastService);

  // Controla la visibilidad del menu en movil
  menuAbierto = false;

  // Con computed los datos se recalculan automaticamente cuando auth.usuarioActual() cambia.
  sesionActiva = computed(() => this.auth.sesionActiva());
  nombreUsuario = computed(() => this.auth.usuarioActual()?.account?.username ?? '');
  emailUsuario = computed(() => this.auth.usuarioActual()?.account?.email ?? '');
  avatarUsuario = computed(() => this.auth.usuarioActual()?.account?.avatar_url ?? '');
  esAdmin = computed(() => this.auth.usuarioActual()?.account?.rol === 'admin');

  alternarMenu() {
    this.menuAbierto = !this.menuAbierto;
  }

  cerrarMenu() {
    this.menuAbierto = false;
  }

  cerrarSesion() {
    this.auth.cerrarSesion();
    this.cerrarMenu();
    this.toast.exito('Sesion cerrada');
    this.router.navigate(['/login']);
  }
}
