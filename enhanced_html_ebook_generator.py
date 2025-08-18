#!/usr/bin/env python3
"""
Enhanced HTML Ebook Generator for Akari Puzzles
Integrates with Raspberry Pi setup and includes advanced print optimization
"""

import json
import argparse
from datetime import datetime
from typing import List, Dict, Optional
import os
from pathlib import Path
import subprocess
import webbrowser
from akari_generator_api import AkariPuzzleGeneratorAPI

class EnhancedHTMLEbookGenerator:
    def __init__(self, config: Dict):
        self.config = config
        self.puzzle_generator = AkariPuzzleGeneratorAPI(
            config.get('api_url', 'https://shrinepuzzle.com/api/puzzle_receiver.php'),
            config.get('api_key', 'shrine_puzzle_api_key_2024')
        )
        
        # Enhanced zen-like Japanese color palette
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
            'print_bg': '#ffffff',     # Pure white for print
            'print_text': '#000000',   # Pure black for print
        }
        
    def create_puzzle_grid_html(self, layout: List[List], size: int, puzzle_num: int, is_solution: bool = False) -> str:
        """Convert puzzle layout to HTML grid with enhanced zen styling"""
        html = f'<div class="puzzle-grid puzzle-{puzzle_num} {"solution" if is_solution else ""}">\n'
        
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
        """Create a solution grid (empty for user to fill) with enhanced styling"""
        html = f'<div class="solution-grid puzzle-{puzzle_num}">\n'
        
        # Add column headers
        html += '  <div class="grid-header">\n'
        html += '    <div class="corner-cell"></div>\n'
        for i in range(size):
            html += f'    <div class="header-cell">{chr(65 + i)}</div>\n'
        html += '  </div>\n'
        
        # Add empty rows with enhanced styling
        for i in range(size):
            html += f'  <div class="grid-row">\n'
            html += f'    <div class="row-header">{i + 1}</div>\n'
            for j in range(size):
                # Check if this cell should be a wall based on original layout
                original_cell = layout[i][j]
                if original_cell == 'X':
                    html += '    <div class="cell wall"></div>\n'
                elif original_cell != 0:
                    html += f'    <div class="cell wall number" data-value="{original_cell}">{original_cell}</div>\n'
                else:
                    html += '    <div class="cell empty solution-cell"></div>\n'
            html += '  </div>\n'
        
        html += '</div>'
        return html
    
    def generate_enhanced_css(self, include_print_optimization: bool = True) -> str:
        """Generate enhanced zen-like CSS with advanced print styling"""
        css = f"""
/* Enhanced Zen-like Akari Puzzle Ebook Styles */
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
    --print-bg: {self.colors['print_bg']};
    --print-text: {self.colors['print_text']};
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
    transition: all 0.3s ease;
}}

/* Enhanced Typography */
h1 {{
    font-size: 2.5rem;
    font-weight: 700;
    text-align: center;
    color: var(--primary);
    margin-bottom: 1rem;
    letter-spacing: 2px;
    background: linear-gradient(45deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

h2 {{
    font-size: 1.8rem;
    font-weight: 600;
    color: var(--secondary);
    margin: 2rem 0 1rem;
    border-bottom: 2px solid var(--accent);
    padding-bottom: 0.5rem;
    position: relative;
}}

h2::after {{
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 50px;
    height: 2px;
    background: var(--primary);
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

/* Enhanced Zen-inspired decorative elements */
.zen-divider {{
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    margin: 2rem 0;
    border-radius: 1px;
    position: relative;
}}

.zen-divider::before {{
    content: '❦';
    position: absolute;
    top: -8px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--bg);
    padding: 0 1rem;
    color: var(--accent);
    font-size: 1.2rem;
}}

.zen-quote {{
    font-style: italic;
    text-align: center;
    color: var(--text-muted);
    font-size: 1.1rem;
    margin: 2rem 0;
    padding: 1.5rem;
    border-left: 4px solid var(--accent);
    background: linear-gradient(135deg, rgba(232, 192, 117, 0.1), rgba(179, 27, 27, 0.05));
    border-radius: 0 10px 10px 0;
    position: relative;
}}

.zen-quote::before {{
    content: '"';
    font-size: 3rem;
    color: var(--accent);
    position: absolute;
    top: -10px;
    left: 20px;
    font-family: serif;
}}

/* Enhanced Puzzle Grid Styles */
.puzzle-container {{
    margin: 2rem 0;
    page-break-inside: avoid;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 15px;
    padding: 1.5rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--grid-line);
}}

.puzzle-header {{
    text-align: center;
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: linear-gradient(135deg, rgba(179, 27, 27, 0.1), rgba(106, 143, 95, 0.1));
    border-radius: 10px;
    border: 1px solid rgba(179, 27, 27, 0.2);
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
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
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
    transition: all 0.2s ease;
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
    position: relative;
}}

.cell.wall.number::before {{
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    right: 2px;
    bottom: 2px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 2px;
}}

.solution-cell {{
    border: 2px dashed var(--grid-line);
    background: var(--white);
    position: relative;
}}

.solution-cell::before {{
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 4px;
    height: 4px;
    background: var(--grid-line);
    border-radius: 50%;
    opacity: 0.3;
}}

/* Enhanced Rules Section */
.rules-section {{
    background: rgba(255, 255, 255, 0.9);
    padding: 2rem;
    border-radius: 15px;
    border: 1px solid var(--grid-line);
    margin: 2rem 0;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}}

.rules-list {{
    list-style: none;
    padding: 0;
}}

.rules-list li {{
    margin-bottom: 1rem;
    padding-left: 2rem;
    position: relative;
    line-height: 1.6;
}}

.rules-list li::before {{
    content: "❦";
    color: var(--primary);
    font-weight: bold;
    position: absolute;
    left: 0;
    top: 0;
}}

/* Enhanced Table of Contents */
.toc {{
    background: rgba(255, 255, 255, 0.95);
    padding: 2rem;
    border-radius: 15px;
    border: 1px solid var(--grid-line);
    margin: 2rem 0;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}}

.toc-item {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.8rem 0;
    border-bottom: 1px solid var(--grid-line);
    transition: all 0.2s ease;
}}

.toc-item:hover {{
    background: rgba(179, 27, 27, 0.05);
    padding-left: 0.5rem;
    border-radius: 5px;
}}

.toc-item:last-child {{
    border-bottom: none;
}}

.toc-number {{
    font-weight: 700;
    color: var(--primary);
    min-width: 2rem;
    background: var(--primary);
    color: white;
    border-radius: 50%;
    width: 2rem;
    height: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
}}

.toc-title {{
    flex: 1;
    margin-left: 1rem;
    font-weight: 500;
}}

.toc-difficulty {{
    color: var(--text-muted);
    font-size: 0.9rem;
    padding: 0.3rem 0.8rem;
    background: var(--accent);
    color: var(--text);
    border-radius: 15px;
    font-weight: 600;
}}

/* Print Button */
.print-button {{
    position: fixed;
    top: 2rem;
    right: 2rem;
    background: var(--primary);
    color: white;
    border: none;
    padding: 1rem 1.5rem;
    border-radius: 50px;
    cursor: pointer;
    font-family: inherit;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(179, 27, 27, 0.3);
    transition: all 0.3s ease;
    z-index: 1000;
}}

.print-button:hover {{
    background: var(--secondary);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(106, 143, 95, 0.4);
}}

.print-button:active {{
    transform: translateY(0);
}}

/* Enhanced Print Styles */
@media print {{
    body {{
        background: var(--print-bg) !important;
        color: var(--print-text) !important;
        font-size: 12pt;
        line-height: 1.4;
        padding: 0 !important;
        margin: 0 !important;
        max-width: none !important;
    }}
    
    .print-button {{
        display: none !important;
    }}
    
    h1 {{
        font-size: 24pt !important;
        color: var(--print-text) !important;
        margin-bottom: 0.5rem !important;
        -webkit-text-fill-color: var(--print-text) !important;
        background: none !important;
    }}
    
    h2 {{
        font-size: 18pt !important;
        color: var(--print-text) !important;
        margin: 1rem 0 0.5rem !important;
        border-bottom: 1px solid #ccc !important;
    }}
    
    h2::after {{
        display: none !important;
    }}
    
    h3 {{
        font-size: 14pt !important;
        color: var(--print-text) !important;
        margin: 1rem 0 0.3rem !important;
    }}
    
    .puzzle-grid, .solution-grid {{
        page-break-inside: avoid !important;
        margin: 1rem auto !important;
        box-shadow: none !important;
    }}
    
    .puzzle-container {{
        page-break-inside: avoid !important;
        margin: 1rem 0 !important;
        background: white !important;
        box-shadow: none !important;
        border: 1px solid #ccc !important;
    }}
    
    .zen-divider {{
        display: none !important;
    }}
    
    .zen-quote {{
        background: none !important;
        border-left: 2px solid #ccc !important;
        color: #666 !important;
    }}
    
    .zen-quote::before {{
        display: none !important;
    }}
    
    .rules-section, .toc {{
        background: white !important;
        border: 1px solid #ccc !important;
        padding: 1rem !important;
        box-shadow: none !important;
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
    
    .cell.wall.number::before {{
        display: none !important;
    }}
    
    .cell.empty {{
        background: white !important;
        border: 1px solid #ccc !important;
    }}
    
    .solution-cell {{
        border: 2px dashed #ccc !important;
        background: white !important;
    }}
    
    .solution-cell::before {{
        display: none !important;
    }}
    
    .toc-item:hover {{
        background: none !important;
        padding-left: 0 !important;
    }}
    
    .toc-number {{
        background: #333 !important;
        color: white !important;
    }}
    
    .toc-difficulty {{
        background: #f0f0f0 !important;
        color: #333 !important;
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
    
    /* Optimize for A4 paper */
    @page {{
        size: A4;
        margin: 1cm;
    }}
}}

/* Responsive Design */
@media (max-width: 768px) {{
    body {{
        padding: 1rem;
    }}
    
    .print-button {{
        position: static;
        margin: 1rem auto;
        display: block;
        width: fit-content;
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
    
    .rules-section, .toc, .puzzle-container {{
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.1);
    }}
}}
"""
        
        return css
    
    def generate_ebook(self, puzzles: List[Dict], output_file: str, title: str = "Akari: Zen Logic Puzzles", 
                      auto_open: bool = False, include_print_button: bool = True):
        """Generate a beautiful HTML ebook with enhanced zen-like Japanese aesthetic"""
        
        # Generate CSS
        css = self.generate_enhanced_css()
        
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
    {f'<button class="print-button" onclick="printEbook()">🖨️ Print PDF</button>' if include_print_button else ''}
    
    <header>
        <h1>{title}</h1>
        <div class="zen-quote">
            In the art of illumination, find the perfect balance of light and shadow
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
                <span class="toc-number">{i}</span>
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
            
            <div style="text-align: center; margin: 1.5rem 0;">
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
                {self.create_puzzle_grid_html(layout, size, f"solution-{i}", is_solution=True)}
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
        // Enhanced print functionality
        function printEbook() {{
            window.print();
        }}
        
        // Add keyboard shortcuts
        document.addEventListener('keydown', function(e) {{
            if (e.ctrlKey && e.key === 'p') {{
                e.preventDefault();
                printEbook();
            }}
            if (e.ctrlKey && e.key === 'Enter') {{
                printEbook();
            }}
        }});
        
        // Auto-adjust grid sizes based on puzzle size
        document.addEventListener('DOMContentLoaded', function() {{
            const grids = document.querySelectorAll('.puzzle-grid, .solution-grid');
            grids.forEach(grid => {{
                const size = grid.querySelectorAll('.grid-row').length;
                if (size > 8) {{
                    grid.style.setProperty('--cell-size', '2rem');
                }} else if (size > 6) {{
                    grid.style.setProperty('--cell-size', '2.2rem');
                }} else {{
                    grid.style.setProperty('--cell-size', '2.5rem');
                }}
            }});
            
            // Add smooth scrolling for TOC items
            const tocItems = document.querySelectorAll('.toc-item');
            tocItems.forEach((item, index) => {{
                item.addEventListener('click', function() {{
                    const puzzleSection = document.querySelectorAll('.puzzle-container')[index];
                    if (puzzleSection) {{
                        puzzleSection.scrollIntoView({{ behavior: 'smooth' }});
                    }}
                }});
                item.style.cursor = 'pointer';
            }});
        }});
        
        // Add print optimization
        window.addEventListener('beforeprint', function() {{
            document.body.classList.add('printing');
        }});
        
        window.addEventListener('afterprint', function() {{
            document.body.classList.remove('printing');
        }});
    </script>
