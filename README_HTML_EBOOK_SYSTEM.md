# HTML Ebook Generation System

A complete system for generating beautiful, zen-like Akari puzzle ebooks using HTML/CSS with print styling, running on Raspberry Pi 5 and integrated with CDN Bunny for distribution.

## 🎯 Overview

This system replaces the current ReportLab PDF approach with a superior HTML/CSS solution that provides:

- **Better Design**: Zen-like Japanese aesthetics with modern CSS
- **Print Optimization**: Dedicated `@media print` styles for perfect PDF generation
- **Interactive Elements**: Clickable navigation, print buttons, responsive design
- **Easy Customization**: CSS variables for theme changes
- **CDN Integration**: Automatic upload to CDN Bunny for fast distribution

## 🏗️ System Architecture

```
Dashboard (PHP) → API Controller → Raspberry Pi 5 → CDN Bunny
     ↓                ↓                ↓              ↓
  User Interface → Job Management → HTML Generation → Distribution
```

### Components

1. **Dashboard Interface** (`admin/html_ebook_manager.php`)
   - Web-based management interface
   - Real-time job monitoring
   - Ebook library and preview

2. **API Controller** (`api/html_ebook_controller.php`)
   - Receives commands from dashboard
   - Manages job queue and status
   - Handles CDN Bunny uploads

3. **Raspberry Pi 5 API** (`puzzle_generator/rpi_html_ebook_api.py`)
   - Flask-based API server
   - Background job processing
   - Direct CDN Bunny integration

4. **HTML Generator** (`puzzle_generator/enhanced_html_ebook_generator.py`)
   - Creates beautiful HTML ebooks
   - Zen-like Japanese design
   - Print-optimized CSS

## 🚀 Quick Start

### 1. Database Setup

```sql
-- Run the SQL file to create the jobs table
mysql -u your_user -p your_database < bin/html_ebook_jobs_table.sql
```

### 2. Raspberry Pi 5 Setup

```bash
# Clone the project to your RPi5
cd /home/pi
git clone https://github.com/your-repo/shrinepuzzle.com.git

# Navigate to puzzle generator
cd shrinepuzzle.com/puzzle_generator

# Make setup script executable
chmod +x setup_rpi_html_ebook.sh

# Run the setup script
./setup_rpi_html_ebook.sh
```

### 3. Configuration

Update the configuration files with your API keys:

**On RPi5** (`puzzle_generator/config.json`):
```json
{
    "cdn_bunny": {
        "storage_zone": "your-storage-zone",
        "api_key": "your-cdn-bunny-api-key",
        "pull_zone": "https://your-pull-zone.b-cdn.net"
    }
}
```

**On Main Server** (`api/html_ebook_controller.php`):
```php
private $cdn_bunny_config = [
    'storage_zone' => 'your-storage-zone',
    'api_key' => 'your-cdn-bunny-api-key',
    'pull_zone' => 'https://your-pull-zone.b-cdn.net'
];
```

### 4. Access Dashboard

Navigate to: `https://your-domain.com/admin/html_ebook_manager.php`

## 📋 Usage

### Generating an Ebook

1. **From Dashboard:**
   - Select puzzle sizes (6×6, 8×8, 10×10, 12×12)
   - Choose difficulties (Easy, Medium, Hard)
   - Set number of puzzles per combination
   - Enter ebook title
   - Click "Generate Ebook"

2. **Process Flow:**
   ```
   Dashboard → API Controller → RPi5 → Generate HTML → Upload to CDN → Download URL
   ```

3. **Job Status:**
   - **Queued**: Job received by RPi5
   - **Generating**: Creating puzzles and HTML
   - **Completed**: HTML file ready
   - **Uploaded**: Available on CDN Bunny

### Monitoring Jobs

- **Active Jobs**: Real-time updates every 10 seconds
- **Job History**: Complete library of generated ebooks
- **Progress Tracking**: Visual progress bars
- **Error Handling**: Detailed error messages

### Downloading Ebooks

- **Direct Download**: Click download button for CDN URL
- **Preview**: View ebook in browser before downloading
- **Print to PDF**: Use browser's print function (Ctrl+P)

## 🎨 Design Features

### Zen-like Japanese Aesthetic

- **Typography**: Noto Serif JP and Inter fonts
- **Color Palette**: Deep crimson, moss green, golden yellow
- **Layout**: Clean, minimalist design with proper spacing
- **Decorative Elements**: Zen dividers and quotes

### Print Optimization

```css
@media print {
    body {
        background: white !important;
        color: black !important;
        font-size: 12pt;
    }
    
    @page {
        size: A4;
        margin: 1cm;
    }
}
```

### Interactive Elements

- **Table of Contents**: Clickable navigation
- **Print Button**: Fixed position for easy access
- **Responsive Design**: Works on all screen sizes
- **Dark Mode**: Automatic theme detection

## 🔧 API Endpoints

### Main Server (PHP)

