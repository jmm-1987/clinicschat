from flask import Flask, render_template, request, jsonify, session
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'tu-clave-secreta-aqui')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///citas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Modelo de la base de datos
class Cita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    tipo_cita = db.Column(db.String(50), nullable=False)  # 'revision' o 'padecimiento'
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.String(10), nullable=False)
    estado = db.Column(db.String(20), default='pendiente')  # 'pendiente', 'confirmada', 'cancelada'
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

# Sistema de respuestas predefinidas
RESPUESTAS_PREDEFINIDAS = {
    # Saludos y bienvenida
    'hola': '¡Hola! Bienvenido a Clínica Dental "De Ejemplo", ¿en qué puedo ayudarte?',
    'buenos días': '¡Buenos días! Bienvenido a Clínica Dental "De Ejemplo", ¿en qué puedo ayudarte?',
    'buenas tardes': '¡Buenas tardes! Bienvenido a Clínica Dental "De Ejemplo", ¿en qué puedo ayudarte?',
    'buenas noches': '¡Buenas noches! Bienvenido a Clínica Dental "De Ejemplo", ¿en qué puedo ayudarte?',
    
    # Información sobre tratamientos
    'información sobre tratamientos': '¿Sobre qué tratamiento específico te gustaría saber más?',
    'tratamientos': '¿Sobre qué tratamiento específico te gustaría saber más?',
    
    # Tratamientos específicos
    'limpieza dental': 'La limpieza dental profesional es fundamental para mantener la salud bucal. Este tratamiento elimina la placa bacteriana y el sarro que se acumula en los dientes y encías. La placa bacteriana se forma constantemente por bacterias que se adhieren a los dientes, y si no se elimina regularmente, puede causar caries y enfermedades de las encías. El proceso incluye la eliminación de sarro, pulido dental y aplicación de flúor. Es recomendable realizarla cada 6 meses para mantener una boca saludable.\n\nEs importante que sepas que cada caso es único y requiere una evaluación personalizada por parte de un profesional. Para determinar si este tratamiento es el más adecuado para tu situación específica, es fundamental que te evalúe un dentista profesional.',
    
    'empastes': 'Los empastes restauran dientes que han sido afectados por caries. La caries se desarrolla cuando las bacterias de la placa producen ácidos que desmineralizan el esmalte dental, creando cavidades. El proceso incluye la eliminación del tejido cariado y la restauración con materiales como composite o amalgama. Es importante tratar las caries temprano para evitar que lleguen al nervio del diente.\n\nEs importante que sepas que cada caso es único y requiere una evaluación personalizada por parte de un profesional. Para determinar si este tratamiento es el más adecuado para tu situación específica, es fundamental que te evalúe un dentista profesional.',
    
    'ortodoncia': 'La ortodoncia corrige la posición de los dientes y la mordida. Los problemas de alineación pueden ser causados por factores genéticos, hábitos infantiles como chuparse el dedo o la pérdida prematura de dientes. El tratamiento aplica fuerzas controladas que mueven gradualmente los dientes a su posición correcta. Esto mejora tanto la estética como la función masticatoria.\n\nEs importante que sepas que cada caso es único y requiere una evaluación personalizada por parte de un profesional. Para determinar si este tratamiento es el más adecuado para tu situación específica, es fundamental que te evalúe un dentista profesional.',
    
    'cirugía oral': 'La cirugía oral trata problemas que no pueden resolverse con tratamientos convencionales. Incluye extracciones complejas, extracción de muelas del juicio impactadas, y cirugías para tratar infecciones o lesiones. Los problemas pueden surgir por dientes impactados, infecciones avanzadas o traumatismos. El proceso incluye anestesia local y técnicas quirúrgicas especializadas.\n\nEs importante que sepas que cada caso es único y requiere una evaluación personalizada por parte de un profesional. Para determinar si este tratamiento es el más adecuado para tu situación específica, es fundamental que te evalúe un dentista profesional.',
    
    'blanqueamiento': 'El blanqueamiento dental aclara el color de los dientes eliminando manchas superficiales y profundas. Las manchas pueden ser causadas por alimentos, bebidas, tabaco o el envejecimiento natural. El proceso utiliza agentes blanqueadores que penetran el esmalte y descomponen las moléculas que causan las manchas. Es un tratamiento estético que mejora la apariencia de la sonrisa.\n\nEs importante que sepas que cada caso es único y requiere una evaluación personalizada por parte de un profesional. Para determinar si este tratamiento es el más adecuado para tu situación específica, es fundamental que te evalúe un dentista profesional.',
    
    'endodoncia': 'La endodoncia trata dientes con infección en el nervio o pulpa dental. Esto ocurre cuando las caries avanzan hasta el nervio, causando dolor e infección. El proceso incluye la eliminación del tejido infectado, limpieza de los conductos radiculares y sellado para prevenir nuevas infecciones. Salva dientes que de otra manera tendrían que extraerse.\n\nEs importante que sepas que cada caso es único y requiere una evaluación personalizada por parte de un profesional. Para determinar si este tratamiento es el más adecuado para tu situación específica, es fundamental que te evalúe un dentista profesional.',
    
    'periodoncia': 'La periodoncia trata las enfermedades de las encías y el hueso que sostiene los dientes. La gingivitis y la periodontitis son causadas por la acumulación de placa bacteriana que inflama las encías y puede destruir el hueso. El tratamiento incluye limpieza profunda de las raíces dentales y control de la infección bacteriana.\n\nEs importante que sepas que cada caso es único y requiere una evaluación personalizada por parte de un profesional. Para determinar si este tratamiento es el más adecuado para tu situación específica, es fundamental que te evalúe un dentista profesional.',
    
    'implantes dentales': 'Los implantes dentales reemplazan dientes perdidos con raíces artificiales de titanio. La pérdida de dientes puede ser causada por caries avanzadas, enfermedad periodontal o traumatismos. El proceso incluye la colocación quirúrgica del implante en el hueso, que se integra con el tiempo, y luego la colocación de la corona dental. Restauran tanto la función como la estética.\n\nEs importante que sepas que cada caso es único y requiere una evaluación personalizada por parte de un profesional. Para determinar si este tratamiento es el más adecuado para tu situación específica, es fundamental que te evalúe un dentista profesional.',
    
    # Solicitud de citas
    'solicitar una cita': '¿Ya tienes un tratamiento abierto con nuestra clínica?',
    'quiero una cita': '¿Ya tienes un tratamiento abierto con nuestra clínica?',
    'necesito una cita': '¿Ya tienes un tratamiento abierto con nuestra clínica?',
    'agendar cita': '¿Ya tienes un tratamiento abierto con nuestra clínica?',
    'sí, quiero agendar una cita': '¿Ya tienes un tratamiento abierto con nuestra clínica?',
    
    # Respuestas sobre tratamiento abierto
    'sí, ya tengo tratamiento': 'Perfecto, para gestionar tu cita existente o alguna consulta acerca de tu tratamiento, por favor contacta directamente con nosotros al teléfono +34 900 123 456. Nuestro equipo te ayudará a programar tu próxima cita.',
    'no, es mi primera vez': 'Entendido, te ayudo a solicitar una nueva cita. ¿Tu cita es para una revisión general periódica o tienes algún padecimiento específico que te gustaría consultar?',
    
    # Tipo de cita
    'revisión general periódica': 'Perfecto, una revisión general es fundamental para mantener tu salud dental. Te ayudo a programar tu cita paso a paso. Primero vamos a seleccionar la fecha y hora que te venga mejor.',
    'tengo algún padecimiento': 'Entiendo tu situación. Es importante que un profesional evalúe tu caso personalmente para determinar el tratamiento más adecuado. Te ayudo a programar tu cita paso a paso. Primero vamos a seleccionar la fecha y hora que te venga mejor.',
    
    # Ubicaciones
    'ubicaciones': 'Tenemos clínicas en varias ciudades. Puedes ver las ubicaciones exactas haciendo clic en el botón "Ver ubicaciones" que aparece en la parte superior del chat.',
    'dónde están': 'Tenemos clínicas en varias ciudades. Puedes ver las ubicaciones exactas haciendo clic en el botón "Ver ubicaciones" que aparece en la parte superior del chat.',
    'dirección': 'Tenemos clínicas en varias ciudades. Puedes ver las ubicaciones exactas haciendo clic en el botón "Ver ubicaciones" que aparece en la parte superior del chat.',
    
    # Horarios
    'horarios': 'Nuestros horarios son: Lunes a Viernes de 9:00 a 18:00, Sábados de 9:00 a 14:00.',
    'cuándo abren': 'Nuestros horarios son: Lunes a Viernes de 9:00 a 18:00, Sábados de 9:00 a 14:00.',
    
    # Teléfono
    'teléfono': 'Nuestro teléfono de contacto es +34 900 123 456.',
    'contacto': 'Nuestro teléfono de contacto es +34 900 123 456.',
    
    # Respuesta por defecto
    'default': 'Gracias por tu mensaje. Si necesitas información sobre tratamientos, puedes hacer clic en "Información sobre tratamientos". Si quieres agendar una cita, puedes hacer clic en "Solicitar una cita". Y si quieres ver nuestras ubicaciones, puedes hacer clic en "Ver ubicaciones".'
}

