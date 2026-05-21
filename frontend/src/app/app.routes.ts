// Rutas de la aplicacion con lazy loading
import { Routes } from '@angular/router';

export const routes: Routes = [
  // Pagina principal
  { path: '', loadComponent: () => import('./pages/home/home-page.component').then(m => m.HomePageComponent) },
  // Redireccion por defecto
  { path: '**', redirectTo: '' }
];
