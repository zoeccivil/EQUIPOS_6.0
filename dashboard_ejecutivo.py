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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
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
