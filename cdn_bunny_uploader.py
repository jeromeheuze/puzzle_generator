#!/usr/bin/env python3
"""
CDN Bunny Uploader for Akari Puzzle Ebooks
Automatically uploads generated PDFs to CDN Bunny for distribution
"""

import os
import requests
import json
import logging
from datetime import datetime
from typing import Dict, Optional
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cdn_bunny_uploader.log'),
        logging.StreamHandler()
    ]
)

class CDNBunnyUploader:
    def __init__(self, storage_zone: str, api_key: str, storage_zone_name: str, region: str = 'de'):
        self.storage_zone = storage_zone
        self.api_key = api_key
        self.storage_zone_name = storage_zone_name
        self.region = region
        self.base_url = f"https://la.storage.bunnycdn.com/{storage_zone_name}"
        self.pull_zone_url = f"https://api.bunny.net/pullzone"
        
        # Headers for API requests
        self.headers = {
            'AccessKey': api_key,
            'Content-Type': 'application/json'
        }
        
        self.upload_headers = {
            'AccessKey': api_key
        }
    
    def upload_file(self, local_path: str, remote_path: str) -> Dict:
        """Upload a file to CDN Bunny"""
        try:
            if not os.path.exists(local_path):
                return {
                    'success': False,
                    'error': f'File not found: {local_path}'
                }
            
            # Read file content
            with open(local_path, 'rb') as f:
                file_content = f.read()
            
            # Upload URL
            upload_url = f"{self.base_url}/{remote_path}"
            
            # Upload file
            response = requests.put(
                upload_url,
                data=file_content,
                headers=self.upload_headers,
                timeout=60
            )
            
            if response.status_code in [200, 201]:
                # Get file info
                file_info = self.get_file_info(remote_path)
                
                # Generate public URL
                public_url = f"https://{self.storage_zone_name}.b-cdn.net/{remote_path}"
                
                return {
                    'success': True,
                    'file_url': public_url,
                    'file_info': file_info,
                    'message': f'File uploaded successfully: {remote_path}'
                }
            else:
                return {
                    'success': False,
                    'error': f'Upload failed: HTTP {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            logging.error(f"Upload error: {str(e)}")
            return {
                'success': False,
                'error': f'Upload exception: {str(e)}'
            }
    
    def get_file_info(self, remote_path: str) -> Optional[Dict]:
        """Get information about an uploaded file"""
        try:
            url = f"{self.base_url}/{remote_path}"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logging.warning(f"Could not get file info: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"Error getting file info: {str(e)}")
            return None
    
    def list_files(self, path: str = "") -> Dict:
        """List files in a directory"""
        try:
            url = f"{self.base_url}/{path}"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'files': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'List failed: HTTP {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'List exception: {str(e)}'
            }
    
    def delete_file(self, remote_path: str) -> Dict:
        """Delete a file from CDN Bunny"""
        try:
            url = f"{self.base_url}/{remote_path}"
            response = requests.delete(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': f'File deleted: {remote_path}'
                }
            else:
                return {
                    'success': False,
                    'error': f'Delete failed: HTTP {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Delete exception: {str(e)}'
            }
    
    def upload_ebook(self, pdf_path: str, title: str = None) -> Dict:
        """Upload an ebook PDF with proper naming and metadata"""
        try:
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if title:
                # Clean title for filename
                clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                clean_title = clean_title.replace(' ', '_').lower()
                filename = f"akari_ebook_{clean_title}_{timestamp}.pdf"
            else:
                filename = f"akari_ebook_{timestamp}.pdf"
            
            # Remote path
            remote_path = f"ebooks/{filename}"
            
            # Upload file
            result = self.upload_file(pdf_path, remote_path)
            
            if result['success']:
                # Add metadata
                metadata = {
                    'title': title or 'Akari Puzzle Collection',
                    'uploaded_at': datetime.now().isoformat(),
                    'file_size': os.path.getsize(pdf_path),
                    'cdn_url': result['file_url']
                }
                
                # Save metadata
                metadata_path = f"ebooks/{filename}.json"
                metadata_result = self.upload_metadata(metadata, metadata_path)
                
                result['metadata'] = metadata
                result['metadata_uploaded'] = metadata_result['success']
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ebook upload exception: {str(e)}'
            }
    
    def upload_metadata(self, metadata: Dict, remote_path: str) -> Dict:
        """Upload metadata JSON file"""
        try:
            metadata_json = json.dumps(metadata, indent=2)
            
            url = f"{self.base_url}/{remote_path}"
            response = requests.put(
                url,
                data=metadata_json.encode('utf-8'),
                headers=self.upload_headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'message': f'Metadata uploaded: {remote_path}'
                }
            else:
                return {
                    'success': False,
                    'error': f'Metadata upload failed: HTTP {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Metadata upload exception: {str(e)}'
            }
    
    def get_upload_stats(self) -> Dict:
        """Get upload statistics"""
        try:
            # List all ebooks
            ebooks_result = self.list_files("ebooks")
            
            if ebooks_result['success']:
                files = ebooks_result['files']
                pdf_files = [f for f in files if f.get('ObjectName', '').endswith('.pdf')]
                
                total_size = sum(f.get('Length', 0) for f in pdf_files)
                
                return {
                    'success': True,
                    'total_ebooks': len(pdf_files),
                    'total_size_bytes': total_size,
                    'total_size_mb': round(total_size / (1024 * 1024), 2),
                    'recent_uploads': sorted(pdf_files, key=lambda x: x.get('LastChanged', ''), reverse=True)[:5]
                }
            else:
                return ebooks_result
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Stats exception: {str(e)}'
            }

