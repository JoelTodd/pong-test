import pygame
from constants import WIDTH, HEIGHT
from menus import run_menu, run_game_over
from game import run_game


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Single-Player Pong")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 32)
    debug_font = pygame.font.SysFont(None, 24)

    run_menu(screen, clock)
    while True:
        final_score = run_game(screen, clock, font, debug_font)
        choice = run_game_over(screen, clock, final_score)
        if choice == "retry":
            continue
        run_menu(screen, clock)


if __name__ == "__main__":
    main()
