#!/usr/bin/env python3
"""
Akari Puzzle Generator for Raspberry Pi 5 - API Version
Generates solvable Akari puzzles and sends them via API
"""

import json
import random
import time
import hashlib
import requests
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
        logging.FileHandler('akari_generator_api.log'),
        logging.StreamHandler()
    ]
)

class AkariPuzzleGeneratorAPI:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
        
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
        """Generate a random Akari layout with improved number placement"""
        layout = [[0 for _ in range(size)] for _ in range(size)]
        
        # Add random walls
        for y in range(size):
            for x in range(size):
                if random.random() < wall_ratio:
                    layout[y][x] = 'X'
        
        # Add numbers only to walls that have adjacent white cells
        walls_with_adjacent_whites = []
        for y in range(size):
            for x in range(size):
                if layout[y][x] == 'X':
                    adjacent_whites = self.count_adjacent_whites(layout, x, y, size)
                    if adjacent_whites > 0:
                        walls_with_adjacent_whites.append((x, y, adjacent_whites))
        
        # Add numbers to some walls with adjacent whites
        for x, y, adjacent_whites in walls_with_adjacent_whites:
            if random.random() < number_ratio:
                # Ensure number is reasonable (1 to adjacent_whites, but not 0)
                number = random.randint(1, min(adjacent_whites, 4))
                layout[y][x] = str(number)
        
        return layout
    
    def is_solvable(self, layout: List[List], size: int) -> bool:
        """
        Comprehensive solvability check for Akari puzzles
        Checks multiple criteria to ensure puzzle is well-designed and solvable
        """
        # 1. Check if there are enough white cells
        white_cells = sum(1 for row in layout for cell in row if cell == 0)
        total_cells = size * size
        
        # Need at least size white cells, but not too many
        if white_cells < size:
            return False
        
        # Too many white cells makes puzzle too easy
        if white_cells > total_cells * 0.85:
            return False
        
        # 2. Check if there are numbered cells (constraints)
        numbered_cells = []
        for y in range(size):
            for x in range(size):
                if isinstance(layout[y][x], str) and layout[y][x].isdigit():
                    numbered_cells.append((x, y, int(layout[y][x])))
        
        # Need at least some numbered cells for constraints
        if len(numbered_cells) == 0:
            return False
        
        # 3. Check if numbered cells have valid constraints
        for x, y, number in numbered_cells:
            adjacent_whites = self.count_adjacent_whites(layout, x, y, size)
            
            # Number cannot exceed adjacent white cells
            if number > adjacent_whites:
                return False
            
            # Number should be reasonable (not 0 unless it's a wall with no adjacent whites)
            if number == 0 and adjacent_whites > 0:
                return False
        
        # 4. Check for isolated white cells (cells with no path to numbered cells)
        if not self._has_connected_white_cells(layout, size):
            return False
        
        # 5. Check for reasonable difficulty balance
        wall_cells = sum(1 for row in layout for cell in row if cell == 'X')
        wall_ratio = wall_cells / total_cells
        
        # Wall ratio should be reasonable (not too sparse, not too dense)
        if wall_ratio < 0.05 or wall_ratio > 0.5:
            return False
        
        # 6. Check if puzzle has interesting structure
        if not self._has_interesting_structure(layout, size):
            return False
        
        return True
    
    def _has_connected_white_cells(self, layout: List[List], size: int) -> bool:
        """Check if white cells are connected to numbered cells"""
        # Find all white cells
        white_positions = []
        for y in range(size):
            for x in range(size):
                if layout[y][x] == 0:
                    white_positions.append((x, y))
        
        if not white_positions:
            return False
        
        # Check if at least some white cells are adjacent to numbered cells
        connected_whites = 0
        for x, y in white_positions:
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < size and 0 <= ny < size and 
                    isinstance(layout[ny][nx], str) and layout[ny][nx].isdigit()):
                    connected_whites += 1
                    break
        
        # For small puzzles (6x6), be more lenient - at least 20% connected
        # For larger puzzles, require more connections
        min_connection_ratio = 0.2 if size <= 6 else 0.3
        return connected_whites >= len(white_positions) * min_connection_ratio
    
    def _has_interesting_structure(self, layout: List[List], size: int) -> bool:
        """Check if puzzle has interesting structural elements"""
        # Count different types of numbered cells
        number_counts = {}
        for y in range(size):
            for x in range(size):
                if isinstance(layout[y][x], str) and layout[y][x].isdigit():
                    number = int(layout[y][x])
                    number_counts[number] = number_counts.get(number, 0) + 1
        
        # Should have variety in numbered cells (not all the same number)
        if len(number_counts) < 1:  # Allow single number for very small puzzles
            return False
        
        # Should have some higher numbers (2, 3, 4) for complexity, but not required for small puzzles
        has_higher_numbers = any(num >= 2 for num in number_counts.keys())
        if size >= 8 and not has_higher_numbers:  # Only require for larger puzzles
            return False
        
        # Check for reasonable distribution of numbers
        total_numbered = sum(number_counts.values())
        if total_numbered < 1 or total_numbered > size * 2:
            return False
        
        return True
    
    def generate_puzzle(self, size: int, difficulty: str = 'medium') -> Optional[Dict]:
        """Generate a single Akari puzzle with improved validation"""
        # Adjust parameters based on difficulty
        difficulty_params = {
            'easy': {'wall_ratio': 0.2, 'number_ratio': 0.4, 'max_attempts': 100},
            'medium': {'wall_ratio': 0.25, 'number_ratio': 0.5, 'max_attempts': 150},
            'hard': {'wall_ratio': 0.3, 'number_ratio': 0.6, 'max_attempts': 200},
            'expert': {'wall_ratio': 0.35, 'number_ratio': 0.7, 'max_attempts': 300}
        }
        
        params = difficulty_params.get(difficulty, difficulty_params['medium'])
        
        for attempt in range(params['max_attempts']):
            layout = self.generate_random_layout(size, params['wall_ratio'], params['number_ratio'])
            
            # Comprehensive validation
            if (self.is_valid_akari_layout(layout, size) and 
                self.is_solvable(layout, size) and
                self._validate_puzzle_quality(layout, size, difficulty)):
                
                seed = self.generate_seed(layout)
                return {
                    'layout': layout,
                    'seed': seed,
                    'size': size,
                    'difficulty': difficulty
                }
        
        logging.warning(f"Failed to generate {difficulty} {size}x{size} puzzle after {params['max_attempts']} attempts")
        return None
    
    def _validate_puzzle_quality(self, layout: List[List], size: int, difficulty: str) -> bool:
        """Additional quality checks for puzzle generation"""
        # Count cells
        white_cells = sum(1 for row in layout for cell in row if cell == 0)
        wall_cells = sum(1 for row in layout for cell in row if cell == 'X')
        numbered_cells = sum(1 for row in layout for cell in row 
                           if isinstance(cell, str) and cell.isdigit())
        
        total_cells = size * size
        
        # Difficulty-specific checks
        if difficulty == 'easy':
            # Easy puzzles should have more white cells and fewer constraints
            if white_cells < total_cells * 0.5 or numbered_cells < 1:
                return False
        elif difficulty == 'medium':
            # Medium puzzles should have balanced constraints
            if white_cells < total_cells * 0.4 or numbered_cells < 2:
                return False
        elif difficulty == 'hard':
            # Hard puzzles should have more constraints
            if white_cells < total_cells * 0.3 or numbered_cells < 3:
                return False
        elif difficulty == 'expert':
            # Expert puzzles should be very constrained
            if white_cells < total_cells * 0.25 or numbered_cells < 4:
                return False
        
        # Check for variety in numbered cells (optional for small puzzles)
        numbers = [int(cell) for row in layout for cell in row 
                  if isinstance(cell, str) and cell.isdigit()]
        if size >= 8 and len(set(numbers)) < 2:  # Need at least 2 different numbers for larger puzzles
            return False
        
        # Check for reasonable wall distribution
        wall_ratio = wall_cells / total_cells
        if wall_ratio < 0.15 or wall_ratio > 0.5:
            return False
        
        return True
    
    def send_puzzles_to_api(self, puzzles: List[Dict], mode: str = 'premium') -> Dict:
        """Send puzzles to the API"""
        if not puzzles:
            return {'success': False, 'error': 'No puzzles to send'}
        
        # Prepare puzzles for API
        api_puzzles = []
        for puzzle in puzzles:
            api_puzzle = {
                'layout': puzzle['layout'],
                'seed': puzzle['seed'],
                'size': puzzle['size'],
                'difficulty': puzzle['difficulty'],
                'mode': mode
            }
            
            # Add date for premium puzzles (future dates)
            if mode == 'premium':
                puzzle_date = datetime.now() + timedelta(days=random.randint(1, 30))
                api_puzzle['date'] = puzzle_date.strftime('%Y-%m-%d')
            
            api_puzzles.append(api_puzzle)
        
        # Send to API
        try:
            payload = {'puzzles': api_puzzles}
            response = self.session.post(self.api_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return {
                        'success': True,
                        'data': result.get('data', {}),
                        'message': result.get('message', 'Puzzles sent successfully')
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('message', 'API returned error'),
                        'details': result.get('data', {})
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
    
    def generate_batch(self, sizes: List[int], difficulties: List[str], 
                      count_per_size: int = 10, mode: str = 'premium') -> Dict:
        """Generate a batch of puzzles and send to API"""
        results = {
            'total_generated': 0,
            'total_sent': 0,
            'failed': 0,
            'by_size': {},
            'by_difficulty': {}
        }
        
        all_puzzles = []
        
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
                        all_puzzles.append(puzzle)
                    else:
                        results['failed'] += 1
                    
                    # Small delay to prevent overwhelming the system
                    time.sleep(0.1)
        
        # Send all puzzles to API
        if all_puzzles:
            logging.info(f"Sending {len(all_puzzles)} puzzles to API...")
            api_result = self.send_puzzles_to_api(all_puzzles, mode)
            
            if api_result['success']:
                api_data = api_result.get('data', {})
                results['total_sent'] = api_data.get('saved', 0)
                results['api_errors'] = api_data.get('errors', [])
                logging.info(f"API Response: {api_result['message']}")
            else:
                logging.error(f"API Error: {api_result['error']}")
                results['api_error'] = api_result['error']
        
        return results
    
    def generate_ebook_puzzles(self, sizes: List[int], count_per_size: int = 20) -> List[Dict]:
        """Generate puzzles specifically for ebooks (no API send)"""
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
    parser = argparse.ArgumentParser(description='Generate Akari puzzles and send to API')
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
    parser.add_argument('--api-url', type=str, 
                       default='https://shrinepuzzle.com/api/puzzle_receiver.php',
                       help='API endpoint URL')
    parser.add_argument('--api-key', type=str, 
                       default='shrine_puzzle_api_key_2024',
                       help='API key for authentication')
    
    args = parser.parse_args()
    
    generator = AkariPuzzleGeneratorAPI(args.api_url, args.api_key)
    
    if args.mode == 'ebook':
        # Generate puzzles for ebooks
        puzzles = generator.generate_ebook_puzzles(args.sizes, args.count)
        generator.save_ebook_puzzles(puzzles, args.output)
        logging.info(f"Generated {len(puzzles)} puzzles for ebook")
        
    else:
        # Generate puzzles and send to API
        results = generator.generate_batch(args.sizes, args.difficulties, args.count, args.mode)
        
        logging.info("Generation complete!")
        logging.info(f"Total generated: {results['total_generated']}")
        logging.info(f"Total sent to API: {results['total_sent']}")
        logging.info(f"Failed: {results['failed']}")
        logging.info(f"By size: {results['by_size']}")
        logging.info(f"By difficulty: {results['by_difficulty']}")
        
        if 'api_error' in results:
            logging.error(f"API Error: {results['api_error']}")
        
        if 'api_errors' in results and results['api_errors']:
            logging.warning(f"API Errors: {results['api_errors']}")

if __name__ == "__main__":
    main()
