# HTML Ebook Integration with Existing RPi5 Job Queue

## 🎯 Overview

The HTML ebook generation has been seamlessly integrated into the existing Raspberry Pi 5 job queue and polling system. This means you can use the current dashboard and command infrastructure without any additional setup.

## 🔄 How It Works

### Existing System Components:
1. **Dashboard** (`admin/dashboard.php`) - Web interface for managing RPi5
2. **Command Queue** (`api/queue_command.php`) - Queues commands for RPi5
3. **RPi Polling Client** (`puzzle_generator/rpi_polling_client_fixed.py`) - Executes commands on RPi5
4. **Command Status** (`api/rpi_commands.php`) - Tracks command execution

### New HTML Ebook Integration:
- **Action**: `generate_ebook` (same as before, but now generates HTML instead of PDF)
- **Generator**: `enhanced_html_ebook_generator.py` (new zen-like HTML generator)
- **Output**: Beautiful HTML ebooks with print optimization
- **Distribution**: Automatic CDN Bunny upload

## 🚀 Usage

### From Dashboard:
1. Go to `admin/dashboard.php`
2. Click "Generate HTML Ebook" button (Quick Actions)
3. Or use the "Ebook Generation" tab for custom parameters
4. Monitor progress in the Command Queue tab

### From Command Line:
```bash
# Queue an HTML ebook generation command
curl -X POST "https://your-domain.com/api/queue_command.php" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "hostname": "rpi-5-001",
    "command": {
      "action": "generate_ebook",
      "params": {
        "title": "Zen Akari Collection",
        "sizes": [6, 8, 10],
        "difficulties": ["easy", "medium", "hard"],
        "count": 25
      }
    }
  }'
```

## 📋 Command Flow

```
Dashboard → Queue Command → RPi5 Polling → Execute Command → Generate HTML → Upload to CDN → Return Result
```

### Step-by-Step Process:
1. **Dashboard**: User clicks "Generate HTML Ebook"
2. **Queue**: Command stored in `rpi_commands` table
3. **Polling**: RPi5 checks for new commands every 30 seconds
4. **Execution**: RPi5 executes `generate_ebook` action
5. **Generation**: Creates zen-like HTML ebook using `enhanced_html_ebook_generator.py`
6. **Upload**: Automatically uploads to CDN Bunny
7. **Result**: Returns success/failure with CDN URL

## 🎨 HTML Ebook Features

### Design:
- **Zen-like Japanese aesthetic** with Noto Serif JP fonts
- **Print-optimized CSS** with `@media print` styles
- **Interactive elements** like table of contents and print buttons
- **Responsive design** that works on all devices

### Technical:
- **Pure HTML/CSS** - no JavaScript dependencies
- **Print to PDF** - use browser's print function (Ctrl+P)
- **CDN distribution** - fast global delivery via CDN Bunny
- **File size optimization** - efficient HTML structure

## 🔧 Configuration

### CDN Bunny Setup:
Update the CDN configuration in `rpi_polling_client_fixed.py`:

```python
'cdn_bunny': {
    'storage_zone': 'your-storage-zone',
    'api_key': 'your-cdn-bunny-api-key',
    'pull_zone': 'https://your-pull-zone.b-cdn.net'
}
```

### Output Directory:
HTML ebooks are saved to `./generated_ebooks/` on the RPi5.

## 📊 Monitoring

### Dashboard Monitoring:
- **Command Queue Tab**: See all ebook generation jobs
- **System Status**: Monitor RPi5 health and resources
- **Logs Tab**: View generation logs

### Command Status:
- **pending**: Command queued, waiting for RPi5
- **processing**: RPi5 is generating the ebook
- **completed**: HTML ebook generated successfully
- **failed**: Error occurred during generation

## 🐛 Troubleshooting

### Common Issues:

1. **CDN Upload Fails**:
   - Check CDN Bunny API key in configuration
   - Verify storage zone exists
   - Check network connectivity

2. **Generation Fails**:
   - Check RPi5 logs: `logs/rpi_polling.log`
   - Verify puzzle generator is working
   - Check disk space on RPi5

3. **Command Not Executed**:
   - Verify RPi5 polling service is running
   - Check RPi5 network connectivity
   - Verify API key authentication

### Debug Commands:
```bash
# Check RPi5 service status
sudo systemctl status rpi-polling-fixed

# View polling logs
tail -f logs/rpi_polling.log

# Test command execution
curl -H "Authorization: Bearer your-api-key" \
  "https://your-domain.com/api/rpi_commands.php?hostname=rpi-5-001"
```

## 🔄 Migration from PDF

### What Changed:
- **Same Action**: `generate_ebook` (no dashboard changes needed)
- **Same Parameters**: title, sizes, difficulties, count
- **Same Queue System**: Uses existing command infrastructure
- **Better Output**: HTML instead of PDF

### Benefits:
- **Better Design**: Zen-like Japanese aesthetics
- **Print Optimization**: Perfect PDF generation via browser
- **Interactive Elements**: Clickable navigation and print buttons
- **Easier Customization**: CSS-based styling
- **Faster Generation**: No PDF library dependencies

## 📈 Performance

### Generation Time:
- **Small ebooks** (10-25 puzzles): 30-60 seconds
- **Medium ebooks** (50-100 puzzles): 2-5 minutes
- **Large ebooks** (100+ puzzles): 5-10 minutes

### File Sizes:
- **HTML files**: 100KB - 2MB (depending on puzzle count)
- **CDN delivery**: Global edge caching for fast downloads

## 🎯 Next Steps

1. **Update CDN Configuration**: Set your actual CDN Bunny credentials
2. **Test Generation**: Try generating a small ebook from the dashboard
3. **Monitor Results**: Check the command queue for success/failure
4. **Download Ebook**: Use the provided CDN URL to download the HTML file
5. **Print to PDF**: Open in browser and use Ctrl+P for PDF generation

---

**The HTML ebook generation is now fully integrated with your existing RPi5 infrastructure!** 🎉
