#!/usr/bin/env python3
import sys
import os
import socket

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from models import db

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✓ Database initialized")
    
    local_ip = get_local_ip()
    port = 80
    
    print("\n" + "="*50)
    print("🚀 Local File Sharer Started!")
    print("="*50)
    print(f"\n📍 Local Access:    http://127.0.0.1:{port}")
    print(f"🌐 Network Access:  http://{local_ip}:{port}")
    print("\n📱 Other devices on the same network can access using the Network Access URL")
    print("⏰ Files automatically expire based on your selected duration")
    print("\nPress Ctrl+C to stop the server\n")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)