"""
WhatsApp Business Integration para EQUIPOS 6.0 MODERN
Envío de mensajes y recordatorios automáticos
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QDateEdit, QComboBox,
    QDoubleSpinBox, QTextEdit, QMessageBox, QGridLayout,
    QGroupBox, QTabWidget
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from app_theme import AppTheme, ModernTable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WhatsAppIntegration(QWidget):
    """
    Integración con WhatsApp Business para envío de mensajes
    """
    
    def __init__(self, firebase_manager, config, parent=None):
        super().__init__(parent)
        self.fm = firebase_manager
        self.config = config
        
        # Verificar configuración de WhatsApp
        self.whatsapp_config = config.get("whatsapp", {})
        self.provider = self.whatsapp_config.get("provider", "")
        
        self._crear_interfaz()
        self._cargar_plantillas()
        self._cargar_historial()
    
    def _crear_interfaz(self):
        """Crea la interfaz de WhatsApp Business"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Título
        titulo = QLabel("📱 WhatsApp Business")
        titulo_font = QFont("Inter", 24)
        titulo_font.setBold(True)
        titulo.setFont(titulo_font)
        titulo.setStyleSheet(f"color: {AppTheme.COLORS['primary']};")
        layout.addWidget(titulo)
        
        # Subtítulo
        subtitulo = QLabel("Envío de mensajes y recordatorios automáticos")
        subtitulo.setStyleSheet(f"color: {AppTheme.COLORS['text_secondary']}; font-size: 14px;")
        layout.addWidget(subtitulo)
        
        # Estado de conexión
        estado_frame = QFrame()
        estado_frame.setProperty("class", "card")
        estado_layout = QHBoxLayout(estado_frame)
        
        if self._verificar_configuracion():
            estado_icon = "✅"
            estado_text = f"Conectado - Provider: {self.provider}"
            estado_color = AppTheme.COLORS["success"]
        else:
            estado_icon = "❌"
            estado_text = "No configurado - Verificar config.json"
            estado_color = AppTheme.COLORS["danger"]
        
        self.label_estado = QLabel(f"{estado_icon} {estado_text}")
        self.label_estado.setStyleSheet(f"color: {estado_color}; font-weight: bold;")
        estado_layout.addWidget(self.label_estado)
        
        estado_layout.addStretch()
        
        btn_config = QPushButton("⚙️ Configuración")
        btn_config.setProperty("class", "secondary")
        btn_config.clicked.connect(self._mostrar_configuracion)
        estado_layout.addWidget(btn_config)
        
        layout.addWidget(estado_frame)
        
        # Tabs: Enviar Mensaje / Historial / Plantillas
        tabs = QTabWidget()
        
        # Tab 1: Enviar Mensaje
        tab_enviar = self._crear_tab_enviar()
        tabs.addTab(tab_enviar, "📤 Enviar Mensaje")
        
        # Tab 2: Historial
        tab_historial = self._crear_tab_historial()
        tabs.addTab(tab_historial, "📜 Historial")
        
        # Tab 3: Plantillas
        tab_plantillas = self._crear_tab_plantillas()
        tabs.addTab(tab_plantillas, "📋 Plantillas")
        
        layout.addWidget(tabs)
    
    def _crear_tab_enviar(self):
        """Crea el tab para enviar mensajes"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Destinatario
        destinatario_group = QGroupBox("Destinatario")
        destinatario_layout = QFormLayout(destinatario_group)
        
        # Tipo de destinatario
        tipo_layout = QHBoxLayout()
        self.combo_tipo_dest = QComboBox()
        self.combo_tipo_dest.addItems(["Cliente", "Operador", "Personalizado"])
        self.combo_tipo_dest.currentIndexChanged.connect(self._cambiar_tipo_destinatario)
        tipo_layout.addWidget(self.combo_tipo_dest)
        destinatario_layout.addRow("Tipo:", tipo_layout)
        
        # Selector de cliente/operador
        self.combo_destinatario = QComboBox()
        self.combo_destinatario.setMinimumWidth(300)
        destinatario_layout.addRow("Seleccionar:", self.combo_destinatario)
        
        # Número manual
        self.input_numero = QLineEdit()
        self.input_numero.setPlaceholderText("+593999999999")
        self.input_numero.setVisible(False)
        destinatario_layout.addRow("Número:", self.input_numero)
        
        layout.addWidget(destinatario_group)
        
        # Mensaje
        mensaje_group = QGroupBox("Mensaje")
        mensaje_layout = QVBoxLayout(mensaje_group)
        
        # Plantilla rápida
        plantilla_layout = QHBoxLayout()
        plantilla_label = QLabel("Plantilla:")
        plantilla_layout.addWidget(plantilla_label)
        
        self.combo_plantilla = QComboBox()
        self.combo_plantilla.addItem("Mensaje personalizado", None)
        self.combo_plantilla.currentIndexChanged.connect(self._aplicar_plantilla)
        plantilla_layout.addWidget(self.combo_plantilla, 1)
        
        mensaje_layout.addLayout(plantilla_layout)
        
        # Área de texto
        self.text_mensaje = QTextEdit()
        self.text_mensaje.setMinimumHeight(200)
        self.text_mensaje.setPlaceholderText("Escribe tu mensaje aquí...")
        mensaje_layout.addWidget(self.text_mensaje)
        
        # Contador de caracteres
        self.label_contador = QLabel("0 / 1600 caracteres")
        self.label_contador.setStyleSheet(f"color: {AppTheme.COLORS['text_secondary']}; font-size: 11px;")
        self.text_mensaje.textChanged.connect(self._actualizar_contador)
        mensaje_layout.addWidget(self.label_contador)
        
        layout.addWidget(mensaje_group)
        
        # Botón enviar
        btn_enviar = QPushButton("📤 Enviar Mensaje")
        btn_enviar.setProperty("class", "primary")
        btn_enviar.setMinimumHeight(48)
        btn_enviar.clicked.connect(self._enviar_mensaje)
        layout.addWidget(btn_enviar)
        
        layout.addStretch()
        
        return widget
    
    def _crear_tab_historial(self):
        """Crea el tab del historial de mensajes"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        btn_actualizar = QPushButton("🔄 Actualizar")
        btn_actualizar.setProperty("class", "secondary")
        btn_actualizar.clicked.connect(self._cargar_historial)
        toolbar.addWidget(btn_actualizar)
        
        toolbar.addStretch()
        
        # Filtro por estado
        filtro_label = QLabel("Estado:")
        toolbar.addWidget(filtro_label)
        
        self.combo_filtro_estado = QComboBox()
        self.combo_filtro_estado.addItems(["Todos", "Enviados", "Errores"])
        self.combo_filtro_estado.currentIndexChanged.connect(self._cargar_historial)
        toolbar.addWidget(self.combo_filtro_estado)
        
        layout.addLayout(toolbar)
        
        # Tabla de historial
        self.tabla_historial = ModernTable([
            "Fecha/Hora",
            "Destinatario",
            "Número",
            "Mensaje",
            "Estado",
            "Acciones"
        ])
        self.tabla_historial.setMinimumHeight(400)
        layout.addWidget(self.tabla_historial)
        
        return widget
    
    def _crear_tab_plantillas(self):
        """Crea el tab de plantillas rápidas"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        info_label = QLabel("Plantillas predefinidas para envíos rápidos")
        info_label.setStyleSheet(f"color: {AppTheme.COLORS['text_secondary']};")
        layout.addWidget(info_label)
        
        # Lista de plantillas
        plantillas = [
            {
                "nombre": "Recordatorio de Pago",
                "mensaje": "Estimado cliente, le recordamos que tiene un pago pendiente por ${monto} correspondiente al alquiler de {equipo}. Por favor, regularice su pago a la brevedad posible. Gracias."
            },
            {
                "nombre": "Confirmación de Alquiler",
                "mensaje": "Su alquiler del equipo {equipo} ha sido confirmado para el {fecha}. Cualquier consulta, estamos a su disposición."
            },
            {
                "nombre": "Mantenimiento Programado",
                "mensaje": "Le informamos que el equipo {equipo} entrará en mantenimiento el {fecha}. Por favor, coordine la devolución con anticipación."
            },
            {
                "nombre": "Agradecimiento",
                "mensaje": "Gracias por su pago de ${monto}. Su cuenta ha sido actualizada correctamente. Seguimos a sus órdenes."
            }
        ]
        
        for plantilla in plantillas:
            plantilla_frame = QFrame()
            plantilla_frame.setProperty("class", "card")
            plantilla_layout = QVBoxLayout(plantilla_frame)
            
            titulo = QLabel(plantilla["nombre"])
            titulo.setStyleSheet(f"color: {AppTheme.COLORS['primary']}; font-weight: bold; font-size: 14px;")
            plantilla_layout.addWidget(titulo)
            
            mensaje = QLabel(plantilla["mensaje"])
            mensaje.setWordWrap(True)
            mensaje.setStyleSheet(f"color: {AppTheme.COLORS['text_secondary']}; padding: 8px 0;")
            plantilla_layout.addWidget(mensaje)
            
            layout.addWidget(plantilla_frame)
        
        layout.addStretch()
        
        return widget
    
    def _verificar_configuracion(self):
        """Verifica si WhatsApp está configurado correctamente"""
        if not self.whatsapp_config:
            return False
        
        provider = self.whatsapp_config.get("provider", "")
        
        if provider == "twilio":
            return all([
                self.whatsapp_config.get("twilio_account_sid"),
                self.whatsapp_config.get("twilio_auth_token"),
                self.whatsapp_config.get("twilio_from")
            ])
        elif provider == "whatsapp_business":
            return all([
                self.whatsapp_config.get("api_token"),
                self.whatsapp_config.get("phone_id")
            ])
        
        return False
    
    def _cargar_plantillas(self):
        """Carga las plantillas en el combo"""
        plantillas = [
            ("Recordatorio de Pago", "Estimado cliente, le recordamos que tiene un pago pendiente por ${monto}..."),
            ("Confirmación de Alquiler", "Su alquiler del equipo {equipo} ha sido confirmado..."),
            ("Mantenimiento", "Le informamos que el equipo {equipo} entrará en mantenimiento..."),
            ("Agradecimiento", "Gracias por su pago de ${monto}. Su cuenta ha sido actualizada...")
        ]
        
        for nombre, texto in plantillas:
            self.combo_plantilla.addItem(nombre, texto)
    
    def _cambiar_tipo_destinatario(self):
        """Cambia el tipo de destinatario"""
        tipo = self.combo_tipo_dest.currentText()
        
        if tipo == "Personalizado":
            self.combo_destinatario.setVisible(False)
            self.input_numero.setVisible(True)
        else:
            self.combo_destinatario.setVisible(True)
            self.input_numero.setVisible(False)
            
            # Cargar lista según tipo
            self.combo_destinatario.clear()
            
            try:
                if tipo == "Cliente":
                    clientes = self.fm.obtener_clientes()
                    for cliente in clientes:
                        nombre = cliente.get("nombre", "Sin nombre")
                        telefono = cliente.get("telefono", "")
                        if telefono:
                            self.combo_destinatario.addItem(f"{nombre} - {telefono}", telefono)
                
                elif tipo == "Operador":
                    operadores = self.fm.obtener_operadores()
                    for operador in operadores:
                        nombre = operador.get("nombre", "Sin nombre")
                        telefono = operador.get("telefono", "")
                        if telefono:
                            self.combo_destinatario.addItem(f"{nombre} - {telefono}", telefono)
                            
            except Exception as e:
                logger.error(f"Error cargando destinatarios: {e}", exc_info=True)
    
    def _aplicar_plantilla(self):
        """Aplica una plantilla al mensaje"""
        texto = self.combo_plantilla.currentData()
        if texto:
            self.text_mensaje.setPlainText(texto)
    
    def _actualizar_contador(self):
        """Actualiza el contador de caracteres"""
        texto = self.text_mensaje.toPlainText()
        longitud = len(texto)
        self.label_contador.setText(f"{longitud} / 1600 caracteres")
        
        if longitud > 1600:
            self.label_contador.setStyleSheet(f"color: {AppTheme.COLORS['danger']}; font-size: 11px;")
        else:
            self.label_contador.setStyleSheet(f"color: {AppTheme.COLORS['text_secondary']}; font-size: 11px;")
    
    def _enviar_mensaje(self):
        """Envía un mensaje de WhatsApp"""
        try:
            # Validar configuración
            if not self._verificar_configuracion():
                QMessageBox.warning(
                    self,
                    "Configuración Incompleta",
                    "WhatsApp no está configurado correctamente.\n\n"
                    "Por favor, verifica la configuración en config.json"
                )
                return
            
            # Obtener destinatario
            tipo = self.combo_tipo_dest.currentText()
            if tipo == "Personalizado":
                numero = self.input_numero.text().strip()
                destinatario = "Personalizado"
            else:
                numero = self.combo_destinatario.currentData()
                destinatario = self.combo_destinatario.currentText().split(" - ")[0]
            
            # Validar número
            if not numero:
                QMessageBox.warning(self, "Error", "Debe seleccionar o ingresar un número de teléfono")
                return
            
            # Validar mensaje
            mensaje = self.text_mensaje.toPlainText().strip()
            if not mensaje:
                QMessageBox.warning(self, "Error", "El mensaje no puede estar vacío")
                return
            
            if len(mensaje) > 1600:
                QMessageBox.warning(self, "Error", "El mensaje es demasiado largo (máximo 1600 caracteres)")
                return
            
            # Simular envío (en producción, usar API real)
            resultado = self._enviar_mensaje_whatsapp(numero, mensaje)
            
            if resultado["success"]:
                # Registrar en Firebase
                datos_mensaje = {
                    "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "destinatario": destinatario,
                    "numero": numero,
                    "mensaje": mensaje,
                    "estado": "enviado",
                    "mensaje_id": resultado.get("message_id", "sim_" + datetime.now().strftime("%Y%m%d%H%M%S"))
                }
                
                self.fm.registrar_mensaje_whatsapp(datos_mensaje)
                
                QMessageBox.information(
                    self,
                    "Mensaje Enviado",
                    f"El mensaje ha sido enviado correctamente a {destinatario}"
                )
                
                # Limpiar formulario
                self.text_mensaje.clear()
                
                # Actualizar historial
                self._cargar_historial()
            else:
                # Registrar error
                datos_mensaje = {
                    "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "destinatario": destinatario,
                    "numero": numero,
                    "mensaje": mensaje,
                    "estado": "error",
                    "error": resultado.get("error", "Error desconocido")
                }
                
                self.fm.registrar_mensaje_whatsapp(datos_mensaje)
                
                QMessageBox.warning(
                    self,
                    "Error al Enviar",
                    f"No se pudo enviar el mensaje:\n{resultado.get('error', 'Error desconocido')}"
                )
            
        except Exception as e:
            logger.error(f"Error enviando mensaje: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al enviar mensaje: {e}")
    
    def _enviar_mensaje_whatsapp(self, numero, mensaje):
        """
        Envía un mensaje de WhatsApp usando el provider configurado
        
        ⚠️ IMPORTANTE: Esta es una implementación SIMULADA para desarrollo.
        
        En producción, debe implementarse la integración real con:
        - Twilio WhatsApp API: https://www.twilio.com/docs/whatsapp
        - WhatsApp Business API: https://developers.facebook.com/docs/whatsapp
        
        Args:
            numero: Número de teléfono con código de país (ej: +593999999999)
            mensaje: Texto del mensaje a enviar
            
        Returns:
            dict: {"success": bool, "message_id": str} o {"success": False, "error": str}
        """
        try:
            # Validar número (debe incluir código de país)
            if not numero.startswith("+"):
                return {"success": False, "error": "El número debe incluir el código de país (ej: +593)"}
            
            # ============================================================
            # TODO: IMPLEMENTAR INTEGRACIÓN REAL CON API DE WHATSAPP
            # ============================================================
            # 
            # Ejemplo con Twilio:
            # if self.provider == "twilio":
            #     from twilio.rest import Client
            #     client = Client(
            #         self.whatsapp_config.get("twilio_account_sid"),
            #         self.whatsapp_config.get("twilio_auth_token")
            #     )
            #     message = client.messages.create(
            #         from_='whatsapp:' + self.whatsapp_config.get("twilio_from"),
            #         body=mensaje,
            #         to='whatsapp:' + numero
            #     )
            #     return {"success": True, "message_id": message.sid}
            # 
            # Ejemplo con WhatsApp Business API:
            # elif self.provider == "whatsapp_business":
            #     import requests
            #     url = f"https://graph.facebook.com/v17.0/{phone_id}/messages"
            #     headers = {
            #         "Authorization": f"Bearer {api_token}",
            #         "Content-Type": "application/json"
            #     }
            #     data = {
            #         "messaging_product": "whatsapp",
            #         "to": numero,
            #         "type": "text",
            #         "text": {"body": mensaje}
            #     }
            #     response = requests.post(url, json=data, headers=headers)
            #     return {"success": True, "message_id": response.json()["messages"][0]["id"]}
            # ============================================================
            
            # Por ahora, simular envío exitoso
            logger.info(f"[SIMULADO] Enviando WhatsApp a {numero}: {mensaje[:50]}...")
            
            return {
                "success": True,
                "message_id": f"sim_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
        except Exception as e:
            logger.error(f"Error en _enviar_mensaje_whatsapp: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _cargar_historial(self):
        """Carga el historial de mensajes enviados"""
        try:
            logger.info("Cargando historial de mensajes...")
            
            # Obtener mensajes
            mensajes = self.fm.obtener_mensajes_whatsapp()
            
            # Filtrar por estado si es necesario
            filtro_estado = self.combo_filtro_estado.currentText()
            if filtro_estado == "Enviados":
                mensajes = [m for m in mensajes if m.get("estado") == "enviado"]
            elif filtro_estado == "Errores":
                mensajes = [m for m in mensajes if m.get("estado") == "error"]
            
            # Limpiar tabla
            self.tabla_historial.clear_table()
            
            # Poblar tabla
            for mensaje in mensajes:
                fecha_hora = mensaje.get("fecha_hora", "")
                destinatario = mensaje.get("destinatario", "")
                numero = mensaje.get("numero", "")
                texto = mensaje.get("mensaje", "")
                estado = mensaje.get("estado", "")
                
                # Truncar mensaje largo
                if len(texto) > 50:
                    texto_mostrar = texto[:47] + "..."
                else:
                    texto_mostrar = texto
                
                # Estado con color
                estado_texto = "✅ Enviado" if estado == "enviado" else "❌ Error"
                
                # Botón ver completo
                btn_ver = QPushButton("👁️")
                btn_ver.setProperty("class", "secondary")
                btn_ver.setMaximumWidth(40)
                btn_ver.setToolTip("Ver mensaje completo")
                btn_ver.clicked.connect(lambda checked, m=mensaje: self._ver_mensaje_completo(m))
                
                # Añadir fila
                row = self.tabla_historial.rowCount()
                self.tabla_historial.insertRow(row)
                
                self.tabla_historial.setItem(row, 0, QTableWidgetItem(fecha_hora))
                self.tabla_historial.setItem(row, 1, QTableWidgetItem(destinatario))
                self.tabla_historial.setItem(row, 2, QTableWidgetItem(numero))
                self.tabla_historial.setItem(row, 3, QTableWidgetItem(texto_mostrar))
                self.tabla_historial.setItem(row, 4, QTableWidgetItem(estado_texto))
                
                # Widget contenedor para botón
                acciones_widget = QWidget()
                acciones_layout = QHBoxLayout(acciones_widget)
                acciones_layout.setContentsMargins(4, 4, 4, 4)
                acciones_layout.addWidget(btn_ver)
                self.tabla_historial.setCellWidget(row, 5, acciones_widget)
            
            logger.info(f"Cargados {len(mensajes)} mensajes en el historial")
            
        except Exception as e:
            logger.error(f"Error cargando historial: {e}", exc_info=True)
    
    def _ver_mensaje_completo(self, mensaje):
        """Muestra el mensaje completo en un diálogo"""
        info = f"""
