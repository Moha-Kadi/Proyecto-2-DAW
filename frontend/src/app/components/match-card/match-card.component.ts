// Tarjeta de partido: usa los datos tal cual vienen del backend
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-match-card',
  standalone: true,
  imports: [],
  templateUrl: './match-card.component.html'
})
export class MatchCardComponent {
  @Input() partido: any;
}
