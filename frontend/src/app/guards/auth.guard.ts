import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

// El router de Angular ejecuta este guard antes de activar una ruta protegida.
// Si devuelve true, permite la navegacion. Si devuelve false, la bloquea.
export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Si no hay sesion activa, bloquea la ruta y redirige al login
  if (!authService.sesionActiva()) {
    authService.cerrarSesion();
    router.navigate(['/login']);
    return false;
  }

  return true;
};
