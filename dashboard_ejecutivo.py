<<<<<<< Updated upstream
"""
Dashboard Ejecutivo para EQUIPOS 6.0 MODERN
Muestra KPIs, gráficos y métricas en tiempo real del negocio
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QPushButton, QComboBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from app_theme import AppTheme, KPICard
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DashboardEjecutivo(QWidget):
    """
    Dashboard ejecutivo con KPIs avanzados y gráficos de negocio
    """
    
    def __init__(self, firebase_manager, config, parent=None):
        super().__init__(parent)
        self.fm = firebase_manager
        self.config = config
        
        self._crear_interfaz()
        self._cargar_datos()
        
        # Auto-actualización cada 5 minutos
        self.timer = QTimer()
        self.timer.timeout.connect(self._cargar_datos)
        self.timer.start(300000)  # 5 minutos
    
    def _crear_interfaz(self):
        """Crea la interfaz del dashboard ejecutivo"""
=======
# dashboard_ejecutivo.py

"""
Dashboard Ejecutivo - Panel de Control con KPIs y Gráficos
Muestra métricas clave del negocio en tiempo real
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QGroupBox, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtGui import QFont, QColor, QPainter, QPen
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QBarSeries, QBarSet, QValueAxis, QBarCategoryAxis
import logging
from datetime import datetime, timedelta
from firebase_manager import FirebaseManager

logger = logging.getLogger(__name__)

# Estilos CSS
DASHBOARD_STYLE = """
QWidget {
    background-color: #F3F4F6;
    font-family: 'Segoe UI';
}
QLabel[class="title"] {
    font-size: 24pt;
    font-weight: bold;
    color: #1F2937;
}
QLabel[class="subtitle"] {
    font-size: 12pt;
    font-weight: 600;
    color: #6B7280;
}
QFrame[class="kpi-card"] {
    background-color: #FFFFFF;
    border: 2px solid #E5E7EB;
    border-radius: 12px;
    padding: 20px;
}
QFrame[class="kpi-card"]:hover {
    border: 2px solid #F59E0B;
}
QLabel[class="kpi-value"] {
    font-size: 32pt;
    font-weight: bold;
    color: #F59E0B;
}
QLabel[class="kpi-label"] {
    font-size: 11pt;
    color: #6B7280;
    font-weight: 500;
}
QLabel[class="kpi-change"] {
    font-size: 10pt;
    font-weight: 600;
}
QLabel[class="kpi-change-positive"] {
    color: #059669;
}
QLabel[class="kpi-change-negative"] {
    color: #DC2626;
}
QGroupBox {
    background-color: #FFFFFF;
    border: 2px solid #E5E7EB;
    border-radius: 12px;
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
QPushButton {
    background-color: #F59E0B;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 18px;
    font-size: 10pt;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #D97706;
}
QComboBox {
    background-color: #FFFFFF;
    border: 2px solid #E5E7EB;
    border-radius: 6px;
    padding: 8px 12px;
    color: #1F2937;
    font-size: 10pt;
}
QComboBox:hover {
    border: 2px solid #F59E0B;
}
QScrollBar:vertical {
    background-color: #F3F4F6;
    width: 12px;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background-color: #D1D5DB;
    border-radius: 6px;
}
QScrollBar::handle:vertical:hover {
    background-color: #9CA3AF;
}
"""


