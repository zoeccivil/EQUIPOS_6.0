"""
Gestor de Combustible para EQUIPOS 6.0 MODERN
Control de cargas y consumo de combustible por equipo
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QDateEdit, QComboBox,
    QDoubleSpinBox, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from app_theme import AppTheme, ModernTable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GestorCombustible(QWidget):
    """
    Gestor de cargas de combustible con cálculo de eficiencia
    """
    
    def __init__(self, firebase_manager, config, parent=None):
        super().__init__(parent)
        self.fm = firebase_manager
        self.config = config
        
        self._crear_interfaz()
        self._cargar_datos()
    
    def _crear_interfaz(self):
        """Crea la interfaz del gestor de combustible"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Título
        titulo = QLabel("⛽ Control de Combustible")
        titulo_font = QFont("Inter", 24)
        titulo_font.setBold(True)
        titulo.setFont(titulo_font)
        titulo.setStyleSheet(f"color: {AppTheme.COLORS['primary']};")
        layout.addWidget(titulo)
        
        # Subtítulo
        subtitulo = QLabel("Gestión de cargas y consumo de equipos")
        subtitulo.setStyleSheet(f"color: {AppTheme.COLORS['text_secondary']}; font-size: 14px;")
        layout.addWidget(subtitulo)
        
        # Barra de herramientas
        toolbar = QHBoxLayout()
        
        btn_nueva_carga = QPushButton("➕ Nueva Carga")
        btn_nueva_carga.setProperty("class", "primary")
        btn_nueva_carga.clicked.connect(self._nueva_carga)
        toolbar.addWidget(btn_nueva_carga)
        
        toolbar.addStretch()
        
        # Filtro por equipo
        filtro_label = QLabel("Equipo:")
        filtro_label.setStyleSheet(f"color: {AppTheme.COLORS['text_secondary']};")
        toolbar.addWidget(filtro_label)
        
        self.combo_equipo = QComboBox()
        self.combo_equipo.addItem("Todos los equipos", None)
        self.combo_equipo.setMinimumWidth(200)
        self.combo_equipo.currentIndexChanged.connect(self._cargar_datos)
        toolbar.addWidget(self.combo_equipo)
        
        btn_actualizar = QPushButton("🔄 Actualizar")
        btn_actualizar.setProperty("class", "secondary")
        btn_actualizar.clicked.connect(self._cargar_datos)
        toolbar.addWidget(btn_actualizar)
        
        layout.addLayout(toolbar)
        
        # Tabla de cargas
        self.tabla = ModernTable([
            "Fecha",
            "Equipo",
            "Litros",
            "Precio/L",
            "Total",
            "Horómetro",
            "Eficiencia",
            "Acciones"
        ])
        self.tabla.setMinimumHeight(400)
        layout.addWidget(self.tabla)
        
        # Resumen
        resumen_frame = QFrame()
        resumen_frame.setProperty("class", "card")
        resumen_layout = QHBoxLayout(resumen_frame)
        
        self.label_total_litros = QLabel("Total Litros: 0.0 L")
        self.label_total_litros.setStyleSheet(f"color: {AppTheme.COLORS['text_primary']}; font-weight: bold;")
        resumen_layout.addWidget(self.label_total_litros)
        
        self.label_total_costo = QLabel("Total Costo: $0.00")
        self.label_total_costo.setStyleSheet(f"color: {AppTheme.COLORS['text_primary']}; font-weight: bold;")
        resumen_layout.addWidget(self.label_total_costo)
        
        self.label_promedio_eficiencia = QLabel("Eficiencia Promedio: N/A")
        self.label_promedio_eficiencia.setStyleSheet(f"color: {AppTheme.COLORS['text_primary']}; font-weight: bold;")
        resumen_layout.addWidget(self.label_promedio_eficiencia)
        
        resumen_layout.addStretch()
        
        layout.addWidget(resumen_frame)
    
    def _cargar_equipos(self):
        """Carga la lista de equipos en el combo"""
        try:
            equipos = self.fm.obtener_equipos()
            self.combo_equipo.clear()
            self.combo_equipo.addItem("Todos los equipos", None)
            
            for equipo in equipos:
                nombre = equipo.get("nombre", "Sin nombre")
                equipo_id = equipo.get("id")
                self.combo_equipo.addItem(nombre, equipo_id)
                
        except Exception as e:
            logger.error(f"Error cargando equipos: {e}", exc_info=True)
    
    def _cargar_datos(self):
        """Carga las cargas de combustible desde Firebase"""
        try:
            logger.info("Cargando cargas de combustible...")
            
            # Cargar equipos si el combo está vacío
            if self.combo_equipo.count() == 1:
                self._cargar_equipos()
            
            # Obtener equipo seleccionado
            equipo_id = self.combo_equipo.currentData()
            
            # Obtener cargas de combustible
            cargas = self.fm.obtener_cargas_combustible(equipo_id=equipo_id)
            
            # Limpiar tabla
            self.tabla.clear_table()
            
            # Totales
            total_litros = 0.0
            total_costo = 0.0
            eficiencias = []
            
            # Poblar tabla
            for carga in cargas:
                fecha = carga.get("fecha", "")
                equipo_nombre = carga.get("equipo_nombre", "Desconocido")
                litros = float(carga.get("litros", 0))
                precio_litro = float(carga.get("precio_litro", 0))
                costo_total = float(carga.get("costo_total", 0))
                horometro = carga.get("horometro_actual", "N/A")
                
                # Calcular eficiencia si hay datos de horómetro
                eficiencia_str = "N/A"
                if carga.get("horometro_actual") and carga.get("horometro_anterior"):
                    horas = float(carga["horometro_actual"]) - float(carga["horometro_anterior"])
                    if horas > 0:
                        eficiencia = litros / horas
                        eficiencia_str = f"{eficiencia:.2f} L/h"
                        eficiencias.append(eficiencia)
                
                # Crear botones de acción
                btn_editar = QPushButton("✏️")
                btn_editar.setProperty("class", "secondary")
                btn_editar.setMaximumWidth(40)
                btn_editar.clicked.connect(lambda checked, c=carga: self._editar_carga(c))
                
                btn_eliminar = QPushButton("🗑️")
                btn_eliminar.setProperty("class", "danger")
                btn_eliminar.setMaximumWidth(40)
                btn_eliminar.clicked.connect(lambda checked, c=carga: self._eliminar_carga(c))
                
                # Añadir fila
                row = self.tabla.rowCount()
                self.tabla.insertRow(row)
                
                self.tabla.setItem(row, 0, QTableWidgetItem(fecha))
                self.tabla.setItem(row, 1, QTableWidgetItem(equipo_nombre))
                self.tabla.setItem(row, 2, QTableWidgetItem(f"{litros:.2f}"))
                self.tabla.setItem(row, 3, QTableWidgetItem(f"${precio_litro:.2f}"))
                self.tabla.setItem(row, 4, QTableWidgetItem(f"${costo_total:.2f}"))
                self.tabla.setItem(row, 5, QTableWidgetItem(str(horometro)))
                self.tabla.setItem(row, 6, QTableWidgetItem(eficiencia_str))
                
                # Widget contenedor para botones
                acciones_widget = QWidget()
                acciones_layout = QHBoxLayout(acciones_widget)
                acciones_layout.setContentsMargins(4, 4, 4, 4)
                acciones_layout.addWidget(btn_editar)
                acciones_layout.addWidget(btn_eliminar)
                self.tabla.setCellWidget(row, 7, acciones_widget)
                
                # Actualizar totales
                total_litros += litros
                total_costo += costo_total
            
            # Actualizar labels de resumen
            self.label_total_litros.setText(f"Total Litros: {total_litros:.2f} L")
            self.label_total_costo.setText(f"Total Costo: ${total_costo:,.2f}")
            
            if eficiencias:
                promedio = sum(eficiencias) / len(eficiencias)
                self.label_promedio_eficiencia.setText(f"Eficiencia Promedio: {promedio:.2f} L/h")
            else:
                self.label_promedio_eficiencia.setText("Eficiencia Promedio: N/A")
            
            logger.info(f"Cargadas {len(cargas)} cargas de combustible")
            
        except Exception as e:
            logger.error(f"Error cargando cargas de combustible: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al cargar datos: {e}")
    
    def _nueva_carga(self):
        """Abre el diálogo para registrar una nueva carga"""
        dialog = DialogoCarga(self.fm, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._cargar_datos()
    
    def _editar_carga(self, carga):
        """Abre el diálogo para editar una carga existente"""
        dialog = DialogoCarga(self.fm, carga=carga, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._cargar_datos()
    
    def _eliminar_carga(self, carga):
        """Elimina una carga de combustible"""
        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro de eliminar la carga de combustible del {carga.get('fecha')}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                if self.fm.eliminar_carga_combustible(carga.get("id")):
                    QMessageBox.information(self, "Éxito", "Carga eliminada correctamente")
                    self._cargar_datos()
                else:
                    QMessageBox.warning(self, "Error", "No se pudo eliminar la carga")
            except Exception as e:
                logger.error(f"Error eliminando carga: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Error al eliminar: {e}")


class DialogoCarga(QDialog):
    """
    Diálogo para crear/editar cargas de combustible
    """
    
    def __init__(self, firebase_manager, carga=None, parent=None):
        super().__init__(parent)
        self.fm = firebase_manager
        self.carga = carga
        self.es_edicion = carga is not None
        
        self.setWindowTitle("Editar Carga" if self.es_edicion else "Nueva Carga de Combustible")
        self.setMinimumWidth(500)
        
        self._crear_interfaz()
        
        if self.es_edicion:
            self._cargar_datos_carga()
    
    def _crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Fecha
        self.date_fecha = QDateEdit()
        self.date_fecha.setDate(QDate.currentDate())
        self.date_fecha.setCalendarPopup(True)
        form_layout.addRow("Fecha:", self.date_fecha)
        
        # Equipo
        self.combo_equipo = QComboBox()
        self.combo_equipo.setMinimumWidth(300)
        self._cargar_equipos()
        form_layout.addRow("Equipo:", self.combo_equipo)
        
        # Litros
        self.spin_litros = QDoubleSpinBox()
        self.spin_litros.setRange(0, 10000)
        self.spin_litros.setDecimals(2)
        self.spin_litros.setSuffix(" L")
        self.spin_litros.valueChanged.connect(self._calcular_total)
        form_layout.addRow("Litros:", self.spin_litros)
        
        # Precio por litro
        self.spin_precio = QDoubleSpinBox()
        self.spin_precio.setRange(0, 1000)
        self.spin_precio.setDecimals(2)
        self.spin_precio.setPrefix("$ ")
        self.spin_precio.valueChanged.connect(self._calcular_total)
        form_layout.addRow("Precio/Litro:", self.spin_precio)
        
        # Total (calculado)
        self.label_total = QLabel("$0.00")
        self.label_total.setStyleSheet(f"color: {AppTheme.COLORS['primary']}; font-weight: bold; font-size: 16px;")
        form_layout.addRow("Costo Total:", self.label_total)
        
        # Horómetro anterior
        self.spin_horometro_ant = QDoubleSpinBox()
        self.spin_horometro_ant.setRange(0, 999999)
        self.spin_horometro_ant.setDecimals(1)
        self.spin_horometro_ant.setSuffix(" h")
        form_layout.addRow("Horómetro Anterior:", self.spin_horometro_ant)
        
        # Horómetro actual
        self.spin_horometro_act = QDoubleSpinBox()
        self.spin_horometro_act.setRange(0, 999999)
        self.spin_horometro_act.setDecimals(1)
        self.spin_horometro_act.setSuffix(" h")
        form_layout.addRow("Horómetro Actual:", self.spin_horometro_act)
        
        # Observaciones
        self.text_observaciones = QTextEdit()
        self.text_observaciones.setMaximumHeight(80)
        self.text_observaciones.setPlaceholderText("Observaciones adicionales...")
        form_layout.addRow("Observaciones:", self.text_observaciones)
        
        layout.addLayout(form_layout)
        
        # Botones
        botones_layout = QHBoxLayout()
        botones_layout.addStretch()
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setProperty("class", "secondary")
        btn_cancelar.clicked.connect(self.reject)
        botones_layout.addWidget(btn_cancelar)
        
        btn_guardar = QPushButton("Guardar")
        btn_guardar.setProperty("class", "primary")
        btn_guardar.clicked.connect(self._guardar)
        botones_layout.addWidget(btn_guardar)
        
        layout.addLayout(botones_layout)
    
    def _cargar_equipos(self):
        """Carga la lista de equipos"""
        try:
            equipos = self.fm.obtener_equipos()
            for equipo in equipos:
                nombre = equipo.get("nombre", "Sin nombre")
                equipo_id = equipo.get("id")
                self.combo_equipo.addItem(nombre, equipo_id)
        except Exception as e:
            logger.error(f"Error cargando equipos: {e}", exc_info=True)
    
    def _cargar_datos_carga(self):
        """Carga los datos de la carga en el formulario"""
        if not self.carga:
            return
        
        try:
            # Fecha
            fecha_str = self.carga.get("fecha", "")
            if fecha_str:
                fecha = QDate.fromString(fecha_str, "yyyy-MM-dd")
                self.date_fecha.setDate(fecha)
            
            # Equipo
            equipo_id = self.carga.get("equipo_id")
            index = self.combo_equipo.findData(equipo_id)
            if index >= 0:
                self.combo_equipo.setCurrentIndex(index)
            
            # Valores
            self.spin_litros.setValue(float(self.carga.get("litros", 0)))
            self.spin_precio.setValue(float(self.carga.get("precio_litro", 0)))
            self.spin_horometro_ant.setValue(float(self.carga.get("horometro_anterior", 0)))
            self.spin_horometro_act.setValue(float(self.carga.get("horometro_actual", 0)))
            self.text_observaciones.setPlainText(self.carga.get("observaciones", ""))
            
        except Exception as e:
            logger.error(f"Error cargando datos de carga: {e}", exc_info=True)
    
    def _calcular_total(self):
        """Calcula el costo total"""
        litros = self.spin_litros.value()
        precio = self.spin_precio.value()
        total = litros * precio
        self.label_total.setText(f"${total:.2f}")
    
    def _guardar(self):
        """Guarda la carga de combustible"""
        try:
            # Validar equipo seleccionado
            if self.combo_equipo.currentIndex() < 0:
                QMessageBox.warning(self, "Error", "Debe seleccionar un equipo")
                return
            
            # Validar litros
            if self.spin_litros.value() <= 0:
                QMessageBox.warning(self, "Error", "Los litros deben ser mayor a 0")
                return
            
            # Preparar datos
            equipo_id = self.combo_equipo.currentData()
            equipo_nombre = self.combo_equipo.currentText()
            
            datos = {
                "fecha": self.date_fecha.date().toString("yyyy-MM-dd"),
                "equipo_id": str(equipo_id),
                "equipo_nombre": equipo_nombre,
                "litros": self.spin_litros.value(),
                "precio_litro": self.spin_precio.value(),
                "costo_total": self.spin_litros.value() * self.spin_precio.value(),
                "horometro_anterior": self.spin_horometro_ant.value() if self.spin_horometro_ant.value() > 0 else None,
                "horometro_actual": self.spin_horometro_act.value() if self.spin_horometro_act.value() > 0 else None,
                "observaciones": self.text_observaciones.toPlainText().strip()
            }
            
            # Guardar
            if self.es_edicion:
                success = self.fm.editar_carga_combustible(self.carga.get("id"), datos)
                mensaje = "Carga actualizada correctamente"
            else:
                success = self.fm.agregar_carga_combustible(datos)
                mensaje = "Carga registrada correctamente"
            
            if success:
                QMessageBox.information(self, "Éxito", mensaje)
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "No se pudo guardar la carga")
                
        except Exception as e:
            logger.error(f"Error guardando carga: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al guardar: {e}")
