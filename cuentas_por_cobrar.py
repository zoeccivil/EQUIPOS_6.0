<<<<<<< Updated upstream
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
=======
# cuentas_por_cobrar.py

"""
Cuentas por Cobrar - Gestión de cobros y seguimiento de pagos pendientes
Permite visualizar deudas, enviar recordatorios y gestionar estados de cuenta
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QDateEdit,
    QComboBox, QMessageBox, QAbstractItemView, QGroupBox, QFrame,
    QTextEdit, QFileDialog, QProgressBar, QCheckBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QBrush
import logging
from datetime import datetime, timedelta
from firebase_manager import FirebaseManager

logger = logging.getLogger(__name__)

# Estilos CSS
CUENTAS_STYLE = """
QWidget {
    background-color: #F3F4F6;
    font-family: 'Segoe UI';
}
QLabel[class="title"] {
    font-size: 20pt;
    font-weight: bold;
    color: #1F2937;
}
QLabel[class="deuda-label"] {
    font-size: 11pt;
    color: #6B7280;
    font-weight: 500;
}
QLabel[class="deuda-value"] {
    font-size: 24pt;
    font-weight: bold;
}
QLabel[class="deuda-vencida"] {
    color: #DC2626;
}
QLabel[class="deuda-por-vencer"] {
    color: #F59E0B;
}
QLabel[class="deuda-al-dia"] {
    color: #059669;
}
QFrame[class="deuda-card"] {
    background-color: #FFFFFF;
    border: 2px solid #E5E7EB;
    border-radius: 12px;
    padding: 20px;
}
QFrame[class="deuda-card-vencida"] {
    background-color: #FFFFFF;
    border: 3px solid #DC2626;
    border-radius: 12px;
    padding: 20px;
}
QFrame[class="deuda-card-advertencia"] {
    background-color: #FFFFFF;
    border: 3px solid #F59E0B;
    border-radius: 12px;
    padding: 20px;
}
QPushButton {
    background-color: #F59E0B;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 18px;
    font-size: 10pt;
    font-weight: 600;
    min-height: 25px;
}
QPushButton:hover {
    background-color: #D97706;
}
QPushButton:pressed {
    background-color: #B45309;
}
QPushButton[class="secondary"] {
    background-color: #E5E7EB;
    color: #374151;
}
QPushButton[class="secondary"]:hover {
    background-color: #D1D5DB;
}
QPushButton[class="danger"] {
    background-color: #DC2626;
    color: white;
}
QPushButton[class="danger"]:hover {
    background-color: #B91C1C;
}
QPushButton[class="success"] {
    background-color: #059669;
    color: white;
}
QPushButton[class="success"]:hover {
    background-color: #047857;
}
QTableWidget {
    background-color: #FFFFFF;
    alternate-background-color: #F9FAFB;
    gridline-color: #E5E7EB;
    selection-background-color: #FEF3C7;
    selection-color: #1F2937;
    border: 1px solid #E5E7EB;
    border-radius: 6px;
}
QTableWidget::item {
    padding: 8px;
}
QHeaderView::section {
    background-color: #1F2937;
    color: #FFFFFF;
    padding: 10px;
    border: none;
    font-weight: 600;
}
QLineEdit, QDoubleSpinBox, QDateEdit, QComboBox, QTextEdit {
    background-color: #FFFFFF;
    border: 2px solid #E5E7EB;
    border-radius: 6px;
    padding: 8px 12px;
    color: #1F2937;
    font-size: 10pt;
}
QLineEdit:hover, QDoubleSpinBox:hover, QDateEdit:hover, QComboBox:hover {
    border: 2px solid #F59E0B;
}
QLineEdit:focus, QDoubleSpinBox:focus, QDateEdit:focus, QComboBox:focus {
    border: 2px solid #F59E0B;
}
QGroupBox {
    background-color: #FFFFFF;
    border: 2px solid #E5E7EB;
    border-radius: 10px;
    margin-top: 14px;
    padding: 15px;
    font-weight: 600;
    font-size: 12pt;
    color: #1F2937;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 8px;
    background-color: #FFFFFF;
}
QProgressBar {
    border: 2px solid #E5E7EB;
    border-radius: 6px;
    text-align: center;
    background-color: #F3F4F6;
    height: 25px;
}
QProgressBar::chunk {
    background-color: #F59E0B;
    border-radius: 4px;
}
"""


class DeudaCard(QFrame):
    """Tarjeta de resumen de deuda"""
    
    def __init__(self, titulo, monto, moneda, tipo="normal", parent=None):
        super().__init__(parent)
        
        if tipo == "vencida":
            self.setProperty("class", "deuda-card-vencida")
        elif tipo == "advertencia":
            self.setProperty("class", "deuda-card-advertencia")
        else:
            self.setProperty("class", "deuda-card")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Título
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setProperty("class", "deuda-label")
        layout.addWidget(lbl_titulo)
        
        # Monto
        self.lbl_monto = QLabel(f"{moneda} {monto:,.2f}")
        self.lbl_monto.setProperty("class", "deuda-value")
        
        if tipo == "vencida":
            self.lbl_monto.setProperty("class", "deuda-value deuda-vencida")
        elif tipo == "advertencia":
            self.lbl_monto.setProperty("class", "deuda-value deuda-por-vencer")
        else:
            self.lbl_monto.setProperty("class", "deuda-value deuda-al-dia")
        
        layout.addWidget(self.lbl_monto)
        
        layout.addStretch()
    
    def actualizar(self, monto, moneda):
        self.lbl_monto.setText(f"{moneda} {monto:,.2f}")


class CuentasPorCobrar(QWidget):
    """Widget principal para gestión de cuentas por cobrar"""
    
    def __init__(self, fm: FirebaseManager, config: dict, parent=None):
        super().__init__(parent)
        self.fm = fm
        self.config = config
        self.moneda = config.get('app', {}).get('moneda', 'RD$')
        
        self.cuentas = []
        self.clientes_mapa = {}
        
        self.setStyleSheet(CUENTAS_STYLE)
        
        self._init_ui()
        self._cargar_clientes()
        self._cargar_datos()
    
    def _init_ui(self):
        """Inicializa la interfaz"""
>>>>>>> Stashed changes
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
<<<<<<< Updated upstream
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
        self.kpi_cobrado = KPICard("Total Cobrado", "$0.00", color=AppTheme.COLORS["success"])
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
=======
        # Header
        header_layout = QHBoxLayout()
        
        titulo = QLabel("💳 Cuentas por Cobrar")
        titulo.setProperty("class", "title")
        header_layout.addWidget(titulo)
        
        header_layout.addStretch()
        
        # Filtros
        lbl_estado = QLabel("Estado:")
        lbl_estado.setStyleSheet("font-weight: 600; color: #374151;")
        header_layout.addWidget(lbl_estado)
        
        self.combo_estado = QComboBox()
        self.combo_estado.addItem("Todas", "todas")
        self.combo_estado.addItem("Vencidas", "vencida")
        self.combo_estado.addItem("Por Vencer (7 días)", "por_vencer")
        self.combo_estado.addItem("Al Día", "al_dia")
        self.combo_estado.addItem("Pagadas", "pagada")
        self.combo_estado.currentIndexChanged.connect(self._aplicar_filtros)
        header_layout.addWidget(self.combo_estado)
        
        lbl_cliente = QLabel("Cliente:")
        lbl_cliente.setStyleSheet("font-weight: 600; color: #374151;")
        header_layout.addWidget(lbl_cliente)
        
        self.combo_cliente = QComboBox()
        self.combo_cliente.addItem("Todos", None)
        self.combo_cliente.currentIndexChanged.connect(self._aplicar_filtros)
        header_layout.addWidget(self.combo_cliente)
        
        btn_actualizar = QPushButton("🔄 Actualizar")
        btn_actualizar.clicked.connect(self._cargar_datos)
        header_layout.addWidget(btn_actualizar)
        
        layout.addLayout(header_layout)
        
        # === RESUMEN DE DEUDAS ===
        resumen_layout = QHBoxLayout()
        resumen_layout.setSpacing(15)
        
        self.card_total = DeudaCard("💰 Total por Cobrar", 0, self.moneda)
        resumen_layout.addWidget(self.card_total)
        
        self.card_vencida = DeudaCard("🚨 Deuda Vencida", 0, self.moneda, tipo="vencida")
        resumen_layout.addWidget(self.card_vencida)
        
        self.card_por_vencer = DeudaCard("⚠️ Por Vencer (7 días)", 0, self.moneda, tipo="advertencia")
        resumen_layout.addWidget(self.card_por_vencer)
        
        self.card_cobrado_mes = DeudaCard("✅ Cobrado Este Mes", 0, self.moneda, tipo="normal")
        resumen_layout.addWidget(self.card_cobrado_mes)
        
        layout.addLayout(resumen_layout)
        
        # === TABLA DE CUENTAS ===
        grupo_tabla = QGroupBox("📋 Detalle de Cuentas")
        layout_tabla = QVBoxLayout(grupo_tabla)
        
        # Botones de acción
        botones_layout = QHBoxLayout()
        
        btn_registrar_pago = QPushButton("💵 Registrar Pago")
        btn_registrar_pago.setProperty("class", "success")
        btn_registrar_pago.clicked.connect(self._registrar_pago)
        botones_layout.addWidget(btn_registrar_pago)
        
        btn_enviar_recordatorio = QPushButton("📧 Enviar Recordatorio")
        btn_enviar_recordatorio.clicked.connect(self._enviar_recordatorio)
        botones_layout.addWidget(btn_enviar_recordatorio)
        
        btn_estado_cuenta = QPushButton("📄 Estado de Cuenta")
        btn_estado_cuenta.setProperty("class", "secondary")
        btn_estado_cuenta.clicked.connect(self._generar_estado_cuenta)
        botones_layout.addWidget(btn_estado_cuenta)
        
        btn_exportar = QPushButton("📊 Exportar Excel")
        btn_exportar.setProperty("class", "secondary")
        btn_exportar.clicked.connect(self._exportar_excel)
        botones_layout.addWidget(btn_exportar)
        
        botones_layout.addStretch()
        layout_tabla.addLayout(botones_layout)
        
        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(9)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Cliente", "Factura", "Fecha Emisión", "Fecha Vencimiento",
            "Monto Total", "Pagado", "Saldo", "Estado"
        ])
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.itemDoubleClicked.connect(self._ver_detalle)
        layout_tabla.addWidget(self.tabla)
        
        layout.addWidget(grupo_tabla)
        
        # === PANEL DE MÉTRICAS ===
        metricas_group = QGroupBox("📊 Métricas de Cobranza")
        metricas_layout = QVBoxLayout(metricas_group)
        
        # Tasa de recuperación
        tasa_layout = QHBoxLayout()
        lbl_tasa = QLabel("Tasa de Recuperación (Este Mes):")
        lbl_tasa.setStyleSheet("font-weight: 600; color: #374151;")
        tasa_layout.addWidget(lbl_tasa)
        
        self.progress_tasa = QProgressBar()
        self.progress_tasa.setRange(0, 100)
        self.progress_tasa.setValue(0)
        self.progress_tasa.setFormat("%p%")
        tasa_layout.addWidget(self.progress_tasa)
        
        self.lbl_tasa_detalle = QLabel("0 / 0")
        self.lbl_tasa_detalle.setStyleSheet("color: #6B7280;")
        tasa_layout.addWidget(self.lbl_tasa_detalle)
        
        metricas_layout.addLayout(tasa_layout)
        
        # Edad promedio de deuda
        edad_layout = QHBoxLayout()
        lbl_edad = QLabel("Edad Promedio de Deuda:")
        lbl_edad.setStyleSheet("font-weight: 600; color: #374151;")
        edad_layout.addWidget(lbl_edad)
        
        self.lbl_edad_promedio = QLabel("0 días")
        self.lbl_edad_promedio.setStyleSheet("font-size: 12pt; font-weight: bold; color: #F59E0B;")
        edad_layout.addWidget(self.lbl_edad_promedio)
        edad_layout.addStretch()
        
        metricas_layout.addLayout(edad_layout)
        
        layout.addWidget(metricas_group)
    
    def _cargar_clientes(self):
        """Carga la lista de clientes"""
        try:
            clientes = self.fm.obtener_entidades(tipo="Cliente", activo=True)
            self.clientes_mapa = {str(c['id']): c['nombre'] for c in clientes}
            
            self.combo_cliente.clear()
            self.combo_cliente.addItem("Todos", None)
            
            for cid, nombre in sorted(self.clientes_mapa.items(), key=lambda x: x[1]):
                self.combo_cliente.addItem(nombre, cid)
                
        except Exception as e:
            logger.error(f"Error cargando clientes: {e}", exc_info=True)
>>>>>>> Stashed changes
    
    def _cargar_datos(self):
        """Carga las cuentas por cobrar desde Firebase"""
        try:
<<<<<<< Updated upstream
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
            total_cobrado = 0.0
            total_facturado = 0.0
            
            hoy = datetime.now().date()
            inicio_mes = hoy.replace(day=1)
            
            for alquiler in alquileres:
                monto = float(alquiler.get("monto", 0))
                total_facturado += monto
                
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
                    total_cobrado += total_abonado
                elif fecha_vencimiento and dias_diff > 0:
                    estado = "Vencido"
                    estado_tipo = "danger"
                    total_vencido += saldo
                    total_pendiente += saldo
                    total_cobrado += total_abonado
                elif fecha_vencimiento and dias_diff > -7:
                    estado = "Por Vencer"
                    estado_tipo = "warning"
                    total_pendiente += saldo
                    total_cobrado += total_abonado
                else:
                    estado = "Pendiente"
                    estado_tipo = "warning"
                    total_pendiente += saldo
                    total_cobrado += total_abonado
                
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
            self.kpi_cobrado.update_value(f"${total_cobrado:,.2f}")
            
            # Calcular tasa de recuperación (cobrado/facturado)
            if total_facturado > 0:
                tasa = (total_cobrado / total_facturado) * 100
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
=======
            # Obtener todos los alquileres con saldo pendiente
            alquileres = self.fm.obtener_alquileres({})
            
            self.cuentas = []
            
            for alquiler in alquileres:
                monto_total = float(alquiler.get('monto_total', 0))
                monto_pagado = float(alquiler.get('monto_pagado', 0))
                saldo = monto_total - monto_pagado
                
                # Solo incluir si hay saldo pendiente o fue pagado recientemente
                if saldo > 0 or (saldo == 0 and alquiler.get('fecha_ultimo_pago')):
                    fecha_vencimiento = alquiler.get('fecha_vencimiento_pago', alquiler.get('fecha_fin'))
                    
                    # Calcular estado
                    estado = self._calcular_estado(fecha_vencimiento, saldo)
                    
                    cuenta = {
                        'id': alquiler.get('id'),
                        'cliente_id': str(alquiler.get('cliente_id', '')),
                        'factura': alquiler.get('numero_factura', f"ALQ-{alquiler.get('id')}"),
                        'fecha_emision': alquiler.get('fecha_inicio', ''),
                        'fecha_vencimiento': fecha_vencimiento,
                        'monto_total': monto_total,
                        'monto_pagado': monto_pagado,
                        'saldo': saldo,
                        'estado': estado,
                        'alquiler': alquiler
                    }
                    
                    self.cuentas.append(cuenta)
            
            self._aplicar_filtros()
            
        except Exception as e:
            logger.error(f"Error cargando cuentas por cobrar: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al cargar datos:\n{e}")
    
    def _calcular_estado(self, fecha_vencimiento, saldo):
        """Calcula el estado de la cuenta"""
        if saldo == 0:
            return "pagada"
        
        if not fecha_vencimiento:
            return "sin_vencimiento"
        
        try:
            fecha_venc = datetime.strptime(fecha_vencimiento, "%Y-%m-%d")
            hoy = datetime.now()
            dias_diferencia = (fecha_venc - hoy).days
            
            if dias_diferencia < 0:
                return "vencida"
            elif dias_diferencia <= 7:
                return "por_vencer"
            else:
                return "al_dia"
        except:
            return "sin_vencimiento"
    
    def _aplicar_filtros(self):
        """Aplica filtros y actualiza la vista"""
        try:
            estado_filtro = self.combo_estado.currentData()
            cliente_id = self.combo_cliente.currentData()
            
            # Filtrar cuentas
            cuentas_filtradas = self.cuentas
            
            if estado_filtro != "todas":
                cuentas_filtradas = [c for c in cuentas_filtradas if c['estado'] == estado_filtro]
            
            if cliente_id:
                cuentas_filtradas = [c for c in cuentas_filtradas if c['cliente_id'] == cliente_id]
            
            # Actualizar resumen
            self._actualizar_resumen()
            
            # Actualizar tabla
            self._actualizar_tabla(cuentas_filtradas)
            
            # Actualizar métricas
            self._actualizar_metricas()
            
        except Exception as e:
            logger.error(f"Error aplicando filtros: {e}", exc_info=True)
    
    def _actualizar_resumen(self):
        """Actualiza las tarjetas de resumen"""
        total_por_cobrar = sum(c['saldo'] for c in self.cuentas if c['estado'] != 'pagada')
        deuda_vencida = sum(c['saldo'] for c in self.cuentas if c['estado'] == 'vencida')
        por_vencer = sum(c['saldo'] for c in self.cuentas if c['estado'] == 'por_vencer')
        
        # Cobrado este mes
        hoy = datetime.now()
        inicio_mes = hoy.replace(day=1).strftime("%Y-%m-%d")
        
        cobrado_mes = 0
        for cuenta in self.cuentas:
            if cuenta['estado'] == 'pagada':
                fecha_pago = cuenta['alquiler'].get('fecha_ultimo_pago', '')
                if fecha_pago >= inicio_mes:
                    cobrado_mes += cuenta['monto_total']
        
        self.card_total.actualizar(total_por_cobrar, self.moneda)
        self.card_vencida.actualizar(deuda_vencida, self.moneda)
        self.card_por_vencer.actualizar(por_vencer, self.moneda)
        self.card_cobrado_mes.actualizar(cobrado_mes, self.moneda)
    
    def _actualizar_tabla(self, cuentas):
        """Actualiza la tabla de cuentas"""
        self.tabla.setRowCount(0)
        
        for cuenta in sorted(cuentas, key=lambda x: (x['estado'] == 'vencida', x['fecha_vencimiento']), reverse=True):
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            
            cliente_nombre = self.clientes_mapa.get(cuenta['cliente_id'], f"ID: {cuenta['cliente_id']}")
            
            # Iconos de estado
            iconos_estado = {
                'vencida': '🚨 Vencida',
                'por_vencer': '⚠️ Por Vencer',
                'al_dia': '✅ Al Día',
                'pagada': '💚 Pagada',
                'sin_vencimiento': '📅 Sin Venc.'
            }
            
            estado_texto = iconos_estado.get(cuenta['estado'], cuenta['estado'])
            
            # Colorear filas según estado
            color_fondo = None
            if cuenta['estado'] == 'vencida':
                color_fondo = QColor("#FEE2E2")  # Rojo claro
            elif cuenta['estado'] == 'por_vencer':
                color_fondo = QColor("#FEF3C7")  # Amarillo claro
            elif cuenta['estado'] == 'pagada':
                color_fondo = QColor("#D1FAE5")  # Verde claro
            
            items = [
                QTableWidgetItem(str(cuenta['id'])),
                QTableWidgetItem(cliente_nombre),
                QTableWidgetItem(cuenta['factura']),
                QTableWidgetItem(cuenta['fecha_emision']),
                QTableWidgetItem(cuenta['fecha_vencimiento'] or '-'),
                QTableWidgetItem(f"{self.moneda} {cuenta['monto_total']:,.2f}"),
                QTableWidgetItem(f"{self.moneda} {cuenta['monto_pagado']:,.2f}"),
                QTableWidgetItem(f"{self.moneda} {cuenta['saldo']:,.2f}"),
                QTableWidgetItem(estado_texto)
            ]
            
            for col, item in enumerate(items):
                if color_fondo:
                    item.setBackground(QBrush(color_fondo))
                
                if col in [5, 6, 7]:  # Montos
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                elif col in [0, 3, 4, 8]:  # ID, fechas, estado
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                self.tabla.setItem(row, col, item)
    
    def _actualizar_metricas(self):
        """Actualiza las métricas de cobranza"""
        try:
            # Tasa de recuperación del mes
            hoy = datetime.now()
            inicio_mes = hoy.replace(day=1).strftime("%Y-%m-%d")
            
            cuentas_mes = [c for c in self.cuentas if c['fecha_emision'] >= inicio_mes]
            
            if cuentas_mes:
                total_emitido = sum(c['monto_total'] for c in cuentas_mes)
                total_cobrado = sum(c['monto_pagado'] for c in cuentas_mes)
                
                tasa = (total_cobrado / total_emitido * 100) if total_emitido > 0 else 0
                
                self.progress_tasa.setValue(int(tasa))
                self.lbl_tasa_detalle.setText(f"{self.moneda} {total_cobrado:,.0f} / {self.moneda} {total_emitido:,.0f}")
            else:
                self.progress_tasa.setValue(0)
                self.lbl_tasa_detalle.setText("0 / 0")
            
            # Edad promedio de deuda
            cuentas_pendientes = [c for c in self.cuentas if c['saldo'] > 0 and c['fecha_vencimiento']]
            
            if cuentas_pendientes:
                edades = []
                for cuenta in cuentas_pendientes:
                    try:
                        fecha_venc = datetime.strptime(cuenta['fecha_vencimiento'], "%Y-%m-%d")
                        edad = (datetime.now() - fecha_venc).days
                        if edad > 0:  # Solo deudas vencidas
                            edades.append(edad)
                    except:
                        continue
                
                if edades:
                    edad_promedio = sum(edades) / len(edades)
                    self.lbl_edad_promedio.setText(f"{edad_promedio:.0f} días")
                else:
                    self.lbl_edad_promedio.setText("0 días")
            else:
                self.lbl_edad_promedio.setText("0 días")
            
        except Exception as e:
            logger.error(f"Error actualizando métricas: {e}", exc_info=True)
    
    def _registrar_pago(self):
        """Registra un pago para la cuenta seleccionada"""
        current_row = self.tabla.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Sin Selección", "Debe seleccionar una cuenta.")
            return
        
        cuenta_id = self.tabla.item(current_row, 0).text()
        cuenta = next((c for c in self.cuentas if str(c['id']) == cuenta_id), None)
        
        if not cuenta:
            QMessageBox.warning(self, "Error", "No se encontró la cuenta.")
            return
        
        if cuenta['saldo'] <= 0:
            QMessageBox.information(self, "Cuenta Pagada", "Esta cuenta ya está completamente pagada.")
            return
        
        dialog = DialogoRegistrarPago(cuenta, self.clientes_mapa, self.moneda, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Actualizar el alquiler con el pago
            monto_pago = dialog.get_monto_pago()
            
            try:
                nuevo_monto_pagado = cuenta['monto_pagado'] + monto_pago
                
                datos_actualizacion = {
                    'monto_pagado': nuevo_monto_pagado,
                    'fecha_ultimo_pago': datetime.now().strftime("%Y-%m-%d")
                }
                
                if nuevo_monto_pagado >= cuenta['monto_total']:
                    datos_actualizacion['estado'] = 'pagado'
                
                if self.fm.editar_alquiler(cuenta['id'], datos_actualizacion):
                    QMessageBox.information(self, "Éxito", f"Pago de {self.moneda} {monto_pago:,.2f} registrado correctamente.")
                    self._cargar_datos()
                else:
                    QMessageBox.critical(self, "Error", "No se pudo registrar el pago.")
            
            except Exception as e:
                logger.error(f"Error registrando pago: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Error al registrar pago:\n{e}")
    
    def _enviar_recordatorio(self):
        """Envía recordatorio de pago al cliente"""
        current_row = self.tabla.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Sin Selección", "Debe seleccionar una cuenta.")
            return
        
        cuenta_id = self.tabla.item(current_row, 0).text()
        cuenta = next((c for c in self.cuentas if str(c['id']) == cuenta_id), None)
        
        if not cuenta:
            return
        
        cliente_nombre = self.clientes_mapa.get(cuenta['cliente_id'], 'Cliente')
        
        # Aquí se integrará con WhatsApp (siguiente módulo)
        mensaje = (
            f"Estimado/a {cliente_nombre},\n\n"
            f"Le recordamos que tiene un saldo pendiente:\n\n"
            f"Factura: {cuenta['factura']}\n"
            f"Monto: {self.moneda} {cuenta['saldo']:,.2f}\n"
            f"Vencimiento: {cuenta['fecha_vencimiento']}\n\n"
            f"Por favor, regularice su pago a la brevedad posible.\n\n"
            f"Saludos cordiales."
        )
        
        dialog = DialogoRecordatorio(cliente_nombre, mensaje, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(
                self,
                "Recordatorio",
                f"Recordatorio preparado para {cliente_nombre}.\n\n"
                f"Integración con WhatsApp próximamente."
            )
    
    def _ver_detalle(self):
        """Muestra detalle de la cuenta seleccionada"""
        current_row = self.tabla.currentRow()
        if current_row < 0:
            return
        
        cuenta_id = self.tabla.item(current_row, 0).text()
        cuenta = next((c for c in self.cuentas if str(c['id']) == cuenta_id), None)
        
        if not cuenta:
            return
        
        cliente_nombre = self.clientes_mapa.get(cuenta['cliente_id'], 'Cliente Desconocido')
        
        detalle = f"""
