// Rutas de la aplicacion con lazy loading
import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';
import { adminGuard } from './guards/admin.guard';

export const routes: Routes = [
  { path: '', loadComponent: () => import('./pages/home/home-page.component').then(m => m.HomePageComponent) },
  { path: 'login', loadComponent: () => import('./pages/login/login.component').then(m => m.LoginComponent) },
  { path: 'registro', loadComponent: () => import('./pages/registro/register.component').then(m => m.RegisterComponent) },
  { path: 'scores', loadComponent: () => import('./pages/scores/scores-page.component').then(m => m.ScoresPageComponent) },
  { path: 'account', loadComponent: () => import('./pages/account/account.component').then(m => m.AccountComponent), canActivate: [authGuard] },
  { path: 'admin', loadComponent: () => import('./pages/admin/admin.component').then(m => m.AdminComponent), canActivate: [adminGuard] },
  { path: '**', redirectTo: '' }
];
