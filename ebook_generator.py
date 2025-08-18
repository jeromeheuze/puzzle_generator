#!/usr/bin/env python3
"""
Ebook Generator for Akari Puzzles
Creates printable PDF ebooks with puzzles and solutions
"""

import json
import argparse
from datetime import datetime
from typing import List, Dict
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from akari_generator import AkariPuzzleGenerator

class EbookGenerator:
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.puzzle_generator = AkariPuzzleGenerator(db_config)
        
    def create_puzzle_grid(self, layout: List[List], size: int) -> List[List]:
        """Convert puzzle layout to printable grid"""
        grid = []
        
        # Add column headers (A, B, C, ...)
        header = [''] + [chr(65 + i) for i in range(size)]
        grid.append(header)
        
        # Add rows with row numbers
        for i, row in enumerate(layout):
            grid_row = [str(i + 1)] + [str(cell) if cell != 0 else '' for cell in row]
            grid.append(grid_row)
        
        return grid
    
    def create_solution_grid(self, layout: List[List], size: int) -> List[List]:
        """Create a solution grid (empty for user to fill)"""
        grid = []
        
        # Add column headers
        header = [''] + [chr(65 + i) for i in range(size)]
        grid.append(header)
        
        # Add empty rows
        for i in range(size):
            grid_row = [str(i + 1)] + [''] * size
            grid.append(grid_row)
        
        return grid
    
    def generate_ebook(self, puzzles: List[Dict], output_file: str, title: str = "Akari Puzzle Collection"):
        """Generate a PDF ebook with puzzles"""
        doc = SimpleDocTemplate(output_file, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkred
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        puzzle_style = ParagraphStyle(
            'PuzzleTitle',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=10,
            alignment=TA_LEFT,
            textColor=colors.black
        )
        
        # Title page
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
        story.append(Spacer(1, 30))
        story.append(Paragraph("How to Play Akari:", styles['Heading2']))
        story.append(Paragraph("""
        • Place bulbs in white cells to light the entire board<br/>
        • Bulbs shine up, down, left, and right until blocked by a black cell<br/>
        • No two bulbs may shine on each other<br/>
        • Numbered black cells must have exactly that many adjacent bulbs<br/>
        • All white cells must be lit or contain a bulb<br/>
        • Use the solution grid to mark your answers
        """, styles['Normal']))
        story.append(PageBreak())
        
        # Table of contents
        story.append(Paragraph("Table of Contents", styles['Heading1']))
        story.append(Spacer(1, 20))
        
        for i, puzzle in enumerate(puzzles, 1):
            story.append(Paragraph(
                f"{i}. {puzzle['size']}x{puzzle['size']} {puzzle['difficulty'].title()} Puzzle",
                styles['Normal']
            ))
        story.append(PageBreak())
        
        # Puzzles
        for i, puzzle in enumerate(puzzles, 1):
            size = puzzle['size']
            layout = puzzle['layout']
            
            # Puzzle title
            story.append(Paragraph(
                f"Puzzle {i}: {size}x{size} {puzzle['difficulty'].title()}",
                puzzle_style
            ))
            story.append(Spacer(1, 10))
            
            # Puzzle grid
            puzzle_grid = self.create_puzzle_grid(layout, size)
            puzzle_table = Table(puzzle_grid, colWidths=[0.5*inch] + [0.4*inch]*size)
            puzzle_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (1, 1), (-1, -1), colors.white),
            ]))
            story.append(puzzle_table)
            story.append(Spacer(1, 20))
            
            # Solution grid
            story.append(Paragraph("Your Solution:", styles['Heading4']))
            solution_grid = self.create_solution_grid(layout, size)
            solution_table = Table(solution_grid, colWidths=[0.5*inch] + [0.4*inch]*size)
            solution_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (1, 1), (-1, -1), colors.white),
            ]))
            story.append(solution_table)
            story.append(PageBreak())
        
        # Solutions section
        story.append(Paragraph("Solutions", styles['Heading1']))
        story.append(Spacer(1, 20))
        
        for i, puzzle in enumerate(puzzles, 1):
            size = puzzle['size']
            layout = puzzle['layout']
            
            story.append(Paragraph(
                f"Solution {i}: {size}x{size} {puzzle['difficulty'].title()}",
                puzzle_style
            ))
            story.append(Spacer(1, 10))
            
            # For now, we'll show the original layout as "solution"
            # In a real implementation, you'd solve the puzzle
            solution_grid = self.create_puzzle_grid(layout, size)
            solution_table = Table(solution_grid, colWidths=[0.5*inch] + [0.4*inch]*size)
            solution_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (1, 1), (-1, -1), colors.white),
            ]))
            story.append(solution_table)
            story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        print(f"Ebook generated: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Generate Akari puzzle ebooks')
    parser.add_argument('--sizes', nargs='+', type=int, default=[6, 8, 10, 12],
                       help='Puzzle sizes to include')
    parser.add_argument('--difficulties', nargs='+', default=['easy', 'medium', 'hard'],
                       help='Difficulties to include')
    parser.add_argument('--count', type=int, default=10,
                       help='Puzzles per size/difficulty combination')
    parser.add_argument('--output', type=str, default='akari_ebook.pdf',
                       help='Output PDF filename')
    parser.add_argument('--title', type=str, default='Akari Puzzle Collection',
                       help='Ebook title')
    
    args = parser.parse_args()
    
    # Database configuration
    db_config = {
        'host': 'localhost',
        'user': 'spectrum_shrine_user',
        'password': 'ehq-!yhv~3soe^jx',
        'database': 'spectrum_shrinepuz',
        'charset': 'utf8mb4'
    }
    
    generator = EbookGenerator(db_config)
    
    # Generate puzzles for ebook
    print(f"Generating {args.count} puzzles per size/difficulty combination...")
    puzzles = generator.puzzle_generator.generate_ebook_puzzles(args.sizes, args.count)
    
    # Filter by difficulties
    puzzles = [p for p in puzzles if p['difficulty'] in args.difficulties]
    
    print(f"Generated {len(puzzles)} puzzles for ebook")
    
    # Generate PDF
    generator.generate_ebook(puzzles, args.output, args.title)
    
    print(f"Ebook created with {len(puzzles)} puzzles")

if __name__ == "__main__":
    main()
