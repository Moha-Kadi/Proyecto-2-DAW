import { inject } from '@angular/core';
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

// Interceptor para adjuntar el token JWT a las peticiones y manejar errores de autenticacion
export const authInterceptor: HttpInterceptorFn = (peticion, siguiente) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  const token = authService.obtenerToken();

  // Clona la peticion para adjuntar el header Authorization
  let req = peticion;
  if (token && peticion.url.includes('/api/')) {
    req = peticion.clone({ // Crear copia de la peticion original con el header Authorization
      setHeaders: { Authorization: `Bearer ${token}` } 
    });
  }

  // Devuelve token en la peticion y maneja errores de autenticacion
  return siguiente(req).pipe(
    catchError((error: HttpErrorResponse) => {
      // 401 = token invalido/expirado, 403 con "desactivada" = cuenta bloqueada
      if (error.status === 401 || error.status === 403) {
        authService.cerrarSesion();
        router.navigate(['/login']);
      }
      // Re lanza el error para que otros interceptors o componentes puedan manejarlo si es necesario (toasts)
      return throwError(() => error);
    })
  );
};
