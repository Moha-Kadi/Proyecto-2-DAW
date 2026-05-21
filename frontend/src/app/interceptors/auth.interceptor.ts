import { inject } from '@angular/core';
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

/*
 * Interceptor funcional de Angular (HttpInterceptorFn).
 *
 * Se ejecuta automaticamente en cada peticion HTTP que pasa por provideHttpClient.
 * Adjunta el token Bearer a las peticiones hacia /api/ y maneja errores 401/403.
 *
 * peticion.clone() es obligatorio porque las HttpRequest son inmutables:
 * no se pueden modificar, solo clonar con los cambios deseados.
 *
 * .pipe(catchError(...)) usa RxJS para interceptar el error antes de que
 * llegue al componente que hizo la peticion. throwError re-lanza el error
 * para que el componente tambien pueda manejarlo si lo necesita.
 */
export const authInterceptor: HttpInterceptorFn = (peticion, siguiente) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  const token = authService.obtenerToken();

  // Clona la peticion para adjuntar el header Authorization
  let req = peticion;
  if (token && peticion.url.includes('/api/')) {
    req = peticion.clone({
      setHeaders: { Authorization: `Bearer ${token}` }
    });
  }

  return siguiente(req).pipe(
    catchError((error: HttpErrorResponse) => {
      // 401 = token invalido/expirado, 403 con "desactivada" = cuenta bloqueada
      if (
        error.status === 401 ||
        (error.status === 403 && String(error.error?.error || '').toLowerCase().includes('desactivada'))
      ) {
        authService.cerrarSesion();
        router.navigate(['/login']);
      }
      // throwError re-lanza el error para que el componente que origino la peticion
      // tambien pueda reaccionar (ej: mostrar un toast de error)
      return throwError(() => error);
    })
  );
};