# Sistema de estado de conversación
ESTADOS_CONVERSACION = {
    'inicial': 'inicial',
    'en_menu_tratamientos': 'en_menu_tratamientos',
    'preguntando_tratamiento_abierto': 'preguntando_tratamiento_abierto',
    'preguntando_tipo_cita': 'preguntando_tipo_cita',
    'solicitando_detalle_padecimiento': 'solicitando_detalle_padecimiento',
    'solicitando_fecha': 'solicitando_fecha',
    'solicitando_hora': 'solicitando_hora',
    'solicitando_nombre': 'solicitando_nombre',
    'solicitando_telefono': 'solicitando_telefono',
    'solicitando_email': 'solicitando_email',
    'confirmando_cita': 'confirmando_cita'
}

def obtener_respuesta(mensaje, estado_actual='inicial', datos_cita=None):
    """Función para obtener la respuesta predefinida basada en el mensaje del usuario y el estado actual"""
    mensaje_lower = mensaje.lower().strip()
    
    # Manejar el flujo de citas basado en el estado
    if estado_actual == ESTADOS_CONVERSACION['preguntando_tratamiento_abierto']:
        if 'sí' in mensaje_lower or 'si' in mensaje_lower or 'ya tengo' in mensaje_lower:
            return {
                'respuesta': 'Perfecto, para gestionar tu cita existente o alguna consulta acerca de tu tratamiento, por favor contacta directamente con nosotros al teléfono +34 900 123 456. Nuestro equipo te ayudará a programar tu próxima cita.',
                'estado': ESTADOS_CONVERSACION['inicial'],
                'datos_cita': datos_cita
            }
        elif 'no' in mensaje_lower or 'primera vez' in mensaje_lower:
            return {
                'respuesta': 'Entendido, te ayudo a solicitar una nueva cita. ¿Tu cita es para una revisión general periódica o tienes algún padecimiento específico que te gustaría consultar?',
                'estado': ESTADOS_CONVERSACION['preguntando_tipo_cita'],
                'datos_cita': datos_cita
            }
    
    elif estado_actual == ESTADOS_CONVERSACION['preguntando_tipo_cita']:
        if 'revisión' in mensaje_lower or 'general' in mensaje_lower:
            if datos_cita is None:
                datos_cita = {}
            datos_cita['tipo_cita'] = 'revision'
            return {
                'respuesta': 'Perfecto, una revisión general es fundamental para mantener tu salud dental. Ahora vamos a seleccionar la fecha de tu cita. ¿Qué día te viene mejor?',
                'estado': ESTADOS_CONVERSACION['solicitando_fecha'],
                'datos_cita': datos_cita,
                'mostrar_calendario': True
            }
        elif 'padecimiento' in mensaje_lower or 'dolor' in mensaje_lower or 'problema' in mensaje_lower:
            if datos_cita is None:
                datos_cita = {}
            datos_cita['tipo_cita'] = 'padecimiento'
            return {
                'respuesta': 'Por favor, describe brevemente tu padecimiento o motivo de consulta:',
                'estado': ESTADOS_CONVERSACION['solicitando_detalle_padecimiento'],
                'datos_cita': datos_cita,
                'mostrar_input_padecimiento': True
            }

    elif estado_actual == ESTADOS_CONVERSACION['solicitando_detalle_padecimiento']:
        if datos_cita is None:
            datos_cita = {}
        datos_cita['detalle_padecimiento'] = mensaje
        return {
            'respuesta': 'Gracias por la información. Ahora vamos a seleccionar la fecha de tu cita. ¿Qué día te viene mejor?',
            'estado': ESTADOS_CONVERSACION['solicitando_fecha'],
            'datos_cita': datos_cita,
            'mostrar_calendario': True
        }
    
    # Manejar estados específicos del flujo de citas
    elif estado_actual == ESTADOS_CONVERSACION['solicitando_fecha']:
        # Aquí el usuario debería seleccionar una fecha del calendario
        # Por ahora, asumimos que el calendario se maneja en el frontend
        return {
            'respuesta': 'Por favor selecciona una fecha del calendario que aparece arriba.',
            'estado': ESTADOS_CONVERSACION['solicitando_fecha'],
            'datos_cita': datos_cita,
            'mostrar_calendario': True
        }
    
    elif estado_actual == ESTADOS_CONVERSACION['solicitando_hora']:
        # El usuario seleccionó una fecha, ahora pedir hora
        if datos_cita and datos_cita.get('fecha'):
            return {
                'respuesta': f'Perfecto, has seleccionado el {datos_cita["fecha"]}. Ahora selecciona la hora que te viene mejor:',
                'estado': ESTADOS_CONVERSACION['solicitando_hora'],
                'datos_cita': datos_cita,
                'mostrar_horas': True
            }
    
    elif estado_actual == ESTADOS_CONVERSACION['solicitando_nombre']:
        # El usuario seleccionó fecha y hora, ahora pedir nombre
        datos_cita['nombre'] = mensaje
        return {
            'respuesta': f'Gracias {mensaje}. Ahora necesito tu número de teléfono de contacto.',
            'estado': ESTADOS_CONVERSACION['solicitando_telefono'],
            'datos_cita': datos_cita
        }
    
    elif estado_actual == ESTADOS_CONVERSACION['solicitando_telefono']:
        # El usuario proporcionó teléfono, ahora pedir email
        datos_cita['telefono'] = mensaje
        return {
            'respuesta': 'Perfecto. Ahora necesito tu dirección de email para enviarte la confirmación de la cita.',
            'estado': ESTADOS_CONVERSACION['solicitando_email'],
            'datos_cita': datos_cita
        }
    
    elif estado_actual == ESTADOS_CONVERSACION['solicitando_email']:
        # El usuario proporcionó email, mostrar confirmación
        datos_cita['email'] = mensaje
        return {
            'respuesta': f'¡Excelente! Aquí tienes el resumen de tu cita:\n\n📅 Fecha: {datos_cita["fecha"]}\n🕐 Hora: {datos_cita["hora"]}\n👤 Nombre: {datos_cita["nombre"]}\n📞 Teléfono: {datos_cita["telefono"]}\n📧 Email: {datos_cita["email"]}\n🏥 Tipo: {"Revisión general" if datos_cita["tipo_cita"] == "revision" else "Padecimiento específico"}\n\n¿Confirmas que quieres agendar esta cita?',
            'estado': ESTADOS_CONVERSACION['confirmando_cita'],
            'datos_cita': datos_cita,
            'mostrar_confirmacion': True
        }
    
    elif estado_actual == ESTADOS_CONVERSACION['confirmando_cita']:
        if 'sí' in mensaje_lower or 'si' in mensaje_lower or 'confirmo' in mensaje_lower:
            # Guardar la cita en la base de datos
            try:
                nueva_cita = Cita(
                    nombre=datos_cita['nombre'],
                    telefono=datos_cita['telefono'],
                    email=datos_cita['email'],
                    tipo_cita=datos_cita['tipo_cita'],
                    fecha=datetime.strptime(datos_cita['fecha'], '%Y-%m-%d').date(),
                    hora=datos_cita['hora']
                )
                db.session.add(nueva_cita)
                db.session.commit()
                
                return {
                    'respuesta': f'¡Perfecto! Tu cita ha sido programada exitosamente para el {datos_cita["fecha"]} a las {datos_cita["hora"]}. Recibirás una confirmación por email. Tu número de cita es #{nueva_cita.id}. ¡Gracias por confiar en nosotros!',
                    'estado': ESTADOS_CONVERSACION['inicial'],
                    'datos_cita': {},
                    'cita_guardada': True
                }
            except Exception as e:
                return {
                    'respuesta': f'Lo sentimos, hubo un error al guardar tu cita. Por favor, inténtalo de nuevo o contacta directamente con nosotros al +34 900 123 456.',
                    'estado': ESTADOS_CONVERSACION['inicial'],
                    'datos_cita': {}
                }
        else:
            return {
                'respuesta': 'Entendido, la cita no se ha confirmado. Si cambias de opinión, puedes volver a solicitar una cita en cualquier momento.',
                'estado': ESTADOS_CONVERSACION['inicial'],
                'datos_cita': {}
            }
    
    # Manejar estado cuando el usuario está en el menú de tratamientos
    elif estado_actual == ESTADOS_CONVERSACION['en_menu_tratamientos']:
        # Si el usuario quiere agendar una cita desde el menú de tratamientos
        if any(palabra in mensaje_lower for palabra in ['sí, quiero agendar', 'quiero agendar', 'agendar cita', 'solicitar cita', 'necesito cita', 'quiero una cita']):
            return {
                'respuesta': '¿Ya tienes un tratamiento abierto con nuestra clínica?',
                'estado': ESTADOS_CONVERSACION['preguntando_tratamiento_abierto'],
                'datos_cita': datos_cita,
                'limpiar_pantalla': True
            }
        # Si el usuario pregunta sobre otro tratamiento
        elif any(palabra in mensaje_lower for palabra in ['limpieza', 'empaste', 'ortodoncia', 'cirugía', 'blanqueamiento', 'endodoncia', 'periodoncia', 'implante']):
            # Buscar la respuesta correspondiente en RESPUESTAS_PREDEFINIDAS
            for clave, respuesta in RESPUESTAS_PREDEFINIDAS.items():
                if clave in mensaje_lower:
                    return {
                        'respuesta': respuesta,
                        'estado': ESTADOS_CONVERSACION['en_menu_tratamientos'],
                        'datos_cita': datos_cita
                    }
        # Si no coincide con nada, mantener en el menú de tratamientos
        return {
            'respuesta': '¿Sobre qué tratamiento específico te gustaría saber más? Tenemos: limpieza dental, empastes, ortodoncia, cirugía oral, blanqueamiento, endodoncia, periodoncia, implantes dentales y otros tratamientos especializados.',
            'estado': ESTADOS_CONVERSACION['en_menu_tratamientos'],
            'datos_cita': datos_cita
        }
    
    # Para otros estados o estado inicial, usar el sistema de respuestas predefinidas
    # Buscar coincidencias exactas primero
    for clave, respuesta in RESPUESTAS_PREDEFINIDAS.items():
        if clave in mensaje_lower:
            # Si es una solicitud de cita, cambiar el estado
            if clave in ['solicitar una cita', 'quiero una cita', 'necesito una cita', 'agendar cita', 'sí, quiero agendar una cita']:
                return {
                    'respuesta': respuesta,
                    'estado': ESTADOS_CONVERSACION['preguntando_tratamiento_abierto'],
                    'datos_cita': datos_cita
                }
            # Si es información sobre tratamientos, cambiar al estado de menú de tratamientos
            elif clave in ['información sobre tratamientos', 'tratamientos']:
                return {
                    'respuesta': respuesta,
                    'estado': ESTADOS_CONVERSACION['en_menu_tratamientos'],
                    'datos_cita': datos_cita
                }
            else:
                return {
                    'respuesta': respuesta,
                    'estado': ESTADOS_CONVERSACION['inicial'],
                    'datos_cita': datos_cita
                }
    
    # Si no hay coincidencias exactas, buscar palabras clave
    palabras_clave = {
        'hola': 'hola',
        'buenos días': 'buenos días',
        'buenas tardes': 'buenas tardes',
        'buenas noches': 'buenas noches',
        'tratamiento': 'información sobre tratamientos',
        'limpieza': 'limpieza dental',
        'empaste': 'empastes',
        'ortodoncia': 'ortodoncia',
        'cirugía': 'cirugía oral',
        'blanqueamiento': 'blanqueamiento',
        'endodoncia': 'endodoncia',
        'periodoncia': 'periodoncia',
        'implante': 'implantes dentales',
        'cita': 'solicitar una cita',
        'agendar': 'solicitar una cita',
        'ubicación': 'ubicaciones',
        'dirección': 'ubicaciones',
        'horario': 'horarios',
        'teléfono': 'teléfono',
        'contacto': 'teléfono'
    }
    
    for palabra, respuesta_clave in palabras_clave.items():
        if palabra in mensaje_lower:
            respuesta = RESPUESTAS_PREDEFINIDAS[respuesta_clave]
            # Si es una solicitud de cita, cambiar el estado
            if respuesta_clave == 'solicitar una cita':
                return {
                    'respuesta': respuesta,
                    'estado': ESTADOS_CONVERSACION['preguntando_tratamiento_abierto'],
                    'datos_cita': datos_cita
                }
            else:
                return {
                    'respuesta': respuesta,
                    'estado': ESTADOS_CONVERSACION['inicial'],
                    'datos_cita': datos_cita
                }
    
    # Si no hay coincidencias, devolver respuesta por defecto
    return {
        'respuesta': RESPUESTAS_PREDEFINIDAS['default'],
        'estado': ESTADOS_CONVERSACION['inicial'],
        'datos_cita': datos_cita
    }
    palabras_clave = {
        'hola': 'hola',
        'buenos días': 'buenos días',
        'buenas tardes': 'buenas tardes',
        'buenas noches': 'buenas noches',
        'tratamiento': 'información sobre tratamientos',
        'limpieza': 'limpieza dental',
        'empaste': 'empastes',
        'ortodoncia': 'ortodoncia',
        'cirugía': 'cirugía oral',
        'blanqueamiento': 'blanqueamiento',
        'endodoncia': 'endodoncia',
        'periodoncia': 'periodoncia',
        'implante': 'implantes dentales',
        'cita': 'solicitar una cita',
        'agendar': 'solicitar una cita',
        'ubicación': 'ubicaciones',
        'dirección': 'ubicaciones',
        'horario': 'horarios',
        'teléfono': 'teléfono',
        'contacto': 'teléfono'
    }
    
    for palabra, respuesta_clave in palabras_clave.items():
        if palabra in mensaje_lower:
            return RESPUESTAS_PREDEFINIDAS[respuesta_clave]
    
    # Si no hay coincidencias, devolver respuesta por defecto
    return RESPUESTAS_PREDEFINIDAS['default']

