// Sidebar con las 5 ligas principales
import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { LIGAS_PRINCIPALES } from '../../services/ligas.service';

@Component({
  selector: 'app-sidebar-ligas',
  standalone: true,
  imports: [],
  templateUrl: './sidebar-ligas.component.html'
})

// Componente para mostrar las ligas principales en la barra lateral
export class SidebarLigasComponent implements OnInit {
  // Evento para emitir la liga seleccionada al componente padre
  @Output() ligaSeleccionada = new EventEmitter<any>();

  // Variable para almacenar las ligas principales y la liga activa
  ligas = LIGAS_PRINCIPALES;
  ligaActiva = '';

  // Al iniciar el componente, seleccionamos la primera liga por defecto
  ngOnInit() {
    this.seleccionar(this.ligas[0]);
  }

  // Método para seleccionar una liga y emitir el evento con la liga seleccionada
  seleccionar(liga: any) {
    this.ligaActiva = liga.name;
    this.ligaSeleccionada.emit(liga);
  }
}
