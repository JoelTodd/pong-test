import pygame
import sys
import random
import math

# --- game constants
WIDTH, HEIGHT = 512, 640
FPS = 60
PADDLE_WIDTH, PADDLE_HEIGHT = 80, 6
BALL_SIZE = 12
PADDLE_SPEED = 8
BALL_SPEED_X_RANGE = (-4, 4)       # choose x speed randomly in this range
BALL_SPEED_Y_RANGE = (4, 6)        # choose y speed randomly in this range
SPEED_INCREMENT = 1.08             # 8% speed increase after top bounce
MAX_BALL_SPEED = 50                # cap the speed so the game stays playable
TRANSITION_RATE = 12               # higher is snappier paddle acceleration
POWERUP_WIDTH, POWERUP_HEIGHT = 100, 4
POWERUP_DURATION = 8.0
POWERUP_CHANCE = 0.005            # chance each frame that a powerup appears
ANGLE_INFLUENCE = 5               # horizontal change from paddle impact
PADDLE_VEL_INFLUENCE = 0.5        # fraction of paddle velocity transferred
GRAVITY = 0.01                     # downward acceleration each frame


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


def random_velocity(up: bool = False) -> tuple[int, int]:
    """Return a random (vx, vy) pair.

    If ``up`` is True the ball will travel upward, otherwise downward.
    The horizontal component may be zero.
    """
    vx = random.choice(list(range(*BALL_SPEED_X_RANGE)))
    vy = random.choice(range(*BALL_SPEED_Y_RANGE))
    if up:
        vy *= -1
    return vx, vy


def duplicate_velocity(vx_current: int, vy_current: int) -> tuple[int, int]:
    """Return a new velocity with the same speed as ``(vx_current, vy_current)``.

    The new direction is randomised while keeping the original vertical
    orientation and never pointing perfectly sideways."""
    speed = (vx_current ** 2 + vy_current ** 2) ** 0.5
    while True:
        angle = random.uniform(0.1, 3.04)  # avoid 0 or PI radians
        vx = speed * math.cos(angle)
        if abs(vx) < 1e-3:
            continue  # skip directions that are effectively sideways
        vy = speed * math.sin(angle)
        if vy_current < 0:
            vy *= -1
        return int(round(vx)), int(round(vy))


next_ball_id = 0


