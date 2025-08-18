# 🎯 Complete Akari Puzzle Generator System

A fully automated, secure, and scalable puzzle generation system with CDN Bunny integration and admin control.

## 🚀 System Overview

This complete system includes:
- **Raspberry Pi 5** puzzle generator with API server
- **CDN Bunny** integration for automatic PDF uploads
- **Admin dashboard** for remote control
- **Secure API** communication
- **Automated scheduling** and monitoring

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Admin Panel   │    │  Puzzle API     │    │  CDN Bunny      │
│   (Web UI)      │◄──►│  (Server)       │◄──►│  (Storage)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  RPi Controller │    │  Puzzle DB      │    │  PDF Ebooks     │
│  (PHP API)      │    │  (MySQL)        │    │  (CDN)          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│  Raspberry Pi   │
│  (Generator)    │
└─────────────────┘
```

## 📋 Requirements

### Server Requirements
- PHP 7.4+
- MySQL 5.7+
- Web server (Apache/Nginx)
- SSL certificate

### Raspberry Pi Requirements
- Raspberry Pi 5 (or any Linux system)
- Python 3.8+
- Internet connection
- 4GB+ RAM recommended

### CDN Bunny Account
- Storage zone
- API key
- Pull zone (optional)

## 🛠️ Installation

### 1. Server Setup

#### Deploy API Files
```bash
# Copy API files to your server
api/puzzle_receiver.php → /path/to/your/website/api/
api/rpi_controller.php → /path/to/your/website/api/
admin/dashboard.php → /path/to/your/website/admin/
```

#### Database Setup
```sql
-- Create admin logs table
CREATE TABLE IF NOT EXISTS admin_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    params TEXT,
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Raspberry Pi Setup

#### Automated Setup
```bash
# Clone repository
git clone <your-repo> puzzle_generator
cd puzzle_generator

# Run complete setup
chmod +x setup_raspberry_pi_complete.sh
./setup_raspberry_pi_complete.sh
```

#### Manual Setup
```bash
# Install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nginx

# Create virtual environment
python3 -m venv akari_env
source akari_env/bin/activate

# Install Python packages
pip install -r requirements.txt

# Create directories
mkdir -p logs output ebooks config ssl
```

### 3. Configuration

#### Update API Keys
```bash
# Edit configuration files
nano config/generator_config.json
nano api/puzzle_receiver.php
nano api/rpi_controller.php
nano admin/dashboard.php
```

#### Configure CDN Bunny
Edit `config/generator_config.json`:
```json
{
    "cdn_bunny": {
        "storage_zone": "your-storage-zone",
        "api_key": "your-cdn-bunny-key",
        "storage_zone_name": "your-zone-name",
        "region": "de"
    }
}
```

## 🧪 Testing

### Test API Connection
```bash
python3 test_api_connection.py
```

### Test CDN Bunny
```bash
python3 test_cdn_bunny.py
```

### Test System Status
```bash
python3 monitor_system.py
```

### Test from Web Browser
Visit: `https://shrinepuzzle.com/api/test_puzzle_api.php`

## 🎮 Usage

### Admin Dashboard
Visit: `https://shrinepuzzle.com/admin/dashboard.php`

Features:
- **System Status**: Monitor RPi health and services
- **Puzzle Generation**: Generate puzzles on demand
- **Ebook Creation**: Create and upload PDF ebooks
- **System Logs**: View real-time logs
- **Configuration**: Update settings remotely

### Command Line Usage

#### Generate Premium Puzzles
```bash
python3 akari_generator_api.py \
  --mode premium \
  --sizes 6 8 10 12 \
  --difficulties easy medium hard expert \
  --count 10
```

#### Generate and Upload Ebook
```bash
python3 ebook_generator.py \
  --sizes 6 8 10 12 \
  --difficulties easy medium hard \
  --count 20 \
  --output "Akari_Master_Collection.pdf" \
  --title "Akari Master Collection"
```

#### Upload to CDN Bunny
```bash
python3 cdn_bunny_uploader.py \
  --pdf-path ebooks/akari_ebook.pdf \
  --title "Akari Collection" \
  --storage-zone your-zone \
  --api-key your-key \
  --storage-zone-name your-zone-name
```

## 🔧 Management

### Service Management
```bash
# Start API server
sudo systemctl start akari-api.service

# Stop API server
sudo systemctl stop akari-api.service

# Restart API server
sudo systemctl restart akari-api.service

# View logs
sudo journalctl -u akari-api.service -f
```

### Monitoring
```bash
# System status
python3 monitor_system.py

# View logs
tail -f logs/akari_generator_api.log
tail -f logs/rpi_api_server.log
tail -f logs/cron.log

# Check cron jobs
crontab -l
```

### Backup
```bash
# Backup configuration
./backup_config.sh

# Manual backup
tar -czf backup_$(date +%Y%m%d).tar.gz config/ logs/ ebooks/
```

## 🔐 Security

### API Keys
- **Puzzle API**: `shrine_puzzle_api_key_2024`
- **Admin API**: `shrine_admin_key_2024`
- **RPi Control**: `rpi_control_key_2024`

