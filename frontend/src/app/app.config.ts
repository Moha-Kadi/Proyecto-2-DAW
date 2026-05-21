import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { routes } from './app.routes';
import { authInterceptor } from './interceptors/auth.interceptor';

// Configuracion global
export const appConfig: ApplicationConfig = {
  providers: [
    // Enrutador con lazy loading
    provideRouter(routes),
    // Cliente HTTP con interceptor de autenticacion
    provideHttpClient(withInterceptors([authInterceptor]))
  ]
};
