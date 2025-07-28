# Chatbot Clínica Dental

Un chatbot inteligente para clínicas dentales construido con Flask y OpenAI, optimizado para dispositivos móviles.

## Características

- 🤖 Chatbot inteligente conectado a OpenAI GPT-3.5
- 📱 Diseño completamente optimizado para móviles
- 🎨 Interfaz moderna y atractiva
- ⚡ Botones de acción rápida para consultas comunes
- 🔒 Configuración segura con variables de entorno
- 📊 Indicador de escritura en tiempo real
- 📅 Sistema completo de programación de citas
- 🗄️ Base de datos SQLite para almacenar citas
- 📋 Calendario interactivo con días y horas disponibles

## Instalación

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd clinicschat
```

### 2. Crear entorno virtual
```bash
python -m venv venv
```

### 3. Activar el entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:
```bash
# Copiar el archivo de ejemplo
cp env_example.txt .env
```

Edita el archivo `.env` y agrega tu API key de OpenAI:
```
OPENAI_API_KEY=tu_api_key_real_de_openai
```

## Uso

### Ejecutar el servidor de desarrollo
```bash
python app.py
```

El servidor se ejecutará en `http://localhost:5000`

### Acceder al chatbot
Abre tu navegador y ve a `http://localhost:5000`

## Despliegue en Render

### Opción 1: Usando render.yaml (Recomendado)
El proyecto incluye un archivo `render.yaml` que automatiza la configuración:

1. **Sube tu código a GitHub**
2. **Ve a [Render.com](https://render.com)**
3. **Crea un nuevo Web Service**
4. **Conecta tu repositorio de GitHub**
5. **Render detectará automáticamente el archivo `render.yaml`**
6. **Configura la variable de entorno:**
   - `OPENAI_API_KEY`: Tu API key de OpenAI

### Opción 2: Configuración manual
Si prefieres configurar manualmente:

1. **Crear una nueva Web Service**
2. **Conectar tu repositorio de GitHub**
3. **Configurar las variables de entorno:**
   - `OPENAI_API_KEY`: Tu API key de OpenAI
   - `PYTHON_VERSION`: 3.9.16

4. **Configurar el comando de build:**
   ```
   pip install -r requirements.txt
   ```

5. **Configurar el comando de start:**
   ```
   gunicorn app:app
   ```

### Variables de entorno requeridas
- `OPENAI_API_KEY`: Tu clave API de OpenAI (obligatoria)
- `SECRET_KEY`: Clave secreta para sesiones (opcional, se genera automáticamente)

## Estructura del Proyecto

```
clinicschat/
├── app.py                 # Aplicación principal de Flask
├── requirements.txt       # Dependencias de Python
├── env_example.txt       # Ejemplo de variables de entorno
├── README.md             # Este archivo
├── test_database.py      # Script de prueba de la base de datos
├── citas.db              # Base de datos SQLite (se crea automáticamente)
└── templates/
    ├── index.html        # Plantilla HTML del chatbot
    └── citas.html        # Plantilla HTML del formulario de citas
```

## Características del Chatbot

### Funcionalidades
- **Información educativa sobre tratamientos**: Proporciona información sobre causas y procesos (sin recomendaciones médicas)
- **Sistema completo de citas**: Programación paso a paso con calendario interactivo
- **Ubicaciones**: Información sobre las ubicaciones de la clínica
- **Chat libre**: Conversación natural con el asistente

### Nuevo Sistema de Citas

#### Flujo de Programación:
1. **Chat inicial**: El chatbot pregunta si es revisión general o padecimiento específico
2. **Formulario de citas**: Se abre automáticamente un formulario paso a paso
3. **Datos del paciente**: Nombre, teléfono y email
4. **Selección de fecha**: Calendario con próximos 30 días disponibles
5. **Selección de hora**: Horarios disponibles en tramos de 30 minutos
6. **Confirmación**: Resumen de la cita y botón de confirmar
7. **Guardado**: La cita se guarda en la base de datos

#### Horarios de la Clínica:
- **Lunes a Viernes**: 9:00 - 18:00
- **Sábados**: 9:00 - 14:00
- **Domingos**: Cerrado

### Diseño Responsivo
- Optimizado para dispositivos móviles
- Interfaz intuitiva y fácil de usar
- Animaciones suaves y feedback visual
- Botones de acción rápida para consultas comunes

### Seguridad
- API key de OpenAI configurada como variable de entorno
- Validación de entrada del usuario
- Manejo de errores robusto

## Personalización

### Cambiar el nombre de la clínica
Edita la variable `clinic_name` en `app.py`:

```python
CHATBOT_CONFIG = {
    'clinic_name': 'Tu Clínica Dental',
    # ... resto de configuración
}
```

### Modificar el prompt del sistema
Edita la variable `system_prompt` en `app.py` para personalizar las respuestas del chatbot.

### Cambiar colores y estilos
Modifica el CSS en `templates/index.html` para personalizar la apariencia.

## Base de Datos

### Estructura de la Tabla Cita:
- `id`: Identificador único
- `nombre`: Nombre completo del paciente
- `telefono`: Número de teléfono
- `email`: Dirección de email
- `tipo_cita`: 'revision' o 'padecimiento'
- `fecha`: Fecha de la cita
- `hora`: Hora de la cita
- `estado`: 'pendiente', 'confirmada', 'cancelada'
- `fecha_creacion`: Fecha de creación del registro

### API Endpoints:
- `GET /api/dias-disponibles`: Obtiene días disponibles
- `GET /api/horas-disponibles/<fecha>`: Obtiene horas disponibles para una fecha
- `POST /api/guardar-cita`: Guarda una nueva cita
- `POST /api/guardar-cita-chat`: Guarda una cita desde el chat
- `GET /api/database-stats`: Obtiene estadísticas de la base de datos
- `GET /api/citas`: Obtiene todas las citas para el panel
- `GET /download-database`: Descarga la base de datos SQLite
- `GET /export-csv`: Exporta citas a CSV
- `GET /admin`: Página de administración de la base de datos
- `GET /panel`: Panel de atención al cliente

### Probar la Base de Datos:
```bash
python test_database.py
```

### Exportar Base de Datos:
```bash
python export_database.py
```

### Acceder a la Administración:
Ve a `http://localhost:5000/admin` para acceder al panel de administración con estadísticas y opciones de descarga.

### Acceder al Panel de Atención:
Ve a `http://localhost:5000/panel` para acceder al panel de atención al cliente con calendario diario, semanal y mensual.

## Troubleshooting

### Error: "No module named 'openai'"
```bash
pip install openai
```

### Error: "OPENAI_API_KEY not found"
Asegúrate de que el archivo `.env` existe y contiene tu API key de OpenAI.

### Error de conexión con OpenAI
Verifica que tu API key sea válida y tengas créditos disponibles en tu cuenta de OpenAI.

## Licencia

Este proyecto está bajo la Licencia MIT.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request para sugerencias o mejoras. 