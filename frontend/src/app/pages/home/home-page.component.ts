// Pagina principal
import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';


@Component({
  selector: 'app-home-page',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './home-page.component.html'
})


// Componente de la pagina principal, muestra un mensaje de bienvenida y enlaces a otras paginas. 
// El contenido se adapta segun si el usuario esta logueado o no.
export class HomePageComponent {
  auth = inject(AuthService);
  sesionActiva = this.auth.sesionActiva;
}
