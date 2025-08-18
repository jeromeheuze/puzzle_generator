#!/usr/bin/env python3
"""
HTML Ebook Generator for Akari Puzzles
Creates beautiful, zen-like Japanese HTML ebooks with CSS print styling
"""

import json
import argparse
from datetime import datetime
from typing import List, Dict
import os
from pathlib import Path
from akari_generator_api import AkariPuzzleGeneratorAPI

class HTMLEbookGenerator:
    def __init__(self, config: Dict):
        self.config = config
        self.puzzle_generator = AkariPuzzleGeneratorAPI(
            config.get('api_url', 'https://shrinepuzzle.com/api/puzzle_receiver.php'),
            config.get('api_key', 'shrine_puzzle_api_key_2024')
        )
        
        # Zen-like Japanese color palette (matching your existing CSS)
        self.colors = {
            'primary': '#b31b1b',      # Deep crimson (shrine gates)
            'secondary': '#6A8F5F',    # Moss green
            'accent': '#E8C075',       # Golden yellow
            'warm': '#F39C12',         # Warm orange
            'light': '#ECF0F1',        # Light gray
            'white': '#ffffff',
            'black': '#2c2c2c',
            'grid_line': '#BDC3C7',    # Soft gray for grid lines
            'wall': '#34495E',         # Dark walls
            'number': '#2C3E50',       # Dark numbers
            'cell_bg': '#F8F9FA',      # Very light background
            'bg': '#f9f6f0',           # Warm off-white background
        }
        
    def create_puzzle_grid_html(self, layout: List[List], size: int, puzzle_num: int) -> str:
        """Convert puzzle layout to HTML grid with zen styling"""
        html = f'<div class="puzzle-grid puzzle-{puzzle_num}">\n'
        
        # Add column headers (A, B, C, ...)
        html += '  <div class="grid-header">\n'
        html += '    <div class="corner-cell"></div>\n'
        for i in range(size):
            html += f'    <div class="header-cell">{chr(65 + i)}</div>\n'
        html += '  </div>\n'
        
        # Add rows with row numbers
        for i, row in enumerate(layout):
            html += f'  <div class="grid-row">\n'
            html += f'    <div class="row-header">{i + 1}</div>\n'
            for j, cell in enumerate(row):
                if cell == 0:
                    html += '    <div class="cell empty"></div>\n'
                elif cell == 'X':
                    html += '    <div class="cell wall"></div>\n'
                else:
                    html += f'    <div class="cell wall number" data-value="{cell}">{cell}</div>\n'
            html += '  </div>\n'
        
        html += '</div>'
        return html
    
    def create_solution_grid_html(self, layout: List[List], size: int, puzzle_num: int) -> str:
        """Create a solution grid (empty for user to fill)"""
        html = f'<div class="solution-grid puzzle-{puzzle_num}">\n'
        
        # Add column headers
        html += '  <div class="grid-header">\n'
        html += '    <div class="corner-cell"></div>\n'
        for i in range(size):
            html += f'    <div class="header-cell">{chr(65 + i)}</div>\n'
        html += '  </div>\n'
        
        # Add empty rows
        for i in range(size):
            html += f'  <div class="grid-row">\n'
            html += f'    <div class="row-header">{i + 1}</div>\n'
            for j in range(size):
                html += '    <div class="cell empty solution-cell"></div>\n'
            html += '  </div>\n'
        
        html += '</div>'
        return html
    
    def generate_css(self) -> str:
        """Generate zen-like CSS with print styling"""
        return f"""
/* Zen-like Akari Puzzle Ebook Styles */
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');

:root {{
    --primary: {self.colors['primary']};
    --secondary: {self.colors['secondary']};
    --accent: {self.colors['accent']};
    --bg: {self.colors['bg']};
    --text: {self.colors['black']};
    --text-muted: #666;
    --grid-line: {self.colors['grid_line']};
    --wall: {self.colors['wall']};
    --cell-bg: {self.colors['cell_bg']};
    --white: {self.colors['white']};
}}

* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}

body {{
    font-family: 'Noto Serif JP', 'Inter', serif;
    line-height: 1.6;
    color: var(--text);
    background: var(--bg);
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
}}

/* Typography */
h1 {{
    font-size: 2.5rem;
    font-weight: 700;
    text-align: center;
    color: var(--primary);
    margin-bottom: 1rem;
    letter-spacing: 2px;
}}

h2 {{
    font-size: 1.8rem;
    font-weight: 600;
    color: var(--secondary);
    margin: 2rem 0 1rem;
    border-bottom: 2px solid var(--accent);
    padding-bottom: 0.5rem;
}}

h3 {{
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--text);
    margin: 1.5rem 0 0.5rem;
}}

p {{
    margin-bottom: 1rem;
    text-align: justify;
}}

/* Zen-inspired decorative elements */
.zen-divider {{
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    margin: 2rem 0;
    border-radius: 1px;
}}

.zen-quote {{
    font-style: italic;
    text-align: center;
    color: var(--text-muted);
    font-size: 1.1rem;
    margin: 2rem 0;
    padding: 1rem;
    border-left: 4px solid var(--accent);
    background: rgba(232, 192, 117, 0.1);
}}

/* Puzzle Grid Styles */
.puzzle-container {{
    margin: 2rem 0;
    page-break-inside: avoid;
}}

.puzzle-header {{
    text-align: center;
    margin-bottom: 1rem;
    padding: 1rem;
    background: linear-gradient(135deg, rgba(179, 27, 27, 0.1), rgba(106, 143, 95, 0.1));
    border-radius: 10px;
}}

.puzzle-grid, .solution-grid {{
    display: inline-grid;
    grid-template-columns: auto repeat(var(--size, 6), 1fr);
    gap: 1px;
    background: var(--grid-line);
    border: 2px solid var(--grid-line);
    border-radius: 8px;
    overflow: hidden;
    margin: 1rem auto;
    max-width: fit-content;
}}

.grid-header, .grid-row {{
    display: contents;
}}

.corner-cell, .header-cell, .row-header, .cell {{
    background: var(--cell-bg);
    padding: 0.8rem;
    min-width: 2.5rem;
    min-height: 2.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.9rem;
}}

.corner-cell {{
    background: var(--primary);
    color: var(--white);
    font-weight: 700;
}}

.header-cell, .row-header {{
    background: var(--secondary);
    color: var(--white);
    font-weight: 600;
}}

.cell.empty {{
    background: var(--white);
    border: 1px solid var(--grid-line);
}}

.cell.wall {{
    background: var(--wall);
    color: var(--white);
    font-weight: 700;
}}

.cell.wall.number {{
    background: var(--primary);
    color: var(--white);
    font-weight: 700;
    font-size: 1.1rem;
}}

.solution-cell {{
    border: 2px dashed var(--grid-line);
    background: var(--white);
}}

/* Rules Section */
.rules-section {{
    background: rgba(255, 255, 255, 0.8);
    padding: 2rem;
    border-radius: 15px;
    border: 1px solid var(--grid-line);
    margin: 2rem 0;
}}

.rules-list {{
    list-style: none;
    padding: 0;
}}

.rules-list li {{
    margin-bottom: 0.8rem;
    padding-left: 1.5rem;
    position: relative;
}}

.rules-list li::before {{
    content: "•";
    color: var(--primary);
    font-weight: bold;
    position: absolute;
    left: 0;
}}

/* Table of Contents */
.toc {{
    background: rgba(255, 255, 255, 0.9);
    padding: 2rem;
    border-radius: 15px;
    border: 1px solid var(--grid-line);
    margin: 2rem 0;
}}

.toc-item {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--grid-line);
}}

.toc-item:last-child {{
    border-bottom: none;
}}

.toc-number {{
    font-weight: 700;
    color: var(--primary);
    min-width: 2rem;
}}

.toc-title {{
    flex: 1;
    margin-left: 1rem;
}}

.toc-difficulty {{
    color: var(--text-muted);
    font-size: 0.9rem;
}}

/* Print Styles */
@media print {{
    body {{
        background: white;
        color: black;
        font-size: 12pt;
        line-height: 1.4;
        padding: 0;
        margin: 0;
    }}
    
    h1 {{
        font-size: 24pt;
        color: black;
        margin-bottom: 0.5rem;
    }}
    
    h2 {{
        font-size: 18pt;
        color: black;
        margin: 1rem 0 0.5rem;
        border-bottom: 1px solid #ccc;
    }}
    
    h3 {{
        font-size: 14pt;
        color: black;
        margin: 1rem 0 0.3rem;
    }}
    
    .puzzle-grid, .solution-grid {{
        page-break-inside: avoid;
        margin: 1rem auto;
    }}
    
    .puzzle-container {{
        page-break-inside: avoid;
        margin: 1rem 0;
    }}
    
    .zen-divider {{
        display: none;
    }}
    
    .zen-quote {{
        background: none;
        border-left: 2px solid #ccc;
        color: #666;
    }}
    
    .rules-section, .toc {{
        background: white;
        border: 1px solid #ccc;
        padding: 1rem;
    }}
    
    .corner-cell, .header-cell, .row-header {{
        background: #333 !important;
        color: white !important;
    }}
    
    .cell.wall {{
        background: #333 !important;
        color: white !important;
    }}
    
    .cell.wall.number {{
        background: #b31b1b !important;
        color: white !important;
    }}
    
    .cell.empty {{
        background: white !important;
        border: 1px solid #ccc !important;
    }}
    
    .solution-cell {{
        border: 2px dashed #ccc !important;
        background: white !important;
    }}
    
    /* Hide non-essential elements */
    .no-print {{
        display: none !important;
    }}
    
    /* Page breaks */
    .page-break {{
        page-break-before: always;
    }}
    
    /* Ensure puzzles don't break across pages */
    .puzzle-section {{
        page-break-inside: avoid;
    }}
}}

/* Responsive Design */
@media (max-width: 768px) {{
    body {{
        padding: 1rem;
    }}
    
    .puzzle-grid, .solution-grid {{
        grid-template-columns: auto repeat(var(--size, 6), 1fr);
    }}
    
    .corner-cell, .header-cell, .row-header, .cell {{
        padding: 0.5rem;
        min-width: 2rem;
        min-height: 2rem;
        font-size: 0.8rem;
    }}
}}

/* Dark mode support */
@media (prefers-color-scheme: dark) {{
    :root {{
        --bg: #1c1c1c;
        --text: #f0f0f0;
        --text-muted: #aaa;
        --cell-bg: #2a2a2a;
        --white: #2a2a2a;
    }}
    
    body {{
        background: var(--bg);
        color: var(--text);
    }}
    
    .rules-section, .toc {{
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.1);
    }}
}}
"""

    def generate_ebook(self, puzzles: List[Dict], output_file: str, title: str = "Akari: Zen Logic Puzzles"):
        """Generate a beautiful HTML ebook with zen-like Japanese aesthetic"""
        
        # Generate CSS
        css = self.generate_css()
        
        # Start HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="Beautiful Akari logic puzzles with zen-like Japanese aesthetic">
    <style>
{css}
    </style>
