import pygame
import sys
import random
import math

# --- game constants ---------------------------------------------------------
WIDTH, HEIGHT = 512, 640
FPS = 60

PADDLE_WIDTH, PADDLE_HEIGHT = 80, 6
BALL_SIZE = 12
PADDLE_SPEED = 8

BALL_SPEED_X_RANGE = (-4, 4)          # horizontal start speed range
BALL_SPEED_Y_RANGE = (4, 6)           # vertical start speed range
SPEED_INCREMENT     = 1.08            # 8 % speed-up on top bounce
MAX_BALL_SPEED      = 50
TRANSITION_RATE     = 12              # paddle acceleration snappiness
POWERUP_WIDTH, POWERUP_HEIGHT = 100, 4
POWERUP_DURATION    = 8.0
POWERUP_CHANCE      = 0.005           # probability per frame
ANGLE_INFLUENCE     = 5               # paddle-impact curve
PADDLE_VEL_INFLUENCE = 0.5            # paddle motion affects ball
GRAVITY             = 0.01            # mild, for extra challenge

# --- helpers ----------------------------------------------------------------
def cubic_bezier(t, p0, p1, p2, p3):
    return (
        (1 - t) ** 3 * p0
        + 3 * (1 - t) ** 2 * t * p1
        + 3 * (1 - t) * t ** 2 * p2
        + t ** 3 * p3
    )

def snappy_ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return cubic_bezier(t, 0.0, 0.1, 0.9, 1.0)

def random_velocity(up: bool = False) -> tuple[int, int]:
    vx = random.choice(list(range(*BALL_SPEED_X_RANGE)))
    vy = random.choice(range(*BALL_SPEED_Y_RANGE))
    if up:
        vy *= -1
    return vx, vy

def duplicate_velocity(vx_current: int, vy_current: int) -> tuple[int, int]:
    """Same speed, different direction (avoid perfectly horizontal)."""
    speed = math.hypot(vx_current, vy_current)
    while True:
        ang = random.uniform(0.1, 3.04)           # avoid 0/π
        vx = speed * math.cos(ang)
        if abs(vx) < 1e-3:
            continue
        vy = speed * math.sin(ang)
        if vy_current < 0:
            vy *= -1
        return int(round(vx)), int(round(vy))