# Configuración del chatbot
CHATBOT_CONFIG = {
    'clinic_name': 'Clínica Dental "De Ejemplo"',
    'welcome_message': 'Bienvenido a Clínica Dental "De Ejemplo", ¿en qué puedo ayudarte?'
}

@app.route('/')
def index():
    return render_template('index.html', config=CHATBOT_CONFIG)

@app.route('/citas')
def citas():
    tipo_cita = request.args.get('tipo', 'revision')
    return render_template('citas.html', tipo_cita=tipo_cita)

@app.route('/admin')
def admin():
    """Página de administración de la base de datos"""
    return render_template('admin.html')

@app.route('/panel')
def panel():
    """Panel de atención al cliente"""
    return render_template('panel.html')

@app.route('/formulario-cita')
def formulario_cita():
    """Página del formulario de citas"""
    # Obtener datos de la sesión si existen
    datos_cita = session.get('datos_cita', {})
    
    # Obtener horas disponibles para la fecha seleccionada
    horas_disponibles = []
    if datos_cita.get('fecha'):
        try:
            horas_disponibles = get_horas_disponibles(datos_cita['fecha'])
        except:
            horas_disponibles = []
    
    return render_template('cita_form.html', 
                         config=CHATBOT_CONFIG,
                         datos_cita=datos_cita,
                         horas_disponibles=horas_disponibles)

