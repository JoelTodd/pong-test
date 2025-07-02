"""Program entry point for the single-player Pong game."""

import pygame
from constants import Screen
from menus import run_menu, run_game_over
from game import run_game
from synth import init_sounds


def main() -> None:
    """Set up Pygame and run the high level game loops."""
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    init_sounds()
    screen = pygame.display.set_mode((Screen.WIDTH, Screen.HEIGHT))
    pygame.display.set_caption("Single-Player Pong")
    clock = pygame.time.Clock()

    # Pre-create fonts so we don't recreate them every frame.
    font = pygame.font.SysFont(None, 32)
    debug_font = pygame.font.SysFont(None, 24)

    # Show the menu screen first.
    run_menu(screen, clock)
    while True:
        # Play one round of the game and get the final score.
        final_score = run_game(screen, clock, font, debug_font)

        # When the player loses, display the game over screen and ask what to do.
        choice = run_game_over(screen, clock, final_score)
        if choice == "retry":
            # Immediately start another round.
            continue
        # Otherwise return to the main menu.
        run_menu(screen, clock)


if __name__ == "__main__":
    main()
