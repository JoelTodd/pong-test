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