</head>
<body>
    <header>
        <h1>{title}</h1>
        <div class="zen-quote">
            "In the art of illumination, find the perfect balance of light and shadow"
        </div>
        <p style="text-align: center; color: var(--text-muted);">
            Generated with care on {datetime.now().strftime('%B %d, %Y')}
        </p>
    </header>
    
    <div class="zen-divider"></div>
    
    <section class="rules-section">
        <h2>How to Play Akari (Light Up)</h2>
        <p><strong>The Art of Illumination:</strong></p>
        <ul class="rules-list">
            <li>Place light bulbs in white cells to illuminate the entire board</li>
            <li>Light travels in straight lines until blocked by walls</li>
            <li>No two bulbs may shine on each other</li>
            <li>Numbered walls must have exactly that many adjacent bulbs</li>
            <li>Every white cell must be lit or contain a bulb</li>
            <li>Find the perfect balance of light and shadow</li>
        </ul>
    </section>
    
    <div class="zen-divider"></div>
    
    <section class="toc">
        <h2>Contents</h2>
        <div class="toc-list">
"""
        
        # Table of contents
        for i, puzzle in enumerate(puzzles, 1):
            html += f"""
            <div class="toc-item">
                <span class="toc-number">{i}.</span>
                <span class="toc-title">{puzzle['size']}×{puzzle['size']} {puzzle['difficulty'].title()} Puzzle</span>
                <span class="toc-difficulty">{puzzle['difficulty'].title()}</span>
            </div>
