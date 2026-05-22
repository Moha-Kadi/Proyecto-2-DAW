// Servicio de fixtures: conecta con los endpoints de partidos del backend
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { lastValueFrom } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class FixturesService {
  // Inyecta el HttpClient para hacer peticiones al backend
  private http = inject(HttpClient);

  // Obtiene el dashboard de partidos, con opcion de filtrar por fecha
  async obtenerDashboardPartidos(fecha?: string) {
    let url = '/api/fixtures/dashboard';
    if (fecha) url += `?fecha=${fecha}`;
    return lastValueFrom(this.http.get<any>(url));
  }

  // Obtiene el detalle completo de un partido por su ID
  async obtenerDetalleCompletoPartido(idPartido: string) {
    return lastValueFrom(this.http.get<any>(`/api/fixtures/${idPartido}/completo`));
  }
}
