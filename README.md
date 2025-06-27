# Single Player Pong

A simple single-player Pong game built in Python using Pygame. The action now
scrolls vertically with your paddle at the bottom of the screen.

![Screenshot](Screenshot%202025-06-26%20212716.png)

## Requirements

- Python 3.9 or later
- [Pygame library](https://www.pygame.org/)

## Installation

1. **Clone this repository** or download `single_player_pong.py` to your computer.
2. Install Pygame using pip:

   ```bash
   pip install pygame
   ```

The ball speeds up slightly with each successful paddle hit, making the
game progressively more challenging. Keep an eye out for the yellow powerup
that appears as a short, unmoving paddle. It sticks around for a few seconds
and duplicates any ball that passes through it, launching the new copy in a
random direction that keeps the same vertical motion and overall speed as the
source ball while never travelling perfectly sideways. The game only resets
when every ball has been missed.
