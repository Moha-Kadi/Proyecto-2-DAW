// Contenedor de liga con cabecera colapsable y lista de partidos
import { Component, Input, Output, EventEmitter } from '@angular/core';
import { MatchCardComponent } from '../match-card/match-card.component';

@Component({
  selector: 'app-league-container',
  standalone: true,
  imports: [MatchCardComponent],
  templateUrl: './league-container.component.html'
})
// Componente que muestra una liga con su cabecera (bandera, nombre, pais) y una lista de partidos.
export class LeagueContainerComponent {
  @Output() clicPartido = new EventEmitter<string>();
  // Recibe la informacion de la liga y sus partidos a traves del input. El formato es el mismo que el que devuelve el backend.
  @Input() liga!: {
    flag: string; logo: string; country: string; name: string;
    matches: any[]; esHoy?: boolean; fechaProximos?: string;
  };

  // Estado del contenedor (expandido o colapsado)
  expandido = true;

  // Alterna el estado del contenedor entre expandido y colapsado
  alternar() {
    this.expandido = !this.expandido;
  }
}
