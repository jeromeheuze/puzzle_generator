# 🎯 Akari Puzzle Generator API for Raspberry Pi 5

A secure, scalable puzzle generation system that creates solvable Akari puzzles and sends them to your database via API.

## 🚀 Features

- **API-based**: Secure HTTP API communication instead of direct database access
- **Multi-size puzzles**: 6x6, 8x8, 10x10, 12x12 boards
- **Difficulty levels**: Easy, Medium, Hard, Expert
- **Batch processing**: Send multiple puzzles in a single API call
- **Ebook generation**: Create printable PDF collections
- **Automatic scheduling**: Daily generation via cron
- **Quality control**: Solvability validation and duplicate prevention
- **Premium content**: Larger, harder puzzles for subscribers

## 🔒 Security Benefits

- **No database credentials** on Raspberry Pi
- **API key authentication** for secure access
- **Input validation** on server side
- **Rate limiting** and request size limits
- **CORS support** for web-based access

## 📋 Requirements

- Raspberry Pi 5 (or any Linux system)
- Python 3.8+
- Internet connection for API communication
- API access to your ShrinePuzzle server

## 🛠️ Setup Instructions

### 1. Server Setup (Your Web Server)

First, ensure the API endpoint is deployed:

```bash
# Copy API files to your server
api/puzzle_receiver.php → /path/to/your/website/api/
```

### 2. Raspberry Pi Setup

```bash
# Clone the repository to your Raspberry Pi
git clone <your-repo> puzzle_generator
cd puzzle_generator

# Make setup script executable
chmod +x setup_raspberry_pi_api.sh

# Run the automated setup
./setup_raspberry_pi_api.sh
```

### 3. Configuration

Edit `config/generator_config.json`:

```json
{
    "api_url": "https://shrinepuzzle.com/api/puzzle_receiver.php",
    "api_key": "shrine_puzzle_api_key_2024",
    "default_sizes": [6, 8, 10, 12],
    "default_difficulties": ["easy", "medium", "hard", "expert"],
    "max_puzzles_per_batch": 50,
    "retry_attempts": 3,
    "retry_delay": 5
}
```

## 🧪 Testing

### Test API Connection

```bash
# Test the API connection
python3 test_api_connection.py
```

### Test from Web Browser

Visit: `https://shrinepuzzle.com/api/test_puzzle_api.php`

## 🎮 Usage Examples

### Generate Premium Puzzles

```bash
# Generate 10 puzzles of each size and difficulty for premium users
python3 akari_generator_api.py \
  --mode premium \
  --sizes 6 8 10 12 \
  --difficulties easy medium hard expert \
  --count 10
```

### Generate Daily Puzzles

```bash
# Generate 7 daily puzzles (one week)
python3 akari_generator_api.py \
  --mode daily \
  --sizes 6 8 \
  --difficulties medium \
  --count 7
```

### Generate Ebook Collection

```bash
# Create a PDF ebook with 20 puzzles of each size
python3 ebook_generator.py \
  --sizes 6 8 10 12 \
  --difficulties easy medium hard \
  --count 20 \
  --output "Akari_Master_Collection.pdf" \
  --title "Akari Master Collection"
```

### Quick Test

```bash
# Generate a small test batch
python3 akari_generator_api.py \
  --mode premium \
  --sizes 6 8 \
  --difficulties easy medium \
  --count 2
```

## 🔧 API Configuration

### API Endpoint

- **URL**: `https://shrinepuzzle.com/api/puzzle_receiver.php`
- **Method**: POST
- **Authentication**: Bearer token or X-API-Key header

### Request Format

```json
{
    "puzzles": [
        {
            "layout": [[0, 0, 0], [0, "X", 0], [0, 0, 0]],
            "seed": "unique_seed_123",
            "size": 6,
            "difficulty": "medium",
            "mode": "premium",
            "date": "2024-01-15"
        }
    ]
}
```

### Response Format

```json
{
    "success": true,
    "message": "Processed 2 puzzles. Saved: 2, Failed: 0",
    "data": {
        "total_received": 2,
        "saved": 2,
        "failed": 0,
        "errors": [],
        "saved_puzzles": [
            {
                "seed": "unique_seed_123",
                "size": 6,
                "difficulty": "medium",
                "mode": "premium",
                "puzzle_id": 123
            }
        ]
    },
    "timestamp": "2024-01-15 10:30:00"
}
```

