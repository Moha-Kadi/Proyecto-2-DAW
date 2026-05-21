// Pagina principal
import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';

/*
 * CommonModule no se importa porque este componente solo usa @if.
 * En Angular 17+, @if forma parte del motor de plantillas y no necesita
 * ser importado desde CommonModule.
 * RouterLink se importa por separado para los enlaces de registro/login.
 */
@Component({
  selector: 'app-home-page',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './home-page.component.html'
})
export class HomePageComponent {
  auth = inject(AuthService);
  sesionActiva = this.auth.sesionActiva;
}