<h2>Detalle de Cuenta</h2>
<hr>
<p><b>Cliente:</b> {cliente_nombre}</p>
<p><b>Factura:</b> {cuenta['factura']}</p>
<p><b>Fecha Emisión:</b> {cuenta['fecha_emision']}</p>
<p><b>Fecha Vencimiento:</b> {cuenta['fecha_vencimiento'] or 'Sin vencimiento'}</p>
<hr>
<p><b>Monto Total:</b> {self.moneda} {cuenta['monto_total']:,.2f}</p>
<p><b>Monto Pagado:</b> {self.moneda} {cuenta['monto_pagado']:,.2f}</p>
<p><b>Saldo Pendiente:</b> <span style="color: #DC2626; font-size: 14pt;"><b>{self.moneda} {cuenta['saldo']:,.2f}</b></span></p>
<hr>
<p><b>Estado:</b> {cuenta['estado'].upper()}</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Detalle de Cuenta")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(detalle)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
    
    def _generar_estado_cuenta(self):
        """Genera estado de cuenta en PDF"""
        current_row = self.tabla.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Sin Selección", "Debe seleccionar una cuenta.")
            return
        
        QMessageBox.information(
            self,
            "Generar Estado de Cuenta",
            "Funcionalidad de generación de PDF próximamente.\n\n"
            "Se integrará con el sistema de reportes existente."
        )
    
    def _exportar_excel(self):
        """Exporta las cuentas a Excel"""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, Alignment, PatternFill
            
            archivo, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Reporte",
                f"CuentasPorCobrar_{datetime.now().strftime('%Y%m%d')}.xlsx",
                "Excel (*.xlsx)"
            )
            
            if not archivo:
                return
            
            wb = Workbook()
            ws = wb.active
            ws.title = "Cuentas por Cobrar"
            
            # Encabezados
            headers = ["Cliente", "Factura", "Fecha Emisión", "Fecha Vencimiento", 
                      "Monto Total", "Pagado", "Saldo", "Estado"]
            
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="1F2937", end_color="1F2937", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")
            
            # Datos
            for row, cuenta in enumerate(self.cuentas, 2):
                cliente_nombre = self.clientes_mapa.get(cuenta['cliente_id'], 'Desconocido')
                
                ws.cell(row=row, column=1, value=cliente_nombre)
                ws.cell(row=row, column=2, value=cuenta['factura'])
                ws.cell(row=row, column=3, value=cuenta['fecha_emision'])
                ws.cell(row=row, column=4, value=cuenta['fecha_vencimiento'] or '-')
                ws.cell(row=row, column=5, value=cuenta['monto_total'])
                ws.cell(row=row, column=6, value=cuenta['monto_pagado'])
                ws.cell(row=row, column=7, value=cuenta['saldo'])
                ws.cell(row=row, column=8, value=cuenta['estado'])
            
            wb.save(archivo)
            
            QMessageBox.information(self, "Éxito", f"Reporte exportado:\n{archivo}")
            
        except ImportError:
            QMessageBox.critical(
                self,
                "Error",
                "Se requiere 'openpyxl' para exportar.\n\nInstale con: pip install openpyxl"
            )
        except Exception as e:
            logger.error(f"Error exportando: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al exportar:\n{e}")


