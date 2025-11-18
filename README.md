# 🤖 Bot PQRS - Universidad Los Libertadores

Bot de WhatsApp automatizado para el sistema de PQRS (Peticiones, Quejas, Reclamos y Sugerencias) de la Universidad Los Libertadores.

## 📋 Descripción

Este bot permite a los usuarios registrar PQRS a través de WhatsApp de forma interactiva. El sistema:
- Guía al usuario a través de un flujo conversacional
- Almacena todas las PQRS de forma persistente
- Envía correos electrónicos automáticamente para cada PQRS
- Envía alertas a Telegram cuando hay múltiples quejas similares (2+ reportes)
- Detecta quejas similares automáticamente

## ✨ Funcionalidades

### ✅ Flujo Conversacional de PQRS
1. **Usuario envía mensaje** → Bot responde con opciones de departamentos
2. **Usuario selecciona departamento** → Bot pide descripción del problema
3. **Usuario describe problema** → Bot confirma y registra la PQRS
4. **Sistema automático:**
   - ✅ Guarda la PQRS en `pqrs_data.json`
   - ✅ Envía correo electrónico a `EMAIL_RECIPIENT`
   - ✅ Si hay 2+ quejas similares → Envía alerta a Telegram

### 📧 Envío de Correos
- **Todas las PQRS** se envían por correo electrónico
- Formato HTML profesional con toda la información
- Configurado con SendGrid (100 emails/día gratis)

### 📱 Alertas en Telegram
- Solo cuando hay **2 o más quejas similares** del mismo departamento
- Se publica en el canal configurado con formato de alerta
- Detecta automáticamente quejas similares por palabras clave

### 💾 Persistencia
- Almacenamiento en `pqrs_data.json` (JSON)
- Las PQRS se mantienen al reiniciar el servidor
- PQRS pendientes de enviar a Telegram se envían automáticamente al iniciar

## 🛠️ Requisitos

- Python 3.8+
- Cuenta de WhatsApp Business API (Meta for Developers)
- Cuenta de SendGrid (gratis, 100 emails/día)
- (Opcional) Bot de Telegram y canal público

## 📦 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd BotLibertador
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install fastapi uvicorn[standard] pydantic pydantic-settings httpx python-dotenv
```

O usando el archivo de requirements (si existe):

```bash
pip install -r requirements.txt
```

## ⚙️ Configuración

### 1. Crear archivo `.env`

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# ============================================
# WhatsApp Business API
# ============================================
WHATSAPP_VERIFY_TOKEN=tu_token_secreto_aqui
WHATSAPP_ACCESS_TOKEN=tu_access_token_de_meta
WHATSAPP_APP_SECRET=tu_app_secret_de_meta
WHATSAPP_PHONE_NUMBER_ID=913262148531141
WHATSAPP_BUSINESS_ACCOUNT_ID=1516424429646060
WHATSAPP_API_VERSION=v22.0

# ============================================
# Telegram (Opcional - Para alertas)
# ============================================
TELEGRAM_BOT_TOKEN=tu_bot_token
TELEGRAM_CHANNEL_ID=@alertas_libertadores

# ============================================
# Email - SendGrid
# ============================================
EMAIL_SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EMAIL_SENDER=b99ronal@gmail.com
EMAIL_RECIPIENT=andresjose.sabagh.5@gmail.com

# ============================================
# Opcional
# ============================================
DEBUG=False
```

### 2. Obtener credenciales de WhatsApp