def create_ball(up: bool = False, pos: tuple[int, int] | None = None) -> dict:
    """Create a new ball dictionary with a unique id."""
    global next_ball_id
    rect = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
    if pos is None:
        rect.center = (random.randint(40, WIDTH - 40), HEIGHT // 2)
    else:
        rect.center = pos
    vx, vy = random_velocity(up)
    ball = {"rect": rect, "vx": vx, "vy": vy, "ax": 0.0, "ay": 0.0, "id": next_ball_id}
    next_ball_id += 1
    return ball


def spawn_powerup() -> dict:
    """Return a new powerup dictionary."""
    x = random.randint(20, WIDTH - POWERUP_WIDTH - 20)
    y = random.randint(80, HEIGHT // 2)
    rect = pygame.Rect(x, y, POWERUP_WIDTH, POWERUP_HEIGHT)
    return {"rect": rect, "timer": POWERUP_DURATION, "collided": set()}


def run_menu() -> None:
    """Display a simple start menu until the user begins or quits."""
    options = ["Start Game", "Quit"]
    selected = 0
    title_font = pygame.font.SysFont(None, 48)
    menu_font = pygame.font.SysFont(None, 32)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if options[selected] == "Start Game":
                        return
                    else:
                        pygame.quit()
                        sys.exit()

        screen.fill("black")

        title_surf = title_font.render("Single-Player Pong", True, "white")
        screen.blit(
            title_surf,
            (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT // 3 - 50),
        )

        for i, option in enumerate(options):
            color = "yellow" if i == selected else "white"
            surf = menu_font.render(option, True, color)
            screen.blit(
                surf,
                (WIDTH // 2 - surf.get_width() // 2, HEIGHT // 2 + i * 40),
            )

        pygame.display.flip()
        clock.tick(FPS)

# --- init
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Single-Player Pong")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
debug_font = pygame.font.SysFont(None, 24)
debug_mode = False

run_menu()

# --- game objects
paddle = pygame.Rect(
    WIDTH // 2 - PADDLE_WIDTH // 2,
    HEIGHT - 20 - PADDLE_HEIGHT,
    PADDLE_WIDTH,
    PADDLE_HEIGHT,
)

balls = [create_ball()]
powerup = None
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
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            debug_mode = not debug_mode

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

    # spawn powerup
    if powerup is None and random.random() < POWERUP_CHANCE:
        powerup = spawn_powerup()

    # update powerup timer
    if powerup is not None:
        powerup["timer"] -= dt
        if powerup["timer"] <= 0:
            powerup = None

    # update balls
    for b in balls[:]:
        rect = b["rect"]
        old_center = rect.center
        prev_vx = b["vx"]
        prev_vy = b["vy"]
        b["vy"] += GRAVITY
        rect.x += b["vx"]
        rect.y += b["vy"]
        new_center = rect.center

        if powerup is not None:
            p_rect = powerup["rect"]
            ball_id = b["id"]
            if ball_id not in powerup["collided"]:
                if p_rect.colliderect(rect) or p_rect.clipline(old_center, new_center):
                    vx, vy = duplicate_velocity(b["vx"], b["vy"])
                    nb = create_ball(up=b["vy"] < 0, pos=rect.center)
                    nb["vx"], nb["vy"] = vx, vy
                    powerup["collided"].update({ball_id, nb["id"]})
                    balls.append(nb)

        if rect.left <= 0 or rect.right >= WIDTH:
            b["vx"] *= -1

        if rect.top <= 0:
            b["vy"] *= -1
            speed = math.hypot(b["vx"], b["vy"])
            if speed < MAX_BALL_SPEED:
                speed = min(speed * SPEED_INCREMENT, MAX_BALL_SPEED)
                angle = math.atan2(b["vy"], b["vx"])
                b["vx"] = int(round(math.cos(angle) * speed))
                b["vy"] = int(round(math.sin(angle) * speed))

        if rect.colliderect(paddle) and b["vy"] > 0:
            offset = (rect.centerx - paddle.centerx) / (PADDLE_WIDTH / 2)
            b["vy"] *= -1
            b["vx"] += offset * ANGLE_INFLUENCE + paddle_vx * PADDLE_VEL_INFLUENCE
            b["vx"] = max(min(b["vx"] * SPEED_INCREMENT, MAX_BALL_SPEED), -MAX_BALL_SPEED)
            b["vy"] = max(min(b["vy"] * SPEED_INCREMENT, MAX_BALL_SPEED), -MAX_BALL_SPEED)
            score += 1

        if dt > 0:
            b["ax"] = (b["vx"] - prev_vx) / dt
            b["ay"] = (b["vy"] - prev_vy) / dt
        else:
            b["ax"] = 0.0
            b["ay"] = 0.0

        if rect.top > HEIGHT:
            balls.remove(b)

    if not balls:
        score = 0
        balls.append(create_ball())

    # draw
    screen.fill("black")
    pygame.draw.rect(screen, "white", paddle)
    for b in balls:
        pygame.draw.ellipse(screen, "white", b["rect"])
    if powerup is not None:
        pygame.draw.rect(screen, "yellow", powerup["rect"])

    score_surf = font.render(f"Score: {score}", True, "white")
    screen.blit(score_surf, (WIDTH - score_surf.get_width() - 10, 10))

    if debug_mode:
        lines = [f"Balls: {len(balls)}"]
        for b in balls:
            speed = math.hypot(b["vx"], b["vy"])
            accel = math.hypot(b.get("ax", 0.0), b.get("ay", 0.0))
            lines.append(
                f"id {b['id']} spd {speed:.2f} acc {accel:.2f}"
            )
        y = 10
        for line in lines:
            surf = debug_font.render(line, True, "green")
            screen.blit(surf, (10, y))
            y += surf.get_height() + 2

    pygame.display.flip()
