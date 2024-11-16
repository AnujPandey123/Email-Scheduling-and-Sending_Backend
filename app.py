import os
from dotenv import load_dotenv
import pandas as pd
from flask import Flask, request, jsonify
from flask_restx import Api, fields
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from groq import Groq
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import threading
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
api = Api(app, version="1.0", title="Email Sending API", description="A simple API to send customized emails")
ns = api.namespace("emails", description="Email operations")

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emails.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize database models
class EmailLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
# Create the database tables within the application context
with app.app_context():
    db.create_all()
# Fetch credentials from environment variables
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Email throttling settings
EMAILS_PER_MINUTE = 10
EMAIL_INTERVAL = 60 / EMAILS_PER_MINUTE

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        if not file.filename.endswith('.csv'):
            return jsonify({"error": "Only CSV files are allowed"}), 400

        df = pd.read_csv(file)
        app.config['csv_data'] = df
        return jsonify({"message": "File uploaded successfully", "data": df.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": f"Error during upload: {str(e)}"}), 500

@app.route('/send_emails', methods=['POST'])
def send_emails():
    data = request.get_json()
    df = app.config.get('csv_data', None)
    if df is None:
        return {"error": "No CSV data found. Please upload a CSV file first."}, 400

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(GMAIL_USER, GMAIL_PASSWORD)

    for _, row in df.iterrows():
        recipient_email = row['email']
        recipient_name = row['name']
        try:
            prompt = data['prompt'].replace("{name}", recipient_name)
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
            )
            personalized_content = chat_completion.choices[0].message.content
            personalized_body = data['bodyTemplate'].replace("{name}", recipient_name).replace("{content}", personalized_content)

            msg = MIMEMultipart()
            msg['From'] = GMAIL_USER
            msg['To'] = recipient_email
            msg['Subject'] = data['subject']
            msg.attach(MIMEText(personalized_body, 'plain'))
            server.sendmail(GMAIL_USER, recipient_email, msg.as_string())

            email_log = EmailLog(
                recipient_email=recipient_email,
                subject=data['subject'],
                status="Sent",
            )
            db.session.add(email_log)
            db.session.commit()
        except Exception as e:
            email_log = EmailLog(
                recipient_email=recipient_email,
                subject=data['subject'],
                status=f"Failed: {str(e)}",
            )
            db.session.add(email_log)
            db.session.commit()

        time.sleep(EMAIL_INTERVAL)

    server.quit()
    return {"message": "Emails have been sent successfully."}, 200

@app.route('/schedule_emails', methods=['POST'])
def schedule_emails():
    data = request.get_json()
    schedule_time = data.get('schedule_time')
    try:
        schedule_time_dt = datetime.fromisoformat(schedule_time)

        delay = (schedule_time_dt - datetime.utcnow()).total_seconds()
        threading.Timer(delay, send_emails).start()
        return {"message": "Emails scheduled successfully."}, 200
    except Exception as e:
        return {"error": f"Failed to schedule emails: {str(e)}"}, 500

@app.route('/email_logs', methods=['GET'])
def get_email_logs():
    logs = EmailLog.query.all()
    return jsonify([{
        "id": log.id,
        "recipient_email": log.recipient_email,
        "subject": log.subject,
        "status": log.status,
        "timestamp": log.timestamp
    } for log in logs])

if __name__ == '__main__':
    app.run(debug=True, port=3001)