"""
        
        html += """
        </div>
    </section>
    
    <div class="zen-divider"></div>
    
    <section class="puzzle-section">
        <h2>Puzzles</h2>
"""
        
        # Puzzles section
        for i, puzzle in enumerate(puzzles, 1):
            size = puzzle['size']
            layout = puzzle['layout']
            
            html += f"""
        <div class="puzzle-container">
            <div class="puzzle-header">
                <h3>Puzzle {i}: {size}×{size} {puzzle['difficulty'].title()}</h3>
            </div>
            
            <div style="--size: {size};">
                {self.create_puzzle_grid_html(layout, size, i)}
            </div>
            
            <div style="text-align: center; margin: 1rem 0;">
                <strong>Your Solution:</strong>
            </div>
            
            <div style="--size: {size};">
                {self.create_solution_grid_html(layout, size, i)}
            </div>
        </div>
        
        <div class="page-break"></div>
"""
        
        html += """
    </section>
    
    <div class="zen-divider"></div>
    
    <section class="puzzle-section">
        <h2>Solutions</h2>
"""
        
        # Solutions section
        for i, puzzle in enumerate(puzzles, 1):
            size = puzzle['size']
            layout = puzzle['layout']
            
            html += f"""
        <div class="puzzle-container">
            <div class="puzzle-header">
                <h3>Solution {i}: {size}×{size} {puzzle['difficulty'].title()}</h3>
            </div>
            
            <div style="--size: {size};">
                {self.create_puzzle_grid_html(layout, size, f"solution-{i}")}
            </div>
        </div>
        
        <div class="page-break"></div>