</body>
</html>
"""
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✨ Enhanced zen HTML ebook generated: {output_file}")
        print(f"📄 Open in browser and press Ctrl+P to print as PDF")
        
        # Auto-open in browser if requested
        if auto_open:
            try:
                webbrowser.open(f'file://{os.path.abspath(output_file)}')
                print(f"🌐 Opened {output_file} in browser")
            except Exception as e:
                print(f"⚠️  Could not auto-open browser: {e}")

def main():
    parser = argparse.ArgumentParser(description='Generate enhanced Akari puzzle HTML ebooks')
    parser.add_argument('--sizes', nargs='+', type=int, default=[6, 8, 10, 12],
                       help='Puzzle sizes to include')
    parser.add_argument('--difficulties', nargs='+', default=['easy', 'medium', 'hard'],
                       help='Difficulties to include')
    parser.add_argument('--count', type=int, default=10,
                       help='Puzzles per size/difficulty combination')
    parser.add_argument('--output', type=str, default='akari_zen_ebook_enhanced.html',
                       help='Output HTML filename')
    parser.add_argument('--title', type=str, default='Akari: Zen Logic Puzzles',
                       help='Ebook title')
    parser.add_argument('--auto-open', action='store_true',
                       help='Automatically open in browser after generation')
    parser.add_argument('--no-print-button', action='store_true',
                       help='Hide the print button')
    
    args = parser.parse_args()
    
    # Configuration
    config = {
        'api_url': 'https://shrinepuzzle.com/api/puzzle_receiver.php',
        'api_key': 'shrine_puzzle_api_key_2024'
    }
    
    generator = EnhancedHTMLEbookGenerator(config)
    
    # Generate puzzles for ebook
    print(f"🎯 Generating {args.count} puzzles per size/difficulty combination...")
    puzzles = generator.puzzle_generator.generate_ebook_puzzles(args.sizes, args.count)
    
    # Filter by difficulties
    puzzles = [p for p in puzzles if p['difficulty'] in args.difficulties]
    
    print(f"✨ Generated {len(puzzles)} puzzles for enhanced zen HTML ebook")
    
    # Generate beautiful HTML
    generator.generate_ebook(
        puzzles, 
        args.output, 
        args.title,
        auto_open=args.auto_open,
        include_print_button=not args.no_print_button
    )
    
    print(f"🎨 Enhanced zen HTML ebook created with {len(puzzles)} puzzles")
    print(f"🌐 Open {args.output} in your browser to view")
    print(f"🖨️  Press Ctrl+P or click the print button to print as PDF")

if __name__ == "__main__":
    main()
