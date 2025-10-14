#!/usr/bin/env python3
"""
Quick start script for NETZ AI test server
"""

import http.server
import socketserver
import json
from urllib.parse import parse_qs
import threading
import time

class NETZTestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "status": "healthy",
                "timestamp": "2025-01-10T15:48:00Z",
                "mode": "test_mode"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode('utf-8'))
                messages = request_data.get('messages', [])
                
                if messages:
                    user_message = messages[-1].get('content', '').lower()
                    
                    if 'bonjour' in user_message:
                        response_text = "Bonjour ! Je suis l'assistant IA de NETZ Informatique. Comment puis-je vous aider aujourd'hui ?"
                    elif 'netz' in user_message:
                        response_text = "NETZ Informatique est une entreprise de services informatiques basée à Haguenau (67500). Contact: 07 67 74 49 03"
                    elif 'tarif' in user_message:
                        response_text = "Tarifs NETZ: Diagnostic GRATUIT, Dépannage 55€/h particuliers, 75€/h entreprises, Formations dès 45€/h"
                    elif 'formation' in user_message:
                        response_text = "Formations NETZ certifiées QUALIOPI: Excel, Word, Python, Cybersécurité. Eligible CPF et OPCO."
                    elif 'contact' in user_message:
                        response_text = "Contact NETZ: 📱 07 67 74 49 03, 📧 contact@netzinformatique.fr, Horaires: Lun-Ven 9h-19h"
                    else:
                        response_text = f"Merci pour votre message. NETZ Informatique vous aide avec tous vos besoins informatiques!"
                    
                    response = {"response": response_text, "language": "fr"}
                else:
                    response = {"error": "No messages provided"}
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {"error": str(e)}
                self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def start_server():
    PORT = 8001
    Handler = NETZTestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🚀 NETZ AI Test Server running on http://localhost:{PORT}")
        print(f"📱 Open browser-test.html to test")
        print(f"❤️  Health: http://localhost:{PORT}/health")
        print(f"🔄 Chat API: http://localhost:{PORT}/api/chat")
        httpd.serve_forever()

if __name__ == "__main__":
    start_server()