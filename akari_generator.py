#!/usr/bin/env python3
"""
Akari Puzzle Generator for Raspberry Pi 5
Generates solvable Akari puzzles and sends them to database
"""

import json
import random
import time
import hashlib
import mysql.connector
from mysql.connector import Error
import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('akari_generator.log'),
        logging.StreamHandler()
    ]
)

class AkariPuzzleGenerator:
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.connection = None
        
    def connect_db(self):
        """Connect to MySQL database"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            logging.info("Database connection established")
            return True
        except Error as e:
            logging.error(f"Database connection failed: {e}")
            return False
    
    def disconnect_db(self):
        """Disconnect from database"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.info("Database connection closed")
    
    def generate_seed(self, layout: List[List]) -> str:
        """Generate a unique seed from layout"""
        layout_str = json.dumps(layout, sort_keys=True)
        return hashlib.md5(layout_str.encode()).hexdigest()[:12]
    
    def is_valid_akari_layout(self, layout: List[List], size: int) -> bool:
        """Check if layout is a valid Akari puzzle"""
        # Check if all cells are valid
        for y in range(size):
            for x in range(size):
                cell = layout[y][x]
                if cell not in [0, 'X'] and not (isinstance(cell, str) and cell.isdigit() and 0 <= int(cell) <= 4):
                    return False
        
        # Check if numbered cells have valid numbers
        for y in range(size):
            for x in range(size):
                if isinstance(layout[y][x], str) and layout[y][x].isdigit():
                    number = int(layout[y][x])
                    if number > 4:  # Max 4 adjacent cells
                        return False
        
        return True
    
    def count_adjacent_whites(self, layout: List[List], x: int, y: int, size: int) -> int:
        """Count adjacent white cells to a numbered cell"""
        count = 0
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < size and 0 <= ny < size and layout[ny][nx] == 0:
                count += 1
        return count
    
    def generate_random_layout(self, size: int, wall_ratio: float = 0.25, number_ratio: float = 0.4) -> List[List]:
        """Generate a random Akari layout"""
        layout = [[0 for _ in range(size)] for _ in range(size)]
        
        # Add random walls
        for y in range(size):
            for x in range(size):
                if random.random() < wall_ratio:
                    layout[y][x] = 'X'
        
        # Add numbers to some walls
        for y in range(size):
            for x in range(size):
                if layout[y][x] == 'X' and random.random() < number_ratio:
                    adjacent_whites = self.count_adjacent_whites(layout, x, y, size)
                    if adjacent_whites > 0:
                        layout[y][x] = str(random.randint(0, min(adjacent_whites, 4)))
        
        return layout
    
    def is_solvable(self, layout: List[List], size: int) -> bool:
        """
        Basic solvability check for Akari puzzles
        This is a simplified check - full solvability requires solving the puzzle
        """
        # Check if there are enough white cells
        white_cells = sum(1 for row in layout for cell in row if cell == 0)
        if white_cells < size:  # Need at least size white cells
            return False
        
        # Check if numbered cells have reasonable constraints
        for y in range(size):
            for x in range(size):
                if isinstance(layout[y][x], str) and layout[y][x].isdigit():
                    number = int(layout[y][x])
                    adjacent_whites = self.count_adjacent_whites(layout, x, y, size)
                    if number > adjacent_whites:
                        return False
        
        return True
    
    def generate_puzzle(self, size: int, difficulty: str = 'medium') -> Optional[Dict]:
        """Generate a single Akari puzzle"""
        # Adjust parameters based on difficulty
        difficulty_params = {
            'easy': {'wall_ratio': 0.2, 'number_ratio': 0.3, 'max_attempts': 50},
            'medium': {'wall_ratio': 0.25, 'number_ratio': 0.4, 'max_attempts': 100},
            'hard': {'wall_ratio': 0.3, 'number_ratio': 0.5, 'max_attempts': 200},
            'expert': {'wall_ratio': 0.35, 'number_ratio': 0.6, 'max_attempts': 300}
        }
        
        params = difficulty_params.get(difficulty, difficulty_params['medium'])
        
        for attempt in range(params['max_attempts']):
            layout = self.generate_random_layout(size, params['wall_ratio'], params['number_ratio'])
            
            if self.is_valid_akari_layout(layout, size) and self.is_solvable(layout, size):
                seed = self.generate_seed(layout)
                return {
                    'layout': layout,
                    'seed': seed,
                    'size': size,
                    'difficulty': difficulty
                }
        
        logging.warning(f"Failed to generate {difficulty} {size}x{size} puzzle after {params['max_attempts']} attempts")
        return None
    
    def save_puzzle_to_db(self, puzzle: Dict, mode: str = 'premium', date: Optional[str] = None) -> bool:
        """Save puzzle to database"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect_db():
                return False
        
        try:
            cursor = self.connection.cursor()
            
            # Use provided date or generate future date for premium puzzles
            if date is None:
                if mode == 'premium':
                    # Generate puzzles for next 30 days
                    puzzle_date = datetime.now() + timedelta(days=random.randint(1, 30))
                    date = puzzle_date.strftime('%Y-%m-%d')
                else:
                    date = datetime.now().strftime('%Y-%m-%d')
            
            # Check if puzzle already exists
            check_query = """
                SELECT id FROM puzzles 
                WHERE game = 'akari' AND mode = %s AND date = %s AND seed = %s
            """
            cursor.execute(check_query, (mode, date, puzzle['seed']))
            
            if cursor.fetchone():
                logging.info(f"Puzzle already exists for {mode} {date}")
                return True
            
            # Insert new puzzle
            insert_query = """
                INSERT INTO puzzles (game, seed, layout, size, mode, date, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            
            layout_json = json.dumps(puzzle['layout'])
            cursor.execute(insert_query, (
                'akari',
                puzzle['seed'],
                layout_json,
                puzzle['size'],
                mode,
                date
            ))
            
            self.connection.commit()
            logging.info(f"Saved {puzzle['size']}x{puzzle['size']} {puzzle['difficulty']} puzzle for {mode} {date}")
            return True
            
        except Error as e:
            logging.error(f"Database error: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def generate_batch(self, sizes: List[int], difficulties: List[str], 
                      count_per_size: int = 10, mode: str = 'premium') -> Dict:
        """Generate a batch of puzzles"""
        results = {
            'total_generated': 0,
            'total_saved': 0,
            'failed': 0,
            'by_size': {},
            'by_difficulty': {}
        }
        
        for size in sizes:
            results['by_size'][size] = 0
            for difficulty in difficulties:
                results['by_difficulty'][difficulty] = 0
                
                logging.info(f"Generating {count_per_size} {difficulty} {size}x{size} puzzles...")
                
                for i in range(count_per_size):
                    puzzle = self.generate_puzzle(size, difficulty)
                    if puzzle:
                        results['total_generated'] += 1
                        results['by_size'][size] += 1
                        results['by_difficulty'][difficulty] += 1
                        
                        if self.save_puzzle_to_db(puzzle, mode):
                            results['total_saved'] += 1
                        else:
                            results['failed'] += 1
                    else:
                        results['failed'] += 1
                    
                    # Small delay to prevent overwhelming the system
                    time.sleep(0.1)
        
        return results
    
    def generate_ebook_puzzles(self, sizes: List[int], count_per_size: int = 20) -> List[Dict]:
        """Generate puzzles specifically for ebooks (no database save)"""
        ebook_puzzles = []
        
        for size in sizes:
            for difficulty in ['easy', 'medium', 'hard']:
                logging.info(f"Generating {count_per_size} {difficulty} {size}x{size} puzzles for ebook...")
                
                for i in range(count_per_size):
                    puzzle = self.generate_puzzle(size, difficulty)
                    if puzzle:
                        puzzle['ebook_id'] = f"ebook_{size}_{difficulty}_{i+1:03d}"
                        puzzle['solution_hint'] = self.generate_solution_hint(puzzle['layout'], size)
                        ebook_puzzles.append(puzzle)
                    
                    time.sleep(0.1)
        
        return ebook_puzzles
    
    def generate_solution_hint(self, layout: List[List], size: int) -> str:
        """Generate a hint for the solution (for ebooks)"""
        # Count total white cells
        white_cells = sum(1 for row in layout for cell in row if cell == 0)
        
        # Count numbered cells
        numbered_cells = sum(1 for row in layout for cell in row 
                           if isinstance(cell, str) and cell.isdigit() and cell != '0')
        
        return f"White cells: {white_cells}, Numbered cells: {numbered_cells}"
    
    def save_ebook_puzzles(self, puzzles: List[Dict], filename: str):
        """Save ebook puzzles to JSON file"""
        ebook_data = {
            'generated_at': datetime.now().isoformat(),
            'total_puzzles': len(puzzles),
            'puzzles': puzzles
        }
        
        with open(filename, 'w') as f:
            json.dump(ebook_data, f, indent=2)
        
        logging.info(f"Saved {len(puzzles)} puzzles to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Generate Akari puzzles for Raspberry Pi 5')
    parser.add_argument('--mode', choices=['premium', 'daily', 'ebook'], default='premium',
                       help='Generation mode')
    parser.add_argument('--sizes', nargs='+', type=int, default=[6, 8, 10, 12],
                       help='Puzzle sizes to generate')
    parser.add_argument('--difficulties', nargs='+', default=['easy', 'medium', 'hard'],
                       help='Difficulties to generate')
    parser.add_argument('--count', type=int, default=10,
                       help='Number of puzzles per size/difficulty combination')
    parser.add_argument('--output', type=str, default='ebook_puzzles.json',
                       help='Output file for ebook puzzles')
    
    args = parser.parse_args()
    
    # Database configuration
    db_config = {
        'host': 'localhost',
        'user': 'spectrum_shrine_user',
        'password': 'ehq-!yhv~3soe^jx',
        'database': 'spectrum_shrinepuz',
        'charset': 'utf8mb4'
    }
    
    generator = AkariPuzzleGenerator(db_config)
    
    if args.mode == 'ebook':
        # Generate puzzles for ebooks
        puzzles = generator.generate_ebook_puzzles(args.sizes, args.count)
        generator.save_ebook_puzzles(puzzles, args.output)
        logging.info(f"Generated {len(puzzles)} puzzles for ebook")
        
    else:
        # Generate puzzles for database
        if generator.connect_db():
            results = generator.generate_batch(args.sizes, args.difficulties, args.count, args.mode)
            generator.disconnect_db()
            
            logging.info("Generation complete!")
            logging.info(f"Total generated: {results['total_generated']}")
            logging.info(f"Total saved: {results['total_saved']}")
            logging.info(f"Failed: {results['failed']}")
            logging.info(f"By size: {results['by_size']}")
            logging.info(f"By difficulty: {results['by_difficulty']}")

if __name__ == "__main__":
    main()
