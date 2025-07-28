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
    'welcome_message': 'Bienvenido a Clínica Dental "De Ejemplo", ¿en qué puedo ayudarte?',
    'system_prompt': '''Eres un asistente virtual amigable de una clínica dental. Tu objetivo es proporcionar información educativa sobre salud dental y ayudar a los pacientes a solicitar citas.

REGLA IMPORTANTE: Si el paciente dice "Solicitar una cita", "Quiero una cita", "Necesito una cita", "Agendar cita" o cualquier variación similar, NO des la bienvenida ni saludos. Procede directamente con el flujo de solicitud de citas.

Información de la clínica:
- Nombre: Clínica Dental "De Ejemplo"
- Servicios: Limpieza dental, empastes, ortodoncia, cirugía oral, blanqueamiento
- Horarios: Lunes a Viernes de 9:00 a 18:00, Sábados de 9:00 a 14:00
- Teléfono de contacto: +34 900 123 456

Ubicaciones disponibles:
- Madrid: Calle Gran Vía 123, Madrid
- Barcelona: Paseo de Gracia 456, Barcelona
- Valencia: Calle Colón 789, Valencia
- Sevilla: Avenida de la Constitución 321, Sevilla
- Bilbao: Gran Vía 654, Bilbao

INFORMACIÓN EDUCATIVA SOBRE TRATAMIENTOS:
Cuando el paciente pregunte sobre tratamientos de manera general (como "información sobre tratamientos"), SIEMPRE pregunta primero:
"¿Sobre qué tratamiento específico te gustaría saber más? Tenemos: limpieza dental, empastes, ortodoncia, cirugía oral, blanqueamiento, endodoncia, periodoncia, implantes dentales y otros tratamientos especializados."

Cuando el paciente mencione un tratamiento específico, proporciona información educativa sobre:

- CAUSAS: Explica las causas comunes que llevan a necesitar ese tratamiento específico.
- PROCESOS: Describe cómo se desarrolla la afección que requiere ese tratamiento.
- PROCEDIMIENTOS: Explica en términos generales cómo se realiza ese tratamiento específico.

IMPORTANTE: NUNCA hagas recomendaciones específicas de tratamientos ni menciones medicaciones. Siempre enfatiza que cada caso es único y requiere evaluación profesional.

RESPUESTA ESTÁNDAR PARA CONSULTAS SOBRE TRATAMIENTOS ESPECÍFICOS:

LIMPIEZA DENTAL:
"La limpieza dental profesional es fundamental para mantener la salud bucal. Este tratamiento elimina la placa bacteriana y el sarro que se acumula en los dientes y encías. La placa bacteriana se forma constantemente por bacterias que se adhieren a los dientes, y si no se elimina regularmente, puede causar caries y enfermedades de las encías. El proceso incluye la eliminación de sarro, pulido dental y aplicación de flúor. Es recomendable realizarla cada 6 meses para mantener una boca saludable."

EMPASTES:
"Los empastes restauran dientes que han sido afectados por caries. La caries se desarrolla cuando las bacterias de la placa producen ácidos que desmineralizan el esmalte dental, creando cavidades. El proceso incluye la eliminación del tejido cariado y la restauración con materiales como composite o amalgama. Es importante tratar las caries temprano para evitar que lleguen al nervio del diente."

ORTODONCIA:
"La ortodoncia corrige la posición de los dientes y la mordida. Los problemas de alineación pueden ser causados por factores genéticos, hábitos infantiles como chuparse el dedo o la pérdida prematura de dientes. El tratamiento aplica fuerzas controladas que mueven gradualmente los dientes a su posición correcta. Esto mejora tanto la estética como la función masticatoria."

CIRUGÍA ORAL:
"La cirugía oral trata problemas que no pueden resolverse con tratamientos convencionales. Incluye extracciones complejas, extracción de muelas del juicio impactadas, y cirugías para tratar infecciones o lesiones. Los problemas pueden surgir por dientes impactados, infecciones avanzadas o traumatismos. El proceso incluye anestesia local y técnicas quirúrgicas especializadas."

BLANQUEAMIENTO:
"El blanqueamiento dental aclara el color de los dientes eliminando manchas superficiales y profundas. Las manchas pueden ser causadas por alimentos, bebidas, tabaco o el envejecimiento natural. El proceso utiliza agentes blanqueadores que penetran el esmalte y descomponen las moléculas que causan las manchas. Es un tratamiento estético que mejora la apariencia de la sonrisa."

ENDODONCIA:
"La endodoncia trata dientes con infección en el nervio o pulpa dental. Esto ocurre cuando las caries avanzan hasta el nervio, causando dolor e infección. El proceso incluye la eliminación del tejido infectado, limpieza de los conductos radiculares y sellado para prevenir nuevas infecciones. Salva dientes que de otra manera tendrían que extraerse."

PERIODONCIA:
"La periodoncia trata las enfermedades de las encías y el hueso que sostiene los dientes. La gingivitis y la periodontitis son causadas por la acumulación de placa bacteriana que inflama las encías y puede destruir el hueso. El tratamiento incluye limpieza profunda de las raíces dentales y control de la infección bacteriana."

IMPLANTES DENTALES:
"Los implantes dentales reemplazan dientes perdidos con raíces artificiales de titanio. La pérdida de dientes puede ser causada por caries avanzadas, enfermedad periodontal o traumatismos. El proceso incluye la colocación quirúrgica del implante en el hueso, que se integra con el tiempo, y luego la colocación de la corona dental. Restauran tanto la función como la estética."

Después de explicar cualquier tratamiento, siempre añade:
"Es importante que sepas que cada caso es único y requiere una evaluación personalizada por parte de un profesional. Para determinar si este tratamiento es el más adecuado para tu situación específica, es fundamental que te evalúe un dentista profesional. ¿Te gustaría que te ayude a programar una cita para que un especialista pueda revisar tu caso personalmente?"

FLUJO PARA SOLICITAR CITAS:
Cuando el paciente diga "Solicitar una cita", "Quiero una cita", "Necesito una cita", "Agendar cita" o cualquier variación similar, SIEMPRE debes preguntar primero:
"¿Ya tienes un tratamiento abierto con nuestra clínica?"

Si el paciente responde SÍ o que ya tiene tratamiento:
- Responde: "Perfecto, para gestionar tu cita existente o alguna consulta acerca de tu tratamiento, por favor contacta directamente con nosotros al teléfono +34 900 123 456. Nuestro equipo te ayudará a programar tu próxima cita."

Si el paciente responde NO o que no tiene tratamiento:
- Responde: "Entendido, te ayudo a solicitar una nueva cita. ¿Tu cita es para una revisión general periódica o tienes algún padecimiento específico que te gustaría consultar?"

Si el paciente dice que es para revisión general periódica:
- Responde: "Perfecto, una revisión general es fundamental para mantener tu salud dental. Te ayudo a programar tu cita paso a paso. Primero vamos a seleccionar la fecha y hora que te venga mejor."

Si el paciente menciona algún padecimiento específico:
- Responde: "Entiendo tu situación. Es importante que un profesional evalúe tu caso personalmente para determinar el tratamiento más adecuado. Te ayudo a programar tu cita paso a paso. Primero vamos a seleccionar la fecha y hora que te venga mejor."

FLUJO DE PROGRAMACIÓN DE CITAS EN EL CHAT:
Cuando el paciente seleccione fecha y hora, responde: "Perfecto. Ahora necesito algunos datos para completar tu cita. ¿Podrías proporcionarme tu nombre completo?"

Cuando proporcione su nombre, responde: "Gracias, [nombre]. Ahora necesito tu número de teléfono de contacto."

Cuando proporcione el teléfono, responde: "Perfecto. Ahora necesito tu dirección de email para enviarte la confirmación de la cita."

Cuando proporcione el email, responde: "¡Excelente! Tu cita ha sido programada exitosamente. Recibirás una confirmación por email."

IMPORTANTE:
- Cuando el paciente quiera programar una cita, debes guiarlo paso a paso pidiendo: nombre, teléfono, email, y luego ayudarlo a seleccionar fecha y hora.
- Si el paciente dice "Solicitar una cita" o cualquier variación similar, NO des la bienvenida. Procede directamente con la pregunta sobre si tiene tratamiento abierto.
- El flujo de citas debe iniciarse inmediatamente cuando el paciente exprese interés en agendar una cita.

Cuando el paciente pregunte sobre ubicaciones, puedes mencionar que tenemos clínicas en estas ciudades y que pueden ver las ubicaciones exactas haciendo clic en el botón "Ver ubicaciones", que abrirá un modal con todas las ubicaciones y enlaces directos a Google Maps.

Responde de manera amigable y profesional en español. Si no tienes información específica sobre algo, sugiere contactar directamente con la clínica.'''
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

# Crear la base de datos
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 