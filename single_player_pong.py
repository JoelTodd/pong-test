import pygame
import sys
import random

# --- game constants
WIDTH, HEIGHT = 640, 480
FPS = 60
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 80
BALL_SIZE = 12
PADDLE_SPEED = 6
BALL_SPEED_X_RANGE = (4, 6)        # choose x speed randomly in this range
BALL_SPEED_Y_RANGE = (-4, 4)       # choose y speed randomly in this range

# --- init
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Single-Player Pong")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

# --- game objects
paddle = pygame.Rect(20, HEIGHT // 2 - PADDLE_HEIGHT // 2,
                     PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_SIZE, BALL_SIZE)

def reset_ball():
    ball.center = (WIDTH // 2, random.randint(40, HEIGHT - 40))
    vx = -random.choice(range(*BALL_SPEED_X_RANGE))    # always heads left
    vy_candidates = [v for v in range(*BALL_SPEED_Y_RANGE) if v != 0]
    vy = random.choice(vy_candidates)
    return vx, vy

ball_vx, ball_vy = reset_ball()
score = 0

# --- main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and paddle.top > 0:
        paddle.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and paddle.bottom < HEIGHT:
        paddle.y += PADDLE_SPEED

    # update ball
    ball.x += ball_vx
    ball.y += ball_vy

    # bounce off top / bottom
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_vy *= -1

    # bounce off right wall
    if ball.right >= WIDTH and ball_vx > 0:
        ball_vx *= -1

    # bounce off paddle
    if ball.colliderect(paddle) and ball_vx < 0:
        ball_vx *= -1
        score += 1

    # ball missed
    if ball.right < 0:
        score = 0
        ball_vx, ball_vy = reset_ball()

    # draw
    screen.fill("black")
    pygame.draw.rect(screen, "white", paddle)
    pygame.draw.ellipse(screen, "white", ball)
    pygame.draw.line(screen, "white", (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 1)

    score_surf = font.render(f"Score: {score}", True, "white")
    screen.blit(score_surf, (WIDTH - score_surf.get_width() - 10, 10))

    pygame.display.flip()
    clock.tick(FPS)
