// Pagina principal: landing para invitados, clasificacion para logueados
import { Component, signal, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { SidebarLigasComponent } from '../../components/sidebar-ligas/sidebar-ligas.component';
import { LigasService } from '../../services/ligas.service';

@Component({
  selector: 'app-home-page',
  standalone: true,
  imports: [RouterLink, SidebarLigasComponent],
  templateUrl: './home-page.component.html'
})

// Componente para la página principal, que muestra la clasificación de la liga seleccionada o un mensaje de bienvenida para invitados
export class HomePageComponent {
  // Inyectamos los servicios de autenticación y ligas
  private auth = inject(AuthService);
  private ligasService = inject(LigasService);

  // Variables reactivas para la sesión, clasificación, estado de carga y liga seleccionada
  sesionActiva = this.auth.sesionActiva;
  clasificacion = signal<any[]>([]);
  cargando = signal(false);
  ligaSeleccionada = signal('');

  // Método para manejar la selección de una liga, obtener su clasificación y actualizar el estado del componente
  async alSeleccionarLiga(liga: any) {
    this.ligaSeleccionada.set(liga.name);
    this.cargando.set(true);
    try {
      // Obtiene la clasificación de la liga seleccionada desde el backend y la asigna a la variable reactiva
      const respuesta = await this.ligasService.obtenerClasificacion(liga.id);
      const standings = respuesta.response[0].league.standings;
      this.clasificacion.set(standings[0]);
    } catch {
      this.clasificacion.set([]);
    }
    this.cargando.set(false);
  }
}