"""
        
        html += """
    </section>
    
    <footer style="text-align: center; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--grid-line); color: var(--text-muted);">
        <p>Thank you for practicing the art of Akari</p>
        <p>Generated by ShrinePuzzle.com</p>
    </footer>
    
    <script>
        // Add print functionality
        function printEbook() {
            window.print();
        }
        
        // Add keyboard shortcut for printing
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'p') {
                e.preventDefault();
                printEbook();
            }
        });
        
        // Auto-adjust grid sizes based on puzzle size
        document.addEventListener('DOMContentLoaded', function() {
            const grids = document.querySelectorAll('.puzzle-grid, .solution-grid');
            grids.forEach(grid => {
                const size = grid.querySelectorAll('.grid-row').length;
                if (size > 8) {
                    grid.style.setProperty('--cell-size', '2rem');
                } else if (size > 6) {
                    grid.style.setProperty('--cell-size', '2.2rem');
                } else {
                    grid.style.setProperty('--cell-size', '2.5rem');
                }
            });
        });
    </script>
</body>
</html>
"""
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✨ Beautiful zen HTML ebook generated: {output_file}")
        print(f"📄 Open in browser and press Ctrl+P to print as PDF")

def main():
    parser = argparse.ArgumentParser(description='Generate beautiful Akari puzzle HTML ebooks')
    parser.add_argument('--sizes', nargs='+', type=int, default=[6, 8, 10, 12],
                       help='Puzzle sizes to include')
    parser.add_argument('--difficulties', nargs='+', default=['easy', 'medium', 'hard'],
                       help='Difficulties to include')
    parser.add_argument('--count', type=int, default=10,
                       help='Puzzles per size/difficulty combination')
    parser.add_argument('--output', type=str, default='akari_zen_ebook.html',
                       help='Output HTML filename')
    parser.add_argument('--title', type=str, default='Akari: Zen Logic Puzzles',
                       help='Ebook title')
    
    args = parser.parse_args()
    
    # Configuration
    config = {
        'api_url': 'https://shrinepuzzle.com/api/puzzle_receiver.php',
        'api_key': 'shrine_puzzle_api_key_2024'
    }
    
    generator = HTMLEbookGenerator(config)
    
    # Generate puzzles for ebook
    print(f"🎯 Generating {args.count} puzzles per size/difficulty combination...")
    puzzles = generator.puzzle_generator.generate_ebook_puzzles(args.sizes, args.count)
    
    # Filter by difficulties
    puzzles = [p for p in puzzles if p['difficulty'] in args.difficulties]
    
    print(f"✨ Generated {len(puzzles)} puzzles for zen HTML ebook")
    
    # Generate beautiful HTML
    generator.generate_ebook(puzzles, args.output, args.title)
    
    print(f"🎨 Beautiful zen HTML ebook created with {len(puzzles)} puzzles")
    print(f"🌐 Open {args.output} in your browser to view")
    print(f"🖨️  Press Ctrl+P to print as PDF with zen styling")

if __name__ == "__main__":
    main()
