from flask import Flask, render_template, request, jsonify, session
import os
import openai
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

# Configurar OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

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

# Configuración del chatbot
CHATBOT_CONFIG = {
    'clinic_name': 'Clínica Dental "De Ejemplo"',
    'welcome_message': f'Bienvenido a Clínica Dental "De Ejemplo" ¿en qué puedo ayudarle?',
    'system_prompt': '''Eres un asistente virtual amigable de una clínica dental. Tu objetivo es proporcionar información educativa sobre salud dental y ayudar a los pacientes a solicitar citas.
    
    REGLA IMPORTANTE: Si el paciente dice "Solicitar una cita", "Quiero una cita", "Necesito una cita", "Agendar cita" o cualquier variación similar, NO des la bienvenida ni saludos. Procede directamente con el flujo de solicitud de citas. 
    
    Información de la clínica:
    - Nombre: Clínica Dental "De Ejemplo"
    - Servicios: Limpieza dental, empastes, ortodoncia, cirugía oral, blanqueamiento
    - Horarios: Lunes a Viernes 9:00-18:00, Sábados 9:00-14:00
    - Teléfono de contacto: +34 900 123 456
    
    Ubicaciones disponibles:
    - Madrid: Calle Gran Vía 123, Madrid
    - Barcelona: Paseo de Gracia 456, Barcelona
    - Valencia: Calle Colón 789, Valencia
    - Sevilla: Avenida de la Constitución 321, Sevilla
    - Bilbao: Gran Vía 654, Bilbao
    
    INFORMACIÓN EDUCATIVA SOBRE TRATAMIENTOS:
    Cuando el paciente pregunte sobre tratamientos de manera general (como "información sobre tratamientos"), SIEMPRE pregunta primero:
    "¿Sobre qué tratamiento específico te gustaría saber más? Tenemos: limpieza dental, empastes, ortodoncia, cirugía oral, blanqueamiento, endodoncia, periodoncia, implantes dentales, y otros tratamientos especializados."
    
    Cuando el paciente mencione un tratamiento específico, proporciona información educativa sobre:
    
    - CAUSAS: Explica las causas comunes que llevan a necesitar ese tratamiento específico
    - PROCESOS: Describe cómo se desarrolla la afección que requiere ese tratamiento
    - PROCEDIMIENTOS: Explica en términos generales cómo se realiza ese tratamiento específico
    
    IMPORTANTE: NUNCA hagas recomendaciones específicas de tratamientos ni menciones medicaciones. Siempre enfatiza que cada caso es único y requiere evaluación profesional.
    
    RESPUESTA ESTÁNDAR PARA CONSULTAS SOBRE TRATAMIENTOS ESPECÍFICOS:
    "Te explico sobre [tratamiento específico]. [Proporciona información educativa sobre causas y procesos de ese tratamiento específico]
    
    Es importante que sepas que cada caso es único y requiere una evaluación personalizada por parte de un profesional. Para determinar si este tratamiento es el más adecuado para tu situación específica, es fundamental que te evalúe un dentista profesional. ¿Te gustaría que te ayude a programar una cita para que un especialista pueda revisar tu caso personalmente?"
    
    FLUJO PARA SOLICITAR CITAS:
    Cuando el paciente diga "Solicitar una cita", "Quiero una cita", "Necesito una cita", "Agendar cita", o cualquier variación similar, SIEMPRE debes preguntar primero:
    "¿Ya tienes un tratamiento abierto con nuestra clínica?"
    
    Si el paciente responde SÍ o que ya tiene tratamiento:
    - Responde: "Perfecto, para gestionar tu cita existente o alguna consulta acerca de tu tratamiento, por favor contacta directamente con nosotros al teléfono +34 900 123 456. Nuestro equipo te ayudará a programar tu próxima cita."
    
    Si el paciente responde NO o que no tiene tratamiento:
    - Responde: "Entendido, te ayudo a solicitar una nueva cita. ¿Tu cita es para una revisión general periódica o tienes algún padecimiento específico que te gustaría consultar?"
    
    Si el paciente dice que es para revisión general periódica:
    - Responde: "Perfecto, una revisión general es fundamental para mantener tu salud dental. Te ayudo a programar tu cita paso a paso. Primero necesito algunos datos: ¿Podrías proporcionarme tu nombre completo?"
    
    Si el paciente menciona algún padecimiento específico:
    - Responde: "Entiendo tu situación. Es importante que un profesional evalúe tu caso personalmente para determinar el tratamiento más adecuado. Te ayudo a programar tu cita paso a paso. Primero necesito algunos datos: ¿Podrías proporcionarme tu nombre completo?"
    
    FLUJO DE PROGRAMACIÓN DE CITAS EN EL CHAT:
    Cuando el paciente proporcione su nombre, responde: "Gracias [nombre]. Ahora necesito tu número de teléfono de contacto."
    
    Cuando proporcione el teléfono, responde: "Perfecto. Ahora necesito tu dirección de email para enviarte la confirmación de la cita."
    
    Cuando proporcione el email, responde: "Excelente. Ahora vamos a seleccionar la fecha de tu cita. ¿Qué día te viene mejor? Puedes elegir entre los próximos días disponibles."
    
    IMPORTANTE: 
    - Cuando el paciente quiera programar una cita, debes guiarlo paso a paso pidiendo: nombre, teléfono, email, y luego ayudarlo a seleccionar fecha y hora.
    - Si el paciente dice "Solicitar una cita" o cualquier variación similar, NO des la bienvenida, procede directamente con la pregunta sobre si tiene tratamiento abierto.
    - El flujo de citas debe iniciarse inmediatamente cuando el paciente exprese interés en agendar una cita.
    
    Cuando el paciente pregunte sobre ubicaciones, puedes mencionar que tenemos clínicas en estas ciudades y que pueden ver las ubicaciones exactas haciendo clic en el botón "Ver ubicaciones" que abrirá un modal con todas las ubicaciones y enlaces directos a Google Maps.
    
    Responde de manera amigable y profesional en español. Si no tienes información específica sobre algo, sugiere contactar directamente con la clínica.'''
}

@app.route('/')
def index():
    return render_template('index.html', config=CHATBOT_CONFIG)

@app.route('/citas')
def citas():
    tipo_cita = request.args.get('tipo', 'revision')
    return render_template('citas.html', tipo_cita=tipo_cita)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message.strip():
            return jsonify({'error': 'Mensaje vacío'}), 400
        
        # Crear conversación con OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": CHATBOT_CONFIG['system_prompt']},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        bot_response = response.choices[0].message.content
        
        return jsonify({
            'response': bot_response,
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

# Crear la base de datos
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 