## ⏰ Automated Generation

### Daily Cron Job

The setup script configures a cron job that runs daily at 2 AM:

```bash
# View current cron jobs
crontab -l

# Edit cron jobs manually
crontab -e
```

### Custom Cron Schedule

```bash
# Generate premium puzzles every 6 hours
0 */6 * * * cd /path/to/puzzle_generator && source akari_env/bin/activate && python3 akari_generator_api.py --mode premium --sizes 6 8 10 12 --difficulties easy medium hard --count 5 >> logs/cron.log 2>&1

# Generate ebooks weekly
0 3 * * 0 cd /path/to/puzzle_generator && source akari_env/bin/activate && python3 ebook_generator.py --sizes 6 8 10 12 --count 15 --output "weekly_collection.pdf" >> logs/ebook_cron.log 2>&1
```

## 📊 Monitoring

### View Logs

```bash
# Real-time log monitoring
tail -f logs/akari_generator_api.log

# View cron job logs
tail -f logs/cron.log

# Check recent activity
ls -la logs/
```

### API Status

```bash
# Test API health
curl -X POST https://shrinepuzzle.com/api/puzzle_receiver.php \
  -H "Authorization: Bearer shrine_puzzle_api_key_2024" \
  -H "Content-Type: application/json" \
  -d '{"puzzles":[]}'
```

## 🔧 Troubleshooting

### Common Issues

1. **API Connection Failed**
   ```bash
   # Test network connectivity
   ping shrinepuzzle.com
   
   # Test API endpoint
   python3 test_api_connection.py
   
   # Check API key
   cat config/generator_config.json
   ```

2. **Authentication Error**
   ```bash
   # Verify API key in config
   cat config/generator_config.json | grep api_key
   
   # Test with curl
   curl -H "Authorization: Bearer 6d0c408d-5898-42d8-aaeb4a3965b1-c463-4e4c" https://shrinepuzzle.com/api/puzzle_receiver.php
   ```

3. **Rate Limiting**
   ```bash
   # Reduce batch size
   python3 akari_generator_api.py --count 5
   
   # Add delays between requests
   # Edit the generator to add sleep() calls
   ```

4. **Network Issues**
   ```bash
   # Check internet connection
   curl -I https://shrinepuzzle.com
   
   # Test DNS resolution
   nslookup shrinepuzzle.com
   ```

## 📈 Business Integration

### Premium Content Strategy

1. **Daily Generation**: 6x6 and 8x8 medium puzzles
2. **Premium Generation**: 10x10 and 12x12 hard/expert puzzles
3. **Ebook Generation**: Weekly collections for sale

### Revenue Streams

- **Premium Subscriptions**: Access to larger puzzles
- **Ebook Sales**: Printable collections
- **API Access**: For developers (future)
- **Educational Licenses**: Schools and institutions

### Content Schedule

```bash
# Daily at 2 AM - Premium puzzles
0 2 * * * /path/to/generate_premium.sh

# Weekly on Sunday - Ebook generation
0 3 * * 0 /path/to/generate_ebooks.sh

# Monthly - Large collection generation
0 4 1 * * /path/to/generate_monthly.sh
```

## 🔐 Security Considerations

### API Key Management

- **Change default key**: Update `shrine_puzzle_api_key_2024` to a secure key
- **Key rotation**: Regularly rotate API keys
- **Access logs**: Monitor API access for suspicious activity

### Network Security

- **HTTPS only**: All API communication uses HTTPS
- **Firewall rules**: Restrict access to necessary ports only
- **VPN**: Consider using VPN for additional security

## 🎯 Next Steps

1. **Deploy API endpoint** to your server
2. **Test API connection** from Raspberry Pi
3. **Generate initial puzzles** for testing
4. **Monitor performance** and adjust batch sizes
5. **Implement puzzle solving** for complete solutions
6. **Add analytics** to track puzzle popularity

## 📞 Support

For issues or questions:
- Check the logs in `logs/` directory
- Test API connectivity with `test_api_connection.py`
- Review server logs for API errors
- Monitor network connectivity
- Test with small batches first

---

**Happy Puzzle Generating! 🧩✨**
