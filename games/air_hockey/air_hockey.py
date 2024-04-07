import pygame
import sys
import random

# Initializing Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PAD_WIDTH = 10
PAD_HEIGHT = 100
BALL_RADIUS = 10
PADDLE_SPEED = 5
BALL_SPEED = 5

# Setting up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Air Hockey")

# Defining classes
class Paddle:
    # Initialize the Paddle object with given x, y coordinates and color.
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = PAD_WIDTH
        self.height = PAD_HEIGHT
        self.color = color

    def draw(self):
        pygame.draw.rect(screen, self.color, pygame.Rect(self.x, self.y, self.width, self.height))

class Ball:
    # Initialize the Ball object with given x, y coordinates and color.
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = BALL_RADIUS
        self.direction = random.choice([(1,1),(-1,1),(1,-1),(-1,-1)])

    def draw(self):
    # Draw the ball on the screen.
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

# Creating objects
player_paddle = Paddle(20, HEIGHT//2-PAD_HEIGHT//2, BLUE)
opponent_paddle = Paddle(WIDTH-20-PAD_WIDTH, HEIGHT//2-PAD_HEIGHT//2, RED)
ball = Ball(WIDTH//2, HEIGHT//2, WHITE)

clock = pygame.time.Clock()

# Scores
player_score = 0
opponent_score = 0

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # AI movement for the red paddle
    if ball.x > WIDTH // 2:
        if ball.y < opponent_paddle.y + PAD_HEIGHT // 2:
            opponent_paddle.y -= PADDLE_SPEED
        elif ball.y > opponent_paddle.y + PAD_HEIGHT // 2:
            opponent_paddle.y += PADDLE_SPEED

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and player_paddle.y - PADDLE_SPEED > 0:
        player_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_s] and player_paddle.y + PAD_HEIGHT + PADDLE_SPEED < HEIGHT:
        player_paddle.y += PADDLE_SPEED

    ball.x += ball.direction[0] * BALL_SPEED
    ball.y += ball.direction[1] * BALL_SPEED

    # Ball collision with walls
    if ball.y - BALL_RADIUS <= 0 or ball.y + BALL_RADIUS >= HEIGHT:
        ball.direction = (ball.direction[0], -ball.direction[1])
    
    # Boundary checking for the ball's position
    if ball.x - BALL_RADIUS <= 0:
        opponent_score += 1
        ball.__init__(WIDTH//2, HEIGHT//2, WHITE)
    elif ball.x + BALL_RADIUS >= WIDTH:
        player_score += 1
        ball.__init__(WIDTH//2, HEIGHT//2, WHITE)
    
    # Ball collision with paddles
    if (ball.x - BALL_RADIUS <= player_paddle.x + PAD_WIDTH and player_paddle.y <= ball.y <= player_paddle.y + PAD_HEIGHT) or \
        (ball.x + BALL_RADIUS >= opponent_paddle.x and opponent_paddle.y <= ball.y <= opponent_paddle.y + PAD_HEIGHT):
        ball.direction = (-ball.direction[0], ball.direction[1])
    
    screen.fill(BLACK)
    player_paddle.draw()
    opponent_paddle.draw()
    ball.draw()

    font = pygame.font.Font(None, 36)
    player_text = font.render('Player: ' + str(player_score), True, WHITE)
    opponent_text = font.render('Opponent: ' + str(opponent_score), True, WHITE)
    screen.blit(player_text, (50, 50))
    screen.blit(opponent_text, (WIDTH - 200, 50))

    pygame.display.flip()
    clock.tick(60)