@app.route('/guardar-cita-form', methods=['POST'])
def guardar_cita_form():
    """Procesar el formulario de citas"""
    try:
        # Obtener datos del formulario
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        tipo_cita = request.form.get('tipo_cita')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        
        # Validar datos requeridos
        if not all([nombre, telefono, email, tipo_cita, fecha, hora]):
            return render_template('cita_form.html',
                                config=CHATBOT_CONFIG,
                                datos_cita={'nombre': nombre, 'telefono': telefono, 'email': email, 'tipo_cita': tipo_cita, 'fecha': fecha, 'hora': hora},
                                horas_disponibles=get_horas_disponibles(fecha) if fecha else [],
                                mensaje='Por favor completa todos los campos requeridos',
                                tipo_mensaje='error')
        
        # Verificar si la hora está disponible
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        cita_existente = Cita.query.filter_by(
            fecha=fecha_obj,
            hora=hora,
            estado='pendiente'
        ).first()
        
        if cita_existente:
            return render_template('cita_form.html',
                                config=CHATBOT_CONFIG,
                                datos_cita={'nombre': nombre, 'telefono': telefono, 'email': email, 'tipo_cita': tipo_cita, 'fecha': fecha, 'hora': hora},
                                horas_disponibles=get_horas_disponibles(fecha),
                                mensaje='Lo sentimos, esa hora ya no está disponible. Por favor selecciona otra hora.',
                                tipo_mensaje='error')
        
        # Crear nueva cita
        nueva_cita = Cita(
            nombre=nombre,
            telefono=telefono,
            email=email,
            tipo_cita=tipo_cita,
            fecha=fecha_obj,
            hora=hora
        )
        
        db.session.add(nueva_cita)
        db.session.commit()
        
        # Limpiar datos de la sesión
        session.pop('datos_cita', None)
        
        return render_template('cita_form.html',
                            config=CHATBOT_CONFIG,
                            mensaje=f'¡Excelente! Tu cita ha sido programada exitosamente para el {fecha} a las {hora}. Recibirás una confirmación por email. Tu número de cita es #{nueva_cita.id}.',
                            tipo_mensaje='success')
        
    except Exception as e:
        return render_template('cita_form.html',
                            config=CHATBOT_CONFIG,
                            datos_cita={'nombre': nombre, 'telefono': telefono, 'email': email, 'tipo_cita': tipo_cita, 'fecha': fecha, 'hora': hora},
                            horas_disponibles=get_horas_disponibles(fecha) if fecha else [],
                            mensaje=f'Error al guardar la cita: {str(e)}',
                            tipo_mensaje='error')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        estado_actual = data.get('estado', 'inicial')
        datos_cita = data.get('datos_cita', {})
        
        if not user_message.strip():
            return jsonify({'error': 'Mensaje vacío'}), 400
        
        # Obtener respuesta predefinida con estado
        resultado = obtener_respuesta(user_message, estado_actual, datos_cita)
        
        # Guardar datos de cita en la sesión si se va a redirigir al formulario
        if resultado.get('redirigir_formulario'):
            session['datos_cita'] = resultado['datos_cita']
        
        return jsonify({
            'response': resultado['respuesta'],
            'estado': resultado['estado'],
            'datos_cita': resultado['datos_cita'],
            'mostrar_calendario': resultado.get('mostrar_calendario', False),
            'mostrar_horas': resultado.get('mostrar_horas', False),
            'mostrar_confirmacion': resultado.get('mostrar_confirmacion', False),
            'mostrar_input_padecimiento': resultado.get('mostrar_input_padecimiento', False),
            'cita_guardada': resultado.get('cita_guardada', False),
            'limpiar_pantalla': resultado.get('limpiar_pantalla', False),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500

# Funciones para manejar citas
def get_dias_disponibles():
    """Obtiene los próximos 30 días disponibles (excluyendo domingos)"""
    dias = []
    fecha_actual = datetime.now().date()
    
    for i in range(1, 31):
        fecha = fecha_actual + timedelta(days=i)
        # Excluir domingos (6 = domingo)
        if fecha.weekday() != 6:
            dias.append({
                'fecha': fecha.strftime('%Y-%m-%d'),
                'dia_semana': fecha.strftime('%A'),
                'dia_mes': fecha.day,
                'mes': fecha.strftime('%B')
            })
    
    return dias

def get_horas_disponibles(fecha_str):
    """Obtiene las horas disponibles para una fecha específica"""
    fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    
    # Horarios de la clínica: 9:00-18:00 (L-V), 9:00-14:00 (S)
    es_sabado = fecha.weekday() == 5
    hora_fin = 14 if es_sabado else 18
    
    horas = []
    hora_actual = 9
    
    while hora_actual < hora_fin:
        hora_str = f"{hora_actual:02d}:00"
        hora_media_str = f"{hora_actual:02d}:30"
        
        # Verificar si la hora está ocupada
        cita_existente = Cita.query.filter_by(
            fecha=fecha,
            hora=hora_str,
            estado='pendiente'
        ).first()
        
        if not cita_existente:
            horas.append(hora_str)
        
        # Verificar la media hora
        cita_existente_media = Cita.query.filter_by(
            fecha=fecha,
            hora=hora_media_str,
            estado='pendiente'
        ).first()
        
        if not cita_existente_media:
            horas.append(hora_media_str)
        
        hora_actual += 1
    
    return horas

@app.route('/api/dias-disponibles')
def api_dias_disponibles():
    """API para obtener días disponibles"""
    dias = get_dias_disponibles()
    return jsonify({'dias': dias})

@app.route('/api/horas-disponibles/<fecha>')
def api_horas_disponibles(fecha):
    """API para obtener horas disponibles para una fecha"""
    horas = get_horas_disponibles(fecha)
    return jsonify({'horas': horas})

@app.route('/api/guardar-cita', methods=['POST'])
def api_guardar_cita():
    """API para guardar una cita"""
    try:
        data = request.get_json()
        
        # Crear nueva cita
        nueva_cita = Cita(
            nombre=data['nombre'],
            telefono=data['telefono'],
            email=data['email'],
            tipo_cita=data['tipo_cita'],
            fecha=datetime.strptime(data['fecha'], '%Y-%m-%d').date(),
            hora=data['hora']
        )
        
        db.session.add(nueva_cita)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'cita_id': nueva_cita.id,
            'mensaje': 'Cita guardada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/guardar-cita-chat', methods=['POST'])
def api_guardar_cita_chat():
    """API para guardar una cita desde el chat"""
    try:
        data = request.get_json()
        
        # Crear nueva cita
        nueva_cita = Cita(
            nombre=data['nombre'],
            telefono=data['telefono'],
            email=data['email'],
            tipo_cita=data['tipo_cita'],
            fecha=datetime.strptime(data['fecha'], '%Y-%m-%d').date(),
            hora=data['hora']
        )
        
        db.session.add(nueva_cita)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'cita_id': nueva_cita.id,
            'mensaje': f'¡Perfecto! Tu cita ha sido programada exitosamente para el {data["fecha"]} a las {data["hora"]}. Recibirás una confirmación por email. Tu número de cita es #{nueva_cita.id}.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/download-database')
