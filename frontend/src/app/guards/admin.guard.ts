import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

// Bloquea el acceso a rutas de administracion si el usuario no esta autenticado o si su rol no es 'admin'.
export const adminGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Obtiene el usuario actual del servicio de autenticacion
  const user = authService.usuarioActual();

  // Sin sesion: redirige al login
  if (!user) {
    router.navigate(['/login']);
    return false;
  }

  // Con sesion pero sin rol admin: redirige al inicio
  if (user.account.rol !== 'admin') {
    router.navigate(['/']);
    return false;
  }

  return true;
};
