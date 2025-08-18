#!/usr/bin/env python3
"""
Fix CDN Bunny Configuration and Test
"""

import json
import os

def fix_cdn_config():
    """Fix the CDN Bunny configuration"""
    
    # Correct configuration using password instead of API key
    correct_config = {
        "api_url": "https://shrinepuzzle.com/api/puzzle_receiver.php",
        "api_key": "shrine_puzzle_api_key_2024",
        "default_sizes": [6, 8, 10, 12],
        "default_difficulties": ["easy", "medium", "hard", "expert"],
        "max_puzzles_per_batch": 50,
        "retry_attempts": 3,
        "retry_delay": 5,
        "cdn_bunny": {
            "storage_zone": "shrinepuzzle",
            "password": "YOUR_CDN_PASSWORD_HERE",  # This is the password from FTP & API access
            "storage_zone_name": "shrinepuzzle",
            "region": "la"
        }
    }
    
    # Update the config file
    with open('config/generator_config.json', 'w') as f:
        json.dump(correct_config, f, indent=4)
    
    print("✅ CDN Bunny configuration updated!")
    print("Storage Zone: shrinepuzzle")
    print("Region: la")
    print("Password: (from FTP & API access section)")
    print("Hostname: la.storage.bunnycdn.com")
    print("CDN URL: https://shrinepuzzle.b-cdn.net")

def test_cdn_connection():
    """Test CDN Bunny connection with corrected config"""
    
    try:
        from cdn_bunny_uploader import CDNBunnyUploader
        
        # Load config
        with open('config/generator_config.json', 'r') as f:
            config = json.load(f)
        
        cdn_config = config['cdn_bunny']
        
        print("🔧 Testing CDN Bunny connection...")
        print(f"Storage Zone: {cdn_config['storage_zone']}")
        print(f"Region: {cdn_config['region']}")
        
        uploader = CDNBunnyUploader(
            storage_zone=cdn_config['storage_zone'],
            password=cdn_config['password'],  # Using password instead of api_key
            storage_zone_name=cdn_config['storage_zone_name'],
            region=cdn_config['region']
        )
        
        # Test listing files from root directory
        print("📁 Testing file listing...")
        result = uploader.list_files("")
        
        if result['success']:
            print("✅ CDN Bunny connection successful!")
            print(f"Found {len(result['files'])} files/directories")
            
            # Show first few items
            for i, item in enumerate(result['files'][:5]):
                print(f"  - {item.get('ObjectName', 'Unknown')}")
            
            if len(result['files']) > 5:
                print(f"  ... and {len(result['files']) - 5} more")
                
            return True
        else:
            print(f"❌ CDN Bunny test failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing CDN Bunny: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing CDN Bunny Configuration...")
    fix_cdn_config()
    print()
    print("📝 Next Steps:")
    print("1. Copy your password from the FTP & API access section")
    print("2. Edit config/generator_config.json")
    print("3. Replace 'YOUR_CDN_PASSWORD_HERE' with your actual password")
    print("4. Run: python3 fix_cdn_bunny.py")
    print()
    test_cdn_connection()