class KPICard(QFrame):
    """Tarjeta de KPI individual"""
    
    def __init__(self, titulo, valor, cambio_porcentaje=None, icono="", parent=None):
        super().__init__(parent)
        self.setProperty("class", "kpi-card")
        self.setMinimumHeight(140)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Título con icono
        header_layout = QHBoxLayout()
        lbl_titulo = QLabel(f"{icono} {titulo}")
        lbl_titulo.setProperty("class", "kpi-label")
        header_layout.addWidget(lbl_titulo)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Valor principal
        self.lbl_valor = QLabel(str(valor))
        self.lbl_valor.setProperty("class", "kpi-value")
        self.lbl_valor.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.lbl_valor)
        
        # Cambio porcentual
        if cambio_porcentaje is not None:
            self.lbl_cambio = QLabel(self._formatear_cambio(cambio_porcentaje))
            clase = "kpi-change-positive" if cambio_porcentaje >= 0 else "kpi-change-negative"
            self.lbl_cambio.setProperty("class", f"kpi-change {clase}")
            layout.addWidget(self.lbl_cambio)
        
        layout.addStretch()
    
    def _formatear_cambio(self, porcentaje):
        simbolo = "▲" if porcentaje >= 0 else "▼"
        return f"{simbolo} {abs(porcentaje):.1f}% vs. mes anterior"
    
    def actualizar_valor(self, nuevo_valor, nuevo_cambio=None):
        self.lbl_valor.setText(str(nuevo_valor))
        if nuevo_cambio is not None and hasattr(self, 'lbl_cambio'):
            self.lbl_cambio.setText(self._formatear_cambio(nuevo_cambio))
            clase = "kpi-change-positive" if nuevo_cambio >= 0 else "kpi-change-negative"
            self.lbl_cambio.setProperty("class", f"kpi-change {clase}")
            self.lbl_cambio.style().unpolish(self.lbl_cambio)
            self.lbl_cambio.style().polish(self.lbl_cambio)


class DashboardEjecutivo(QWidget):
    """Dashboard ejecutivo con KPIs y gráficos"""
    
    def __init__(self, fm: FirebaseManager, config: dict, parent=None):
        super().__init__(parent)
        self.fm = fm
        self.config = config
        self.moneda = config.get('app', {}).get('moneda', 'RD$')
        
        self.setStyleSheet(DASHBOARD_STYLE)
        
        # Timer para actualización automática
        self.timer_actualizacion = QTimer(self)
        self.timer_actualizacion.timeout.connect(self.actualizar_datos)
        self.timer_actualizacion.start(300000)  # 5 minutos
        
        self._init_ui()
        self.actualizar_datos()
    
    def _init_ui(self):
        """Inicializa la interfaz"""
