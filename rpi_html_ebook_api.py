#!/usr/bin/env python3
"""
Raspberry Pi 5 HTML Ebook API Server
Receives commands from dashboard and generates HTML ebooks with CDN Bunny integration
"""

import json
import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from enhanced_html_ebook_generator import EnhancedHTMLEbookGenerator

app = Flask(__name__)
CORS(app)

class RPiHTMLEbookAPI:
    def __init__(self):
        self.api_key = 'shrine_puzzle_api_key_2024'
        self.config = {
            'api_url': 'https://shrinepuzzle.com/api/puzzle_receiver.php',
            'api_key': 'shrine_puzzle_api_key_2024',
            'output_dir': './generated_ebooks',
            'log_file': './html_ebook_generation.log',
            'cdn_bunny': {
                'storage_zone': 'shrinepuzzle-ebooks',
                'api_key': 'your_cdn_bunny_api_key_here',
                'pull_zone': 'https://shrinepuzzle-ebooks.b-cdn.net'
            }
        }
        
        self.generator = EnhancedHTMLEbookGenerator(self.config)
        self.active_jobs = {}
        
        # Ensure output directory exists
        os.makedirs(self.config['output_dir'], exist_ok=True)
        
    def log_message(self, message: str, job_id: str = None):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        job_prefix = f"[{job_id}] " if job_id else ""
        log_entry = f"[{timestamp}] {job_prefix}{message}"
        print(log_entry)
        
        # Write to log file
        with open(self.config['log_file'], 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    
    def verify_api_key(self, request):
        """Verify API key from request"""
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        return api_key == self.api_key
    
    def generate_html_ebook(self, job_id: str, params: dict):
        """Generate HTML ebook in background thread"""
        try:
            self.log_message(f"Starting HTML ebook generation", job_id)
            self.active_jobs[job_id] = {'status': 'generating', 'progress': 10}
            
            # Extract parameters
            sizes = params.get('sizes', [6, 8, 10])
            difficulties = params.get('difficulties', ['easy', 'medium', 'hard'])
            count = params.get('count', 10)
            title = params.get('title', f'Akari Collection - {datetime.now().strftime("%Y-%m-%d")}')
            
            self.log_message(f"Parameters: sizes={sizes}, difficulties={difficulties}, count={count}", job_id)
            
            # Generate puzzles
            self.active_jobs[job_id]['progress'] = 30
            puzzles = self.generator.puzzle_generator.generate_ebook_puzzles(sizes, count)
            
            # Filter by difficulties
            puzzles = [p for p in puzzles if p['difficulty'] in difficulties]
            
            if not puzzles:
                raise Exception("No puzzles generated with specified parameters")
            
            self.log_message(f"Generated {len(puzzles)} puzzles", job_id)
            
            # Create output filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')
            output_file = os.path.join(self.config['output_dir'], f"akari_ebook_{job_id}_{safe_title}.html")
            
            # Generate HTML ebook
            self.active_jobs[job_id]['progress'] = 60
            self.generator.generate_ebook(
                puzzles, 
                output_file, 
                title,
                auto_open=False,
                include_print_button=True
            )
            
            self.log_message(f"HTML ebook generated: {output_file}", job_id)
            
            # Update job status
            self.active_jobs[job_id] = {
                'status': 'completed',
                'progress': 90,
                'output_file': output_file,
                'puzzle_count': len(puzzles),
                'completed_at': datetime.now().isoformat()
            }
            
            # Upload to CDN Bunny
            self.active_jobs[job_id]['progress'] = 95
            cdn_result = self.upload_to_cdn_bunny(output_file, title, job_id)
            
            if cdn_result['success']:
                self.active_jobs[job_id].update({
                    'status': 'uploaded',
                    'progress': 100,
                    'cdn_url': cdn_result['cdn_url'],
                    'uploaded_at': datetime.now().isoformat()
                })
                self.log_message(f"Uploaded to CDN: {cdn_result['cdn_url']}", job_id)
            else:
                self.log_message(f"CDN upload failed: {cdn_result['error']}", job_id)
            
            # Notify main server of completion
            self.notify_completion(job_id)
            
        except Exception as e:
            self.log_message(f"Generation failed: {str(e)}", job_id)
            self.active_jobs[job_id] = {
                'status': 'failed',
                'progress': 0,
                'error': str(e),
                'failed_at': datetime.now().isoformat()
            }
            self.notify_completion(job_id)
    
    def upload_to_cdn_bunny(self, file_path: str, title: str, job_id: str):
        """Upload file to CDN Bunny"""
        try:
            self.log_message("Starting CDN Bunny upload", job_id)
            
            filename = Path(file_path).name
            cdn_filename = f'akari_ebook_{job_id}_{filename}'
            
            url = f"https://storage.bunnycdn.com/{self.config['cdn_bunny']['storage_zone']}/{cdn_filename}"
            
            with open(file_path, 'rb') as f:
                headers = {
                    'AccessKey': self.config['cdn_bunny']['api_key'],
                    'Content-Type': 'text/html'
                }
                
                response = requests.put(url, data=f, headers=headers, timeout=60)
                
                if response.status_code == 201:
                    cdn_url = f"{self.config['cdn_bunny']['pull_zone']}/{cdn_filename}"
                    self.log_message(f"CDN upload successful: {cdn_url}", job_id)
                    return {
                        'success': True,
                        'cdn_url': cdn_url,
                        'filename': cdn_filename
                    }
                else:
                    error_msg = f"Upload failed: HTTP {response.status_code}"
                    self.log_message(f"CDN upload failed: {error_msg}", job_id)
                    return {
                        'success': False,
                        'error': error_msg
                    }
                    
        except Exception as e:
            error_msg = f"CDN upload error: {str(e)}"
            self.log_message(error_msg, job_id)
            return {
                'success': False,
                'error': error_msg
            }
    
    def notify_completion(self, job_id: str):
        """Notify main server of job completion"""
        try:
            job_info = self.active_jobs.get(job_id, {})
            
            notification_data = {
                'job_id': job_id,
                'status': job_info.get('status', 'unknown'),
                'progress': job_info.get('progress', 0),
                'output_file': job_info.get('output_file'),
                'cdn_url': job_info.get('cdn_url'),
                'error': job_info.get('error'),
                'completed_at': job_info.get('completed_at') or job_info.get('uploaded_at') or job_info.get('failed_at')
            }
            
            # Send notification to main server
            main_server_url = 'https://shrinepuzzle.com/api/html_ebook_controller.php?action=notify'
            
            response = requests.post(
                main_server_url,
                json=notification_data,
                headers={
                    'Content-Type': 'application/json',
                    'X-API-Key': self.api_key
                },
                timeout=30
            )
            
            if response.status_code == 200:
                self.log_message("Successfully notified main server", job_id)
            else:
                self.log_message(f"Failed to notify main server: HTTP {response.status_code}", job_id)
                
        except Exception as e:
            self.log_message(f"Error notifying main server: {str(e)}", job_id)

# Initialize API
api = RPiHTMLEbookAPI()

@app.route('/api/html_ebook_generator', methods=['POST'])
def handle_ebook_generation():
    """Handle HTML ebook generation requests"""
    if not api.verify_api_key(request):
        return jsonify({'success': False, 'error': 'Invalid API key'}), 401
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        action = data.get('action')
        job_id = data.get('job_id')
        params = data.get('params', {})
        
        if action != 'generate_html_ebook':
            return jsonify({'success': False, 'error': 'Invalid action'}), 400
        
        if not job_id:
            return jsonify({'success': False, 'error': 'Missing job_id'}), 400
        
        # Check if job is already running
        if job_id in api.active_jobs:
            return jsonify({'success': False, 'error': 'Job already running'}), 409
        
        # Start generation in background thread
        thread = threading.Thread(
            target=api.generate_html_ebook,
            args=(job_id, params)
        )
        thread.daemon = True
        thread.start()
        
        api.log_message(f"Job queued for generation", job_id)
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'status': 'queued',
            'message': 'HTML ebook generation started'
        })
        
    except Exception as e:
        api.log_message(f"API error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/html_ebook_status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get status of a specific job"""
    if not api.verify_api_key(request):
        return jsonify({'success': False, 'error': 'Invalid API key'}), 401
    
    job_info = api.active_jobs.get(job_id, {})
    
    if not job_info:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    
    return jsonify({
        'success': True,
        'job_id': job_id,
        'data': job_info
    })

@app.route('/api/html_ebook_list', methods=['GET'])
def list_jobs():
    """List all active jobs"""
    if not api.verify_api_key(request):
        return jsonify({'success': False, 'error': 'Invalid API key'}), 401
    
    jobs = []
    for job_id, job_info in api.active_jobs.items():
        jobs.append({
            'job_id': job_id,
            **job_info
        })
    
    return jsonify({
        'success': True,
        'jobs': jobs,
        'total': len(jobs)
    })

@app.route('/api/html_ebook_download/<job_id>', methods=['GET'])
def download_ebook(job_id):
    """Download generated ebook"""
    if not api.verify_api_key(request):
        return jsonify({'success': False, 'error': 'Invalid API key'}), 401
    
    job_info = api.active_jobs.get(job_id, {})
    
    if not job_info:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    
    if job_info.get('status') not in ['completed', 'uploaded']:
        return jsonify({'success': False, 'error': 'Ebook not ready for download'}), 400
    
    output_file = job_info.get('output_file')
    cdn_url = job_info.get('cdn_url')
    
    if cdn_url:
        return jsonify({
            'success': True,
            'download_url': cdn_url,
            'filename': Path(output_file).name if output_file else 'akari_ebook.html'
        })
    elif output_file and os.path.exists(output_file):
        # Serve file directly if CDN upload failed
        return jsonify({
            'success': True,
            'download_url': f"/api/html_ebook_file/{job_id}",
            'filename': Path(output_file).name
        })
    else:
        return jsonify({'success': False, 'error': 'No download available'}), 404

@app.route('/api/html_ebook_file/<job_id>', methods=['GET'])
def serve_ebook_file(job_id):
    """Serve ebook file directly"""
    if not api.verify_api_key(request):
        return jsonify({'success': False, 'error': 'Invalid API key'}), 401
    
    job_info = api.active_jobs.get(job_id, {})
    
    if not job_info:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    
    output_file = job_info.get('output_file')
    
    if not output_file or not os.path.exists(output_file):
        return jsonify({'success': False, 'error': 'File not found'}), 404
    
    # Serve file with proper headers
    from flask import send_file
    return send_file(
        output_file,
        as_attachment=True,
        download_name=Path(output_file).name,
        mimetype='text/html'
    )

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_jobs': len(api.active_jobs)
    })

