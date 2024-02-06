# Import modules
import pygame
import random
from pygame.locals import *

# Initialize pygame
pygame.init()

# Game Resolution
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 300

try:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Play TicTacToe')
except pygame.error as e:
    print("Failed to initialize screen:", e)
    pygame.quit()

# Variables and Functions
line_width = 6
markers = []
clicked = False
pos = []
player = 1
winner = 0
game_over = False

# Colors
green = (0, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)

# Font styles
try:
    font = pygame.font.SysFont(None, 40)
except pygame.error as e:
    print("Failed to load font:", e)
    pygame.quit()

# Play Again Rect
again_rect = Rect(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2, 160, 50)
player1_rect = Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 60, 200, 50)
ai_rect = Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 60, 200, 50)

def draw_grid():
    # Function to draw the grid on the screen.
    try:
        bg = (255, 255, 255)
        grid = (50, 50, 50)
        screen.fill(bg)
        for x in range(1, 3):
            pygame.draw.line(screen, grid, (0, x * 100), (SCREEN_WIDTH, x * 100), line_width)
            pygame.draw.line(screen, grid, (x * 100, 0), (x * 100, SCREEN_HEIGHT), line_width)
    except pygame.error as e:
        print("Failed to draw grid:", e)

for x in range(3):
    row = [0] * 3
    markers.append(row)

def draw_markers():
    # Function to draw the markers (X and O) on the screen.
    try:
        x_pos = 0
        for x in markers:
            y_pos = 0
            for y in x:
                if y == 1:
                    pygame.draw.line(screen, green, (x_pos * 100 + 15, y_pos * 100 + 15), (x_pos * 100 + 85, y_pos * 100 + 85), line_width)
                    pygame.draw.line(screen, green, (x_pos * 100 + 15, y_pos * 100 + 85), (x_pos * 100 + 85, y_pos * 100 + 15), line_width)
                if y == -1:
                    pygame.draw.circle(screen, red, (x_pos * 100 + 50, y_pos * 100 + 50), 38, line_width)
                y_pos += 1
            x_pos += 1
    except pygame.error as e:
        print("Failed to draw markers:", e)

def check_winner():
    # Function to check if there is a winner.
    try:
        global winner
        global game_over

        y_pos = 0
        for x in markers:
            # Check columns:
            if sum(x) == 3:
                winner = 1
                game_over = True
            if sum(x) == -3:
                winner = 2
                game_over = True

            # Check rows:
            if markers[0][y_pos] + markers[1][y_pos] + markers[2][y_pos] == 3:
                winner = 1
                game_over = True
            if markers[0][y_pos] + markers[1][y_pos] + markers[2][y_pos] == -3:
                winner = 2
                game_over = True
            y_pos += 1

        # Check cross:
        if markers[0][0] + markers[1][1] + markers[2][2] == 3 or markers[2][0] + markers[1][1] + markers[0][2] == 3:
            winner = 1
            game_over = True
        if markers[0][0] + markers[1][1] + markers[2][2] == -3 or markers[2][0] + markers[1][1] + markers[0][2] == -3:
            winner = 2
            game_over = True
    except Exception as e:
        print("Error occurred while checking winner:", e)

def draw_winner(winner):
    # Function to draw the winner message on the screen.
    try:
        if winner == 1:
            win_text = "Player 1 wins!"
            pygame.draw.rect(screen, green, player1_rect)
        elif winner == 2:
            win_text = "AI wins!"
            pygame.draw.rect(screen, green, ai_rect)
        win_img = font.render(win_text, True, blue)
        screen.blit(win_img, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))

        again_text = 'Play again?'
        again_img = font.render(again_text, True, blue)
        pygame.draw.rect(screen, green, again_rect)
        screen.blit(again_img, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 10))
    except pygame.error as e:
        print("Failed to draw winner:", e)

# Game Setup and Exit Handler
try:
    run = True
    while run:
        draw_grid()
        draw_markers()

        # Event handlers:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if game_over == 0:
                if event.type == pygame.MOUSEBUTTONDOWN and clicked is False:
                    clicked = True
                if event.type == pygame.MOUSEBUTTONUP and clicked is True:
                    clicked = False
                    pos = pygame.mouse.get_pos()
                    try:
                        cell_x = pos[0]
                        cell_y = pos[1]
                        if markers[cell_x // 100][cell_y // 100] == 0:
                            markers[cell_x // 100][cell_y // 100] = player
                            player *= -1

                            check_winner() # Moved after the player's move
                            if game_over == False:
                                # Easy AI opponent's turn
                                empty_cells = [(i, j) for i in range(3) for j in range(3) if markers[i][j] == 0]
                                ai_move = random.choice(empty_cells)
                                markers[ai_move[0]][ai_move[1]] = player
                                player *= -1
                                check_winner()
                    except Exception as e:
                        print("Error occurred while handling mouse input:", e)

        if game_over is True:
            draw_winner(winner)
            # Check Mouseclick to see if user/s clicked on Play Again
            if event.type == pygame.MOUSEBUTTONDOWN and clicked is False:
                clicked = True
            if event.type == pygame.MOUSEBUTTONUP and clicked is True:
                clicked = False
                pos = pygame.mouse.get_pos()
                if again_rect.collidepoint(pos):
                    # Reset Variables
                    markers = []
                    pos = []
                    player = 1
                    winner = 0
                    game_over = False

                    for x in range(3):
                        row = [0] * 3
                        markers.append(row)

        # Update Game Running
        pygame.display.update()
except Exception as e:
    print("An error occurred:", e)

# To end pygame
pygame.quit()
