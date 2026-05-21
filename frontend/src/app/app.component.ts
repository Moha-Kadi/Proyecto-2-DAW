import { Component, inject, OnInit } from '@angular/core';
import { RouterOutlet, Router, NavigationEnd } from '@angular/router';
import { HeaderComponent } from './layout/header/header.component';
import { FooterComponent } from './layout/footer/footer.component';
import { ToastsComponent } from './shared/toast/toasts.component';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, HeaderComponent, FooterComponent, ToastsComponent],
  templateUrl: './app.component.html'
})
export class App implements OnInit {
  private router = inject(Router);
  private auth = inject(AuthService);

  // Booleano que controla si se muestra o no la cabecera y el pie de pagina segun la URL actual.
  mostrarCabeceraPie = true;

  // Al inciar la aplicacion, verificamos si hay un token guardado y su validez.
  ngOnInit() {
    if (this.auth.obtenerToken()) {
      this.auth.verificarToken();
    }

    // Nos suscribimos a los eventos de navegacion para mostrar u ocultar cabecera y pie segun la URL.
    this.router.events.subscribe(e => {
      if (e instanceof NavigationEnd) {
        this.actualizarVisibilidadLayout(e.urlAfterRedirects);
      }
    });

    // Calcula el estado inicial antes de que el primer NavigationEnd se emita
    this.actualizarVisibilidadLayout(this.router.url);
  }

  // Muestra u oculta cabecera y pie segun la URL actual.
  private actualizarVisibilidadLayout(url: string): void {
    this.mostrarCabeceraPie = !url.includes('/login') && !url.includes('/registro');
  }
}