def download_database():
    """Descarga la base de datos SQLite"""
    try:
        from flask import send_file
        import os
        
        db_path = 'citas.db'
        
        if not os.path.exists(db_path):
            return jsonify({'error': 'Base de datos no encontrada'}), 404
        
        return send_file(
            db_path,
            as_attachment=True,
            download_name=f'citas_database_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db',
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        return jsonify({'error': f'Error al descargar la base de datos: {str(e)}'}), 500

@app.route('/api/database-stats')
def database_stats():
    """Obtiene estadísticas de la base de datos"""
    try:
        total_citas = Cita.query.count()
        citas_pendientes = Cita.query.filter_by(estado='pendiente').count()
        citas_confirmadas = Cita.query.filter_by(estado='confirmada').count()
        citas_canceladas = Cita.query.filter_by(estado='cancelada').count()
        
        # Estadísticas por tipo de cita
        revisiones = Cita.query.filter_by(tipo_cita='revision').count()
        padecimientos = Cita.query.filter_by(tipo_cita='padecimiento').count()
        
        # Últimas 5 citas
        ultimas_citas = Cita.query.order_by(Cita.fecha_creacion.desc()).limit(5).all()
        ultimas_citas_data = []
        for cita in ultimas_citas:
            ultimas_citas_data.append({
                'id': cita.id,
                'nombre': cita.nombre,
                'fecha': cita.fecha.strftime('%Y-%m-%d'),
                'hora': cita.hora,
                'tipo': cita.tipo_cita,
                'estado': cita.estado,
                'fecha_creacion': cita.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'total_citas': total_citas,
            'citas_pendientes': citas_pendientes,
            'citas_confirmadas': citas_confirmadas,
            'citas_canceladas': citas_canceladas,
            'revisiones': revisiones,
            'padecimientos': padecimientos,
            'ultimas_citas': ultimas_citas_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500

@app.route('/export-csv')
def export_csv():
    """Exporta la base de datos a CSV"""
    try:
        import csv
        from io import StringIO
        from flask import Response
        
        # Obtener todas las citas
        citas = Cita.query.order_by(Cita.fecha_creacion.desc()).all()
        
        # Crear CSV en memoria
        si = StringIO()
        cw = csv.writer(si)
        
        # Escribir encabezados
        cw.writerow(['ID', 'Nombre', 'Teléfono', 'Email', 'Tipo de Cita', 
                     'Fecha', 'Hora', 'Estado', 'Fecha de Creación'])
        
        # Escribir datos
        for cita in citas:
            tipo_cita = 'Revisión General' if cita.tipo_cita == 'revision' else 'Padecimiento'
            cw.writerow([
                cita.id,
                cita.nombre,
                cita.telefono,
                cita.email,
                tipo_cita,
                cita.fecha.strftime('%Y-%m-%d'),
                cita.hora,
                cita.estado,
                cita.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Crear respuesta
        output = si.getvalue()
        si.close()
        
        return Response(
            output,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=citas_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
        )
        
    except Exception as e:
        return jsonify({'error': f'Error al exportar CSV: {str(e)}'}), 500

@app.route('/api/citas')
def api_citas():
    """API para obtener todas las citas"""
    try:
        citas = Cita.query.order_by(Cita.fecha, Cita.hora).all()
        citas_data = []
        
        for cita in citas:
            citas_data.append({
                'id': cita.id,
                'nombre': cita.nombre,
                'telefono': cita.telefono,
                'email': cita.email,
                'tipo_cita': cita.tipo_cita,
                'fecha': cita.fecha.strftime('%Y-%m-%d'),
                'hora': cita.hora,
                'estado': cita.estado,
                'fecha_creacion': cita.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({'citas': citas_data})
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener citas: {str(e)}'}), 500

# Crear la base de datos
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 