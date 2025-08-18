#!/usr/bin/env python3
"""
Ebook Generator for Akari Puzzles
Creates beautiful, zen-like Japanese PDF ebooks with puzzles and solutions
"""

import json
import argparse
from datetime import datetime
from typing import List, Dict
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from akari_generator_api import AkariPuzzleGeneratorAPI

class EbookGenerator:
    def __init__(self, config: Dict):
        self.config = config
        # Use API version instead of database version
        self.puzzle_generator = AkariPuzzleGeneratorAPI(
            config.get('api_url', 'https://shrinepuzzle.com/api/puzzle_receiver.php'),
            config.get('api_key', 'shrine_puzzle_api_key_2024')
        )
        
        # Zen-like Japanese color palette
        self.colors = {
            'primary': colors.HexColor('#2C3E50'),      # Dark blue-gray
            'secondary': colors.HexColor('#34495E'),    # Lighter blue-gray
            'accent': colors.HexColor('#E74C3C'),       # Soft red
            'warm': colors.HexColor('#F39C12'),         # Warm orange
            'light': colors.HexColor('#ECF0F1'),        # Light gray
            'white': colors.white,
            'black': colors.black,
            'grid_line': colors.HexColor('#BDC3C7'),    # Soft gray for grid lines
            'wall': colors.HexColor('#34495E'),         # Dark walls
            'number': colors.HexColor('#2C3E50'),       # Dark numbers
            'cell_bg': colors.HexColor('#F8F9FA'),      # Very light background
        }
        
    def create_puzzle_grid(self, layout: List[List], size: int) -> List[List]:
        """Convert puzzle layout to printable grid with zen styling"""
        grid = []
        
        # Add column headers (A, B, C, ...) with zen styling
        header = [''] + [chr(65 + i) for i in range(size)]
        grid.append(header)
        
        # Add rows with row numbers
        for i, row in enumerate(layout):
            grid_row = [str(i + 1)] + [str(cell) if cell != 0 else '' for cell in row]
            grid.append(grid_row)
        
        return grid
    
    def create_solution_grid(self, layout: List[List], size: int) -> List[List]:
        """Create a solution grid (empty for user to fill) with zen styling"""
        grid = []
        
        # Add column headers
        header = [''] + [chr(65 + i) for i in range(size)]
        grid.append(header)
        
        # Add empty rows
        for i in range(size):
            grid_row = [str(i + 1)] + [''] * size
            grid.append(grid_row)
        
        return grid
    
    def create_zen_table_style(self, size: int, is_solution: bool = False) -> TableStyle:
        """Create a zen-like table style for puzzle grids"""
        style = TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('BACKGROUND', (0, 0), (0, -1), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.colors['white']),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            
            # Grid styling
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['grid_line']),
            ('BACKGROUND', (1, 1), (-1, -1), self.colors['cell_bg']),
            
            # Cell-specific styling
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (1, 1), (-1, -1), 12),
            ('TEXTCOLOR', (1, 1), (-1, -1), self.colors['number']),
        ])
        
        return style
    
    def generate_ebook(self, puzzles: List[Dict], output_file: str, title: str = "Akari Puzzle Collection"):
        """Generate a beautiful PDF ebook with zen-like Japanese aesthetic"""
        doc = SimpleDocTemplate(output_file, pagesize=A4, 
                              leftMargin=1*inch, rightMargin=1*inch,
                              topMargin=1*inch, bottomMargin=1*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Zen-inspired custom styles
        title_style = ParagraphStyle(
            'ZenTitle',
            parent=styles['Heading1'],
            fontSize=32,
            spaceAfter=40,
            alignment=TA_CENTER,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold',
            leading=36
        )
        
        subtitle_style = ParagraphStyle(
            'ZenSubtitle',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=25,
            alignment=TA_CENTER,
            textColor=self.colors['secondary'],
            fontName='Helvetica',
            leading=22
        )
        
        section_style = ParagraphStyle(
            'ZenSection',
            parent=styles['Heading2'],
            fontSize=20,
            spaceAfter=15,
            alignment=TA_LEFT,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold',
            leading=24
        )
        
        puzzle_style = ParagraphStyle(
            'ZenPuzzle',
            parent=styles['Heading3'],
            fontSize=16,
            spaceAfter=12,
            alignment=TA_LEFT,
            textColor=self.colors['secondary'],
            fontName='Helvetica-Bold',
            leading=20
        )
        
        body_style = ParagraphStyle(
            'ZenBody',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            alignment=TA_LEFT,
            textColor=self.colors['primary'],
            fontName='Helvetica',
            leading=16
        )
        
        # Beautiful title page
        story.append(Paragraph(f"<b>{title}</b>", title_style))
        story.append(Spacer(1, 30))
        
        # Zen-inspired subtitle
        zen_subtitle = f"<i>Japanese Logic Puzzles for Mindful Practice</i>"
        story.append(Paragraph(zen_subtitle, subtitle_style))
        story.append(Spacer(1, 40))
        
        # Generation info with zen styling
        gen_info = f"<b>Generated with care on</b> {datetime.now().strftime('%B %d, %Y')}"
        story.append(Paragraph(gen_info, body_style))
        story.append(Spacer(1, 50))
        
        # Decorative line
        story.append(HRFlowable(width="100%", thickness=2, color=self.colors['accent'], spaceBefore=20, spaceAfter=20))
        
        # How to play section with zen styling
        story.append(Paragraph("How to Play Akari (Light Up)", section_style))
        story.append(Spacer(1, 15))
        
        rules_text = """
        <b>The Art of Illumination:</b><br/>
        • Place light bulbs in white cells to illuminate the entire board<br/>
        • Light travels in straight lines until blocked by walls<br/>
        • No two bulbs may shine on each other<br/>
        • Numbered walls must have exactly that many adjacent bulbs<br/>
        • Every white cell must be lit or contain a bulb<br/>
        • Find the perfect balance of light and shadow
        """
        story.append(Paragraph(rules_text, body_style))
        story.append(PageBreak())
        
        # Table of contents with zen styling
        story.append(Paragraph("Contents", section_style))
        story.append(Spacer(1, 20))
        
        for i, puzzle in enumerate(puzzles, 1):
            toc_entry = f"<b>{i}.</b> {puzzle['size']}×{puzzle['size']} {puzzle['difficulty'].title()} Puzzle"
            story.append(Paragraph(toc_entry, body_style))
        
        story.append(PageBreak())
        
        # Puzzles section
        story.append(Paragraph("Puzzles", section_style))
        story.append(Spacer(1, 25))
        
        for i, puzzle in enumerate(puzzles, 1):
            size = puzzle['size']
            layout = puzzle['layout']
            
            # Puzzle header with zen styling
            puzzle_header = f"<b>Puzzle {i}:</b> {size}×{size} {puzzle['difficulty'].title()}"
            story.append(Paragraph(puzzle_header, puzzle_style))
            story.append(Spacer(1, 15))
            
            # Calculate optimal cell size based on puzzle size
            if size <= 6:
                cell_size = 0.5 * inch
                header_size = 0.4 * inch
            elif size <= 8:
                cell_size = 0.4 * inch
                header_size = 0.35 * inch
            else:
                cell_size = 0.35 * inch
                header_size = 0.3 * inch
            
            # Puzzle grid with zen styling
            puzzle_grid = self.create_puzzle_grid(layout, size)
            puzzle_table = Table(puzzle_grid, colWidths=[header_size] + [cell_size]*size)
            puzzle_table.setStyle(self.create_zen_table_style(size))
            story.append(puzzle_table)
            story.append(Spacer(1, 25))
            
            # Solution grid label
            story.append(Paragraph("<b>Your Solution:</b>", body_style))
            story.append(Spacer(1, 10))
            
            # Solution grid
            solution_grid = self.create_solution_grid(layout, size)
            solution_table = Table(solution_grid, colWidths=[header_size] + [cell_size]*size)
            solution_table.setStyle(self.create_zen_table_style(size, is_solution=True))
            story.append(solution_table)
            story.append(PageBreak())
        
        # Solutions section with zen styling
        story.append(Paragraph("Solutions", section_style))
        story.append(Spacer(1, 25))
        
        for i, puzzle in enumerate(puzzles, 1):
            size = puzzle['size']
            layout = puzzle['layout']
            
            # Solution header
            solution_header = f"<b>Solution {i}:</b> {size}×{size} {puzzle['difficulty'].title()}"
            story.append(Paragraph(solution_header, puzzle_style))
            story.append(Spacer(1, 15))
            
            # Calculate cell sizes
            if size <= 6:
                cell_size = 0.5 * inch
                header_size = 0.4 * inch
            elif size <= 8:
                cell_size = 0.4 * inch
                header_size = 0.35 * inch
            else:
                cell_size = 0.35 * inch
                header_size = 0.3 * inch
            
            # Solution grid (showing original layout as solution for now)
            solution_grid = self.create_puzzle_grid(layout, size)
            solution_table = Table(solution_grid, colWidths=[header_size] + [cell_size]*size)
            solution_table.setStyle(self.create_zen_table_style(size))
            story.append(solution_table)
            story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        print(f"✨ Beautiful zen ebook generated: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Generate beautiful Akari puzzle ebooks')
    parser.add_argument('--sizes', nargs='+', type=int, default=[6, 8, 10, 12],
                       help='Puzzle sizes to include')
    parser.add_argument('--difficulties', nargs='+', default=['easy', 'medium', 'hard'],
                       help='Difficulties to include')
    parser.add_argument('--count', type=int, default=10,
                       help='Puzzles per size/difficulty combination')
    parser.add_argument('--output', type=str, default='akari_zen_ebook.pdf',
                       help='Output PDF filename')
    parser.add_argument('--title', type=str, default='Akari: Zen Logic Puzzles',
                       help='Ebook title')
    
    args = parser.parse_args()
    
    # Configuration (API-based instead of database)
    config = {
        'api_url': 'https://shrinepuzzle.com/api/puzzle_receiver.php',
        'api_key': 'shrine_puzzle_api_key_2024'
    }
    
    generator = EbookGenerator(config)
    
    # Generate puzzles for ebook using API version
    print(f"🎯 Generating {args.count} puzzles per size/difficulty combination...")
    puzzles = generator.puzzle_generator.generate_ebook_puzzles(args.sizes, args.count)
    
    # Filter by difficulties
    puzzles = [p for p in puzzles if p['difficulty'] in args.difficulties]
    
    print(f"✨ Generated {len(puzzles)} puzzles for zen ebook")
    
    # Generate beautiful PDF
    generator.generate_ebook(puzzles, args.output, args.title)
    
    print(f"🎨 Beautiful zen ebook created with {len(puzzles)} puzzles")

if __name__ == "__main__":
    main()
