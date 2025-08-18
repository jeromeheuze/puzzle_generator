#!/usr/bin/env python3
"""
Test script for HTML Ebook Generator
Creates a sample HTML ebook with test puzzles
"""

import json
from html_ebook_generator import HTMLEbookGenerator

def create_test_puzzles():
    """Create sample puzzles for testing"""
    return [
        {
            'size': 6,
            'difficulty': 'easy',
            'layout': [
                [0, 0, 'X', 'X', 0, 0],
                [0, 0, 'X', 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 'X', 0, 0, 0],
                [0, 'X', 0, 0, 0, 'X']
            ]
        },
        {
            'size': 6,
            'difficulty': 'medium',
            'layout': [
                [0, 0, 0, 0, 0, '1'],
                ['1', 'X', 0, 0, 0, 0],
                [0, 0, 'X', 'X', 0, 0],
                [0, 0, 0, 0, 0, 'X'],
                ['X', 0, 0, '1', 'X', 0],
                [0, 0, 0, 'X', 0, 0]
            ]
        },
        {
            'size': 8,
            'difficulty': 'hard',
            'layout': [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 'X', 0, 0, 0],
                [0, 0, 0, '2', 0, 0, 0, 'X'],
                [0, 0, 'X', 0, 0, 0, 0, 0],
                [0, 0, 0, 'X', 0, 0, 0, 'X'],
                [0, 0, 'X', 0, 'X', 'X', '1', '1'],
                [0, 0, 0, '2', 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ]
        }
    ]

def main():
    print("🎯 Testing HTML Ebook Generator...")
    
    # Configuration
    config = {
        'api_url': 'https://shrinepuzzle.com/api/puzzle_receiver.php',
        'api_key': 'shrine_puzzle_api_key_2024'
    }
    
    # Create generator
    generator = HTMLEbookGenerator(config)
    
    # Create test puzzles
    test_puzzles = create_test_puzzles()
    
    print(f"✨ Created {len(test_puzzles)} test puzzles")
    
    # Generate HTML ebook
    output_file = 'test_akari_zen_ebook.html'
    title = 'Test Akari: Zen Logic Puzzles'
    
    generator.generate_ebook(test_puzzles, output_file, title)
    
    print(f"🎨 Test HTML ebook created: {output_file}")
    print(f"🌐 Open {output_file} in your browser to view")
    print(f"🖨️  Press Ctrl+P to print as PDF")

if __name__ == "__main__":
    main()
