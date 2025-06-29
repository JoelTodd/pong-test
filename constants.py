"""Collection of gameplay constants.

These values control the size and speed of the game elements as well as
physics related tweaks.  They are grouped here so beginners can easily change
them and see how the game behaviour changes.
"""

WIDTH, HEIGHT = 512, 640  # size of the game window
FPS = 60  # frames per second, influences overall game speed

PADDLE_WIDTH, PADDLE_HEIGHT = 80, 6  # dimensions of the player's paddle
BALL_SIZE = 12                       # diameter of the ball
PADDLE_SPEED = 8                     # how fast the paddle moves

BALL_SPEED_X_RANGE = (-4, 4)          # range for random initial horizontal velocity
BALL_SPEED_Y_RANGE = (4, 6)           # range for random initial vertical velocity
SPEED_INCREMENT     = 1.08            # how much the ball speeds up after bounces
MAX_BALL_SPEED      = 50              # cap on ball speed to keep things playable
TRANSITION_RATE     = 12              # controls smoothing of paddle acceleration
POWERUP_WIDTH, POWERUP_HEIGHT = 100, 4  # dimensions of the powerup bar
POWERUP_DURATION    = 8.0             # how long a powerup stays on screen
POWERUP_CHANCE      = 0.005           # chance each frame for a new powerup to spawn
ANGLE_INFLUENCE     = 5               # how sharply the ball can be angled off the paddle
PADDLE_VEL_INFLUENCE = 0.5            # paddle motion contributes to ball direction
GRAVITY             = 0.01            # mild downward pull to make the game harder
