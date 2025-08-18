#!/usr/bin/env python3
"""
Raspberry Pi API Server for Admin Control
Handles commands from the admin backend
"""

import json
import subprocess
import os
import sys
import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import ssl

# Import our modules
from akari_generator_api import AkariPuzzleGeneratorAPI
from ebook_generator import EbookGenerator
from cdn_bunny_uploader import CDNBunnyUploader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rpi_api_server.log'),
        logging.StreamHandler()
    ]
)

# Configuration
API_KEY = 'rpi_control_key_2024'  # Change this!
PORT = 8080
HOST = '0.0.0.0'

# Load configuration
def load_config():
    try:
        with open('config/generator_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'api_url': 'https://shrinepuzzle.com/api/puzzle_receiver.php',
            'api_key': 'shrine_puzzle_api_key_2024',
            'cdn_bunny': {
                'storage_zone': 'your-storage-zone',
                'api_key': 'your-cdn-bunny-key',
                'storage_zone_name': 'your-zone-name',
                'region': 'de'
            }
        }

class RPiAPIHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.config = load_config()
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        logging.info(f"{self.client_address[0]} - {format % args}")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/execute':
            self.handle_execute()
        else:
            self.send_error(404, 'Not Found')
    
    def do_GET(self):
        if self.path == '/api/status':
            self.handle_status()
        elif self.path == '/api/logs':
            self.handle_logs()
        elif self.path == '/api/stats':
            self.handle_stats()
        else:
            self.send_error(404, 'Not Found')
    
    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def validate_auth(self):
        auth_header = self.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return False
        token = auth_header[7:]
        return token == API_KEY
    
    def handle_execute(self):
        if not self.validate_auth():
            self.send_json_response({'success': False, 'error': 'Unauthorized'}, 401)
            return
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            command = data.get('command')
            params = data.get('params', {})
            
            logging.info(f"Executing command: {command} with params: {params}")
            
            # Execute command in background thread
            thread = threading.Thread(target=self.execute_command, args=(command, params))
            thread.daemon = True
            thread.start()
            
            # Return immediate response
            self.send_json_response({
                'success': True,
                'message': f'Command {command} started',
                'command': command
            })
            
        except Exception as e:
            logging.error(f"Execute error: {str(e)}")
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, 500)
    
    def execute_command(self, command: str, params: Dict):
        """Execute command in background thread"""
        try:
            result = None
            
            if command == 'generate_puzzles':
                result = self.generate_puzzles(params)
            elif command == 'generate_ebook':
                result = self.generate_ebook(params)
            elif command == 'get_status':
                result = self.get_status()
            elif command == 'get_logs':
                result = self.get_logs(params)
            elif command == 'update_config':
                result = self.update_config(params)
            elif command == 'restart_service':
                result = self.restart_service()
            elif command == 'get_ebooks':
                result = self.get_ebooks()
            elif command == 'get_stats':
                result = self.get_stats()
            elif command == 'ping':
                result = {'success': True, 'message': 'pong'}
            else:
                result = {'success': False, 'error': f'Unknown command: {command}'}
            
            # Log result
            logging.info(f"Command {command} completed: {result}")
            
        except Exception as e:
            logging.error(f"Command execution error: {str(e)}")
    
    def generate_puzzles(self, params: Dict) -> Dict:
        """Generate puzzles"""
        try:
            generator = AkariPuzzleGeneratorAPI(
                self.config['api_url'],
                self.config['api_key']
            )
            
            sizes = params.get('sizes', [6, 8, 10, 12])
            difficulties = params.get('difficulties', ['easy', 'medium', 'hard'])
            count = params.get('count', 10)
            mode = params.get('mode', 'premium')
            
            result = generator.generate_batch(sizes, difficulties, count, mode)
            
            return {
                'success': True,
                'data': result,
                'message': f'Generated {result["total_generated"]} puzzles'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_ebook(self, params: Dict) -> Dict:
        """Generate and upload ebook"""
        try:
            # Generate ebook
            sizes = params.get('sizes', [6, 8, 10, 12])
            difficulties = params.get('difficulties', ['easy', 'medium', 'hard'])
            count = params.get('count', 20)
            title = params.get('title', 'Akari Puzzle Collection')
            output_file = f"ebooks/akari_ebook_{int(time.time())}.pdf"
            
            # Ensure ebooks directory exists
            os.makedirs('ebooks', exist_ok=True)
            
            # Generate PDF
            generator = EbookGenerator(self.config)
            puzzles = generator.puzzle_generator.generate_ebook_puzzles(sizes, count)
            puzzles = [p for p in puzzles if p['difficulty'] in difficulties]
            
            generator.generate_ebook(puzzles, output_file, title)
            
            # Upload to CDN Bunny
            if 'cdn_bunny' in self.config:
                uploader = CDNBunnyUploader(
                    storage_zone=self.config['cdn_bunny']['storage_zone'],
                    api_key=self.config['cdn_bunny']['api_key'],
                    storage_zone_name=self.config['cdn_bunny']['storage_zone_name'],
                    region=self.config['cdn_bunny']['region']
                )
                
                upload_result = uploader.upload_ebook(output_file, title)
                
                return {
                    'success': True,
                    'data': {
                        'local_file': output_file,
                        'upload_result': upload_result
                    },
                    'message': f'Ebook generated and uploaded: {title}'
                }
            else:
                return {
                    'success': True,
                    'data': {'local_file': output_file},
                    'message': f'Ebook generated: {title}'
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_status(self) -> Dict:
        """Get system status"""
        try:
            # Check disk space
            disk = subprocess.check_output(['df', '-h', '/']).decode()
            
            # Check memory
            memory = subprocess.check_output(['free', '-h']).decode()
            
            # Check uptime
            uptime = subprocess.check_output(['uptime']).decode()
            
            # Check service status
            try:
                cron_status = subprocess.check_output(['systemctl', 'is-active', 'cron']).decode().strip()
            except:
                cron_status = 'unknown'
            
            return {
                'success': True,
                'data': {
                    'disk': disk,
                    'memory': memory,
                    'uptime': uptime,
                    'cron_status': cron_status,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_logs(self, params: Dict) -> Dict:
        """Get recent logs"""
        try:
            lines = params.get('lines', 50)
            log_file = params.get('log_file', 'akari_generator_api.log')
            
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    log_lines = f.readlines()
                    recent_logs = log_lines[-lines:] if len(log_lines) > lines else log_lines
                
                return {
                    'success': True,
                    'data': {
                        'logs': recent_logs,
                        'total_lines': len(log_lines)
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'Log file not found: {log_file}'
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_config(self, params: Dict) -> Dict:
        """Update configuration"""
        try:
            # Update config file
            config_path = 'config/generator_config.json'
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    current_config = json.load(f)
                
                # Update with new params
                current_config.update(params)
                
                with open(config_path, 'w') as f:
                    json.dump(current_config, f, indent=2)
                
                # Reload config
                self.config = current_config
                
                return {
                    'success': True,
                    'message': 'Configuration updated'
                }
            else:
                return {
                    'success': False,
                    'error': 'Config file not found'
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def restart_service(self) -> Dict:
        """Restart puzzle generation service"""
        try:
            # Restart cron service
            subprocess.run(['sudo', 'systemctl', 'restart', 'cron'])
            
            return {
                'success': True,
                'message': 'Service restarted'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_ebooks(self) -> Dict:
        """Get list of uploaded ebooks"""
        try:
            if 'cdn_bunny' in self.config:
                uploader = CDNBunnyUploader(
                    storage_zone=self.config['cdn_bunny']['storage_zone'],
                    api_key=self.config['cdn_bunny']['api_key'],
                    storage_zone_name=self.config['cdn_bunny']['storage_zone_name'],
                    region=self.config['cdn_bunny']['region']
                )
                
                result = uploader.list_files("ebooks")
                return result
            else:
                # List local ebooks
                ebooks_dir = 'ebooks'
                if os.path.exists(ebooks_dir):
                    files = [f for f in os.listdir(ebooks_dir) if f.endswith('.pdf')]
                    return {
                        'success': True,
                        'files': [{'ObjectName': f} for f in files]
                    }
                else:
                    return {
                        'success': True,
                        'files': []
                    }
                    
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_stats(self) -> Dict:
        """Get generation statistics"""
        try:
            # Get puzzle stats from database via API
            generator = AkariPuzzleGeneratorAPI(
                self.config['api_url'],
                self.config['api_key']
            )
            
            # Get CDN stats
            cdn_stats = None
            if 'cdn_bunny' in self.config:
                uploader = CDNBunnyUploader(
                    storage_zone=self.config['cdn_bunny']['storage_zone'],
                    api_key=self.config['cdn_bunny']['api_key'],
                    storage_zone_name=self.config['cdn_bunny']['storage_zone_name'],
                    region=self.config['cdn_bunny']['region']
                )
                cdn_stats = uploader.get_upload_stats()
            
            return {
                'success': True,
                'data': {
                    'cdn_stats': cdn_stats,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def handle_status(self):
        """Handle GET /api/status"""
        if not self.validate_auth():
            self.send_json_response({'success': False, 'error': 'Unauthorized'}, 401)
            return
        
        result = self.get_status()
        self.send_json_response(result)
    
    def handle_logs(self):
        """Handle GET /api/logs"""
        if not self.validate_auth():
            self.send_json_response({'success': False, 'error': 'Unauthorized'}, 401)
            return
        
        # Parse query parameters
        parsed_url = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_url.query)
        
        result = self.get_logs({
            'lines': int(params.get('lines', [50])[0]),
            'log_file': params.get('log_file', ['akari_generator_api.log'])[0]
        })
        
        self.send_json_response(result)
    
    def handle_stats(self):
        """Handle GET /api/stats"""
        if not self.validate_auth():
            self.send_json_response({'success': False, 'error': 'Unauthorized'}, 401)
            return
        
        result = self.get_stats()
        self.send_json_response(result)

def main():
    print(f"🚀 Starting RPi API Server on {HOST}:{PORT}")
    print(f"🔑 API Key: {API_KEY}")
    
    # Create server
    server = HTTPServer((HOST, PORT), RPiAPIHandler)
    
    # Optional: Add SSL
    # context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # context.load_cert_chain('cert.pem', 'key.pem')
    # server.socket = context.wrap_socket(server.socket, server_side=True)
    
    try:
        print(f"✅ Server started. Listening on {HOST}:{PORT}")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
