// Pagina de resultados de partidos agrupados por liga
import { Component, inject, signal, OnInit } from '@angular/core';
import { LeagueContainerComponent } from '../../components/league-container/league-container.component';
import { FixturesService } from '../../services/fixtures.service';
import { LIGAS_PRINCIPALES } from '../../services/ligas.service';

@Component({
  selector: 'app-scores-page',
  standalone: true,
  imports: [LeagueContainerComponent],
  templateUrl: './scores-page.component.html'
})
// Componente de la pagina de resultados, muestra los partidos agrupados por liga y permite filtrar por estado y fecha.
export class ScoresPageComponent implements OnInit {
  private fixtures = inject(FixturesService);

  // Variables reactivas para el partido seleccionado, fecha actual, estado de carga y las ligas con sus partidos
  partidoSeleccionado = signal<any>(null);
  fechaActual = signal(new Date());
  cargando = signal(true);

  // Inicializa las 5 ligas con arrays de partidos vacios
  ligas = signal<any>(LIGAS_PRINCIPALES.map(l => ({
    id: l.id, flag: l.flag, logo: l.logo, country: l.country, name: l.name,
    matches: [], esHoy: true, fechaProximos: undefined
  })));

  // Al cargar el componente, obtiene los partidos del dia actual
  ngOnInit() {
    this.cargarPartidos();
  }

  // Formatea la fecha actual en formato YYYY-MM-DD para usarla en el endpoint del backend
  get formatoFecha(): string {
    return this.fechaActual().toISOString().slice(0, 10);
  }

  // Carga los partidos del dia actual desde el backend y los asigna a las ligas correspondientes
  async cargarPartidos() {
    this.cargando.set(true);
    try {
      const respuestas = await this.fixtures.obtenerDashboardPartidos(this.formatoFecha);
      this.ligas.set(this.ligas().map((liga: any) => {
        const res = respuestas[liga.id.toString()];
        return { ...liga, esHoy: res?.es_hoy ?? true, fechaProximos: res?.fecha_proximos,
          matches: res?.partidos || [] };
      }));
    } catch { }
    this.cargando.set(false);
  }

  // Funciones para cambiar la fecha de los partidos mostrados, ya sea al dia anterior, siguiente o a hoy
  diaAnterior() { this.cambiarDia(-1); }
  diaSiguiente() { this.cambiarDia(1); }

  // Cambia la fecha actual sumando el delta (en dias) y recarga los partidos
  private cambiarDia(delta: number) {
    const d = new Date(this.fechaActual());
    d.setDate(d.getDate() + delta);
    this.fechaActual.set(d);
    this.cargarPartidos();
  }

  // Cambia la fecha actual a la seleccionada en el input de tipo date y recarga los partidos
  cambiarFecha(event: any) {
    if (event.target.value) {
      this.fechaActual.set(new Date(event.target.value + 'T00:00:00'));
      this.cargarPartidos();
    }
  }

  // Cambia la fecha actual al dia de hoy y recarga los partidos
  irAHoy() {
    this.fechaActual.set(new Date());
    this.cargarPartidos();
  }

  // Al hacer clic en un partido, obtiene su detalle completo desde el backend y lo muestra 
  async clicPartido(id: string) {
    this.cargando.set(true);
    try {
      this.partidoSeleccionado.set(await this.fixtures.obtenerDetalleCompletoPartido(id));
      window.scrollTo(0, 0);
    } catch { }
    this.cargando.set(false);
  }

  // Cierra el detalle del partido seleccionado
  cerrarDetalle() {
    this.partidoSeleccionado.set(null);
  }
}