### Security Recommendations
1. **Change default keys** to secure values
2. **Use HTTPS** for all API communication
3. **Implement proper authentication** for admin dashboard
4. **Regular key rotation**
5. **Monitor access logs**

## 📊 Monitoring & Analytics

### System Metrics
- CPU and memory usage
- Disk space utilization
- Service status
- Log file sizes
- Uptime tracking

### Business Metrics
- Puzzles generated per day
- Ebooks created and uploaded
- CDN storage usage
- API response times
- Error rates

### Log Analysis
```bash
# View recent errors
grep "ERROR" logs/akari_generator_api.log | tail -20

# Check API performance
grep "API Response" logs/akari_generator_api.log

# Monitor CDN uploads
grep "Upload successful" logs/cdn_bunny_uploader.log
```

## 🔄 Automation

### Daily Schedule
- **2:00 AM**: Generate premium puzzles
- **3:00 AM**: Create weekly ebook (Sundays)
- **4:00 AM**: System backup (Mondays)

### Custom Scheduling
```bash
# Edit cron jobs
crontab -e

# Example: Generate puzzles every 6 hours
0 */6 * * * cd /path/to/puzzle_generator && source akari_env/bin/activate && python3 akari_generator_api.py --mode premium --sizes 6 8 10 12 --difficulties easy medium hard --count 5 >> logs/cron.log 2>&1

# Example: Generate ebooks weekly
0 3 * * 0 cd /path/to/puzzle_generator && source akari_env/bin/activate && python3 ebook_generator.py --sizes 6 8 10 12 --count 15 --output "weekly_collection.pdf" >> logs/ebook_cron.log 2>&1
```

## 🚨 Troubleshooting

### Common Issues

#### API Connection Failed
```bash
# Test network connectivity
ping shrinepuzzle.com

# Check API endpoint
curl -I https://shrinepuzzle.com/api/puzzle_receiver.php

# Verify API key
python3 test_api_connection.py
```

#### CDN Bunny Upload Failed
```bash
# Test CDN connection
python3 test_cdn_bunny.py

# Check credentials
cat config/generator_config.json | grep cdn_bunny

# Verify storage zone
curl -H "AccessKey: YOUR_KEY" https://storage.bunnycdn.com/YOUR_ZONE/
```

#### Service Not Starting
```bash
# Check service status
sudo systemctl status akari-api.service

# View service logs
sudo journalctl -u akari-api.service -f

# Check Python environment
source akari_env/bin/activate
python3 -c "import requests; print('OK')"
```

#### Low Disk Space
```bash
# Check disk usage
df -h

# Clean old logs
find logs/ -name "*.log" -mtime +7 -delete

# Clean old ebooks
find ebooks/ -name "*.pdf" -mtime +30 -delete
```

## 📈 Business Integration

### Revenue Streams
1. **Premium Subscriptions**: Access to larger/harder puzzles
2. **Ebook Sales**: Printable collections via CDN
3. **API Access**: Developer access (future)
4. **Educational Licenses**: Schools and institutions

### Content Strategy
- **Daily**: 6x6 and 8x8 medium puzzles
- **Premium**: 10x10 and 12x12 hard/expert puzzles
- **Weekly**: Ebook collections for sale
- **Monthly**: Large premium collections

### Analytics Integration
```bash
# Track puzzle generation
mysql -u user -p database -e "SELECT DATE(created_at) as date, COUNT(*) as count FROM puzzles WHERE game='akari' GROUP BY DATE(created_at) ORDER BY date DESC LIMIT 7;"

# Monitor CDN usage
python3 cdn_bunny_uploader.py --stats
```

## 🔮 Future Enhancements

### Planned Features
1. **Puzzle Solving**: Implement actual solution generation
2. **Quality Metrics**: Track difficulty and solve rates
3. **User Analytics**: Monitor popular puzzles
4. **Advanced Algorithms**: More sophisticated generation
5. **Multi-game Support**: Sudoku, KenKen, Nurikabe
6. **Mobile App**: PWA with offline support
7. **Social Features**: Leaderboards and sharing
8. **AI Integration**: Machine learning for puzzle quality

### Technical Improvements
1. **Load Balancing**: Multiple RPi instances
2. **Database Optimization**: Caching and indexing
3. **CDN Optimization**: Edge computing
4. **Security Enhancements**: Rate limiting, DDoS protection
5. **Monitoring**: Prometheus/Grafana integration

## 📞 Support

### Documentation
- **API Documentation**: `/api/` endpoints
- **Configuration Guide**: `config/generator_config.json`
- **Log Files**: `logs/` directory
- **Test Scripts**: `test_*.py` files

### Monitoring Tools
- **System Monitor**: `monitor_system.py`
- **Service Status**: `systemctl status akari-api.service`
- **Log Viewer**: `tail -f logs/*.log`
- **Admin Dashboard**: Web interface

### Emergency Procedures
1. **Service Down**: `sudo systemctl restart akari-api.service`
2. **Database Issues**: Check `bin/dbconnect.php`
3. **CDN Problems**: Verify credentials in config
4. **Full Reset**: Run setup script again

---

**🎯 Happy Puzzle Generating! 🧩✨**

*This complete system provides a robust, scalable, and automated solution for generating and distributing Akari puzzles with professional-grade infrastructure and monitoring.*