1. Ve a [Meta for Developers](https://developers.facebook.com/)
2. Crea una app y configura WhatsApp Business API
3. Obtén:
   - **Phone Number ID**: En configuración de WhatsApp
   - **Business Account ID**: En tu cuenta de negocio
   - **Access Token**: Token temporal o permanente
   - **App Secret**: En configuración de la app
   - **Verify Token**: Crea uno personalizado (ej: `mi_token_secreto_123`)

### 3. Configurar SendGrid (Email)

1. Crea cuenta en [SendGrid](https://sendgrid.com/) (gratis)
2. Ve a **Settings** → **API Keys** → **Create API Key**
3. Copia la API Key (empieza con `SG.`)
4. Ve a **Settings** → **Sender Authentication** → **Single Sender Verification**
5. Crea y verifica un sender (email desde el que se enviará)
6. Actualiza `EMAIL_SENDER` en `.env` con el email verificado

### 4. Configurar Telegram (Opcional)

1. Crea un bot con [@BotFather](https://t.me/botfather) en Telegram
2. Obtén el `TELEGRAM_BOT_TOKEN`
3. Crea un canal público (ej: `@alertas_libertadores`)
4. Agrega el bot como **administrador** del canal
5. Actualiza `TELEGRAM_CHANNEL_ID` en `.env` con el username del canal

### 5. Configurar Webhook de WhatsApp

1. **Usar ngrok** para exponer tu servidor local:
   ```bash
   ngrok http 8000
   ```

2. **Copiar la URL** que ngrok te da (ej: `https://xxxxx.ngrok-free.app`)

3. **En Meta for Developers:**
   - Ve a tu app → WhatsApp → Configuration
   - **Webhook URL:** `https://xxxxx.ngrok-free.app/webhook`
   - **Verify Token:** El mismo que pusiste en `WHATSAPP_VERIFY_TOKEN`
   - **Suscríbete a:** `messages` y `status`

## 🚀 Ejecución

### Opción 1: Usando Python directamente

```bash
python main.py
```

### Opción 2: Usando Uvicorn

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Opción 3: Scripts incluidos

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

El servidor iniciará en: `http://localhost:8000`

## 📡 Endpoints de la API

### `GET /`
Endpoint raíz con información del servicio.

### `GET /webhook`
Verificación del webhook de WhatsApp (usado por Meta durante la configuración).

### `POST /webhook`
Recibe mensajes y estados de WhatsApp. **Este es el endpoint principal que usa WhatsApp.**

### `POST /send-message`
Envía un mensaje de texto manualmente (útil para pruebas).

**Request:**
```json
{
  "to": "+57 324 6537538",
  "message": "Hola, este es un mensaje de prueba",
  "preview_url": false
}
```

### `POST /send-template`
Envía un mensaje de plantilla (template) de WhatsApp.

**Request:**
```json
{
  "to": "+57 324 6537538",
  "template_name": "hello_world",
  "language_code": "en_US",
  "components": []
}
```

### `GET /health`
Health check del servicio.

### `GET /docs`
Documentación interactiva de la API (Swagger UI) en `http://localhost:8000/docs`

## 🔄 Flujo de PQRS

### Estados de la Conversación

1. **INICIAL**: Usuario envía primer mensaje → Bot muestra opciones de departamentos
2. **ESPERANDO_DEPARTAMENTO**: Usuario debe seleccionar departamento (1-7 o nombre)
3. **ESPERANDO_DESCRIPCION**: Usuario debe describir el problema
4. **COMPLETADO**: PQRS registrada, correo enviado, confirmación al usuario

### Departamentos Disponibles

- **1.** Tecnología (TEC)
- **2.** Aseo y Mantenimiento (ASE)
- **3.** Educativo (EDU)
- **4.** Administrativo (ADM)
- **5.** Biblioteca (BIB)
- **6.** Seguridad (SEG)
- **7.** Otro (OTR)

### Ejemplo de Conversación

```
Usuario: Hola
Bot: 👋 ¡Bienvenido al Sistema de PQRS!
     ¿A qué departamento tiene que ver tu solicitud?
     
     Elige una opción:
     1. Tecnología
     2. Aseo y Mantenimiento
     3. Educativo
     ...

Usuario: 2
Bot: Perfecto, has seleccionado: Aseo y Mantenimiento
     Por favor, describe el problema...

Usuario: El baño del segundo piso está tapado
Bot: ✅ PQRS Registrada Exitosamente
     📋 Número de referencia: PQRS-ASE-20251117184514
     🏢 Departamento: Aseo y Mantenimiento
     📅 Fecha: 17/11/2025 18:45
     ...
```

## 📁 Estructura del Proyecto

```
BotLibertador/
├── main.py                      # Aplicación FastAPI principal
├── config.py                    # Configuración y variables de entorno
├── .env                         # Variables de entorno (no incluido en git)
├── pqrs_data.json              # Almacenamiento de PQRS (generado automáticamente)
│
├── models/                      # Modelos de datos
│   ├── __init__.py
│   └── whatsapp.py             # Modelos de WhatsApp (webhooks, mensajes)
│
├── services/                    # Servicios de negocio
│   ├── __init__.py
│   ├── whatsapp_service.py     # Servicio para enviar mensajes por WhatsApp
│   ├── message_handler.py      # Lógica principal del bot y flujo PQRS
│   ├── email_service.py        # Servicio para enviar correos (SendGrid)
│   ├── announcement_service.py # Servicio para Telegram
│   └── pqrs_storage.py         # Almacenamiento persistente de PQRS
│
├── utils/                       # Utilidades
│   ├── __init__.py
│   ├── phone_utils.py          # Normalización de números de teléfono
│   └── security.py             # Validación de webhooks y seguridad
│
├── start.bat                    # Script de inicio (Windows)
├── start.sh                     # Script de inicio (Linux/Mac)
└── test_main.http              # Archivo de pruebas HTTP
```

## 📧 Configuración de Email (SendGrid)

### Pasos para Configurar SendGrid

1. **Crear cuenta**: https://sendgrid.com/
2. **Obtener API Key**: Settings → API Keys → Create API Key
3. **Verificar Sender**: Settings → Sender Authentication → Single Sender Verification
   - Crea un sender con el email que quieras usar
   - Verifica el email (SendGrid enviará un correo)
4. **Actualizar `.env`**:
   ```env
   EMAIL_SENDGRID_API_KEY=SG.tu_api_key_aqui
   EMAIL_SENDER=email_verificado@ejemplo.com
   EMAIL_RECIPIENT=andresjose.sabagh.5@gmail.com
   ```

### Formato del Correo

Cada PQRS genera un correo HTML con:
- 📋 ID de PQRS
- 📅 Fecha de registro
- 🏢 Departamento y código
- 📱 Teléfono del usuario
- 📝 Descripción completa del problema

## 📱 Configuración de Telegram (Opcional)

### Para Alertas Automáticas

1. **Crear bot**: Habla con [@BotFather](https://t.me/botfather)
2. **Obtener token**: `/newbot` → copia el token
3. **Crear canal público**: Crea un canal en Telegram (ej: `@alertas_libertadores`)
4. **Agregar bot como admin**: Configuración del canal → Administradores → Agregar
5. **Actualizar `.env`**:
   ```env
   TELEGRAM_BOT_TOKEN=tu_token_del_bot
   TELEGRAM_CHANNEL_ID=@alertas_libertadores
   ```

### Comportamiento

- **Primera queja**: NO se envía a Telegram (solo se guarda y envía correo)
- **Segunda queja similar**: ✅ Se envía alerta "⚠️ ALERTA - Múltiples reportes similares"
- **Tercera y siguientes**: ✅ Cada una genera una alerta nueva

## 🔍 Detección de Quejas Similares

El sistema detecta automáticamente quejas similares basándose en:
- **Mismo departamento** (mismo código)
- **Palabras similares** en la descripción (mínimo 2 palabras en común)
- **Últimas 50 PQRS** del mismo departamento

Ejemplo:
- Queja 1: "El baño del segundo piso está tapado"
- Queja 2: "El baño de hombres del segundo piso está dañado"
- → Ambas tienen "baño", "segundo", "piso" → Son similares ✅

## 💾 Almacenamiento

### Archivo `pqrs_data.json`

Todas las PQRS se guardan en formato JSON:
```json
[
  {
    "pqrs_id": "PQRS-ASE-20251117184514",
    "departamento": "Aseo y Mantenimiento",
    "codigo_departamento": "ASE",
    "descripcion": "El baño está tapado",
    "fecha": "2025-11-17T18:45:14.123456",
    "telefono": "573246537538",
    "enviado_telegram": false,
    "fecha_registro": "2025-11-17T18:45:14.123789"
  }
]
```

### Persistencia

- ✅ Las PQRS se mantienen al reiniciar el servidor
- ✅ Al iniciar, se envían automáticamente las PQRS pendientes de Telegram
- ⚠️ **Nota**: Para producción, considera usar una base de datos (SQLite, PostgreSQL, etc.)

## 🧪 Pruebas

### Probar el Bot Manualmente

1. **Inicia el servidor**
2. **Configura el webhook** con ngrok
3. **Envía un mensaje** a tu número de WhatsApp Business desde WhatsApp
4. **Sigue el flujo** conversacional

### Probar Endpoints API

1. **Swagger UI**: Abre `http://localhost:8000/docs` en tu navegador
2. **Archivo HTTP**: Usa `test_main.http` con la extensión REST Client de VS Code

### Limpiar Datos de Prueba

Para limpiar todas las PQRS y empezar de cero:
```bash
# Edita pqrs_data.json y ponlo así:
[]
```

## 🐛 Troubleshooting

### Error: "Error validating access token"
- **Causa**: El token de WhatsApp expiró (tokens temporales duran 24 horas)
- **Solución**: Obtén un nuevo token en Meta for Developers o configura un token permanente

### Error: "chat not found" en Telegram
- **Causa**: El bot no es administrador del canal o el ID está mal
- **Solución**: 
  1. Verifica que el bot sea admin del canal
  2. Verifica que `TELEGRAM_CHANNEL_ID` sea correcto (ej: `@alertas_libertadores`)

### Error: "The from address does not match a verified Sender Identity"
- **Causa**: El email en `EMAIL_SENDER` no está verificado en SendGrid
- **Solución**: Verifica el sender en SendGrid Dashboard → Sender Authentication

### No se envían correos
- **Causa**: API Key de SendGrid incorrecta o sender no verificado
- **Solución**: 
  1. Verifica `EMAIL_SENDGRID_API_KEY` en `.env`
  2. Verifica que el sender esté verificado en SendGrid

## 📝 Variables de Entorno Completas

```env
# WhatsApp
WHATSAPP_VERIFY_TOKEN=tu_token_secreto
WHATSAPP_ACCESS_TOKEN=tu_access_token
WHATSAPP_APP_SECRET=tu_app_secret
WHATSAPP_PHONE_NUMBER_ID=913262148531141
WHATSAPP_BUSINESS_ACCOUNT_ID=1516424429646060
WHATSAPP_API_VERSION=v22.0

# Telegram (Opcional)
TELEGRAM_BOT_TOKEN=tu_bot_token
TELEGRAM_CHANNEL_ID=@alertas_libertadores

# Email - SendGrid
EMAIL_SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxx
EMAIL_SENDER=b99ronal@gmail.com
EMAIL_RECIPIENT=andresjose.sabagh.5@gmail.com

# Opcional
DEBUG=False
```

## 🚀 Despliegue

### Desarrollo Local
- Usa `ngrok` para exponer el servidor
- Configura el webhook de WhatsApp con la URL de ngrok

### Producción
1. **Servidor**: Despliega en un VPS (AWS, DigitalOcean, etc.) o servicio como Heroku, Railway
2. **Dominio**: Usa un dominio propio para el webhook (no ngrok)
3. **Base de datos**: Considera migrar a PostgreSQL o MySQL para producción
4. **SSL**: Asegúrate de tener HTTPS (Let's Encrypt)
5. **Token permanente**: Obtén un token permanente de WhatsApp (no temporal)

## 📚 Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido
- **Uvicorn**: Servidor ASGI
- **Pydantic**: Validación de datos
- **httpx**: Cliente HTTP asíncrono
- **SendGrid API**: Envío de correos electrónicos
- **Telegram Bot API**: Alertas en canal público
- **Meta WhatsApp Business API**: Mensajería

## 📄 Licencia

Este proyecto es para uso interno de la Universidad Los Libertadores.

## 👨‍💻 Autor

Desarrollado para el sistema de PQRS de la Universidad Los Libertadores.

---

## 🎯 Resumen Rápido

1. ✅ **Instala dependencias**: `pip install -r requirements.txt`
2. ✅ **Configura `.env`** con todas las variables
3. ✅ **Verifica sender en SendGrid**
4. ✅ **Configura webhook** de WhatsApp
5. ✅ **Inicia servidor**: `python main.py`
6. ✅ **Prueba enviando un mensaje** a WhatsApp

¡Listo! 🎉

