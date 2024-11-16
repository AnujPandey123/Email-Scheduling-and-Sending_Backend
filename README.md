
# Email Scheduling and Sending Service (Backend)

## Objective:
The backend of this project handles the following tasks:
1. Uploading CSV files for email list.
2. Customizing and sending emails based on provided user inputs.
3. Scheduling emails for later delivery.
4. Providing email logs for tracking the status of sent emails.

---

## Technologies Used:
- **Python**
- **Flask** (web framework)
- **Flask-SQLAlchemy** (for database management)
- **SQLite** (for database storage)
- **Email Service Provider (ESP)** (for sending emails)
- **Celery** (for scheduling tasks, if needed)

---

## Setup Instructions

### 1. Clone the repository:
```bash
git clone https://github.com/your-repo/email-sender-backend.git
cd email-sender-backend
```

### 2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install dependencies:
```bash
pip install -r requirements.txt
```

### 4. Create and configure the `.env` file:
Create a `.env` file at the root of the project directory and add the necessary configurations for email and database settings. Here’s an example:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
EMAIL_HOST=smtp.your-esp.com
EMAIL_PORT=587
EMAIL_USER=your-email@example.com
EMAIL_PASS=your-email-password
```

### 5. Initialize the database:
Run the following command to create the necessary tables in your database.
```bash
flask db upgrade
```

### 6. Run the Flask server:
```bash
flask run
```

The API will be available at: `http://127.0.0.1:5000/`

---

## API Endpoints

- **POST /upload**
   - Upload a CSV file with email data.
   - Input: CSV file.
   - Output: Success or error message.

- **POST /send_emails**
   - Sends personalized emails based on the CSV data and customization options.
   - Input: JSON with email subject, body template, and prompt.
   - Output: Success or error message.

- **POST /schedule_emails**
   - Schedule emails for future delivery.
   - Input: JSON with the scheduled time.
   - Output: Success or error message.

- **GET /email_logs**
   - Fetch logs of sent emails with details such as recipient, subject, status, and timestamp.
   - Output: JSON array of logs.

---

## Running with Docker (Optional)

### 1. Build the Docker image:
```bash
docker build -t email-sender-backend .
```

### 2. Run the container:
```bash
docker run -p 5000:5000 email-sender-backend
```

---

## Frontend Instructions (To Be Run Separately)
Refer to the [Frontend README](../frontend/README.md) for the client-side setup.

---
