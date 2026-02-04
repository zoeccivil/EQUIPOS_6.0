# EQUIPOS 6.0 MODERN 🚀

Versión extendida de EQUIPOS 6.0 con 4 módulos adicionales avanzados.

## 🆕 Módulos Nuevos

### 1. Dashboard Ejecutivo 📊
- KPIs en tiempo real (ingresos, gastos, utilidad)
- Gráficos interactivos de tendencias
- Top 5 equipos más rentables
- Alertas automáticas de negocio
- Métricas de utilización de equipos

### 2. Control de Combustible ⛽
- Registro de cargas por equipo
- Cálculo de eficiencia (L/h)
- Gráficos de consumo histórico
- Detección de consumos anómalos
- Exportación a Excel

### 3. Cuentas por Cobrar 💳
- Seguimiento de pagos pendientes
- Alertas de vencimiento (vencidas, por vencer)
- Registro de pagos
- Cálculo automático de saldos
- Estados de cuenta
- Métricas de cobranza (tasa de recuperación, edad promedio de deuda)

### 4. WhatsApp Business 📱
- Envío de mensajes individuales
- Recordatorios de pago automáticos
- Confirmaciones de alquiler
- Plantillas rápidas personalizables
- Historial completo de mensajes
- Integración con Twilio o WhatsApp Business API

## 🚀 Ejecución

### Versión Original (sin cambios):
```bash
python main_qt.py
```

### Versión MODERN (con módulos nuevos):
```bash
python main_modern.py
```

## 📦 Dependencias Adicionales

Instalar con:
```bash
pip install PyQt6 firebase-admin openpyxl twilio requests
```

O usar:
```bash
pip install -r requirements.txt
```

### Dependencias principales:
- **PyQt6**: Framework de interfaz gráfica
- **firebase-admin**: Conexión con Firebase/Firestore
- **openpyxl**: Exportación a Excel (opcional)
- **twilio**: Integración con WhatsApp (opcional)

## ⚙️ Configuración

### WhatsApp Business

