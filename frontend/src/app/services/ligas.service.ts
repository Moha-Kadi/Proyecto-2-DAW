// Datos de las 5 ligas principales (IDs, banderas y logos)
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { lastValueFrom } from 'rxjs';

export const LIGAS_PRINCIPALES = [
  { id: 140, country: 'ESPAÑA', name: 'LaLiga EA Sports', logo: 'https://media.api-sports.io/football/leagues/140.png', flag: 'https://media.api-sports.io/flags/es.svg' },
  { id: 39, country: 'INGLATERRA', name: 'Premier League', logo: 'https://media.api-sports.io/football/leagues/39.png', flag: 'https://media.api-sports.io/flags/gb.svg' },
  { id: 135, country: 'ITALIA', name: 'Serie A', logo: 'https://media.api-sports.io/football/leagues/135.png', flag: 'https://media.api-sports.io/flags/it.svg' },
  { id: 78, country: 'ALEMANIA', name: 'Bundesliga', logo: 'https://media.api-sports.io/football/leagues/78.png', flag: 'https://media.api-sports.io/flags/de.svg' },
  { id: 61, country: 'FRANCIA', name: 'Ligue 1', logo: 'https://media.api-sports.io/football/leagues/61.png', flag: 'https://media.api-sports.io/flags/fr.svg' },
];

// Servicio para obtener la clasificación de una liga a través de la API
@Injectable({ providedIn: 'root' })
export class LigasService {
  // Inyectamos el HttpClient para realizar las peticiones a la API
  private http = inject(HttpClient);

  // Metodo para obtener la clasificacion a traves de la API, mediante el ID de la liga seleccionada
  async obtenerClasificacion(idLiga: number) {
    return lastValueFrom(this.http.get<any>(`/api/clasificacion?id_liga=${idLiga}`));
  }
}