# --- entity factories -------------------------------------------------------
_next_ball_id = 0
def create_ball(up: bool = False, pos: tuple[int, int] | None = None) -> dict:
    global _next_ball_id
    rect = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
    rect.center = pos or (random.randint(40, WIDTH - 40), HEIGHT // 2)
    vx, vy = random_velocity(up)
    ball = {"rect": rect, "vx": vx, "vy": vy, "ax": 0.0, "ay": 0.0, "id": _next_ball_id}
    _next_ball_id += 1
    return ball

def spawn_powerup() -> dict:
    x = random.randint(20, WIDTH - POWERUP_WIDTH - 20)
    y = random.randint(80, HEIGHT // 2)
    rect = pygame.Rect(x, y, POWERUP_WIDTH, POWERUP_HEIGHT)
    return {"rect": rect, "timer": POWERUP_DURATION, "collided": set()}

# --- menus ------------------------------------------------------------------
def run_menu() -> None:
    options = ["Start Game", "Quit"]
    selected = 0
    title_font = pygame.font.SysFont(None, 48)
    menu_font  = pygame.font.SysFont(None, 32)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if options[selected] == "Start Game":
                        return
                    pygame.quit(); sys.exit()

        screen.fill("black")
        title = title_font.render("Single-Player Pong", True, "white")
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3 - 50))

        for i, option in enumerate(options):
            colour = "yellow" if i == selected else "white"
            surf   = menu_font.render(option, True, colour)
            screen.blit(surf, (WIDTH//2 - surf.get_width()//2, HEIGHT//2 + i*40))

        pygame.display.flip()
        clock.tick(FPS)

def run_game_over(score: int) -> str:
    options = ["Retry", "Main Menu"]
    selected = 0
    title_font = pygame.font.SysFont(None, 48)
    menu_font  = pygame.font.SysFont(None, 32)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return "retry" if selected == 0 else "menu"

        screen.fill("black")
        title = title_font.render("Game Over", True, "white")
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3 - 50))

        score_surf = menu_font.render(f"Score: {score}", True, "white")
        screen.blit(score_surf, (WIDTH//2 - score_surf.get_width()//2, HEIGHT//2 - 40))

        for i, option in enumerate(options):
            colour = "yellow" if i == selected else "white"
            surf   = menu_font.render(option, True, colour)
            screen.blit(surf, (WIDTH//2 - surf.get_width()//2, HEIGHT//2 + i*40))

        pygame.display.flip()
        clock.tick(FPS)

# --- main game loop ---------------------------------------------------------
def run_game() -> int:
    global debug_mode

    paddle = pygame.Rect(
        WIDTH//2 - PADDLE_WIDTH//2,
        HEIGHT - 20 - PADDLE_HEIGHT,
        PADDLE_WIDTH,
        PADDLE_HEIGHT,
    )

    balls   = [create_ball()]
    powerup = None
    score   = 0

    paddle_vx = 0
    paddle_target_vx = 0
    paddle_start_vx  = 0
    transition_t     = 1.0

    while True:
        dt = clock.tick(FPS) / 1000.0

        # ---- input & debug toggle -----------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                debug_mode = not debug_mode

        keys = pygame.key.get_pressed()
        new_target_vx = 0
        if keys[pygame.K_LEFT]  and paddle.left  > 0:      new_target_vx = -PADDLE_SPEED
        if keys[pygame.K_RIGHT] and paddle.right < WIDTH:  new_target_vx =  PADDLE_SPEED

        if new_target_vx != paddle_target_vx:
            paddle_target_vx = new_target_vx
            paddle_start_vx  = paddle_vx
            transition_t     = 0.0

        if transition_t < 1.0:
            transition_t = min(transition_t + TRANSITION_RATE*dt, 1.0)
            prog = snappy_ease(transition_t)
            paddle_vx = paddle_start_vx + (paddle_target_vx - paddle_start_vx)*prog
        else:
            paddle_vx = paddle_target_vx

        paddle.x += paddle_vx
        paddle.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        # ---- possibly spawn power-up --------------------------------------
        if powerup is None and random.random() < POWERUP_CHANCE:
            powerup = spawn_powerup()

        # ---- update balls -------------------------------------------------
        for b in balls[:]:
            rect = b["rect"]
            prev_vx, prev_vy = b["vx"], b["vy"]

            # gravity & motion
            b["vy"] += GRAVITY
            rect.x  += b["vx"]
            rect.y  += b["vy"]

            # walls
            if rect.left <= 0 or rect.right >= WIDTH:
                b["vx"] *= -1
            if rect.top <= 0:
                b["vy"] *= -1
                speed = math.hypot(b["vx"], b["vy"])
                if speed < MAX_BALL_SPEED:
                    speed = min(speed*SPEED_INCREMENT, MAX_BALL_SPEED)
                    angle = math.atan2(b["vy"], b["vx"])
                    b["vx"] = int(round(math.cos(angle)*speed))
                    b["vy"] = int(round(math.sin(angle)*speed))

            # paddle collision
            if rect.colliderect(paddle) and b["vy"] > 0:
                offset = (rect.centerx - paddle.centerx) / (PADDLE_WIDTH/2)
                b["vy"] *= -1
                b["vx"] += offset*ANGLE_INFLUENCE + paddle_vx*PADDLE_VEL_INFLUENCE
                b["vx"] = max(min(b["vx"]*SPEED_INCREMENT, MAX_BALL_SPEED), -MAX_BALL_SPEED)
                b["vy"] = max(min(b["vy"]*SPEED_INCREMENT, MAX_BALL_SPEED), -MAX_BALL_SPEED)
                score  += 1

            # power-up collision
            if powerup:
                p_rect = powerup["rect"]
                ball_id = b["id"]
                if p_rect.colliderect(rect) and ball_id not in powerup["collided"]:
                    vx_new, vy_new = duplicate_velocity(b["vx"], b["vy"])
                    nb = create_ball(up=b["vy"] < 0, pos=rect.center)
                    nb["vx"], nb["vy"] = vx_new, vy_new
                    powerup["collided"].update({ball_id, nb["id"]})
                    balls.append(nb)
                elif not p_rect.colliderect(rect):
                    powerup["collided"].discard(ball_id)

            # acceleration for debug HUD
            if dt > 0:
                b["ax"] = (b["vx"] - prev_vx)/dt
                b["ay"] = (b["vy"] - prev_vy)/dt
            else:
                b["ax"] = b["ay"] = 0.0

            # off the bottom?
            if rect.top > HEIGHT:
                balls.remove(b)

        # --- power-up timer -------------------------------------------------
        if powerup:
            powerup["timer"] -= dt
            if powerup["timer"] <= 0:
                powerup = None

        # --- game-over condition -------------------------------------------
        if not balls:
            return score

        # --- draw -----------------------------------------------------------
        screen.fill("black")
        pygame.draw.rect(screen, "white", paddle)
        for b in balls:
            pygame.draw.ellipse(screen, "white", b["rect"])
        if powerup:
            pygame.draw.rect(screen, "yellow", powerup["rect"])

        score_surf = font.render(f"Score: {score}", True, "white")
        screen.blit(score_surf, (WIDTH - score_surf.get_width() - 10, 10))

        if debug_mode:
            lines = [f"Balls: {len(balls)}"]
            for b in balls:
                speed  = math.hypot(b["vx"], b["vy"])
                accel  = math.hypot(b["ax"], b["ay"])
                lines.append(f"id {b['id']} spd {speed:.2f} acc {accel:.2f}")
            y = 10
            for line in lines:
                surf = debug_font.render(line, True, "green")
                screen.blit(surf, (10, y)); y += surf.get_height() + 2

        pygame.display.flip()

# --- program entry ----------------------------------------------------------
def main() -> None:
    run_menu()
    while True:
        final_score = run_game()
        choice = run_game_over(final_score)
        if choice == "retry":
            continue
        run_menu()

if __name__ == "__main__":
    pygame.init()
    screen      = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Single-Player Pong")
    clock       = pygame.time.Clock()
    font        = pygame.font.SysFont(None, 32)
    debug_font  = pygame.font.SysFont(None, 24)
    debug_mode  = False
    main()