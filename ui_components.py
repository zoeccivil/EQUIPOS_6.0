"""
Componentes UI Reutilizables para EQUIPOS 6.0
Estilo moderno "Tierra & Asfalto"
"""

from PyQt6.QtWidgets import (
    QWidget, QLabel, QFrame, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLineEdit, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QIcon
from app_theme_modern import ModernTheme
from icons import get_icon, get_icon_pixmap


class SidebarButton(QPushButton):
    """
    Botón de navegación para el sidebar con iconos SVG y estados visuales.
    
    Estados:
    - Normal: Fondo transparente, texto gris claro
    - Hover: Fondo semitransparente blanco
    - Activo/Checked: Fondo amarillo, texto oscuro, negrita
    """
    
    def __init__(self, text: str, icon_name: str = None, parent: QWidget = None):
        super().__init__(text, parent)
        self.icon_name = icon_name
        self.setCheckable(True)
        self.setMinimumHeight(48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Configurar icono si se proporciona
        if icon_name:
            self._update_icon()
        
        # Estilo inicial
        self._apply_style()
        
        # Conectar señales para actualizar iconos
        self.toggled.connect(self._on_toggled)
    
    def _apply_style(self):
        """Aplica el estilo CSS al botón"""
        c = ModernTheme.COLORS
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {c['text_sidebar_muted']};
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                text-align: left;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {c['bg_sidebar_hover']};
                color: {c['text_sidebar']};
            }}
            QPushButton:checked {{
                background-color: {c['primary']};
                color: {c['primary_text']};
                font-weight: 700;
            }}
        """)
    
    def _update_icon(self):
        """Actualiza el icono según el estado del botón"""
        if not self.icon_name:
            return
        
        # Color del icono según estado
        if self.isChecked():
            color = ModernTheme.COLORS['primary_text']
        else:
            color = ModernTheme.COLORS['text_sidebar_muted']
        
        icon = get_icon(self.icon_name, color)
        self.setIcon(icon)
        self.setIconSize(QSize(20, 20))
    
    def _on_toggled(self, checked: bool):
        """Actualiza el icono cuando cambia el estado"""
        self._update_icon()


class StatCard(QFrame):
    """
    Tarjeta KPI moderna con icono, título, valor y barra de color.
    Replica el diseño de las tarjetas del prototipo HTML.
    
    Args:
        title: Título de la métrica (ej: "Ingresos Totales")
        value: Valor principal (ej: "RD$ 250,000")
        icon_name: Nombre del icono SVG
        accent_color: Color de acento para el icono y barra inferior
        footer_text: Texto adicional en el pie (opcional)
    """
    
    def __init__(self, title: str, value: str = "N/A", icon_name: str = None,
                 accent_color: str = None, footer_text: str = None, parent: QWidget = None):
        super().__init__(parent)
        self.accent_color = accent_color or ModernTheme.COLORS['primary']
        
        # Configurar frame
        self.setProperty("class", "card")
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {ModernTheme.COLORS['bg_card']};
                border: 1px solid {ModernTheme.COLORS['border']};
                border-radius: 12px;
                padding: 0px;
            }}
        """)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 16)
        main_layout.setSpacing(12)
        
        # Header: icono + título
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        # Icono en círculo de color
        if icon_name:
            icon_container = QFrame()
            icon_container.setFixedSize(40, 40)
            icon_container.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.accent_color}20;
                    border-radius: 20px;
                }}
            """)
            
            icon_layout = QHBoxLayout(icon_container)
            icon_layout.setContentsMargins(0, 0, 0, 0)
            
            icon_label = QLabel()
            pixmap = get_icon_pixmap(icon_name, self.accent_color, (20, 20))
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_layout.addWidget(icon_label)
            
            header_layout.addWidget(icon_container)
        
        # Título
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"""
            color: {ModernTheme.COLORS['text_muted']};
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Valor principal
        self.value_label = QLabel(value)
        value_font = QFont("Segoe UI", 28)
        value_font.setWeight(QFont.Weight.Bold)
        self.value_label.setFont(value_font)
        self.value_label.setStyleSheet(f"color: {ModernTheme.COLORS['text_main']};")
        main_layout.addWidget(self.value_label)
        
        # Footer (opcional)
        if footer_text:
            self.footer_label = QLabel(footer_text)
            self.footer_label.setStyleSheet(f"""
                color: {ModernTheme.COLORS['text_muted']};
                font-size: 12px;
            """)
            main_layout.addWidget(self.footer_label)
        else:
            self.footer_label = None
        
        main_layout.addStretch()
        
        # Barra de color inferior
        color_bar = QFrame()
        color_bar.setFixedHeight(4)
        color_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {self.accent_color}80;
                border: none;
                border-radius: 0px;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }}
        """)
        main_layout.addWidget(color_bar)
        
        # Sombra sutil
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
    
    def update_value(self, value: str, footer_text: str = None):
        """Actualiza el valor y el footer de la tarjeta"""
        self.value_label.setText(value)
        if footer_text and self.footer_label:
            self.footer_label.setText(footer_text)


class StatusBadge(QLabel):
    """
    Etiqueta tipo píldora para estados (pagado, pendiente, vencido).
    
    Métodos de conveniencia:
    - setPaid(): Estilo verde para "Pagado"
    - setPending(): Estilo amarillo para "Pendiente"
    - setOverdue(): Estilo rojo para "Vencido"
    """
    
    def __init__(self, text: str = "", status_type: str = "default", parent: QWidget = None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMaximumWidth(120)
        self._apply_status(status_type)
    
    def _apply_status(self, status_type: str):
        """Aplica el estilo según el tipo de estado"""
        c = ModernTheme.COLORS
        
        styles = {
            'success': (c['success_bg'], c['success_text']),
            'paid': (c['success_bg'], c['success_text']),
            'warning': (c['warning_bg'], c['warning_text']),
            'pending': (c['warning_bg'], c['warning_text']),
            'danger': (c['danger_bg'], c['danger_text']),
            'overdue': (c['danger_bg'], c['danger_text']),
            'default': (c['border'], c['text_muted'])
        }
        
        bg_color, text_color = styles.get(status_type, styles['default'])
        
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: 20px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }}
        """)
    
    def setPaid(self):
        """Configura el badge como 'Pagado' (verde)"""
        self.setText("Pagado")
        self._apply_status('paid')
    
    def setPending(self):
        """Configura el badge como 'Pendiente' (amarillo)"""
        self.setText("Pendiente")
        self._apply_status('pending')
    
    def setOverdue(self):
        """Configura el badge como 'Vencido' (rojo)"""
        self.setText("Vencido")
        self._apply_status('overdue')
    
    def setStatus(self, status_text: str, status_type: str):
        """Configura texto y estilo manualmente"""
        self.setText(status_text)
        self._apply_status(status_type)


