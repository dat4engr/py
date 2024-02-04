import pygame
import sys

# Initialize pygame
pygame.init()

# Set up the game window
WIDTH = 300
HEIGHT = 300
BG_COLOR = (255, 255, 255)
LINE_COLOR = (0, 0, 0)
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic-Tac-Toe")
window.fill(BG_COLOR)

# Define the board
board = [['', '', ''], ['', '', ''], ['', '', '']]

# Set up players
player = 'X'
game_over = False

# Set up font
FONT_SIZE = 80
FONT_COLOR = (0, 0, 0)
font = pygame.font.Font(None, FONT_SIZE)

# Thickness of X and O symbols
SYMBOL_THICKNESS = 5

# Draw the board lines
def draw_lines():
    # Horizontal lines
    pygame.draw.line(window, LINE_COLOR, (0, 100), (300, 100), SYMBOL_THICKNESS)
    pygame.draw.line(window, LINE_COLOR, (0, 200), (300, 200), SYMBOL_THICKNESS)
    # Vertical lines
    pygame.draw.line(window, LINE_COLOR, (100, 0), (100, 300), SYMBOL_THICKNESS)
    pygame.draw.line(window, LINE_COLOR, (200, 0), (200, 300), SYMBOL_THICKNESS)

# Draw the X and O symbols
def draw_symbols():
    for row in range(3):
        for col in range(3):
            if board[row][col] == 'X':
                x_pos = col * 100 + 50
                y_pos = row * 100 + 50
                pygame.draw.line(window, LINE_COLOR, (x_pos - 40, y_pos - 40), (x_pos + 40, y_pos + 40), SYMBOL_THICKNESS)
                pygame.draw.line(window, LINE_COLOR, (x_pos + 40, y_pos - 40), (x_pos - 40, y_pos + 40), SYMBOL_THICKNESS)
            elif board[row][col] == 'O':
                x_pos = col * 100 + 50
                y_pos = row * 100 + 50
                pygame.draw.circle(window, LINE_COLOR, (x_pos, y_pos), 40, SYMBOL_THICKNESS)

# Check for a win
def check_win(player):
    for row in range(3):
        if board[row][0] == board[row][1] == board[row][2] == player:
            pygame.draw.line(window, (255, 0, 0), (0, (row + 0.5) * 100), (300, (row + 0.5) * 100), SYMBOL_THICKNESS*2)
            return True
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] == player:
            pygame.draw.line(window, (255, 0, 0), ((col + 0.5) * 100, 0), ((col + 0.5) * 100, 300), SYMBOL_THICKNESS*2)
            return True
    if board[0][0] == board[1][1] == board[2][2] == player:
        pygame.draw.line(window, (255, 0, 0), (50, 50), (250, 250), SYMBOL_THICKNESS*2)
        return True
    if board[0][2] == board[1][1] == board[2][0] == player:
        pygame.draw.line(window, (255, 0, 0), (250, 50), (50, 250), SYMBOL_THICKNESS*2)
        return True
    return False

# Restart the game
def restart_game():
    # Reset the board
    for row in range(3):
        for col in range(3):
            board[row][col] = ''
    # Reset the player
    player = 'X'
    # Reset game over state
    game_over = False
    # Clear the window
    window.fill(BG_COLOR)

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            x_pos, y_pos = pygame.mouse.get_pos()
            if x_pos < 100 and y_pos < 100 and board[0][0] == '':
                board[0][0] = player
                player = 'O' if player == 'X' else 'X'
            elif x_pos < 200 and y_pos < 100 and board[0][1] == '':
                board[0][1] = player
                player = 'O' if player == 'X' else 'X'
            elif x_pos < 300 and y_pos < 100 and board[0][2] == '':
                board[0][2] = player
                player = 'O' if player == 'X' else 'X'
            elif x_pos < 100 and y_pos < 200 and board[1][0] == '':
                board[1][0] = player
                player = 'O' if player == 'X' else 'X'
            elif x_pos < 200 and y_pos < 200 and board[1][1] == '':
                board[1][1] = player
                player = 'O' if player == 'X' else 'X'
            elif x_pos < 300 and y_pos < 200 and board[1][2] == '':
                board[1][2] = player
                player = 'O' if player == 'X' else 'X'
            elif x_pos < 100 and y_pos < 300 and board[2][0] == '':
                board[2][0] = player
                player = 'O' if player == 'X' else 'X'
            elif x_pos < 200 and y_pos < 300 and board[2][1] == '':
                board[2][1] = player
                player = 'O' if player == 'X' else 'X'
            elif x_pos < 300 and y_pos < 300 and board[2][2] == '':
                board[2][2] = player
                player = 'O' if player == 'X' else 'X'
            if check_win('X'):
                game_over = True
                message = font.render("X wins!", True, FONT_COLOR)
                window.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 2 - message.get_height() // 2))
            elif check_win('O'):
                game_over = True
                message = font.render("O wins!", True, FONT_COLOR)
                window.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 2 - message.get_height() // 2))
            elif all(board[i][j] != '' for i in range(3) for j in range(3)):
                game_over = True
                message = font.render("It's a tie!", True, FONT_COLOR)
                window.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 2 - message.get_height() // 2))
        elif event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_RETURN:
                restart_game()
    
    if not game_over:
        window.fill(BG_COLOR)
        draw_lines()
        draw_symbols()

    pygame.display.flip()
