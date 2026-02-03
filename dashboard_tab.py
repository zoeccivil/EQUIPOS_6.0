"""
Dashboard Tab para EQUIPOS 4.0
Refactor con AppTheme (Industrial Dark Mode)
- KPICard para métricas
- Tabla de alquileres recientes
- Filtrado por Año, Mes y Equipo (equipo_id en userData)
- Cálculos de tops basados en ingresos_data
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QComboBox,
    QGroupBox, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from datetime import datetime
from firebase_manager import FirebaseManager
from app_theme import AppTheme, KPICard
import logging

logger = logging.getLogger(__name__)


class DashboardTab(QWidget):
    """
    Widget que muestra KPIs y alquileres recientes.
    Espera que firebase_manager exponga:
      - obtener_estadisticas_dashboard(filtros: {ano, mes, equipo_id})
        -> {
             "ingresos_totales": float,
             "gastos_totales": float,
             "pendiente_cobro": float,
             "utilidad_neta": float,
             "ocupacion_pct": float (0-100),
             "ingresos_data": [
                 {"equipo_id": str/int, "operador_id": str/int, "monto": float, "monto_facturado": float?, "total": float?, "horas": float?, "horas_operadas": float?},
                 ...
             ]
           }
      - obtener_alquileres_recientes(filtros: {ano, mes, equipo_id, limit})
        -> [
             {"id": str, "equipo_id": str/int, "equipo_nombre": str, "placa": str,
              "cliente_nombre": str, "fecha": "YYYY-MM-DD", "monto": float,
              "estado": "pagado"|"pendiente"|"vencido"}
           ]
    """

    def __init__(self, firebase_manager: FirebaseManager, parent=None):
        super().__init__(parent)
        self.fm = firebase_manager

        self.meses_mapa = {
            "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
            "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
        }

        # Mapas (se llenarán desde app_gui)
        self.equipos_mapa_nombre_id = {}  # nombre -> id
        self.equipos_mapa_id_nombre = {}  # id -> nombre
        self.operadores_mapa_id_nombre = {}  # id -> nombre

        self._setup_ui()
        self._configurar_filtros_inicial()
        self.clientes_mapa_id_nombre = {}

    # ---------------- UI ----------------

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # === Filtros ===
        filtros_group = QGroupBox("Filtros")
        filtros_layout = QHBoxLayout(filtros_group)

        filtros_layout.addWidget(QLabel("Año:"))
        self.combo_anio = QComboBox()
        filtros_layout.addWidget(self.combo_anio)

        filtros_layout.addWidget(QLabel("Mes:"))
        self.combo_mes = QComboBox()
        self.combo_mes.addItems(self.meses_mapa.keys())
        filtros_layout.addWidget(self.combo_mes)

        filtros_layout.addWidget(QLabel("Equipo:"))
        self.combo_equipo = QComboBox()
        filtros_layout.addWidget(self.combo_equipo)
        filtros_layout.addStretch()

        main_layout.addWidget(filtros_group, stretch=0)

        # === Grid de Tarjetas KPI ===
        grid_layout = QGridLayout()
        grid_layout.setSpacing(16)

        self.card_ingresos = KPICard("Ingresos Totales", "RD$ 0.00", color=AppTheme.COLORS["success"])
        grid_layout.addWidget(self.card_ingresos, 0, 0)

        self.card_pendiente = KPICard("Pendiente Cobro", "RD$ 0.00", color=AppTheme.COLORS["warning"])
        grid_layout.addWidget(self.card_pendiente, 0, 1)

        self.card_utilidad = KPICard("Utilidad Neta", "RD$ 0.00", color=AppTheme.COLORS["primary"])
        grid_layout.addWidget(self.card_utilidad, 0, 2)

        self.card_ocupacion = KPICard("Ocupación Equipos", "0.00%", color=AppTheme.COLORS["info"] if "info" in AppTheme.COLORS else AppTheme.COLORS["primary"])
        grid_layout.addWidget(self.card_ocupacion, 0, 3)

        # Tops
        self.card_top_equipo = KPICard("Equipo Más Rentable", "N/A")
        grid_layout.addWidget(self.card_top_equipo, 1, 0, 1, 2)

        self.card_top_operador = KPICard("Operador con Más Horas", "N/A")
        grid_layout.addWidget(self.card_top_operador, 1, 2, 1, 2)

        main_layout.addLayout(grid_layout, stretch=0)

        # === Tabla de Alquileres Recientes ===
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Equipo", "Cliente", "Fecha", "Monto", "Estado", ""
        ])
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setWordWrap(False)
        self.table.setShowGrid(True)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        main_layout.addWidget(self.table, stretch=1)

        # Conexiones
        self.combo_anio.currentIndexChanged.connect(self.refrescar_datos)
        self.combo_mes.currentIndexChanged.connect(self.refrescar_datos)
        self.combo_equipo.currentIndexChanged.connect(self.refrescar_datos)

    def _configurar_filtros_inicial(self):
        """Pobla los filtros de fecha (sin datos de DB)."""
        self.combo_anio.blockSignals(True)
        self.combo_mes.blockSignals(True)

        self.combo_anio.clear()
        anio_actual = datetime.now().year
        anios = [str(anio_actual - i) for i in range(5)]
        self.combo_anio.addItems(anios)
        self.combo_anio.setCurrentText(str(anio_actual))

        nombre_mes_actual = list(self.meses_mapa.keys())[datetime.now().month - 1]
        self.combo_mes.setCurrentText(nombre_mes_actual)

        self.combo_anio.blockSignals(False)
        self.combo_mes.blockSignals(False)

    # ---------------- Mapas ----------------

    def actualizar_mapas(self, mapas: dict):
        logger.info("Dashboard: Mapas recibidos. Poblando filtros...")
        logger.debug(f"Mapas equipos size={len(mapas.get('equipos', {}) or {})}, operadores size={len(mapas.get('operadores', {}) or {})}")
        self.equipos_mapa_id_nombre = mapas.get("equipos", {}) or {}
        self.operadores_mapa_id_nombre = mapas.get("operadores", {}) or {}

        self.equipos_mapa_nombre_id = {nombre: id for id, nombre in self.equipos_mapa_id_nombre.items()}

        self.combo_equipo.blockSignals(True)
        self.combo_equipo.clear()
        self.combo_equipo.addItem("Todos", None)
        for nombre in sorted(self.equipos_mapa_nombre_id.keys()):
            self.combo_equipo.addItem(nombre, self.equipos_mapa_nombre_id[nombre])
        self.combo_equipo.blockSignals(False)
        self.clientes_mapa_id_nombre = mapas.get("clientes", {}) or {}

    def refrescar_datos(self):
        if not all([self.combo_anio.currentText(), self.combo_mes.currentText()]):
            logger.warning("Dashboard: filtros incompletos.")
            return
        if not self.equipos_mapa_id_nombre or not self.operadores_mapa_id_nombre:
            logger.warning("Dashboard: Mapas aún no cargados, saltando refresco.")
            return

        anio = int(self.combo_anio.currentText())
        mes = self.meses_mapa[self.combo_mes.currentText()]
        equipo_id = self.combo_equipo.currentData()  # None = todos
        filtros = {'ano': anio, 'mes': mes, 'equipo_id': equipo_id}

        print(f"[Dashboard] Refrescando datos con filtros: {filtros}")

        try:
            kpis = self.fm.obtener_estadisticas_dashboard(filtros) or {}
            print(f"[Dashboard] KPIs recibidos: {kpis}")
            self._actualizar_kpis(kpis)
        except Exception as e:
            logger.error(f"Error refrescando KPIs: {e}", exc_info=True)
            print(f"[Dashboard] Error KPIs: {e}")

        try:
            recientes = self.fm.obtener_alquileres_recientes({**filtros, "limit": 20}) or []
            print(f"[Dashboard] Alquileres recientes recibidos: {len(recientes)} items")
            self._actualizar_tabla(recientes)
        except Exception as e:
            logger.error(f"Error cargando alquileres recientes: {e}", exc_info=True)
            print(f"[Dashboard] Error recientes: {e}")

    def _actualizar_kpis(self, kpis: dict):
        print(f"[Dashboard] _actualizar_kpis con: {kpis}")
        moneda = "RD$"
        ingresos = float(kpis.get('ingresos_totales', kpis.get('ingresos_mes', 0.0)) or 0.0)
        gastos = float(kpis.get('gastos_totales', kpis.get('gastos_mes', 0.0)) or 0.0)
        pendiente = float(kpis.get('pendiente_cobro', kpis.get('saldo_pendiente', 0.0)) or 0.0)
        utilidad = float(kpis.get('utilidad_neta', ingresos - gastos) or (ingresos - gastos))
        ocupacion = float(kpis.get('ocupacion_pct', 0.0) or 0.0)

        self.card_ingresos.update_value(f"{moneda} {ingresos:,.2f}")
        self.card_pendiente.update_value(f"{moneda} {pendiente:,.2f}")
        self.card_utilidad.update_value(f"{moneda} {utilidad:,.2f}")
        self.card_ocupacion.update_value(f"{ocupacion:,.2f}%")

        ingresos_data = kpis.get('ingresos_data', []) or []
        print(f"[Dashboard] ingresos_data len={len(ingresos_data)}")

        # Top Equipo
        equipos_ingresos = {}
        for ingreso in ingresos_data:
            eq_id = str(ingreso.get('equipo_id') or "")
            monto = float(
                ingreso.get('monto', 0)
                or ingreso.get('monto_facturado', 0)
                or ingreso.get('total', 0)
                or 0
            )
            if eq_id:
                equipos_ingresos[eq_id] = equipos_ingresos.get(eq_id, 0.0) + monto

        top_equipo_id = max(equipos_ingresos, key=equipos_ingresos.get) if equipos_ingresos else None
        top_equipo_nombre = "N/A"
        top_equipo_monto = 0.0
        if top_equipo_id:
            top_equipo_nombre = self.equipos_mapa_id_nombre.get(top_equipo_id, f"ID: {top_equipo_id}")
            top_equipo_monto = equipos_ingresos[top_equipo_id]
        self.card_top_equipo.update_value(f"{top_equipo_nombre}\n({moneda} {top_equipo_monto:,.2f})")

        # Top Operador
        operadores_horas = {}
        for ingreso in ingresos_data:
            op_id = str(ingreso.get('operador_id') or "")
            horas = float(ingreso.get('horas', 0) or ingreso.get('horas_operadas', 0) or 0)
            if op_id and horas:
                operadores_horas[op_id] = operadores_horas.get(op_id, 0.0) + horas

        top_operador_id = max(operadores_horas, key=operadores_horas.get) if operadores_horas else None
        top_operador_nombre = "N/A"
        top_operador_horas = 0.0
        if top_operador_id:
            top_operador_nombre = self.operadores_mapa_id_nombre.get(top_operador_id, f"ID: {top_operador_id}")
            top_operador_horas = operadores_horas[top_operador_id]
        self.card_top_operador.update_value(f"{top_operador_nombre}\n({top_operador_horas:.2f} Horas)")

    def _actualizar_tabla(self, rows: list[dict]):
        print(f"[Dashboard] _actualizar_tabla con {len(rows)} filas")
        self.table.setRowCount(0)
        for r, d in enumerate(rows):
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(d.get("id", ""))))

            equipo_nombre = d.get("equipo_nombre") or self.equipos_mapa_id_nombre.get(str(d.get("equipo_id", "")), "")
            placa = d.get("placa") or ""
            equipo_txt = equipo_nombre if not placa else f"{equipo_nombre} ({placa})"
            self.table.setItem(r, 1, QTableWidgetItem(equipo_txt))

            cliente_nombre = d.get("cliente_nombre") or self.clientes_mapa_id_nombre.get(str(d.get("cliente_id", "")), "")
            self.table.setItem(r, 2, QTableWidgetItem(cliente_nombre))

            self.table.setItem(r, 3, QTableWidgetItem(str(d.get("fecha", ""))))

            monto_txt = f"RD$ {float(d.get('monto', 0) or 0):,.2f}"
            self.table.setItem(r, 4, QTableWidgetItem(monto_txt))
            self.table.item(r, 4).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            estado = str(d.get("estado", "")).lower()
            estado_item = QTableWidgetItem(estado.capitalize() if estado else "")
            if estado == "pagado":
                estado_item.setForeground(QColor("#42BE65"))
            elif estado == "pendiente":
                estado_item.setForeground(QColor("#F1C21B"))
            elif estado == "vencido":
                estado_item.setForeground(QColor("#FF8389"))
            self.table.setItem(r, 5, estado_item)

            self.table.setItem(r, 6, QTableWidgetItem("⋯"))

        self.table.resizeColumnsToContents()
        for r in range(self.table.rowCount()):
            for c in [4, 5]:
                item = self.table.item(r, c)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)