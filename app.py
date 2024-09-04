from flask import Flask, request
from twilio.rest import Client
import PyPDF2
import os

app = Flask(__name__)

# Configura tus credenciales de Twilio
TWILIO_ACCOUNT_SID = os.getenv('ACe3b30530004f5f0e00ae549afd10765c')
TWILIO_AUTH_TOKEN = os.getenv('0bfdac3a779f6958ae8c66d98f6613dd')
TWILIO_PHONE_NUMBER = os.getenv('14155238886')
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

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
    if message.lower().startswith('read pdf'):
        pdf_path = 'path_to_your_pdf.pdf'
        return read_pdf(pdf_path)
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

if __name__ == '__main__':
    app.run(debug=True)
