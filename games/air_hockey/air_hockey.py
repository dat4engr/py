import pygame
import sys
import random

# Initializing Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100
BALL_RADIUS = 10
PADDLE_SPEED = 5
BALL_SPEED = 5

# Setting up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Air Hockey")

# Defining classes
class Paddle:
    # Initialize the Paddle object with given x, y coordinates and color.
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
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
        self.scored = False

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

# Creating objects
player_paddle = Paddle(20, SCREEN_HEIGHT//2-PADDLE_HEIGHT//2, BLUE)
opponent_paddle = Paddle(SCREEN_WIDTH-20-PADDLE_WIDTH, SCREEN_HEIGHT//2-PADDLE_HEIGHT//2, RED)
ball = Ball(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, WHITE)

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
    if ball.x > SCREEN_WIDTH // 2:
        if ball.y < opponent_paddle.y + PADDLE_HEIGHT // 2:
            opponent_paddle.y = max(opponent_paddle.y - PADDLE_SPEED, 0)
        elif ball.y > opponent_paddle.y + PADDLE_HEIGHT // 2:
            opponent_paddle.y = min(opponent_paddle.y + PADDLE_SPEED, SCREEN_HEIGHT - PADDLE_HEIGHT)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_paddle.y = max(player_paddle.y - PADDLE_SPEED, 0)
    if keys[pygame.K_s]:
        player_paddle.y = min(player_paddle.y + PADDLE_SPEED, SCREEN_HEIGHT - PADDLE_HEIGHT)

    # Update ball position
    new_ball_x = ball.x + ball.direction[0] * BALL_SPEED
    new_ball_y = ball.y + ball.direction[1] * BALL_SPEED

    # Boundary checking for the ball's position
    if new_ball_x - BALL_RADIUS <= 0 and not ball.scored:
        opponent_score += 1
        ball.scored = True
    elif new_ball_x + BALL_RADIUS >= SCREEN_WIDTH and not ball.scored:
        player_score += 1
        ball.scored = True

    if ball.scored:  # Reset position if score was made
        ball.__init__(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, WHITE)

    # Check if ball is within bounds before updating position
    if BALL_RADIUS <= new_ball_y <= SCREEN_HEIGHT - BALL_RADIUS:
        ball.x = new_ball_x
        ball.y = new_ball_y
    else:
        ball.direction = (ball.direction[0], -ball.direction[1])

    # Ball collision with paddles
    if (ball.x - BALL_RADIUS <= player_paddle.x + PADDLE_WIDTH and player_paddle.y <= ball.y <= player_paddle.y + PADDLE_HEIGHT) or \
        (ball.x + BALL_RADIUS >= opponent_paddle.x and opponent_paddle.y <= ball.y <= opponent_paddle.y + PADDLE_HEIGHT):
        ball.direction = (-ball.direction[0], ball.direction[1])
    
    screen.fill(BLACK)
    player_paddle.draw()
    opponent_paddle.draw()
    ball.draw()

    font = pygame.font.Font(None, 36)
    player_text = font.render('Player: ' + str(player_score), True, WHITE)
    opponent_text = font.render('Opponent: ' + str(opponent_score), True, WHITE)
    screen.blit(player_text, (50, 50))
    screen.blit(opponent_text, (SCREEN_WIDTH - 200, 50))

    pygame.display.flip()
    clock.tick(60)
