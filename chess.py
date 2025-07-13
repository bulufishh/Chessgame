import pygame
import sys
from typing import List, Tuple, Optional

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 640, 640
BOARD_SIZE = 8
SQUARE_SIZE = WIDTH // BOARD_SIZE
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT = (247, 247, 105)
LAST_MOVE = (246, 246, 105)

class ChessGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', SQUARE_SIZE // 2)
        
        # Load piece images
        self.piece_images = self.load_piece_images()
        
        # Game state
        self.board = self.initialize_board()
        self.turn = 'white'
        self.selected_piece = None
        self.valid_moves = []
        self.last_move = None
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)
        self.check = False
        self.game_over = False

    def load_piece_images(self):
        """Load and scale all chess piece images"""
        pieces = {
            'r': 'rook_black.png',
            'n': 'knight_black.png',
            'b': 'bishop_black.png',
            'q': 'queen_black.png',
            'k': 'king_black.png',
            'p': 'pawn_black.png',
            'R': 'rook_white.png',
            'N': 'knight_white.png',
            'B': 'bishop_white.png',
            'Q': 'queen_white.png',
            'K': 'king_white.png',
            'P': 'pawn_white.png'
        }
        
        piece_images = {}
        for key, filename in pieces.items():
            try:
                img = pygame.image.load(f'pieces/{filename}').convert_alpha()
                piece_images[key] = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                # Fallback to Unicode symbols
                unicode_pieces = {
                    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
                    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
                }
                piece_images[key] = unicode_pieces.get(key, '?')
                
        return piece_images

    def initialize_board(self) -> List[List[str]]:
        """Set up the initial chess board"""
        board = [['' for _ in range(8)] for _ in range(8)]
        
        # Set up pawns
        for col in range(8):
            board[1][col] = 'p'
            board[6][col] = 'P'
        
        # Set up other pieces
        pieces = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
        for col, piece in enumerate(pieces):
            board[0][col] = piece
            board[7][col] = piece.upper()
        
        return board

    def draw_board(self):
        """Draw the chess board and pieces"""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                # Draw square
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(self.screen, color, 
                                (col * SQUARE_SIZE, row * SQUARE_SIZE, 
                                 SQUARE_SIZE, SQUARE_SIZE))
                
                # Highlight selected piece and valid moves
                if self.selected_piece and (row, col) == self.selected_piece:
                    highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    highlight.fill((*HIGHLIGHT, 150))
                    self.screen.blit(highlight, (col * SQUARE_SIZE, row * SQUARE_SIZE))
                
                if (row, col) in self.valid_moves:
                    pygame.draw.circle(self.screen, (*HIGHLIGHT, 150),
                                     (col * SQUARE_SIZE + SQUARE_SIZE // 2, 
                                      row * SQUARE_SIZE + SQUARE_SIZE // 2), 
                                      SQUARE_SIZE // 4)
                
                # Highlight last move
                if self.last_move:
                    start, end = self.last_move
                    if (row, col) == start or (row, col) == end:
                        last_move_highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                        last_move_highlight.fill((*LAST_MOVE, 150))
                        self.screen.blit(last_move_highlight, (col * SQUARE_SIZE, row * SQUARE_SIZE))
                
                # Draw piece
                piece = self.board[row][col]
                if piece:
                    if isinstance(self.piece_images.get(piece), pygame.Surface):
                        # Draw image if available
                        img = self.piece_images[piece]
                        self.screen.blit(img, (col * SQUARE_SIZE, row * SQUARE_SIZE))
                    else:
                        # Fallback to text
                        text = self.font.render(str(self.piece_images.get(piece, '?')), True, 
                                             BLACK if piece.isupper() else WHITE)
                        text_rect = text.get_rect(center=(col*SQUARE_SIZE + SQUARE_SIZE//2,
                                            row*SQUARE_SIZE + SQUARE_SIZE//2))
                        self.screen.blit(text, text_rect)
        
        # Draw check indicator
        if self.check:
            king_row, king_col = self.white_king_pos if self.turn == 'white' else self.black_king_pos
            check_highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            check_highlight.fill((255, 0, 0, 150))
            self.screen.blit(check_highlight, (king_col * SQUARE_SIZE, king_row * SQUARE_SIZE))

        # Display game status
        status_text = f"{self.turn.capitalize()}'s turn"
        if self.check:
            status_text += " (CHECK)"
        if self.game_over:
            status_text = "Checkmate!" if self.check else "Stalemate!"
        
        text_surface = pygame.font.SysFont('Arial', 20).render(status_text, True, WHITE)
        self.screen.blit(text_surface, (10, HEIGHT - 30))

    def get_valid_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get all valid moves for a piece at (row, col)"""
        piece = self.board[row][col]
        if not piece or (piece.isupper() and self.turn == 'black') or (piece.islower() and self.turn == 'white'):
            return []
        
        moves = []
        directions = []
        
        # Pawn moves
        if piece.lower() == 'p':
            direction = -1 if piece.isupper() else 1
            start_row = 6 if piece.isupper() else 1
            
            # Forward moves
            if self.is_empty(row + direction, col):
                moves.append((row + direction, col))
                if row == start_row and self.is_empty(row + 2 * direction, col):
                    moves.append((row + 2 * direction, col))
            
            # Captures
            for dc in [-1, 1]:
                if self.is_opponent(row + direction, col + dc, piece):
                    moves.append((row + direction, col + dc))
            
            return moves
        
        # Knight moves
        elif piece.lower() == 'n':
            knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                           (1, -2), (1, 2), (2, -1), (2, 1)]
            for dr, dc in knight_moves:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    if self.is_empty(new_row, new_col) or self.is_opponent(new_row, new_col, piece):
                        moves.append((new_row, new_col))
            return moves
        
        # Bishop, Rook, Queen directions
        if piece.lower() == 'b' or piece.lower() == 'q':
            directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        if piece.lower() == 'r' or piece.lower() == 'q':
            directions += [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        # Sliding pieces (bishop, rook, queen)
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                
                if self.is_empty(new_row, new_col):
                    moves.append((new_row, new_col))
                elif self.is_opponent(new_row, new_col, piece):
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        # King moves
        if piece.lower() == 'k':
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        if self.is_empty(new_row, new_col) or self.is_opponent(new_row, new_col, piece):
                            moves.append((new_row, new_col))
            return moves
        
        # Filter out moves that would leave king in check
        valid_moves = []
        for move_row, move_col in moves:
            if not self.would_be_in_check(row, col, move_row, move_col, piece):
                valid_moves.append((move_row, move_col))
        
        return valid_moves

    def is_empty(self, row: int, col: int) -> bool:
        """Check if a square is empty"""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col] == ''
        return False

    def is_opponent(self, row: int, col: int, piece: str) -> bool:
        """Check if a square contains an opponent's piece"""
        if 0 <= row < 8 and 0 <= col < 8:
            target = self.board[row][col]
            if target:
                return (target.isupper() and piece.islower()) or (target.islower() and piece.isupper())
        return False

    def would_be_in_check(self, start_row: int, start_col: int, 
                         end_row: int, end_col: int, piece: str) -> bool:
        """Check if moving a piece would leave the king in check"""
        # Simulate the move
        captured_piece = self.board[end_row][end_col]
        self.board[end_row][end_col] = self.board[start_row][start_col]
        self.board[start_row][start_col] = ''
        
        # Find the king's position
        king_pos = None
        king = 'K' if self.turn == 'white' else 'k'
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == king:
                    king_pos = (row, col)
                    break
            if king_pos:
                break
        
        # Check if king is under attack
        in_check = self.is_square_under_attack(king_pos[0], king_pos[1], 'black' if self.turn == 'white' else 'white')
        
        # Undo the move
        self.board[start_row][start_col] = self.board[end_row][end_col]
        self.board[end_row][end_col] = captured_piece
        
        return in_check

    def is_square_under_attack(self, row: int, col: int, by_color: str) -> bool:
        """Check if a square is under attack by the specified color"""
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and ((by_color == 'white' and piece.isupper()) or (by_color == 'black' and piece.islower())):
                    # Temporarily pretend the square is empty to see if it can be attacked
                    original_piece = self.board[row][col]
                    self.board[row][col] = ''
                    
                    # Get all possible moves for this piece
                    pseudo_moves = []
                    if piece.lower() == 'p':
                        direction = -1 if piece.isupper() else 1
                        for dc in [-1, 1]:
                            if 0 <= c + dc < 8:
                                pseudo_moves.append((r + direction, c + dc))
                    else:
                        pseudo_moves = self.get_pseudo_legal_moves(r, c, piece)
                    
                    # Restore the piece
                    self.board[row][col] = original_piece
                    
                    # Check if any move targets our square
                    if (row, col) in pseudo_moves:
                        return True
        return False

    def get_pseudo_legal_moves(self, row: int, col: int, piece: str) -> List[Tuple[int, int]]:
        """Get moves without checking for king safety (for attack detection)"""
        moves = []
        
        # Pawn captures
        if piece.lower() == 'p':
            direction = -1 if piece.isupper() else 1
            for dc in [-1, 1]:
                if 0 <= col + dc < 8:
                    moves.append((row + direction, col + dc))
            return moves
        
        # Reuse the get_valid_moves logic but without the king safety check
        directions = []
        if piece.lower() == 'n':
            knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                           (1, -2), (1, 2), (2, -1), (2, 1)]
            for dr, dc in knight_moves:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    moves.append((new_row, new_col))
            return moves
        
        if piece.lower() == 'b' or piece.lower() == 'q':
            directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        if piece.lower() == 'r' or piece.lower() == 'q':
            directions += [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                moves.append((new_row, new_col))
                if self.board[new_row][new_col] != '':
                    break
        
        if piece.lower() == 'k':
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        moves.append((new_row, new_col))
        
        return moves

    def make_move(self, start_row: int, start_col: int, end_row: int, end_col: int):
        """Execute a move on the board"""
        piece = self.board[start_row][start_col]
        
        # Update king position if moved
        if piece.lower() == 'k':
            if piece == 'K':
                self.white_king_pos = (end_row, end_col)
            else:
                self.black_king_pos = (end_row, end_col)
        
        # Record the move
        self.last_move = ((start_row, start_col), (end_row, end_col))
        
        # Move the piece
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = ''
        
        # Pawn promotion (always to queen for simplicity)
        if piece.lower() == 'p' and (end_row == 0 or end_row == 7):
            self.board[end_row][end_col] = 'Q' if piece.isupper() else 'q'
        
        # Switch turns
        self.turn = 'black' if self.turn == 'white' else 'white'
        
        # Check for check/checkmate
        self.update_game_state()

    def update_game_state(self):
        """Update check and checkmate status"""
        king_pos = self.white_king_pos if self.turn == 'white' else self.black_king_pos
        self.check = self.is_square_under_attack(king_pos[0], king_pos[1], 
                                               'black' if self.turn == 'white' else 'white')
        
        # Check for checkmate or stalemate
        has_legal_move = False
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and ((self.turn == 'white' and piece.isupper()) or 
                             (self.turn == 'black' and piece.islower())):
                    if self.get_valid_moves(row, col):
                        has_legal_move = True
                        break
            if has_legal_move:
                break
        
        if not has_legal_move:
            self.game_over = True

    def handle_click(self, row: int, col: int):
        """Handle mouse clicks on the board"""
        if self.game_over:
            return
        
        # If a piece is already selected
        if self.selected_piece:
            selected_row, selected_col = self.selected_piece
            
            # Check if clicking on a valid move
            if (row, col) in self.valid_moves:
                self.make_move(selected_row, selected_col, row, col)
                self.selected_piece = None
                self.valid_moves = []
            # Check if clicking on another piece of the same color
            elif ((self.turn == 'white' and self.board[row][col].isupper()) or 
                  (self.turn == 'black' and self.board[row][col].islower())):
                self.selected_piece = (row, col)
                self.valid_moves = self.get_valid_moves(row, col)
            else:
                self.selected_piece = None
                self.valid_moves = []
        # Select a piece if it's the current player's turn
        elif ((self.turn == 'white' and self.board[row][col].isupper()) or 
              (self.turn == 'black' and self.board[row][col].islower())):
            self.selected_piece = (row, col)
            self.valid_moves = self.get_valid_moves(row, col)

    def run(self):
        """Main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        x, y = pygame.mouse.get_pos()
                        col = x // SQUARE_SIZE
                        row = y // SQUARE_SIZE
                        self.handle_click(row, col)
            
            # Draw everything
            self.screen.fill(BLACK)
            self.draw_board()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ChessGame()
    game.run()