def main():
    parser = argparse.ArgumentParser(description='Upload PDF ebooks to CDN Bunny')
    parser.add_argument('--pdf-path', required=True, help='Path to PDF file to upload')
    parser.add_argument('--title', help='Ebook title for naming')
    parser.add_argument('--storage-zone', required=True, help='CDN Bunny storage zone')
    parser.add_argument('--api-key', required=True, help='CDN Bunny API key')
    parser.add_argument('--storage-zone-name', required=True, help='CDN Bunny storage zone name')
    parser.add_argument('--region', default='de', help='CDN Bunny region (default: de)')
    parser.add_argument('--list', action='store_true', help='List uploaded files')
    parser.add_argument('--stats', action='store_true', help='Show upload statistics')
    
    args = parser.parse_args()
    
    uploader = CDNBunnyUploader(
        storage_zone=args.storage_zone,
        api_key=args.api_key,
        storage_zone_name=args.storage_zone_name,
        region=args.region
    )
    
    if args.list:
        # List files
        result = uploader.list_files("ebooks")
        if result['success']:
            print("📚 Uploaded ebooks:")
            for file in result['files']:
                print(f"  - {file.get('ObjectName', 'Unknown')} ({file.get('Length', 0)} bytes)")
        else:
            print(f"❌ Error listing files: {result['error']}")
    
    elif args.stats:
        # Show statistics
        stats = uploader.get_upload_stats()
        if stats['success']:
            print("📊 Upload Statistics:")
            print(f"  Total ebooks: {stats['total_ebooks']}")
            print(f"  Total size: {stats['total_size_mb']} MB")
            print("  Recent uploads:")
            for upload in stats['recent_uploads']:
                print(f"    - {upload.get('ObjectName', 'Unknown')}")
        else:
            print(f"❌ Error getting stats: {stats['error']}")
    
    else:
        # Upload file
        print(f"📤 Uploading: {args.pdf_path}")
        result = uploader.upload_ebook(args.pdf_path, args.title)
        
        if result['success']:
            print(f"✅ Upload successful!")
            print(f"   URL: {result['file_url']}")
            print(f"   Size: {result['metadata']['file_size']} bytes")
            print(f"   Title: {result['metadata']['title']}")
        else:
            print(f"❌ Upload failed: {result['error']}")

if __name__ == "__main__":
    main()
