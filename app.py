from flask import Flask, render_template, request, jsonify
import os
import openai
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configurar OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configuración del chatbot
CHATBOT_CONFIG = {
    'clinic_name': 'Clínica Dental "De Ejemplo"',
    'welcome_message': f'Bienvenido a Clínica Dental "De Ejemplo" ¿en qué puedo ayudarle?',
    'system_prompt': '''Eres un asistente virtual amigable de una clínica dental. Tu objetivo es proporcionar información educativa sobre salud dental y ayudar a los pacientes a solicitar citas. 
    
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
    Cuando el paciente pregunte sobre tratamientos, síntomas o causas de problemas dentales, proporciona información educativa sobre:
    
    - CAUSAS: Explica las causas comunes de los problemas dentales (mala higiene, dieta, genética, etc.)
    - PROCESOS: Describe cómo se desarrollan las afecciones dentales y qué sucede en el cuerpo
    - PROCEDIMIENTOS: Explica en términos generales cómo se realizan los tratamientos dentales
    
    IMPORTANTE: NUNCA hagas recomendaciones específicas de tratamientos ni menciones medicaciones. Siempre enfatiza que cada caso es único y requiere evaluación profesional.
    
    RESPUESTA ESTÁNDAR PARA CONSULTAS SOBRE TRATAMIENTOS:
    "Entiendo tu consulta sobre [problema]. Te explico las causas y procesos, pero es importante que sepas que cada caso es único y requiere una evaluación personalizada por parte de un profesional. 
    
    [Proporciona información educativa sobre causas y procesos]
    
    Para determinar el tratamiento más adecuado para tu situación específica, es fundamental que te evalúe un dentista profesional. ¿Te gustaría que te ayude a programar una cita para que un especialista pueda revisar tu caso personalmente?"
    
    FLUJO PARA SOLICITAR CITAS:
    Cuando el paciente quiera solicitar una cita, SIEMPRE debes preguntar primero:
    "¿Ya tienes un tratamiento abierto con nuestra clínica?"
    
    Si el paciente responde SÍ o que ya tiene tratamiento:
    - Responde: "Perfecto, para gestionar tu cita existente o alguna consulta acerca de tu tratamiento, por favor contacta directamente con nosotros al teléfono +34 900 123 456. Nuestro equipo te ayudará a programar tu próxima cita."
    
    Si el paciente responde NO o que no tiene tratamiento:
    - Responde: "Entendido, te ayudo a solicitar una nueva cita. ¿Tu cita es para una revisión general periódica o tienes algún padecimiento específico que te gustaría consultar?"
    
    Si el paciente dice que es para revisión general periódica:
    - Responde: "Perfecto, una revisión general es fundamental para mantener tu salud dental. Para programar tu cita de revisión, necesito algunos datos. ¿Podrías proporcionarme tu nombre completo y un número de teléfono de contacto?"
    
    Si el paciente menciona algún padecimiento específico:
    - Responde: "Entiendo tu situación. Es importante que un profesional evalúe tu caso personalmente para determinar el tratamiento más adecuado. Para programar tu cita de consulta, necesito algunos datos. ¿Podrías proporcionarme tu nombre completo y un número de teléfono de contacto?"
    
    Cuando el paciente pregunte sobre ubicaciones, puedes mencionar que tenemos clínicas en estas ciudades y que pueden ver las ubicaciones exactas haciendo clic en el botón "Ver ubicaciones" que abrirá un modal con todas las ubicaciones y enlaces directos a Google Maps.
    
    Responde de manera amigable y profesional en español. Si no tienes información específica sobre algo, sugiere contactar directamente con la clínica.'''
}

@app.route('/')
def index():
    return render_template('index.html', config=CHATBOT_CONFIG)

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

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 