- `POST /api/html_ebook_controller.php?action=generate` - Start generation
- `GET /api/html_ebook_controller.php?action=list` - List ebooks
- `GET /api/html_ebook_controller.php?action=status&job_id=X` - Check status
- `POST /api/html_ebook_controller.php?action=upload` - Upload to CDN

### Raspberry Pi 5 (Python/Flask)

- `POST /api/html_ebook_generator` - Receive generation commands
- `GET /api/html_ebook_status/<job_id>` - Job status
- `GET /api/html_ebook_list` - List active jobs
- `GET /api/html_ebook_download/<job_id>` - Download ebook
- `GET /api/health` - Health check

## 📊 Database Schema

```sql
CREATE TABLE html_ebook_jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id VARCHAR(255) UNIQUE NOT NULL,
    params LONGTEXT NOT NULL,
    status ENUM('queued','generating','completed','uploaded','failed'),
    progress INT DEFAULT 0,
    output_file VARCHAR(500),
    cdn_url VARCHAR(500),
    error_message TEXT,
    puzzle_count INT,
    file_size BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    uploaded_at TIMESTAMP NULL,
    failed_at TIMESTAMP NULL
);
```

## 🛠️ Maintenance

### Service Management

```bash
# Check service status
sudo systemctl status rpi-html-ebook-api

# View logs
sudo journalctl -u rpi-html-ebook-api -f

# Restart service
sudo systemctl restart rpi-html-ebook-api

# Enable/disable auto-start
sudo systemctl enable rpi-html-ebook-api
sudo systemctl disable rpi-html-ebook-api
```

### Health Monitoring

- **Automatic Health Checks**: Every 5 minutes via cron
- **Auto-restart**: Service restarts if unhealthy
- **Log Rotation**: Automatic cleanup of old logs
- **File Cleanup**: Old ebooks removed after 7 days

### Backup and Recovery

```bash
# Backup generated ebooks
tar -czf ebooks_backup_$(date +%Y%m%d).tar.gz generated_ebooks/

# Backup database
mysqldump -u user -p database html_ebook_jobs > ebooks_jobs_backup.sql

# Restore from backup
tar -xzf ebooks_backup_20241201.tar.gz
mysql -u user -p database < ebooks_jobs_backup.sql
```

## 🔒 Security

### API Authentication

- **API Key Required**: All endpoints require valid API key
- **CORS Protection**: Configured for specific origins
- **Rate Limiting**: Built into Flask application
- **Input Validation**: All parameters validated

### System Security

- **Firewall**: UFW configured with minimal ports
- **Service Isolation**: Systemd service with security restrictions
- **File Permissions**: Proper ownership and permissions
- **Log Monitoring**: Security events logged

## 📈 Performance

### Optimization Features

- **Background Processing**: Jobs run in separate threads
- **Memory Management**: Automatic cleanup of completed jobs
- **CDN Distribution**: Fast global delivery via CDN Bunny
- **Caching**: Browser caching for static assets

### Resource Usage

- **CPU**: Limited to 50% via systemd
- **Memory**: Maximum 512MB per service
- **Storage**: Automatic cleanup of old files
- **Network**: Optimized for CDN uploads

## 🐛 Troubleshooting

### Common Issues

1. **Service Won't Start**
   ```bash
   # Check logs
   sudo journalctl -u rpi-html-ebook-api -n 50
   
   # Check dependencies
   source venv/bin/activate
   python -c "import flask, requests"
   ```

2. **CDN Upload Fails**
   - Verify API key in config.json
   - Check network connectivity
   - Verify storage zone exists

3. **Dashboard Connection Issues**
   - Check RPi5 IP address
   - Verify firewall settings
   - Test API endpoint directly

### Debug Mode

```bash
# Enable debug logging
sudo systemctl stop rpi-html-ebook-api
cd /home/pi/shrinepuzzle.com/puzzle_generator
source venv/bin/activate
python rpi_html_ebook_api.py --debug
```

## 🔄 Updates and Upgrades

### Updating the System

```bash
# Pull latest code
cd /home/pi/shrinepuzzle.com
git pull origin main

# Restart services
sudo systemctl restart rpi-html-ebook-api
sudo systemctl restart nginx
```

### Adding New Features

1. **New Puzzle Types**: Modify `enhanced_html_ebook_generator.py`
2. **Design Changes**: Update CSS in generator
3. **API Extensions**: Add new endpoints to Flask app
4. **Dashboard Features**: Enhance PHP interface

## 📚 Examples

### Generate Basic Ebook

```bash
# From command line
curl -X POST "https://your-domain.com/api/html_ebook_controller.php?action=generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "sizes": [6, 8],
    "difficulties": ["easy", "medium"],
    "count": 10,
    "title": "My Akari Collection"
  }'
```

### Check Job Status

```bash
curl -H "X-API-Key: your-api-key" \
  "https://your-domain.com/api/html_ebook_controller.php?action=status&job_id=ebook_123"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Noto Fonts**: Beautiful Japanese typography
- **CDN Bunny**: Fast global content delivery
- **Flask**: Lightweight Python web framework
- **Bootstrap**: Responsive UI components

---

**Need Help?** Check the logs, review this README, or create an issue in the repository.
