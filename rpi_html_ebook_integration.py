#!/usr/bin/env python3
"""
Raspberry Pi HTML Ebook Integration
Integrates HTML ebook generation with existing RPi puzzle generation system
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from enhanced_html_ebook_generator import EnhancedHTMLEbookGenerator

class RPiHTMLEbookIntegration:
    def __init__(self, config: Dict):
        self.config = config
        self.html_generator = EnhancedHTMLEbookGenerator(config)
        
        # RPi-specific paths
        self.output_dir = config.get('output_dir', './generated_ebooks')
        self.log_file = config.get('log_file', './html_ebook_generation.log')
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
    def log_message(self, message: str):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        # Write to log file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    
    def generate_daily_ebook(self, date_str: str = None):
        """Generate daily HTML ebook with puzzles from database"""
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        self.log_message(f"Starting daily HTML ebook generation for {date_str}")
        
        try:
            # Generate puzzles for the day
            puzzles = self.html_generator.puzzle_generator.generate_daily_puzzles(date_str)
            
            if not puzzles:
                self.log_message("No puzzles found for the specified date")
                return False
            
            # Create output filename
            output_file = os.path.join(self.output_dir, f"akari_daily_{date_str}.html")
            title = f"Daily Akari Puzzles - {date_str}"
            
            # Generate HTML ebook
            self.html_generator.generate_ebook(
                puzzles, 
                output_file, 
                title,
                auto_open=False,
                include_print_button=True
            )
            
            self.log_message(f"Daily HTML ebook generated: {output_file}")
            self.log_message(f"Generated {len(puzzles)} puzzles")
            
            return True
            
        except Exception as e:
            self.log_message(f"Error generating daily ebook: {e}")
            return False
    
    def generate_weekly_ebook(self, week_start: str = None):
        """Generate weekly HTML ebook with puzzles from database"""
        if not week_start:
            # Calculate current week start (Monday)
            today = datetime.now()
            days_since_monday = today.weekday()
            week_start = (today - timedelta(days=days_since_monday)).strftime('%Y-%m-%d')
        
        self.log_message(f"Starting weekly HTML ebook generation for week starting {week_start}")
        
        try:
            # Generate puzzles for the week
            puzzles = self.html_generator.puzzle_generator.generate_weekly_puzzles(week_start)
            
            if not puzzles:
                self.log_message("No puzzles found for the specified week")
                return False
            
            # Create output filename
            output_file = os.path.join(self.output_dir, f"akari_weekly_{week_start}.html")
            title = f"Weekly Akari Puzzles - Week of {week_start}"
            
            # Generate HTML ebook
            self.html_generator.generate_ebook(
                puzzles, 
                output_file, 
                title,
                auto_open=False,
                include_print_button=True
            )
            
            self.log_message(f"Weekly HTML ebook generated: {output_file}")
            self.log_message(f"Generated {len(puzzles)} puzzles")
            
            return True
            
        except Exception as e:
            self.log_message(f"Error generating weekly ebook: {e}")
            return False
    
    def generate_custom_ebook(self, sizes: List[int], difficulties: List[str], count: int, title: str = None):
        """Generate custom HTML ebook with specified parameters"""
        if not title:
            title = f"Custom Akari Collection - {datetime.now().strftime('%Y-%m-%d')}"
        
        self.log_message(f"Starting custom HTML ebook generation: {title}")
        self.log_message(f"Parameters: sizes={sizes}, difficulties={difficulties}, count={count}")
        
        try:
            # Generate puzzles
            puzzles = self.html_generator.puzzle_generator.generate_ebook_puzzles(sizes, count)
            
            # Filter by difficulties
            puzzles = [p for p in puzzles if p['difficulty'] in difficulties]
            
            if not puzzles:
                self.log_message("No puzzles generated with specified parameters")
                return False
            
            # Create output filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')
            output_file = os.path.join(self.output_dir, f"akari_custom_{safe_title}.html")
            
            # Generate HTML ebook
            self.html_generator.generate_ebook(
                puzzles, 
                output_file, 
                title,
                auto_open=False,
                include_print_button=True
            )
            
            self.log_message(f"Custom HTML ebook generated: {output_file}")
            self.log_message(f"Generated {len(puzzles)} puzzles")
            
            return True
            
        except Exception as e:
            self.log_message(f"Error generating custom ebook: {e}")
            return False
    
    def cleanup_old_ebooks(self, days_to_keep: int = 30):
        """Clean up old HTML ebooks"""
        self.log_message(f"Cleaning up ebooks older than {days_to_keep} days")
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            deleted_count = 0
            
            for file_path in Path(self.output_dir).glob("*.html"):
                if file_path.stat().st_mtime < cutoff_date.timestamp():
                    file_path.unlink()
                    deleted_count += 1
                    self.log_message(f"Deleted old ebook: {file_path.name}")
            
            self.log_message(f"Cleanup complete: deleted {deleted_count} old ebooks")
            return deleted_count
            
        except Exception as e:
            self.log_message(f"Error during cleanup: {e}")
            return 0
    
    def list_generated_ebooks(self):
        """List all generated HTML ebooks"""
        self.log_message("Listing generated HTML ebooks:")
        
        try:
            ebooks = list(Path(self.output_dir).glob("*.html"))
            
            if not ebooks:
                self.log_message("No HTML ebooks found")
                return []
            
            for ebook in sorted(ebooks, key=lambda x: x.stat().st_mtime, reverse=True):
                size = ebook.stat().st_size
                modified = datetime.fromtimestamp(ebook.stat().st_mtime)
                self.log_message(f"  {ebook.name} ({size:,} bytes, {modified.strftime('%Y-%m-%d %H:%M')})")
            
            return ebooks
            
        except Exception as e:
            self.log_message(f"Error listing ebooks: {e}")
            return []

def main():
    parser = argparse.ArgumentParser(description='Raspberry Pi HTML Ebook Integration')
    parser.add_argument('--mode', choices=['daily', 'weekly', 'custom'], required=True,
                       help='Generation mode')
    parser.add_argument('--date', type=str, help='Date for daily/weekly generation (YYYY-MM-DD)')
    parser.add_argument('--sizes', nargs='+', type=int, default=[6, 8, 10],
                       help='Puzzle sizes for custom generation')
    parser.add_argument('--difficulties', nargs='+', default=['easy', 'medium', 'hard'],
                       help='Difficulties for custom generation')
    parser.add_argument('--count', type=int, default=10,
                       help='Puzzles per size/difficulty for custom generation')
    parser.add_argument('--title', type=str, help='Custom ebook title')
    parser.add_argument('--output-dir', type=str, default='./generated_ebooks',
                       help='Output directory for generated ebooks')
    parser.add_argument('--cleanup', action='store_true',
                       help='Clean up old ebooks after generation')
    parser.add_argument('--list', action='store_true',
                       help='List existing ebooks')
    
    args = parser.parse_args()
    
    # Configuration
    config = {
        'api_url': 'https://shrinepuzzle.com/api/puzzle_receiver.php',
        'api_key': 'shrine_puzzle_api_key_2024',
        'output_dir': args.output_dir,
        'log_file': './html_ebook_generation.log'
    }
    
    # Create integration instance
    integration = RPiHTMLEbookIntegration(config)
    
    # List existing ebooks if requested
    if args.list:
        integration.list_generated_ebooks()
        return
    
    # Generate ebook based on mode
    success = False
    
    if args.mode == 'daily':
        success = integration.generate_daily_ebook(args.date)
    elif args.mode == 'weekly':
        success = integration.generate_weekly_ebook(args.date)
    elif args.mode == 'custom':
        success = integration.generate_custom_ebook(
            args.sizes, 
            args.difficulties, 
            args.count, 
            args.title
        )
    
    # Cleanup if requested and generation was successful
    if args.cleanup and success:
        integration.cleanup_old_ebooks()
    
    if success:
        integration.log_message("HTML ebook generation completed successfully")
        sys.exit(0)
    else:
        integration.log_message("HTML ebook generation failed")
        sys.exit(1)

if __name__ == "__main__":
    from datetime import timedelta
    main()
