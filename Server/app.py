from flask import Flask, request, jsonify
from datetime import datetime
import threading
import time
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load environment variables
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')  # Format: 'whatsapp:+14155238886'
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Message queue for scheduled messages
message_queue = []

def send_whatsapp_message(to, message):
    try:
        print(f"Sending WhatsApp message to: {to}")
        response = twilio_client.messages.create(
            body=message,
            from_=f'whatsapp:{TWILIO_PHONE_NUMBER}',
            to=f'whatsapp:+91{to}'  # Customize for other country codes if needed
        )
        print(f"WhatsApp message SID: {response.sid}")
        return True, None
    except Exception as e:
        print(f"Error sending WhatsApp: {e}")
        return False, str(e)

def send_email(to, message):
    try:
        print(f"Sending Email to: {to}")
        msg = MIMEText(message)
        msg['Subject'] = 'Automated Message'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        return True, None
    except Exception as e:
        print(f"Error sending email: {e}")
        return False, str(e)

def process_scheduled_messages():
    while True:
        now = datetime.now()
        to_remove = []

        for i, msg in enumerate(message_queue):
            if msg['scheduled_time'] <= now:
                print(f"Processing scheduled message to: {msg['destination']}")
                if msg['type'] == 'whatsapp':
                    success, error = send_whatsapp_message(msg['destination'], msg['message'])
                else:
                    success, error = send_email(msg['destination'], msg['message'])

                if success:
                    print(f"Message sent successfully to {msg['destination']}")
                else:
                    print(f"Failed to send scheduled message: {error}")

                to_remove.append(i)

        # Clean up sent messages
        for i in sorted(to_remove, reverse=True):
            message_queue.pop(i)

        time.sleep(60)  # Check every 60 seconds

# Start background scheduler
scheduler_thread = threading.Thread(target=process_scheduled_messages)
scheduler_thread.daemon = True
scheduler_thread.start()

@app.route('/send-message', methods=['POST'])
def handle_message():
    try:
        data = request.get_json()
        destination = data['destination']
        message = data['message']
        is_scheduled = data['isScheduled']
        schedule_time = data.get('scheduleTime', '')
        msg_type = data['type']  # 'whatsapp' or 'email'

        if msg_type not in ['whatsapp', 'email']:
            return jsonify({'error': 'Invalid message type. Must be "whatsapp" or "email".'}), 400

        if is_scheduled:
            try:
                scheduled_time = datetime.strptime(schedule_time, '%Y-%m-%dT%H:%M')
                message_queue.append({
                    'destination': destination,
                    'message': message,
                    'scheduled_time': scheduled_time,
                    'type': msg_type
                })
                return jsonify({'message': f'Message scheduled for {scheduled_time}'}), 200
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DDTHH:MM'}), 400
        else:
            if msg_type == 'whatsapp':
                success, error = send_whatsapp_message(destination, message)
            else:
                success, error = send_email(destination, message)

            if success:
                return jsonify({'message': 'Message sent successfully'}), 200
            else:
                return jsonify({'error': error}), 500
    except Exception as e:
        print(f"Unhandled error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