@app.route('/api/cleanup', methods=['POST'])
def cleanup_old_files():
    """Clean up old generated files"""
    if not api.verify_api_key(request):
        return jsonify({'success': False, 'error': 'Invalid API key'}), 401
    
    try:
        # Clean up files older than 7 days
        cutoff_time = time.time() - (7 * 24 * 60 * 60)
        deleted_count = 0
        
        for file_path in Path(api.config['output_dir']).glob("*.html"):
            if file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                deleted_count += 1
                api.log_message(f"Deleted old file: {file_path.name}")
        
        # Clean up completed jobs older than 24 hours
        current_time = datetime.now()
        jobs_to_remove = []
        
        for job_id, job_info in api.active_jobs.items():
            if job_info.get('status') in ['completed', 'uploaded', 'failed']:
                completed_at = job_info.get('completed_at') or job_info.get('uploaded_at') or job_info.get('failed_at')
                if completed_at:
                    try:
                        completed_time = datetime.fromisoformat(completed_at)
                        if (current_time - completed_time).total_seconds() > 24 * 60 * 60:
                            jobs_to_remove.append(job_id)
                    except:
                        pass
        
        for job_id in jobs_to_remove:
            del api.active_jobs[job_id]
            api.log_message(f"Removed old job: {job_id}")
        
        return jsonify({
            'success': True,
            'deleted_files': deleted_count,
            'removed_jobs': len(jobs_to_remove)
        })
        
    except Exception as e:
        api.log_message(f"Cleanup error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get('PORT', 8080))
    api.log_message(f"Starting RPi HTML Ebook API server on port {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )
