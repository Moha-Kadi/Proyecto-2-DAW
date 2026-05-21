import { Injectable, signal } from '@angular/core';

export interface Notificacion {
  id: string;
  tipo: 'exito' | 'error';
  mensaje: string;
}

@Injectable({ providedIn: 'root' })
export class ToastService {
  // Notificaciones
  notificaciones = signal<Notificacion[]>([]);
  private contador = 0;

  // Muestra un toast de exito
  exito(mensaje: string) {
    this.mostrar(mensaje, 'exito');
  }

  // Muestra un toast de error
  error(mensaje: string) {
    this.mostrar(mensaje, 'error');
  }

  // Mostrar notificacion y actualizamos el signal para que angular reaccione y la muestre en pantalla.
  private mostrar(mensaje: string, tipo: 'exito' | 'error') {
    const id = (++this.contador).toString();
    this.notificaciones.update(lista => [...lista, { id, tipo, mensaje }]); // Vuelca los datos a la lista de notificaciones.
    setTimeout(() => this.ocultar(id), 4000); // Timeout de 4 segundos para ocultar la notificacion automaticamente
  }

  // Elimina una notificacion por ID
  ocultar(id: string) {
    this.notificaciones.update(lista => lista.filter(n => n.id !== id));
  }
}
