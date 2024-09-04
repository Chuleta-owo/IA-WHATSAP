from flask import Flask, request, jsonify
from twilio.rest import Client
import PyPDF2
import os
import re

app = Flask(__name__)

# Configura tus credenciales de Twilio
TWILIO_ACCOUNT_SID = os.getenv('ACe3b30530004f5f0e00ae549afd10765c')
TWILIO_AUTH_TOKEN = os.getenv('0bfdac3a779f6958ae8c66d98f6613dd')
TWILIO_PHONE_NUMBER = os.getenv('+14155238886')
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Almacén de manuales (simulado como un diccionario)
manuales = {}

@app.route('/upload', methods=['POST'])
def upload_manual():
    """Sube un manual PDF para su procesamiento"""
    file = request.files.get('file')
    manual_id = request.form.get('manual_id')
    
    if file and manual_id:
        file_path = f'manuales/{manual_id}.pdf'
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
        # Procesar el PDF y almacenar el texto
        texto = read_pdf(file_path)
        manuales[manual_id] = texto
        return jsonify({"message": "Manual subido y procesado exitosamente"}), 200
    else:
        return jsonify({"message": "Archivo o ID del manual faltante"}), 400

@app.route('/sms', methods=['POST'])
def sms_reply():
    """Responde a los mensajes entrantes de WhatsApp"""
    from_number = request.form.get('From')
    body = request.form.get('Body')
    
    # Procesa el mensaje recibido
    response_message = process_message(body)
    
    # Envía una respuesta
    client.messages.create(
        body=response_message,
        from_=TWILIO_PHONE_NUMBER,
        to=from_number
    )
    
    return str(response_message)

def process_message(message):
    """Procesa el mensaje y devuelve una respuesta"""
    if message.lower().startswith('ask'):
        question = message[4:].strip()
        return answer_question(question)
    elif message.lower().startswith('read pdf'):
        manual_id = message[9:].strip()
        return read_manual(manual_id)
    else:
        return "Lo siento, no entiendo tu solicitud."

def read_pdf(pdf_path):
    """Lee el contenido de un archivo PDF"""
    if not os.path.exists(pdf_path):
        return "Archivo PDF no encontrado."
    
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            text += page.extract_text()
    
    return text if text else "No se pudo extraer texto del PDF."

def answer_question(question):
    """Busca la respuesta a una pregunta en los manuales"""
    for manual_id, texto in manuales.items():
        # Utiliza una búsqueda simple para encontrar la respuesta
        if re.search(re.escape(question), texto, re.IGNORECASE):
            # Extrae una respuesta relevante (esto es simplificado)
            return f"Encontré una respuesta en el manual {manual_id}: {extract_answer(texto, question)}"
    
    return "No pude encontrar una respuesta a tu pregunta en los manuales disponibles."

def extract_answer(texto, question):
    """Extrae una respuesta del texto del manual"""
    # Simplificación: encuentra la primera ocurrencia de la pregunta en el texto
    pattern = re.compile(r'(?<=\b{}\b).*'.format(re.escape(question)), re.IGNORECASE)
    match = pattern.search(texto)
    if match:
        return match.group(0).strip()
    return "Respuesta no encontrada."

def read_manual(manual_id):
    """Lee el contenido de un manual específico"""
    texto = manuales.get(manual_id)
    if texto:
        return f"Contenido del manual {manual_id}: {texto[:1000]}..."  # Muestra solo los primeros 1000 caracteres
    return "Manual no encontrado."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

