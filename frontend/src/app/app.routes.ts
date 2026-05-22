// Rutas de la aplicacion con lazy loading
import { Routes } from '@angular/router';

export const routes: Routes = [
  // Pagina principal
  { path: '', loadComponent: () => import('./pages/home/home-page.component').then(m => m.HomePageComponent) },
  // Login
  { path: 'login', loadComponent: () => import('./pages/login/login.component').then(m => m.LoginComponent) },
  // Registro
  { path: 'registro', loadComponent: () => import('./pages/registro/register.component').then(m => m.RegisterComponent) },
  // Redireccion por defecto
  { path: '**', redirectTo: '' }
];
