import pygame
import sys
import random

# --- game constants
WIDTH, HEIGHT = 640, 480
FPS = 60
PADDLE_WIDTH, PADDLE_HEIGHT = 80, 10
BALL_SIZE = 12
PADDLE_SPEED = 7
BALL_SPEED_X_RANGE = (-4, 4)       # choose x speed randomly in this range
BALL_SPEED_Y_RANGE = (4, 6)        # choose y speed randomly in this range
SPEED_INCREMENT = 1.05             # 5% speed increase on every paddle hit
MAX_BALL_SPEED = 50                # cap the speed so the game stays playable

# --- init
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Single-Player Pong")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

# --- game objects
paddle = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2,
                     HEIGHT - 20 - PADDLE_HEIGHT,
                     PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_SIZE, BALL_SIZE)

def reset_ball():
    ball.center = (random.randint(40, WIDTH - 40), HEIGHT // 2)
    vx_candidates = [v for v in range(*BALL_SPEED_X_RANGE) if v != 0]
    vx = random.choice(vx_candidates)
    vy = random.choice(range(*BALL_SPEED_Y_RANGE))    # always heads down
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
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.x -= PADDLE_SPEED
    if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
        paddle.x += PADDLE_SPEED

    # update ball
    ball.x += ball_vx
    ball.y += ball_vy

    # bounce off left / right walls
    if ball.left <= 0 or ball.right >= WIDTH:
        ball_vx *= -1

    # bounce off top
    if ball.top <= 0:
        ball_vy *= -1

    # bounce off paddle
    if ball.colliderect(paddle) and ball_vy > 0:
        ball_vy *= -1
        ball_vx = max(min(ball_vx * SPEED_INCREMENT, MAX_BALL_SPEED), -MAX_BALL_SPEED)
        ball_vy = max(min(ball_vy * SPEED_INCREMENT, MAX_BALL_SPEED), -MAX_BALL_SPEED)
        score += 1

    # ball missed
    if ball.top > HEIGHT:
        score = 0
        ball_vx, ball_vy = reset_ball()

    # draw
    screen.fill("black")
    pygame.draw.rect(screen, "white", paddle)
    pygame.draw.ellipse(screen, "white", ball)

    score_surf = font.render(f"Score: {score}", True, "white")
    screen.blit(score_surf, (WIDTH - score_surf.get_width() - 10, 10))

    pygame.display.flip()
    clock.tick(FPS)
