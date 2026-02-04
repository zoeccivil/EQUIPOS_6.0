"""
Cuentas por Cobrar para EQUIPOS 6.0 MODERN
Seguimiento de pagos pendientes y cobranza
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QDateEdit, QComboBox,
    QDoubleSpinBox, QTextEdit, QMessageBox, QGridLayout
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from app_theme import AppTheme, ModernTable, KPICard
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CuentasPorCobrar(QWidget):
    """
    Gestión de cuentas por cobrar y cobranza
    """
    
    def __init__(self, firebase_manager, config, parent=None):
        super().__init__(parent)
        self.fm = firebase_manager
        self.config = config
        
        self._crear_interfaz()
        self._cargar_datos()
    
    def _crear_interfaz(self):
        """Crea la interfaz de cuentas por cobrar"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Título
        titulo = QLabel("💳 Cuentas por Cobrar")
        titulo_font = QFont("Inter", 24)
        titulo_font.setBold(True)
        titulo.setFont(titulo_font)
        titulo.setStyleSheet(f"color: {AppTheme.COLORS['primary']};")
        layout.addWidget(titulo)
        
        # Subtítulo
        subtitulo = QLabel("Seguimiento de pagos pendientes y cobranza")
        subtitulo.setStyleSheet(f"color: {AppTheme.COLORS['text_secondary']}; font-size: 14px;")
        layout.addWidget(subtitulo)
        
        # KPIs de cobranza (grid 1x4)
        kpis_container = QFrame()
        kpis_layout = QGridLayout(kpis_container)
        kpis_layout.setSpacing(16)
        
        self.kpi_pendiente = KPICard("Por Cobrar", "$0.00", color=AppTheme.COLORS["warning"])
        self.kpi_vencido = KPICard("Vencido", "$0.00", color=AppTheme.COLORS["danger"])
        self.kpi_cobrado = KPICard("Cobrado (Mes)", "$0.00", color=AppTheme.COLORS["success"])
        self.kpi_tasa = KPICard("Tasa de Recuperación", "0%", color=AppTheme.COLORS["primary"])
        
        kpis_layout.addWidget(self.kpi_pendiente, 0, 0)
        kpis_layout.addWidget(self.kpi_vencido, 0, 1)
        kpis_layout.addWidget(self.kpi_cobrado, 0, 2)
        kpis_layout.addWidget(self.kpi_tasa, 0, 3)
        
        layout.addWidget(kpis_container)
        
        # Barra de herramientas
        toolbar = QHBoxLayout()
        
        # Filtro por estado
        filtro_label = QLabel("Estado:")
        filtro_label.setStyleSheet(f"color: {AppTheme.COLORS['text_secondary']};")
        toolbar.addWidget(filtro_label)
        
        self.combo_estado = QComboBox()
        self.combo_estado.addItems([
            "Todas",
            "Pendientes",
            "Vencidas",
            "Por Vencer (7 días)",
            "Pagadas"
        ])
        self.combo_estado.setMinimumWidth(180)
        self.combo_estado.currentIndexChanged.connect(self._cargar_datos)
        toolbar.addWidget(self.combo_estado)
        
        toolbar.addStretch()
        
        btn_actualizar = QPushButton("🔄 Actualizar")
        btn_actualizar.setProperty("class", "secondary")
        btn_actualizar.clicked.connect(self._cargar_datos)
        toolbar.addWidget(btn_actualizar)
        
        btn_registrar_pago = QPushButton("💰 Registrar Pago")
        btn_registrar_pago.setProperty("class", "primary")
        btn_registrar_pago.clicked.connect(self._registrar_pago)
        toolbar.addWidget(btn_registrar_pago)
        
        layout.addLayout(toolbar)
        
        # Tabla de cuentas por cobrar
        self.tabla = ModernTable([
            "Cliente",
            "Equipo",
            "Fecha Alquiler",
            "Fecha Vencimiento",
            "Monto",
            "Pagado",
            "Saldo",
            "Estado",
            "Días",
            "Acciones"
        ])
        self.tabla.setMinimumHeight(400)
        layout.addWidget(self.tabla)
    
    def _cargar_datos(self):
        """Carga las cuentas por cobrar desde Firebase"""
        try:
            logger.info("Cargando cuentas por cobrar...")
            
            # Obtener alquileres tipo "Ingreso"
            filtros = {"tipo": "Ingreso"}
            alquileres = self.fm.obtener_alquileres(filtros)
            
            # Filtrar según estado seleccionado
            estado_filtro = self.combo_estado.currentText()
            
            # Limpiar tabla
            self.tabla.clear_table()
            
            # Totales
            total_pendiente = 0.0
            total_vencido = 0.0
            total_cobrado_mes = 0.0
            total_original = 0.0
            
            hoy = datetime.now().date()
            inicio_mes = hoy.replace(day=1)
            
            for alquiler in alquileres:
                monto = float(alquiler.get("monto", 0))
                total_original += monto
                
                # Obtener abonos del alquiler
                abonos = self.fm.obtener_abonos({"alquiler_id": alquiler.get("id")})
                total_abonado = sum(float(a.get("monto", 0)) for a in abonos)
                saldo = monto - total_abonado
                
                # Determinar estado
                pagado = alquiler.get("pagado", False) or saldo <= 0
                
                # Fecha de vencimiento (30 días después del alquiler)
                fecha_alquiler_str = alquiler.get("fecha", "")
                if fecha_alquiler_str:
                    fecha_alquiler = datetime.strptime(fecha_alquiler_str, "%Y-%m-%d").date()
                    fecha_vencimiento = fecha_alquiler + timedelta(days=30)
                    dias_diff = (hoy - fecha_vencimiento).days
                else:
                    fecha_vencimiento = None
                    dias_diff = 0
                
                # Determinar estado y aplicar filtros
                if pagado:
                    estado = "Pagado"
                    estado_tipo = "success"
                    if fecha_vencimiento and fecha_vencimiento >= inicio_mes:
                        total_cobrado_mes += monto
                elif fecha_vencimiento and dias_diff > 0:
                    estado = "Vencido"
                    estado_tipo = "danger"
                    total_vencido += saldo
                    total_pendiente += saldo
                elif fecha_vencimiento and dias_diff > -7:
                    estado = "Por Vencer"
                    estado_tipo = "warning"
                    total_pendiente += saldo
                else:
                    estado = "Pendiente"
                    estado_tipo = "warning"
                    total_pendiente += saldo
                
                # Aplicar filtro de estado
                if estado_filtro == "Pendientes" and pagado:
                    continue
                elif estado_filtro == "Vencidas" and estado != "Vencido":
                    continue
                elif estado_filtro == "Por Vencer (7 días)" and estado != "Por Vencer":
                    continue
                elif estado_filtro == "Pagadas" and not pagado:
                    continue
                
                # Añadir a la tabla
                cliente_nombre = alquiler.get("cliente_nombre", "Desconocido")
                equipo_nombre = alquiler.get("equipo_nombre", "Desconocido")
                fecha_alq_str = fecha_alquiler_str if fecha_alquiler_str else "N/A"
                fecha_venc_str = fecha_vencimiento.strftime("%Y-%m-%d") if fecha_vencimiento else "N/A"
                
                # Crear botones de acción
                btn_ver = QPushButton("👁️")
                btn_ver.setProperty("class", "secondary")
                btn_ver.setMaximumWidth(40)
                btn_ver.setToolTip("Ver detalles")
                btn_ver.clicked.connect(lambda checked, a=alquiler: self._ver_detalles(a))
                
                btn_pagar = QPushButton("💰")
                btn_pagar.setProperty("class", "success")
                btn_pagar.setMaximumWidth(40)
                btn_pagar.setToolTip("Registrar pago")
                btn_pagar.setEnabled(not pagado)
                btn_pagar.clicked.connect(lambda checked, a=alquiler: self._registrar_pago(a))
                
                # Añadir fila
                row = self.tabla.rowCount()
                self.tabla.insertRow(row)
                
                self.tabla.setItem(row, 0, QTableWidgetItem(cliente_nombre))
                self.tabla.setItem(row, 1, QTableWidgetItem(equipo_nombre))
                self.tabla.setItem(row, 2, QTableWidgetItem(fecha_alq_str))
                self.tabla.setItem(row, 3, QTableWidgetItem(fecha_venc_str))
                self.tabla.setItem(row, 4, QTableWidgetItem(f"${monto:,.2f}"))
                self.tabla.setItem(row, 5, QTableWidgetItem(f"${total_abonado:,.2f}"))
                self.tabla.setItem(row, 6, QTableWidgetItem(f"${saldo:,.2f}"))
                
                # Estado con color
                estado_item = QTableWidgetItem(estado)
                if estado_tipo == "success":
                    estado_item.setForeground(Qt.GlobalColor.green)
                elif estado_tipo == "danger":
                    estado_item.setForeground(Qt.GlobalColor.red)
                else:
                    estado_item.setForeground(Qt.GlobalColor.yellow)
                self.tabla.setItem(row, 7, estado_item)
                
                dias_str = f"{abs(dias_diff)} días" if fecha_vencimiento else "N/A"
                if dias_diff > 0:
                    dias_str = f"+{dias_str}"
                elif dias_diff < 0:
                    dias_str = f"-{abs(dias_diff)} días"
                self.tabla.setItem(row, 8, QTableWidgetItem(dias_str))
                
                # Widget contenedor para botones
                acciones_widget = QWidget()
                acciones_layout = QHBoxLayout(acciones_widget)
                acciones_layout.setContentsMargins(4, 4, 4, 4)
                acciones_layout.addWidget(btn_ver)
                acciones_layout.addWidget(btn_pagar)
                self.tabla.setCellWidget(row, 9, acciones_widget)
            
            # Actualizar KPIs
            self.kpi_pendiente.update_value(f"${total_pendiente:,.2f}")
            self.kpi_vencido.update_value(f"${total_vencido:,.2f}")
            self.kpi_cobrado.update_value(f"${total_cobrado_mes:,.2f}")
            
            # Calcular tasa de recuperación
            if total_original > 0:
                tasa = (total_cobrado_mes / total_original) * 100
                self.kpi_tasa.update_value(f"{tasa:.1f}%")
            else:
                self.kpi_tasa.update_value("0%")
            
            logger.info(f"Cargadas {self.tabla.rowCount()} cuentas por cobrar")
            
        except Exception as e:
            logger.error(f"Error cargando cuentas por cobrar: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al cargar datos: {e}")
    
    def _registrar_pago(self, alquiler=None):
        """Abre el diálogo para registrar un pago"""
        if alquiler is None:
            QMessageBox.information(
                self,
                "Información",
                "Seleccione un alquiler de la tabla para registrar el pago"
            )
            return
        
        dialog = DialogoPago(self.fm, alquiler, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._cargar_datos()
    
    def _ver_detalles(self, alquiler):
        """Muestra los detalles y abonos de un alquiler"""
        try:
            # Obtener abonos
            abonos = self.fm.obtener_abonos({"alquiler_id": alquiler.get("id")})
            
            monto = float(alquiler.get("monto", 0))
            total_abonado = sum(float(a.get("monto", 0)) for a in abonos)
            saldo = monto - total_abonado
            
            # Formatear información
            info = f"""
<h3>Detalles del Alquiler</h3>
<p><b>Cliente:</b> {alquiler.get('cliente_nombre', 'N/A')}</p>
<p><b>Equipo:</b> {alquiler.get('equipo_nombre', 'N/A')}</p>
<p><b>Fecha:</b> {alquiler.get('fecha', 'N/A')}</p>
<p><b>Monto Total:</b> ${monto:,.2f}</p>
<p><b>Total Abonado:</b> ${total_abonado:,.2f}</p>
<p><b>Saldo Pendiente:</b> ${saldo:,.2f}</p>

<h3>Historial de Pagos ({len(abonos)})</h3>
"""
            
            if abonos:
                info += "<ul>"
                for abono in sorted(abonos, key=lambda x: x.get("fecha", ""), reverse=True):
                    fecha = abono.get("fecha", "N/A")
                    monto_abono = float(abono.get("monto", 0))
                    info += f"<li>{fecha}: ${monto_abono:,.2f}</li>"
                info += "</ul>"
            else:
                info += "<p><i>No hay pagos registrados</i></p>"
            
            # Mostrar diálogo
            msg = QMessageBox(self)
            msg.setWindowTitle("Estado de Cuenta")
            msg.setTextFormat(Qt.TextFormat.RichText)
            msg.setText(info)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()
            
        except Exception as e:
            logger.error(f"Error mostrando detalles: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al cargar detalles: {e}")


class DialogoPago(QDialog):
    """
    Diálogo para registrar un pago/abono
    """
    
    def __init__(self, firebase_manager, alquiler, parent=None):
        super().__init__(parent)
        self.fm = firebase_manager
        self.alquiler = alquiler
        
        self.setWindowTitle("Registrar Pago")
        self.setMinimumWidth(450)
        
        self._crear_interfaz()
    
    def _crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Información del alquiler
        info_frame = QFrame()
        info_frame.setProperty("class", "card")
        info_layout = QVBoxLayout(info_frame)
        
        info_label = QLabel(f"""
<b>Cliente:</b> {self.alquiler.get('cliente_nombre', 'N/A')}<br>
<b>Equipo:</b> {self.alquiler.get('equipo_nombre', 'N/A')}<br>
<b>Fecha Alquiler:</b> {self.alquiler.get('fecha', 'N/A')}
        """)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_layout.addWidget(info_label)
        
        layout.addWidget(info_frame)
        
        # Calcular saldo
        monto_total = float(self.alquiler.get("monto", 0))
        abonos = self.fm.obtener_abonos({"alquiler_id": self.alquiler.get("id")})
        total_abonado = sum(float(a.get("monto", 0)) for a in abonos)
        saldo = monto_total - total_abonado
        
        # Mostrar saldo
        saldo_label = QLabel(f"Saldo Pendiente: ${saldo:,.2f}")
        saldo_label.setStyleSheet(f"color: {AppTheme.COLORS['warning']}; font-weight: bold; font-size: 16px; padding: 12px;")
        saldo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(saldo_label)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Fecha
        self.date_fecha = QDateEdit()
        self.date_fecha.setDate(QDate.currentDate())
        self.date_fecha.setCalendarPopup(True)
        form_layout.addRow("Fecha de Pago:", self.date_fecha)
        
        # Monto
        self.spin_monto = QDoubleSpinBox()
        self.spin_monto.setRange(0, saldo)
        self.spin_monto.setValue(saldo)
        self.spin_monto.setDecimals(2)
        self.spin_monto.setPrefix("$ ")
        form_layout.addRow("Monto del Pago:", self.spin_monto)
        
        # Método de pago
        self.combo_metodo = QComboBox()
        self.combo_metodo.addItems([
            "Efectivo",
            "Transferencia",
            "Cheque",
            "Depósito",
            "Otro"
        ])
        form_layout.addRow("Método de Pago:", self.combo_metodo)
        
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
        
        btn_guardar = QPushButton("Registrar Pago")
        btn_guardar.setProperty("class", "primary")
        btn_guardar.clicked.connect(self._guardar)
        botones_layout.addWidget(btn_guardar)
        
        layout.addLayout(botones_layout)
    
    def _guardar(self):
        """Registra el pago"""
        try:
            # Validar monto
            monto = self.spin_monto.value()
            if monto <= 0:
                QMessageBox.warning(self, "Error", "El monto debe ser mayor a 0")
                return
            
            # Preparar datos del abono
            datos_abono = {
                "fecha": self.date_fecha.date().toString("yyyy-MM-dd"),
                "alquiler_id": self.alquiler.get("id"),
                "cliente_id": self.alquiler.get("cliente_id"),
                "monto": monto,
                "metodo_pago": self.combo_metodo.currentText(),
                "observaciones": self.text_observaciones.toPlainText().strip()
            }
            
            # Registrar abono
            abono_id = self.fm.agregar_abono(datos_abono)
            
            if abono_id:
                # Verificar si está completamente pagado
                monto_total = float(self.alquiler.get("monto", 0))
                abonos = self.fm.obtener_abonos({"alquiler_id": self.alquiler.get("id")})
                total_abonado = sum(float(a.get("monto", 0)) for a in abonos) + monto
                
                # Si está pagado, actualizar el alquiler
                if total_abonado >= monto_total:
                    self.fm.editar_alquiler(self.alquiler.get("id"), {"pagado": True})
                
                QMessageBox.information(self, "Éxito", "Pago registrado correctamente")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "No se pudo registrar el pago")
                
        except Exception as e:
            logger.error(f"Error registrando pago: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al registrar pago: {e}")