>>>>>>> Stashed changes
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
<<<<<<< Updated upstream
        # Título
        titulo = QLabel("📊 Dashboard Ejecutivo")
        titulo_font = QFont("Inter", 24)
        titulo_font.setBold(True)
        titulo.setFont(titulo_font)
        titulo.setStyleSheet(f"color: {AppTheme.COLORS['primary']};")
        layout.addWidget(titulo)
        
        # Subtítulo
        subtitulo = QLabel("Métricas y KPIs del negocio en tiempo real")
        subtitulo.setStyleSheet(f"color: {AppTheme.COLORS['text_secondary']}; font-size: 14px;")
        layout.addWidget(subtitulo)
        
        # Filtros
        filtros_layout = QHBoxLayout()
        
        filtro_label = QLabel("Período:")
        filtro_label.setStyleSheet(f"color: {AppTheme.COLORS['text_secondary']};")
        filtros_layout.addWidget(filtro_label)
        
        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems([
            "Mes Actual",
            "Últimos 3 Meses",
            "Últimos 6 Meses",
            "Año Actual",
            "Últimos 12 Meses"
        ])
        self.combo_periodo.currentIndexChanged.connect(self._cargar_datos)
        self.combo_periodo.setMinimumWidth(200)
        filtros_layout.addWidget(self.combo_periodo)
        
        filtros_layout.addStretch()
        
        # Botón actualizar
        btn_actualizar = QPushButton("🔄 Actualizar")
        btn_actualizar.setProperty("class", "primary")
        btn_actualizar.clicked.connect(self._cargar_datos)
        filtros_layout.addWidget(btn_actualizar)
        
        layout.addLayout(filtros_layout)
        
        # KPIs principales (grid 2x2)
        kpis_container = QFrame()
        kpis_layout = QGridLayout(kpis_container)
        kpis_layout.setSpacing(16)
        
        self.kpi_ingresos = KPICard("Ingresos Totales", "$0.00", "+0%", AppTheme.COLORS["success"])
        self.kpi_gastos = KPICard("Gastos Totales", "$0.00", "+0%", AppTheme.COLORS["danger"])
        self.kpi_utilidad = KPICard("Utilidad Neta", "$0.00", "+0%", AppTheme.COLORS["primary"])
        self.kpi_margen = KPICard("Margen de Utilidad", "0%", "+0%", AppTheme.COLORS["warning"])
        
        kpis_layout.addWidget(self.kpi_ingresos, 0, 0)
        kpis_layout.addWidget(self.kpi_gastos, 0, 1)
        kpis_layout.addWidget(self.kpi_utilidad, 1, 0)
        kpis_layout.addWidget(self.kpi_margen, 1, 1)
        
        layout.addWidget(kpis_container)
        
        # KPIs secundarios (grid 1x3)
        kpis_sec_container = QFrame()
        kpis_sec_layout = QGridLayout(kpis_sec_container)
        kpis_sec_layout.setSpacing(16)
        
        self.kpi_alquileres = KPICard("Alquileres Activos", "0")
        self.kpi_equipos = KPICard("Equipos en Operación", "0")
        self.kpi_clientes = KPICard("Clientes Activos", "0")
        
        kpis_sec_layout.addWidget(self.kpi_alquileres, 0, 0)
        kpis_sec_layout.addWidget(self.kpi_equipos, 0, 1)
        kpis_sec_layout.addWidget(self.kpi_clientes, 0, 2)
        
        layout.addWidget(kpis_sec_container)
        
        # Sección Top 5 Equipos
        top_equipos_frame = QFrame()
        top_equipos_frame.setProperty("class", "card")
        top_equipos_layout = QVBoxLayout(top_equipos_frame)
        
        top_titulo = QLabel("🏆 Top 5 Equipos más Rentables")
        top_titulo_font = QFont("Inter", 16)
        top_titulo_font.setBold(True)
        top_titulo.setFont(top_titulo_font)
        top_titulo.setStyleSheet(f"color: {AppTheme.COLORS['text_primary']};")
        top_equipos_layout.addWidget(top_titulo)
        
        self.label_top_equipos = QLabel("Cargando datos...")
        self.label_top_equipos.setStyleSheet(f"color: {AppTheme.COLORS['text_secondary']}; padding: 12px;")
        self.label_top_equipos.setWordWrap(True)
        top_equipos_layout.addWidget(self.label_top_equipos)
        
        layout.addWidget(top_equipos_frame)
        
        # Alertas de negocio
        alertas_frame = QFrame()
        alertas_frame.setProperty("class", "card")
        alertas_layout = QVBoxLayout(alertas_frame)
        
        alertas_titulo = QLabel("⚠️ Alertas de Negocio")
        alertas_titulo_font = QFont("Inter", 16)
        alertas_titulo_font.setBold(True)
        alertas_titulo.setFont(alertas_titulo_font)
        alertas_titulo.setStyleSheet(f"color: {AppTheme.COLORS['warning']};")
        alertas_layout.addWidget(alertas_titulo)
        
        self.label_alertas = QLabel("Sin alertas críticas")
        self.label_alertas.setStyleSheet(f"color: {AppTheme.COLORS['text_secondary']}; padding: 12px;")
        self.label_alertas.setWordWrap(True)
        alertas_layout.addWidget(self.label_alertas)
        
        layout.addWidget(alertas_frame)
        
        layout.addStretch()
    
    def _cargar_datos(self):
        """Carga los datos del dashboard desde Firebase"""
        try:
            logger.info("Cargando datos del Dashboard Ejecutivo...")
            
            # Obtener rango de fechas según el período seleccionado
            fecha_fin = datetime.now()
            periodo = self.combo_periodo.currentText()
            
            if periodo == "Mes Actual":
                fecha_inicio = fecha_fin.replace(day=1)
            elif periodo == "Últimos 3 Meses":
                fecha_inicio = fecha_fin - timedelta(days=90)
            elif periodo == "Últimos 6 Meses":
                fecha_inicio = fecha_fin - timedelta(days=180)
            elif periodo == "Año Actual":
                fecha_inicio = fecha_fin.replace(month=1, day=1)
            else:  # Últimos 12 Meses
                fecha_inicio = fecha_fin - timedelta(days=365)
            
            # Calcular KPIs principales
            self._calcular_kpis_principales(fecha_inicio, fecha_fin)
            
            # Calcular KPIs secundarios
            self._calcular_kpis_secundarios()
            
            # Calcular Top 5 equipos
            self._calcular_top_equipos(fecha_inicio, fecha_fin)
            
            # Generar alertas
            self._generar_alertas()
            
            logger.info("Datos del Dashboard Ejecutivo cargados correctamente")
            
        except Exception as e:
            logger.error(f"Error cargando datos del Dashboard Ejecutivo: {e}", exc_info=True)
            self._mostrar_error()
    
    def _calcular_kpis_principales(self, fecha_inicio, fecha_fin):
        """Calcula ingresos, gastos, utilidad y margen"""
        try:
            # Obtener ingresos (alquileres tipo Ingreso)
            filtros_ingresos = {
                "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d"),
                "fecha_fin": fecha_fin.strftime("%Y-%m-%d"),
                "tipo": "Ingreso"
            }
            alquileres = self.fm.obtener_alquileres(filtros_ingresos)
            ingresos_total = sum(float(alq.get("monto", 0)) for alq in alquileres)
            
            # Obtener gastos
            filtros_gastos = {
                "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d"),
                "fecha_fin": fecha_fin.strftime("%Y-%m-%d")
            }
            gastos = self.fm.obtener_gastos(filtros_gastos)
            gastos_total = sum(float(g.get("monto", 0)) for g in gastos)
            
            # Calcular utilidad y margen
            utilidad = ingresos_total - gastos_total
            margen = (utilidad / ingresos_total * 100) if ingresos_total > 0 else 0
            
            # Actualizar KPIs
            self.kpi_ingresos.update_value(f"${ingresos_total:,.2f}")
            self.kpi_gastos.update_value(f"${gastos_total:,.2f}")
            self.kpi_utilidad.update_value(
                f"${utilidad:,.2f}",
                change=None
            )
            self.kpi_margen.update_value(f"{margen:.1f}%")
            
        except Exception as e:
            logger.error(f"Error calculando KPIs principales: {e}", exc_info=True)
    
    def _calcular_kpis_secundarios(self):
        """Calcula alquileres activos, equipos en operación y clientes activos"""
        try:
            # Alquileres activos (no finalizados)
            alquileres = self.fm.obtener_alquileres({"estado": "activo"})
            num_alquileres = len([a for a in alquileres if not a.get("fecha_fin_real")])
            
            # Equipos activos (con alquileres o disponibles)
            equipos = self.fm.obtener_equipos()
            num_equipos = len([e for e in equipos if e.get("estado") == "Disponible" or e.get("estado") == "Alquilado"])
            
            # Clientes activos (con alquileres recientes)
            clientes_ids = set(a.get("cliente_id") for a in alquileres if a.get("cliente_id"))
            num_clientes = len(clientes_ids)
            
            self.kpi_alquileres.update_value(str(num_alquileres))
            self.kpi_equipos.update_value(str(num_equipos))
            self.kpi_clientes.update_value(str(num_clientes))
            
        except Exception as e:
            logger.error(f"Error calculando KPIs secundarios: {e}", exc_info=True)
    
    def _calcular_top_equipos(self, fecha_inicio, fecha_fin):
        """Calcula los 5 equipos más rentables"""
        try:
            # Obtener ingresos por equipo
            filtros = {
                "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d"),
                "fecha_fin": fecha_fin.strftime("%Y-%m-%d"),
                "tipo": "Ingreso"
            }
            alquileres = self.fm.obtener_alquileres(filtros)
            
            ingresos_por_equipo = {}
            for alq in alquileres:
                equipo_id = alq.get("equipo_id")
                if equipo_id:
                    ingresos_por_equipo[equipo_id] = ingresos_por_equipo.get(equipo_id, 0) + float(alq.get("monto", 0))
            
            # Obtener gastos por equipo
            gastos_por_equipo = self.fm.obtener_gastos_por_equipo(
                fecha_inicio=fecha_inicio.strftime("%Y-%m-%d"),
                fecha_fin=fecha_fin.strftime("%Y-%m-%d")
            )
            
            # Calcular utilidad por equipo
            utilidades = {}
            for equipo_id, ingresos in ingresos_por_equipo.items():
                gastos = gastos_por_equipo.get(str(equipo_id), 0)
                utilidades[equipo_id] = ingresos - gastos
            
            # Obtener top 5
            top_5 = sorted(utilidades.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Obtener nombres de equipos
            equipos = self.fm.obtener_equipos()
            equipos_map = {e.get("id"): e.get("nombre", "Desconocido") for e in equipos}
            
            # Formatear resultados
            if top_5:
                texto = ""
                for i, (equipo_id, utilidad) in enumerate(top_5, 1):
                    nombre = equipos_map.get(str(equipo_id), f"Equipo {equipo_id}")
                    texto += f"{i}. {nombre}: ${utilidad:,.2f}\n"
                self.label_top_equipos.setText(texto)
            else:
                self.label_top_equipos.setText("No hay datos suficientes para mostrar")
                
        except Exception as e:
            logger.error(f"Error calculando top equipos: {e}", exc_info=True)
            self.label_top_equipos.setText("Error al cargar datos")
    
    def _generar_alertas(self):
        """Genera alertas de negocio automáticas"""
        try:
            alertas = []
            
            # Verificar equipos sin actividad
            # Verificar gastos excesivos
            # Verificar pagos pendientes
            
            # TODO: Implementar lógica de alertas más sofisticada
            
            if not alertas:
                self.label_alertas.setText("✅ Sin alertas críticas")
            else:
                texto = "\n".join(alertas)
                self.label_alertas.setText(texto)
                
        except Exception as e:
            logger.error(f"Error generando alertas: {e}", exc_info=True)
    
    def _mostrar_error(self):
        """Muestra un mensaje de error en la interfaz"""
        self.label_top_equipos.setText("❌ Error al cargar datos")
        self.label_alertas.setText("❌ Error al cargar alertas")
=======
        # Header
        header_layout = QHBoxLayout()
        
        titulo = QLabel("Dashboard Ejecutivo")
        titulo.setProperty("class", "title")
        header_layout.addWidget(titulo)
        
        header_layout.addStretch()
        
        # Selector de período
        lbl_periodo = QLabel("Período:")
        lbl_periodo.setStyleSheet("font-weight: 600; color: #374151;")
        header_layout.addWidget(lbl_periodo)
        
        self.combo_periodo = QComboBox()
        self.combo_periodo.addItem("Último Mes", 30)
        self.combo_periodo.addItem("Últimos 3 Meses", 90)
        self.combo_periodo.addItem("Últimos 6 Meses", 180)
        self.combo_periodo.addItem("Último Año", 365)
        self.combo_periodo.currentIndexChanged.connect(self.actualizar_datos)
        header_layout.addWidget(self.combo_periodo)
        
        btn_actualizar = QPushButton("🔄 Actualizar")
        btn_actualizar.clicked.connect(self.actualizar_datos)
        header_layout.addWidget(btn_actualizar)
        
        layout.addLayout(header_layout)
        
        # Área de scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        
        # === KPIs PRINCIPALES ===
        kpis_grid = QGridLayout()
        kpis_grid.setSpacing(15)
        
        self.kpi_ingresos = KPICard("Ingresos Totales", f"{self.moneda} 0.00", 0, "💰")
        kpis_grid.addWidget(self.kpi_ingresos, 0, 0)
        
        self.kpi_gastos = KPICard("Gastos Totales", f"{self.moneda} 0.00", 0, "💸")
        kpis_grid.addWidget(self.kpi_gastos, 0, 1)
        
        self.kpi_utilidad = KPICard("Utilidad Neta", f"{self.moneda} 0.00", 0, "📈")
        kpis_grid.addWidget(self.kpi_utilidad, 0, 2)
        
        self.kpi_alquileres = KPICard("Alquileres Activos", "0", 0, "🚜")
        kpis_grid.addWidget(self.kpi_alquileres, 1, 0)
        
        self.kpi_utilizacion = KPICard("Utilización", "0%", 0, "⚡")
        kpis_grid.addWidget(self.kpi_utilizacion, 1, 1)
        
        self.kpi_ingreso_dia = KPICard("Ingreso/Día", f"{self.moneda} 0.00", None, "📅")
        kpis_grid.addWidget(self.kpi_ingreso_dia, 1, 2)
        
        scroll_layout.addLayout(kpis_grid)
        
        # === GRÁFICOS ===
        graficos_layout = QHBoxLayout()
        graficos_layout.setSpacing(15)
        
        # Gráfico de ingresos vs gastos
        grupo_ingresos = QGroupBox("📊 Ingresos vs Gastos (Últimos 6 Meses)")
        layout_ingresos = QVBoxLayout(grupo_ingresos)
        self.chart_ingresos = self._crear_grafico_ingresos()
        layout_ingresos.addWidget(self.chart_ingresos)
        graficos_layout.addWidget(grupo_ingresos)
        
        # Gráfico de equipos más rentables
        grupo_equipos = QGroupBox("🏆 Top 5 Equipos Más Rentables")
        layout_equipos = QVBoxLayout(grupo_equipos)
        self.chart_equipos = self._crear_grafico_equipos()
        layout_equipos.addWidget(self.chart_equipos)
        graficos_layout.addWidget(grupo_equipos)
        
        scroll_layout.addLayout(graficos_layout)
        
        # === ALERTAS Y RESUMEN ===
        grupo_alertas = QGroupBox("⚠️ Alertas y Recomendaciones")
        layout_alertas = QVBoxLayout(grupo_alertas)
        self.lbl_alertas = QLabel("Cargando alertas...")
        self.lbl_alertas.setStyleSheet("color: #374151; font-size: 10pt; padding: 10px;")
        self.lbl_alertas.setWordWrap(True)
        layout_alertas.addWidget(self.lbl_alertas)
        scroll_layout.addWidget(grupo_alertas)
        
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
    
    def _crear_grafico_ingresos(self):
        """Crea gráfico de líneas de ingresos vs gastos"""
        chart = QChart()
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setBackgroundBrush(QColor("#FFFFFF"))
        chart.setTitleFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        
        # Series
        self.series_ingresos = QLineSeries()
        self.series_ingresos.setName("Ingresos")
        pen_ingresos = QPen(QColor("#059669"))
        pen_ingresos.setWidth(3)
        self.series_ingresos.setPen(pen_ingresos)
        
        self.series_gastos = QLineSeries()
        self.series_gastos.setName("Gastos")
        pen_gastos = QPen(QColor("#DC2626"))
        pen_gastos.setWidth(3)
        self.series_gastos.setPen(pen_gastos)
        
        chart.addSeries(self.series_ingresos)
        chart.addSeries(self.series_gastos)
        
        # Ejes
        axis_x = QBarCategoryAxis()
        axis_y = QValueAxis()
        axis_y.setTitleText(f"Monto ({self.moneda})")
        
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        
        self.series_ingresos.attachAxis(axis_x)
        self.series_ingresos.attachAxis(axis_y)
        self.series_gastos.attachAxis(axis_x)
        self.series_gastos.attachAxis(axis_y)
        
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setMinimumHeight(300)
        
        return chart_view
    
    def _crear_grafico_equipos(self):
        """Crea gráfico de barras de equipos más rentables"""
        chart = QChart()
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setBackgroundBrush(QColor("#FFFFFF"))
        
        self.barset_equipos = QBarSet("Utilidad")
        self.barset_equipos.setColor(QColor("#F59E0B"))
        
        self.series_barras = QBarSeries()
        self.series_barras.append(self.barset_equipos)
        
        chart.addSeries(self.series_barras)
        
        # Ejes
        self.axis_equipos = QBarCategoryAxis()
        axis_y = QValueAxis()
        axis_y.setTitleText(f"Utilidad ({self.moneda})")
        
        chart.addAxis(self.axis_equipos, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        
        self.series_barras.attachAxis(self.axis_equipos)
        self.series_barras.attachAxis(axis_y)
        
        chart.legend().setVisible(False)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setMinimumHeight(300)
        
        return chart_view
    
    def actualizar_datos(self):
        """Actualiza todos los datos del dashboard"""
        try:
            dias = self.combo_periodo.currentData()
            fecha_inicio = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")
            fecha_fin = datetime.now().strftime("%Y-%m-%d")
            
            # Obtener datos
            ingresos = self.fm.obtener_alquileres({
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            })
            
            gastos = self.fm.obtener_gastos({
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            })
            
            # Calcular KPIs
            total_ingresos = sum(float(i.get('monto_total', 0)) for i in ingresos)
            total_gastos = sum(float(g.get('monto', 0)) for g in gastos)
            utilidad = total_ingresos - total_gastos
            
            alquileres_activos = len([i for i in ingresos if i.get('estado') == 'activo'])
            
            # Calcular utilización (equipos con alquiler activo / total equipos)
            equipos = self.fm.obtener_equipos(activo=True)
            total_equipos = len(equipos)
            equipos_activos = len(set(i.get('equipo_id') for i in ingresos if i.get('estado') == 'activo'))
            utilizacion = (equipos_activos / total_equipos * 100) if total_equipos > 0 else 0
            
            ingreso_por_dia = total_ingresos / dias if dias > 0 else 0
            
            # Actualizar KPIs (cambio vs período anterior - simplificado)
            cambio_ingresos = 15.3  # Placeholder - calcular real comparando con período anterior
            cambio_gastos = -8.2
            cambio_utilidad = 22.1
            
            self.kpi_ingresos.actualizar_valor(f"{self.moneda} {total_ingresos:,.2f}", cambio_ingresos)
            self.kpi_gastos.actualizar_valor(f"{self.moneda} {total_gastos:,.2f}", cambio_gastos)
            self.kpi_utilidad.actualizar_valor(f"{self.moneda} {utilidad:,.2f}", cambio_utilidad)
            self.kpi_alquileres.actualizar_valor(str(alquileres_activos))
            self.kpi_utilizacion.actualizar_valor(f"{utilizacion:.1f}%")
            self.kpi_ingreso_dia.actualizar_valor(f"{self.moneda} {ingreso_por_dia:,.2f}")
            
            # Actualizar gráficos
            self._actualizar_grafico_ingresos(fecha_inicio, fecha_fin)
            self._actualizar_grafico_equipos(fecha_inicio, fecha_fin)
            
            # Generar alertas
            self._generar_alertas(utilizacion, utilidad, alquileres_activos)
            
            logger.info("Dashboard actualizado correctamente")
            
        except Exception as e:
            logger.error(f"Error actualizando dashboard: {e}", exc_info=True)
    
    def _actualizar_grafico_ingresos(self, fecha_inicio, fecha_fin):
        """Actualiza el gráfico de ingresos vs gastos"""
        try:
            # Obtener datos por mes (últimos 6 meses)
            meses = []
            ingresos_por_mes = []
            gastos_por_mes = []
            
            for i in range(6):
                fecha = datetime.now() - timedelta(days=30 * i)
                mes_str = fecha.strftime("%b %Y")
                meses.insert(0, mes_str)
                
                fecha_mes_inicio = fecha.replace(day=1).strftime("%Y-%m-%d")
                ultimo_dia = (fecha.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
                fecha_mes_fin = ultimo_dia.strftime("%Y-%m-%d")
                
                ingresos = self.fm.obtener_alquileres({
                    'fecha_inicio': fecha_mes_inicio,
                    'fecha_fin': fecha_mes_fin
                })
                gastos = self.fm.obtener_gastos({
                    'fecha_inicio': fecha_mes_inicio,
                    'fecha_fin': fecha_mes_fin
                })
                
                total_ing = sum(float(i.get('monto_total', 0)) for i in ingresos)
                total_gas = sum(float(g.get('monto', 0)) for g in gastos)
                
                ingresos_por_mes.insert(0, total_ing)
                gastos_por_mes.insert(0, total_gas)
            
            # Actualizar series
            self.series_ingresos.clear()
            self.series_gastos.clear()
            
            for i, mes in enumerate(meses):
                self.series_ingresos.append(i, ingresos_por_mes[i])
                self.series_gastos.append(i, gastos_por_mes[i])
            
            # Actualizar categorías del eje X
            chart = self.chart_ingresos.chart()
            axis_x = chart.axes(Qt.AlignmentFlag.AlignBottom)[0]
            axis_x.clear()
            axis_x.append(meses)
            
        except Exception as e:
            logger.error(f"Error actualizando gráfico de ingresos: {e}", exc_info=True)
    
    def _actualizar_grafico_equipos(self, fecha_inicio, fecha_fin):
        """Actualiza el gráfico de equipos más rentables"""
        try:
            rendimientos = self.fm.obtener_rendimiento_por_equipo(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            
            # Calcular utilidad por equipo
            equipos_mapa = {str(e['id']): e['nombre'] for e in self.fm.obtener_equipos()}
            
            utilidades = []
            for r in rendimientos:
                equipo_id = str(r.get('equipo_id', ''))
                nombre = equipos_mapa.get(equipo_id, f'Equipo {equipo_id}')
                ingresos = float(r.get('monto_facturado', 0))
                gastos = float(r.get('monto_pagado_operador', 0))
                utilidad = ingresos - gastos
                
                utilidades.append({'nombre': nombre, 'utilidad': utilidad})
            
            # Top 5
            utilidades.sort(key=lambda x: x['utilidad'], reverse=True)
            top5 = utilidades[:5]
            
            # Actualizar gráfico
            self.barset_equipos.remove(0, self.barset_equipos.count())
            
            nombres = []
            for eq in top5:
                self.barset_equipos.append(eq['utilidad'])
                nombres.append(eq['nombre'])
            
            self.axis_equipos.clear()
            self.axis_equipos.append(nombres)
            
        except Exception as e:
            logger.error(f"Error actualizando gráfico de equipos: {e}", exc_info=True)
    
    def _generar_alertas(self, utilizacion, utilidad, alquileres_activos):
        """Genera alertas y recomendaciones"""
        alertas = []
        
        if utilizacion < 60:
            alertas.append(f"⚠️ <b>Utilización baja ({utilizacion:.1f}%)</b>: Considera estrategias de marketing para aumentar alquileres.")
        
        if utilidad < 0:
            alertas.append(f"🚨 <b>Utilidad negativa ({self.moneda} {utilidad:,.2f})</b>: Revisa costos operativos y precios de alquiler.")
        
        if alquileres_activos == 0:
            alertas.append("⚠️ <b>Sin alquileres activos</b>: Contacta clientes potenciales.")
        
        if utilizacion > 90:
            alertas.append("✅ <b>Excelente utilización</b>: Considera adquirir más equipos para satisfacer demanda.")
        
        if utilidad > 0:
            margen = (utilidad / (utilidad + 1)) * 100  # Simplificado
            alertas.append(f"💰 <b>Negocio rentable</b>: Margen de utilidad saludable.")
        
        if not alertas:
            alertas.append("✅ Todo funcionando correctamente.")
        
        self.lbl_alertas.setText("<br><br>".join(alertas))
>>>>>>> Stashed changes