class DialogoRegistrarPago(QDialog):
    """Diálogo para registrar un pago"""
    
    def __init__(self, cuenta, clientes_mapa, moneda, parent=None):
        super().__init__(parent)
        self.cuenta = cuenta
        self.moneda = moneda
        
        cliente_nombre = clientes_mapa.get(cuenta['cliente_id'], 'Cliente')
        
        self.setWindowTitle("Registrar Pago")
        self.setMinimumWidth(450)
        self.setStyleSheet(CUENTAS_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Título
        titulo = QLabel("💵 Registrar Pago")
        titulo.setStyleSheet("font-size: 16pt; font-weight: bold; color: #1F2937;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Info de la cuenta
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 6px; padding: 15px;")
        info_layout = QVBoxLayout(info_frame)
        
        lbl_cliente = QLabel(f"<b>Cliente:</b> {cliente_nombre}")
        lbl_factura = QLabel(f"<b>Factura:</b> {cuenta['factura']}")
        lbl_saldo = QLabel(f"<b>Saldo Pendiente:</b> <span style='color: #DC2626; font-size: 14pt;'>{moneda} {cuenta['saldo']:,.2f}</span>")
        
        info_layout.addWidget(lbl_cliente)
        info_layout.addWidget(lbl_factura)
        info_layout.addWidget(lbl_saldo)
        
        layout.addWidget(info_frame)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        lbl_monto = QLabel("Monto del Pago:")
        lbl_monto.setStyleSheet("font-weight: 600; color: #374151;")
        self.spin_monto = QDoubleSpinBox()
        self.spin_monto.setRange(0.01, cuenta['saldo'])
        self.spin_monto.setValue(cuenta['saldo'])
        self.spin_monto.setDecimals(2)
        self.spin_monto.setPrefix(f"{moneda} ")
        form_layout.addRow(lbl_monto, self.spin_monto)
        
        lbl_fecha = QLabel("Fecha de Pago:")
        lbl_fecha.setStyleSheet("font-weight: 600; color: #374151;")
        self.fecha_pago = QDateEdit(calendarPopup=True)
        self.fecha_pago.setDate(QDate.currentDate())
        self.fecha_pago.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow(lbl_fecha, self.fecha_pago)
        
        lbl_metodo = QLabel("Método de Pago:")
        lbl_metodo.setStyleSheet("font-weight: 600; color: #374151;")
        self.combo_metodo = QComboBox()
        self.combo_metodo.addItems(["Transferencia", "Efectivo", "Cheque", "Tarjeta"])
        form_layout.addRow(lbl_metodo, self.combo_metodo)
        
        lbl_referencia = QLabel("Referencia:")
        lbl_referencia.setStyleSheet("font-weight: 600; color: #374151;")
        self.txt_referencia = QLineEdit()
        self.txt_referencia.setPlaceholderText("Número de referencia, cheque, etc...")
        form_layout.addRow(lbl_referencia, self.txt_referencia)
>>>>>>> Stashed changes
        
        layout.addLayout(form_layout)
        
        # Botones
        botones_layout = QHBoxLayout()
<<<<<<< Updated upstream
        botones_layout.addStretch()
        
        btn_cancelar = QPushButton("Cancelar")
=======
        
        btn_guardar = QPushButton("💾 Registrar Pago")
        btn_guardar.setProperty("class", "success")
        btn_guardar.clicked.connect(self.accept)
        btn_guardar.setMinimumWidth(150)
        botones_layout.addWidget(btn_guardar)
        
        btn_cancelar = QPushButton("✖️ Cancelar")
        btn_cancelar.setProperty("class", "secondary")
        btn_cancelar.clicked.connect(self.reject)
        btn_cancelar.setMinimumWidth(120)
        botones_layout.addWidget(btn_cancelar)
        
        layout.addLayout(botones_layout)
    
    def get_monto_pago(self):
        return self.spin_monto.value()


class DialogoRecordatorio(QDialog):
    """Diálogo para enviar recordatorio"""
    
    def __init__(self, cliente_nombre, mensaje, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Enviar Recordatorio")
        self.setMinimumSize(500, 400)
        self.setStyleSheet(CUENTAS_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        titulo = QLabel(f"📧 Recordatorio para {cliente_nombre}")
        titulo.setStyleSheet("font-size: 14pt; font-weight: bold; color: #1F2937;")
        layout.addWidget(titulo)
        
        lbl_mensaje = QLabel("Mensaje:")
        lbl_mensaje.setStyleSheet("font-weight: 600; color: #374151;")
        layout.addWidget(lbl_mensaje)
        
        self.txt_mensaje = QTextEdit()
        self.txt_mensaje.setPlainText(mensaje)
        layout.addWidget(self.txt_mensaje)
        
        botones_layout = QHBoxLayout()
        
        btn_enviar = QPushButton("📤 Enviar")
        btn_enviar.clicked.connect(self.accept)
        botones_layout.addWidget(btn_enviar)
        
        btn_cancelar = QPushButton("✖️ Cancelar")
>>>>>>> Stashed changes
        btn_cancelar.setProperty("class", "secondary")
        btn_cancelar.clicked.connect(self.reject)
        botones_layout.addWidget(btn_cancelar)
        
<<<<<<< Updated upstream
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
=======
        layout.addLayout(botones_layout)
>>>>>>> Stashed changes
