// Detalle de partido con 3 pestanas: resumen, estadisticas y alineaciones
import { Component, Input, Output, EventEmitter, signal, computed } from '@angular/core';

@Component({
  selector: 'app-match-detail',
  standalone: true,
  imports: [],
  templateUrl: './match-detail.component.html'
})
export class MatchDetailComponent {
  // Datos del partido que vienen del componente padre (scores-page)
  @Input() partido: any;
  // Avisa al padre cuando el usuario pulsa el boton de volver
  @Output() cerrar = new EventEmitter<any>();

  // Pestana activa: resumen, estadisticas o alineaciones
  pestanaActiva = signal('resumen');

  cambiarPestana(nuevaPestana: string) {
    this.pestanaActiva.set(nuevaPestana);
  }

  // Convierte las estadisticas en datos listos para las barras de comparacion
  estadisticasProcesadas = computed(() => {
    // Las estadisticas vienen en un array con dos objetos: uno para el equipo local y otro para el visitante
    const estadisticas = this.partido?.statistics || [];
    if (estadisticas.length < 2) return [];

    // Separar las estadisticas de local y visitante
    const statsLocal = estadisticas[0]?.statistics || [];
    const statsVisitante = estadisticas[1]?.statistics || [];

    return statsLocal.map((datoLocal: any) => {
      // Busca la misma estadistica en el visitante para comparar
      const datoVisitante = statsVisitante.find((d: any) => d.type === datoLocal.type);
      const valorLocal = parseFloat(datoLocal.value ?? 0); // Si el valor es null o undefined, lo tratamos como 0
      const valorVisitante = datoVisitante ? parseFloat(datoVisitante.value ?? 0) : 0; // Si no se encuentra la estadistica en el visitante, asumimos que es 0

      // Calcula el porcentaje para las barras de comparacion, evitando division por cero
      const total = valorLocal + valorVisitante;
      const porcentajeLocal = total > 0 ? (valorLocal / total) * 100 : 50;

      return {
        nombre: traducirEstadistica(datoLocal.type),
        valorLocal: valorLocal,
        valorVisitante: valorVisitante,
        porcentajeLocal: porcentajeLocal,
        porcentajeVisitante: 100 - porcentajeLocal
      };
      // Solo mostramos las estadisticas donde al menos un equipo tenga valor distinto de 0
    }).filter((fila: any) => fila.valorLocal !== 0 || fila.valorVisitante !== 0);
  });

  // Separa las alineaciones de local y visitante
  alineaciones = computed(() => {
    const alineaciones = this.partido?.lineups || [];
    if (alineaciones.length < 2) return null;
    return {
      local: procesarAlineacion(alineaciones[0]),
      visitante: procesarAlineacion(alineaciones[1])
    };
  });
}

// Extrae titulares, suplentes, formacion y entrenador de los datos de un equipo
function procesarAlineacion(datosEquipo: any) {
  if (!datosEquipo) return null;
  return {
    formacion: datosEquipo.formation,
    entrenador: datosEquipo.coach,
    titulares: datosEquipo.startXI?.map((p: any) => p.player) || [],
    suplentes: datosEquipo.substitutes?.map((p: any) => p.player) || []
  };
}

// Traduce los nombres de estadisticas del ingles al español
function traducirEstadistica(nombreIngles: string): string {
  const traducciones: any = {
    'Shots on Goal': 'Tiros a puerta', 'Shots off Goal': 'Tiros fuera',
    'Total Shots': 'Tiros totales', 'Blocked Shots': 'Tiros bloqueados',
    'Shots insidebox': 'Tiros dentro area', 'Shots outsidebox': 'Tiros fuera area',
    'Fouls': 'Faltas', 'Corner Kicks': 'Corneres', 'Offsides': 'Fueras de juego',
    'Ball Possession': 'Posesion', 'Yellow Cards': 'Tarjetas amarillas',
    'Red Cards': 'Tarjetas rojas', 'Goalkeeper Saves': 'Paradas portero',
    'Total passes': 'Pases totales', 'Passes accurate': 'Pases precisos',
    'Passes %': '% Pases', 'expected_goals': 'Goles esperados',
    'goals_prevented': 'Goles evitados'
  };
  return traducciones[nombreIngles] || nombreIngles;
}