class TopBar(QWidget):
    """
    Barra superior de navegación con título y búsqueda.
    
    Args:
        title: Título de la página actual
        show_search: Si True, muestra la barra de búsqueda
    """
    
    def __init__(self, title: str = "", show_search: bool = True, parent: QWidget = None):
        super().__init__(parent)
        self.setFixedHeight(70)
        
        # Estilo del widget
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {ModernTheme.COLORS['bg_card']};
                border-bottom: 1px solid {ModernTheme.COLORS['border']};
            }}
        """)
        
        # Layout principal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(16)
        
        # Título
        self.title_label = QLabel(title)
        title_font = QFont("Segoe UI", 20)
        title_font.setWeight(QFont.Weight.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet(f"color: {ModernTheme.COLORS['text_main']};")
        layout.addWidget(self.title_label)
        
        layout.addStretch()
        
        # Barra de búsqueda (opcional)
        if show_search:
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Buscar...")
            self.search_input.setFixedWidth(300)
            self.search_input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {ModernTheme.COLORS['bg_body']};
                    border: 1px solid {ModernTheme.COLORS['border']};
                    border-radius: 8px;
                    padding: 8px 12px 8px 36px;
                    font-size: 14px;
                }}
                QLineEdit:focus {{
                    border: 2px solid {ModernTheme.COLORS['primary']};
                    padding: 7px 11px 7px 35px;
                }}
            """)
            
            # Icono de búsqueda (placeholder visual)
            search_icon_label = QLabel()
            search_icon_pixmap = get_icon_pixmap('search', ModernTheme.COLORS['text_muted'], (16, 16))
            search_icon_label.setPixmap(search_icon_pixmap)
            search_icon_label.setStyleSheet("background: transparent; border: none;")
            
            # Container para superponer icono y input
            search_container = QWidget()
            search_layout = QHBoxLayout(search_container)
            search_layout.setContentsMargins(12, 0, 0, 0)
            search_layout.setSpacing(0)
            search_layout.addWidget(search_icon_label)
            search_layout.addWidget(self.search_input)
            
            layout.addWidget(self.search_input)
        else:
            self.search_input = None
    
    def set_title(self, title: str):
        """Actualiza el título de la barra"""
        self.title_label.setText(title)


class ModernCard(QFrame):
    """
    Contenedor de tarjeta genérico con fondo blanco y bordes redondeados.
    Ideal para agrupar contenido con sombra sutil.
    
    Args:
        title: Título opcional de la tarjeta
        padding: Padding interior en píxeles
    """
    
    def __init__(self, title: str = None, padding: int = 20, parent: QWidget = None):
        super().__init__(parent)
        
        # Estilo
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {ModernTheme.COLORS['bg_card']};
                border: 1px solid {ModernTheme.COLORS['border']};
                border-radius: 12px;
            }}
        """)
        
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(padding, padding, padding, padding)
        self.main_layout.setSpacing(16)
        
        # Título si se proporciona
        if title:
            title_label = QLabel(title)
            title_font = QFont("Segoe UI", 16)
            title_font.setWeight(QFont.Weight.Bold)
            title_label.setFont(title_font)
            title_label.setStyleSheet(f"color: {ModernTheme.COLORS['text_main']};")
            self.main_layout.addWidget(title_label)
        
        # Sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
    
    def add_widget(self, widget: QWidget):
        """Añade un widget al contenido de la tarjeta"""
        self.main_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """Añade un layout al contenido de la tarjeta"""
        self.main_layout.addLayout(layout)


class ModernButton(QPushButton):
    """
    Botón moderno con estilos predefinidos.
    
    Args:
        text: Texto del botón
        button_type: Tipo ('primary', 'secondary', 'success', 'danger')
        icon_name: Nombre del icono SVG (opcional)
    """
    
    def __init__(self, text: str, button_type: str = "primary", 
                 icon_name: str = None, parent: QWidget = None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.icon_name = icon_name
        
        # Configurar icono
        if icon_name:
            self._set_icon()
        
        # Aplicar clase CSS
        self.setProperty("class", button_type)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def _set_icon(self):
        """Configura el icono del botón"""
        if not self.icon_name:
            return
        
        # Color del icono según tipo
        color_map = {
            'primary': ModernTheme.COLORS['primary_text'],
            'secondary': ModernTheme.COLORS['text_main'],
            'success': '#FFFFFF',
            'danger': '#FFFFFF'
        }
        
        color = color_map.get(self.button_type, ModernTheme.COLORS['text_main'])
        icon = get_icon(self.icon_name, color)
        self.setIcon(icon)
        self.setIconSize(QSize(18, 18))
