#!/usr/bin/env python3

import os
import subprocess
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import concurrent.futures

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pytz import timezone

# Import the Config class from config.py
from config import Config


#######################################
# Load environment variables (.env)
#######################################
load_dotenv()

#######################################
# Initialize Flask + CORS
#######################################
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

#######################################
# Ping-based host check
#######################################
def ping_host(hostname):
    """
    Ping once (-c 1) with a 2-second timeout (-W 2).
    Return True if ping is successful (exit code 0).
    """
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '2', hostname],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return (result.returncode == 0)
    except Exception as e:
        print(f"Ping error for {hostname}: {e}")
        return False

#######################################
# Check a single server (ping approach)
#######################################
def check_single_server(server_info):
    """
    server_info: (name, url) from Config.SERVERS
    We strip 'http://' or 'https://' from the URL so we can ping the hostname.
    """
    name, url = server_info
    
    # Extract hostname from the URL
    hostname = url.replace('http://', '').replace('https://', '').split('/')[0]
    
    is_alive = ping_host(hostname)
    status = 'online' if is_alive else 'offline'
    print(f"Server {name} ({hostname}) is {status}")
    
    return name, {
        'status': status,
        'last_checked': datetime.now().isoformat()
    }

#######################################
# (Optional) send email alert if offline
#######################################
def send_alert(server_name, status):
    """
    Sends an email alert if the server is offline,
    reading credentials from .env: EMAIL_USERNAME, EMAIL_PASSWORD, ADMIN_EMAIL
    """
    email_user = os.getenv('EMAIL_USERNAME')
    email_pass = os.getenv('EMAIL_PASSWORD')
    admin_email = os.getenv('ADMIN_EMAIL')
    if not email_user or not email_pass or not admin_email:
        print("Email credentials not configured, skipping alert.")
        return

    try:
        current_time = datetime.now().astimezone(timezone('America/Chicago'))
        msg = MIMEText(f"Server {server_name} is {status} as of {current_time.strftime('%Y-%m-%d %I:%M:%S %p CST')}")
        msg['Subject'] = f"SERVER ALERT: {server_name}"
        msg['From'] = email_user
        msg['To'] = admin_email

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_user, email_pass)
            server.send_message(msg)
        print(f"Alert email sent for {server_name}")
    except Exception as e:
        print(f"Failed to send email alert for {server_name}: {str(e)}")

#######################################
# Flask route: GET /api/status
#######################################
@app.route('/api/status')
def get_status():
    """
    Check all servers concurrently (ThreadPoolExecutor) and return JSON.
    If a server is offline, optionally send an alert email.
    """
    try:
        results = {}
        # Up to 6 parallel checks
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(check_single_server, (name, url)): name
                for name, url in Config.SERVERS.items()
            }
            for future in concurrent.futures.as_completed(futures):
                name, status_data = future.result()
                results[name] = status_data
                
                # If offline, optionally send alert
                if status_data['status'] == 'offline':
                    send_alert(name, 'offline')
        
        print("Results:", results)
        return jsonify(results)
    except Exception as e:
        print(f"Error in get_status: {str(e)}")
        return jsonify({"error": str(e)}), 500

#######################################
# Optional home route
#######################################
@app.route('/')
def home():
    return jsonify({"message": "Ping-based server monitor is running"})


if __name__ == '__main__':
    # Run on 0.0.0.0:5000
    app.run(host='0.0.0.0', port=5000, debug=True)
