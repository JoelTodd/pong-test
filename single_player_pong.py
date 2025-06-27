import pygame
import sys
import random

# --- game constants
WIDTH, HEIGHT = 512, 640
FPS = 60
PADDLE_WIDTH, PADDLE_HEIGHT = 80, 10
BALL_SIZE = 12
PADDLE_SPEED = 7
BALL_SPEED_X_RANGE = (-4, 4)       # choose x speed randomly in this range
BALL_SPEED_Y_RANGE = (4, 6)        # choose y speed randomly in this range
SPEED_INCREMENT = 1.05             # 5% speed increase on every paddle hit
MAX_BALL_SPEED = 50                # cap the speed so the game stays playable
TRANSITION_RATE = 10               # higher is snappier paddle acceleration


def cubic_bezier(t, p0, p1, p2, p3):
    """Simple cubic Bezier curve evaluator."""
    return (
        (1 - t) ** 3 * p0
        + 3 * (1 - t) ** 2 * t * p1
        + 3 * (1 - t) * t ** 2 * p2
        + t ** 3 * p3
    )


def snappy_ease(t: float) -> float:
    """Return a smooth yet quick easing value for 0<=t<=1."""
    t = max(0.0, min(1.0, t))
    return cubic_bezier(t, 0.0, 0.1, 0.9, 1.0)

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

# paddle movement smoothing
paddle_vx = 0
paddle_target_vx = 0
paddle_start_vx = 0
transition_t = 1.0

# --- main loop
while True:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # input
    keys = pygame.key.get_pressed()
    new_target_vx = 0
    if keys[pygame.K_LEFT] and paddle.left > 0:
        new_target_vx = -PADDLE_SPEED
    elif keys[pygame.K_RIGHT] and paddle.right < WIDTH:
        new_target_vx = PADDLE_SPEED

    if new_target_vx != paddle_target_vx:
        paddle_target_vx = new_target_vx
        paddle_start_vx = paddle_vx
        transition_t = 0.0

    if transition_t < 1.0:
        transition_t = min(transition_t + TRANSITION_RATE * dt, 1.0)
        prog = snappy_ease(transition_t)
        paddle_vx = paddle_start_vx + (paddle_target_vx - paddle_start_vx) * prog
    else:
        paddle_vx = paddle_target_vx

    paddle.x += paddle_vx
    if paddle.left < 0:
        paddle.left = 0
    if paddle.right > WIDTH:
        paddle.right = WIDTH

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