<h3>Detalles del Mensaje</h3>
<p><b>Fecha/Hora:</b> {mensaje.get('fecha_hora', 'N/A')}</p>
<p><b>Destinatario:</b> {mensaje.get('destinatario', 'N/A')}</p>
<p><b>Número:</b> {mensaje.get('numero', 'N/A')}</p>
<p><b>Estado:</b> {mensaje.get('estado', 'N/A')}</p>
{f"<p><b>Error:</b> {mensaje.get('error', '')}</p>" if mensaje.get('error') else ""}

<h3>Mensaje:</h3>
<p>{mensaje.get('mensaje', 'N/A')}</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Detalles del Mensaje")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(info)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
    
    def _mostrar_configuracion(self):
        """Muestra información sobre la configuración de WhatsApp"""
        info = """
<h3>Configuración de WhatsApp Business</h3>

<p>Para usar esta funcionalidad, debes configurar WhatsApp en <b>config.json</b>:</p>

<h4>Opción A: Twilio (Recomendado para desarrollo)</h4>
<pre>
{
  "whatsapp": {
    "provider": "twilio",
    "twilio_account_sid": "ACxxxxxxxx",
    "twilio_auth_token": "tu_token",
    "twilio_from": "+14155238886"
  }
}
</pre>

<h4>Opción B: WhatsApp Business API (Producción)</h4>
<pre>
{
  "whatsapp": {
    "provider": "whatsapp_business",
    "api_token": "EAAxxxxxxxx",
    "phone_id": "123456789"
  }
}
</pre>

<p><b>Nota:</b> Después de editar config.json, reinicia la aplicación.</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Configuración de WhatsApp")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(info)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
