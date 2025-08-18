#!/usr/bin/env python3
"""
Raspberry Pi Polling Client - Fixed Version
Sends status updates and checks for commands from the web server
"""

import requests
import json
import time
import logging
import os
from datetime import datetime
from typing import Dict, Optional
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rpi_polling.log'),
        logging.StreamHandler()
    ]
)

class RPIPollingClient:
    def __init__(self, web_server_url: str, api_key: str, poll_interval: int = 30):
        self.web_server_url = web_server_url
        self.api_key = api_key
        self.poll_interval = poll_interval
        self.session = requests.Session()
        
        # Headers for all requests
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        try:
            # Get uptime - try multiple possible paths
            uptime = None
            uptime_paths = ['/usr/bin/uptime', '/bin/uptime', 'uptime']
            for path in uptime_paths:
                try:
                    uptime = subprocess.check_output([path]).decode().strip()
                    break
                except (FileNotFoundError, subprocess.CalledProcessError):
                    continue
            
            if not uptime:
                uptime = "uptime command not found"
            
            # Get disk usage - try multiple possible paths
            disk = None
            df_paths = ['/bin/df', '/usr/bin/df', 'df']
            for path in df_paths:
                try:
                    disk = subprocess.check_output([path, '-h', '/']).decode().strip()
                    break
                except (FileNotFoundError, subprocess.CalledProcessError):
                    continue
            
            if not disk:
                disk = "df command not found"
            
            # Get memory usage - try multiple possible paths
            memory = None
            free_paths = ['/usr/bin/free', '/bin/free', 'free']
            for path in free_paths:
                try:
                    memory = subprocess.check_output([path, '-h']).decode().strip()
                    break
                except (FileNotFoundError, subprocess.CalledProcessError):
                    continue
            
            if not memory:
                memory = "free command not found"
            
            # Check service status - try multiple possible paths
            api_status = None
            systemctl_paths = ['/bin/systemctl', '/usr/bin/systemctl', 'systemctl']
            for path in systemctl_paths:
                try:
                    api_status = subprocess.check_output([path, 'is-active', 'akari-api.service']).decode().strip()
                    break
                except (FileNotFoundError, subprocess.CalledProcessError):
                    continue
            
            if not api_status:
                api_status = "systemctl command not found"
            
            # Get recent log entries
            log_file = 'logs/akari_generator_api.log'
            recent_logs = []
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    recent_logs = lines[-10:]  # Last 10 lines
            
            return {
                'timestamp': datetime.now().isoformat(),
                'hostname': os.uname().nodename,
                'uptime': uptime,
                'disk_usage': disk,
                'memory_usage': memory,
                'api_service_status': api_status,
                'recent_logs': recent_logs,
                'online': True
            }
        except Exception as e:
            logging.error(f"Error getting system status: {str(e)}")
            return {
                'timestamp': datetime.now().isoformat(),
                'hostname': os.uname().nodename,
                'online': True,
                'error': str(e)
            }
    
    def send_status_update(self) -> bool:
        """Send status update to web server"""
        try:
            status = self.get_system_status()
            
            response = self.session.post(
                f"{self.web_server_url}/api/rpi_status.php",
                json={'status': status},
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                logging.info("Status update sent successfully")
                return True
            else:
                logging.error(f"Status update failed: HTTP {response.status_code}")
                logging.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Error sending status update: {str(e)}")
            return False
    
    def check_for_commands(self) -> Optional[Dict]:
        """Check for commands from web server"""
        try:
            hostname = os.uname().nodename
            # Use params to avoid subtle URL formatting/caching issues and improve observability
            logging.info(f"Checking for commands (hostname={hostname})")
            response = self.session.get(
                f"{self.web_server_url}/api/rpi_commands.php",
                headers=self.headers,
                params={"hostname": hostname, "_t": int(time.time())},
                timeout=30
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except Exception as json_error:
                    logging.error(f"Failed to parse command response JSON: {str(json_error)} | Body: {response.text[:500]}")
                    return None

                has_commands = bool(data.get('data', {}).get('has_commands'))
                if has_commands:
                    logging.info(f"Received command: {data.get('data', {}).get('command')}")
                    return data.get('data')
                else:
                    logging.info("No commands available")
                    return None
            else:
                logging.error(f"Command check failed: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"Error checking for commands: {str(e)}")
            return None
    
    def execute_command(self, command: Dict) -> Dict:
        """Execute a command and return results"""
        try:
            action = command.get('action')
            params = command.get('params', {})
            
            if action == 'generate_puzzles':
                return self.generate_puzzles(params)
            elif action == 'generate_ebook':
                return self.generate_ebook(params)
            elif action == 'get_logs':
                return self.get_logs(params)
            elif action == 'restart_service':
                return self.restart_service()
            elif action == 'cleanup_stuck_commands':
                return self.cleanup_stuck_commands(params)
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}
                
        except Exception as e:
            logging.error(f"Error executing command: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def generate_puzzles(self, params: Dict) -> Dict:
        """Generate puzzles"""
        try:
            from akari_generator_api import AkariPuzzleGeneratorAPI
            
            # Use the same API key as the polling client
            generator = AkariPuzzleGeneratorAPI(
                "https://shrinepuzzle.com/api/puzzle_receiver.php",
                "shrine_admin_key_2024"  # Use the same key as the polling client
            )
            
            sizes = params.get('sizes', [6, 8])
            difficulties = params.get('difficulties', ['easy', 'medium'])
            count = params.get('count', 5)
            mode = params.get('mode', 'premium')
            
            result = generator.generate_batch(
                sizes=sizes,
                difficulties=difficulties,
                count_per_size=count,
                mode=mode
            )
            
            return {
                'success': True,
                'action': 'generate_puzzles',
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_ebook(self, params: Dict) -> Dict:
        """Generate ebook"""
        try:
            from ebook_generator import EbookGenerator
            
            # Load config
            with open('config/generator_config.json', 'r') as f:
                config = json.load(f)
            
            generator = EbookGenerator(config)
            
            title = params.get('title', 'Akari Puzzle Collection')
            sizes = params.get('sizes', [6, 8])
            difficulties = params.get('difficulties', ['easy', 'medium'])
            count = params.get('count', 20)
            
            # Generate puzzles first
            from akari_generator_api import AkariPuzzleGeneratorAPI
            puzzle_gen = AkariPuzzleGeneratorAPI(config['api_url'], config['api_key'])
            puzzles = puzzle_gen.generate_ebook_puzzles(sizes, count)
            
            # Generate PDF
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"akari_ebook_{timestamp}.pdf"
            filepath = f"ebooks/{filename}"
            
            generator.generate_ebook(puzzles, filepath, title)
            
            # Upload to CDN
            from cdn_bunny_uploader import CDNBunnyUploader
            cdn_config = config['cdn_bunny']
            uploader = CDNBunnyUploader(
                cdn_config['storage_zone'],
                cdn_config['password'],
                cdn_config['storage_zone_name'],
                cdn_config['region']
            )
            
            upload_result = uploader.upload_ebook(filepath, title)
            
            return {
                'success': True,
                'action': 'generate_ebook',
                'file_path': filepath,
                'cdn_url': upload_result.get('file_url'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_logs(self, params: Dict) -> Dict:
        """Get system logs"""
        try:
            log_file = params.get('log_file', 'logs/akari_generator_api.log')
            lines = params.get('lines', 50)
            
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    log_lines = f.readlines()
                    recent_logs = log_lines[-lines:] if len(log_lines) > lines else log_lines
                
                return {
                    'success': True,
                    'action': 'get_logs',
                    'log_file': log_file,
                    'logs': recent_logs,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'success': False, 'error': f'Log file not found: {log_file}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def restart_service(self) -> Dict:
        """Restart the API service"""
        try:
            # Try multiple systemctl paths
            systemctl_paths = ['/bin/systemctl', '/usr/bin/systemctl', 'systemctl']
            for path in systemctl_paths:
                try:
                    subprocess.run([path, 'restart', 'akari-api.service'], check=True)
                    return {
                        'success': True,
                        'action': 'restart_service',
                        'message': 'Service restarted successfully',
                        'timestamp': datetime.now().isoformat()
                    }
                except (FileNotFoundError, subprocess.CalledProcessError):
                    continue
            
            return {'success': False, 'error': 'systemctl command not found'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def cleanup_stuck_commands(self, params: Dict) -> Dict:
        """Clean up stuck commands by calling the web server API"""
        try:
            older_than_minutes = params.get('older_than_minutes', 30)
            
            response = self.session.post(
                f"{self.web_server_url}/api/cleanup_stuck_commands.php",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'action': 'cleanup_stuck_commands',
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f'Cleanup failed: HTTP {response.status_code}',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_command_result(self, command_id: str, result: Dict) -> bool:
        """Send command execution result back to web server"""
        try:
            response = self.session.post(
                f"{self.web_server_url}/api/rpi_result.php",
                json={
                    'command_id': command_id,
                    'result': result
                },
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                logging.info("Command result sent successfully")
                return True
            else:
                logging.error(f"Failed to send command result: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"Error sending command result: {str(e)}")
            return False
    
    def run_polling_loop(self):
        """Main polling loop"""
        logging.info("Starting RPi polling client...")
        
        while True:
            try:
                # Send status update
                self.send_status_update()
                
                # Check for commands
                logging.info("Polling for commands...")
                command_data = self.check_for_commands()
                
                if command_data:
                    command = command_data.get('command')
                    command_id = command_data.get('command_id')
                    
                    # Execute command
                    logging.info(f"Executing command_id={command_id} action={command.get('action')}")
                    result = self.execute_command(command)
                    
                    # Send result back
                    sent_ok = self.send_command_result(command_id, result)
                    if not sent_ok:
                        logging.error(f"Failed to send result for command_id={command_id}")
                    else:
                        logging.info(f"Result sent for command_id={command_id}")
                
                # Wait before next poll
                time.sleep(self.poll_interval)
                
            except KeyboardInterrupt:
                logging.info("Polling client stopped by user")
                break
            except Exception as e:
                logging.error(f"Error in polling loop: {str(e)}")
                time.sleep(self.poll_interval)

def main():
    # Load config
    with open('config/generator_config.json', 'r') as f:
        config = json.load(f)
    
    # Create polling client
    client = RPIPollingClient(
        web_server_url="https://shrinepuzzle.com",
        api_key="shrine_admin_key_2024",
        poll_interval=30  # Poll every 30 seconds
    )
    
    # Start polling
    client.run_polling_loop()

if __name__ == "__main__":
    main()