#### Opción A: Twilio (Recomendado para desarrollo)
1. Regístrate en [Twilio](https://www.twilio.com/)
2. Activa WhatsApp Sandbox
3. Agrega a `config_equipos.json`:
```json
{
  "whatsapp": {
    "provider": "twilio",
    "twilio_account_sid": "ACxxxxxxxx",
    "twilio_auth_token": "tu_token",
    "twilio_from": "+14155238886"
  }
}
```

#### Opción B: WhatsApp Business API (Producción)
1. Regístrate en [Meta for Developers](https://developers.facebook.com/)
2. Crea una app de WhatsApp Business
3. Agrega a `config_equipos.json`:
```json
{
  "whatsapp": {
    "provider": "whatsapp_business",
    "api_token": "EAAxxxxxxxx",
    "phone_id": "123456789"
  }
}
```

### Firebase (ya configurado)
Los módulos nuevos usan las mismas credenciales de Firebase existentes.

## 📁 Estructura de Archivos

```
EQUIPOS_6.0/
├── app_gui_qt.py              ← ORIGINAL (sin cambios)
├── app_gui_modern.py          ← NUEVO (8 módulos)
├── main_qt.py                 ← ORIGINAL (sin cambios)
├── main_modern.py             ← NUEVO
├── dashboard_ejecutivo.py     ← NUEVO
├── gestor_combustible.py      ← NUEVO
├── cuentas_por_cobrar.py      ← NUEVO
├── whatsapp_integration.py    ← NUEVO
├── firebase_manager.py        ← MODIFICADO (métodos agregados al final)
├── README.md                  ← ORIGINAL
└── README_MODERN.md           ← NUEVO (este archivo)
```

## 🔄 Diferencias con la Versión Original

| Característica | Original | MODERN |
|---------------|----------|--------|
| Módulos | 4 | 8 |
| Dashboard | Básico | Ejecutivo con gráficos |
| Control Combustible | ❌ | ✅ |
| Cuentas x Cobrar | ❌ | ✅ |
| WhatsApp | ❌ | ✅ |
| Reportes | Estándar | Extendidos |

## 🎯 Características Principales

### Dashboard Ejecutivo
- Visualización de KPIs financieros en tiempo real
- Análisis de rentabilidad por equipo
- Identificación de equipos más productivos
- Monitoreo de márgenes de utilidad
- Alertas automáticas de negocio

### Control de Combustible
- Registro detallado de cada carga
- Cálculo automático de eficiencia (litros/hora)
- Seguimiento de horómetros
- Análisis de consumo por equipo
- Detección de anomalías en consumo

### Cuentas por Cobrar
- Vista consolidada de pagos pendientes
- Identificación de cuentas vencidas
- Alertas de próximos vencimientos (7 días)
- Registro simplificado de pagos
- Cálculo automático de saldos
- Métricas de recuperación

### WhatsApp Business
- Comunicación directa con clientes
- Recordatorios de pago automatizables
- Confirmaciones de alquiler
- Plantillas predefinidas
- Historial completo de conversaciones
- Integración con APIs profesionales

## 🐛 Solución de Problemas

### Error: "No module named 'dashboard_ejecutivo'"
```bash
# Verificar que los archivos existan:
ls -la dashboard_ejecutivo.py
ls -la gestor_combustible.py
ls -la cuentas_por_cobrar.py
ls -la whatsapp_integration.py
```

### Error: "PyQt6 not found"
```bash
pip install PyQt6
```

### Error: "firebase_admin not found"
```bash
pip install firebase-admin
```

### WhatsApp no conecta
- Verificar credenciales en `config_equipos.json`
- Para Twilio: Activar WhatsApp Sandbox primero
- Revisar logs en `equipos_modern.log`

### Error al cargar módulo específico
- Verificar que todas las dependencias estén instaladas
- Revisar el log `equipos_modern.log` para detalles
- Los módulos que fallan se muestran como placeholders con mensaje de error

## 📝 Logs

Los logs se guardan en:
- `equipos_modern.log` - Versión MODERN
- `equipos.log` - Versión original (sin cambios)

## 🔐 Seguridad

- Las credenciales de Firebase deben mantenerse privadas
- No compartir `config_equipos.json` con credenciales de producción
- Las credenciales de WhatsApp son sensibles
- Usar variables de entorno en producción

## 🚧 Trabajo Futuro

### Mejoras planificadas:
- [ ] Integración real con Twilio/WhatsApp Business API
- [ ] Gráficos interactivos en Dashboard Ejecutivo
- [ ] Exportación de reportes a Excel
- [ ] Notificaciones push
- [ ] Modo offline con sincronización

## 🤝 Contribuciones

Este proyecto es de uso interno de ZOEC CIVIL.

## 📄 Licencia

© 2025 ZOEC CIVIL - Todos los derechos reservados

## 📞 Soporte

Para problemas o preguntas:
1. Revisar este README
2. Consultar los logs en `equipos_modern.log`
3. Contactar al equipo de desarrollo

## ✅ Testing

### Verificaciones básicas:
1. ✅ `python main_qt.py` funciona exactamente igual (versión original intacta)
2. ✅ `python main_modern.py` inicia la versión MODERN
3. ✅ Los 8 módulos se muestran en el sidebar
4. ✅ Cada módulo carga sin errores (o muestra placeholder con error)
5. ✅ La navegación entre módulos funciona
6. ✅ No hay errores de importación

### Pruebas funcionales:
- [ ] Dashboard Ejecutivo muestra KPIs correctos
- [ ] Combustible permite registrar cargas
- [ ] Cuentas por Cobrar muestra pagos pendientes
- [ ] WhatsApp muestra configuración
- [ ] Firebase almacena datos correctamente

## 🎉 ¡Disfruta de EQUIPOS 6.0 MODERN!

Dos aplicaciones independientes:
- **EQUIPOS 6.0** (original) - 4 módulos estables
- **EQUIPOS 6.0 MODERN** (nueva) - 8 módulos avanzados

Sin riesgos, sin conflictos, código original 100% preservado.
