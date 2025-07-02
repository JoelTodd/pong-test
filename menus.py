"""Simple text-based menus shown before and after gameplay."""

import pygame
import sys
from constants import Screen
from demo import DemoGame
from synth import SOUNDS


def run_menu(screen, clock) -> None:
    """Display the main menu until the user chooses to start or quit.

    Parameters
    ----------
    screen:
        Display surface used for rendering.
    clock:
        Clock for controlling the frame rate.
    """

    options = ["Start Game", "Quit"]
    selected = 0

    title_font = pygame.font.SysFont(None, 48)
    menu_font = pygame.font.SysFont(None, 32)
    demo = DemoGame()
    demo_surface = pygame.Surface(
        (Screen.WIDTH, Screen.HEIGHT), pygame.SRCALPHA
    )

    while True:
        dt = clock.tick(Screen.FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    # Move selection up.
                    selected = (selected - 1) % len(options)
                    SOUNDS["menu_move"].play()
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    # Move selection down.
                    selected = (selected + 1) % len(options)
                    SOUNDS["menu_move"].play()
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if options[selected] == "Start Game":
                        SOUNDS["menu_select"].play()
                        return
                    pygame.quit()
                    SOUNDS["menu_select"].play()
                    sys.exit()

        demo.update(dt)
        screen.fill("black")
        demo_surface.fill((0, 0, 0, 0))
        demo.draw(demo_surface)
        demo_surface.set_alpha(128)
        screen.blit(demo_surface, (0, 0))
        title = title_font.render("Single-Player Pong", True, "white")
        screen.blit(
            title,
            (
                Screen.WIDTH // 2 - title.get_width() // 2,
                Screen.HEIGHT // 3 - 50,
            ),
        )

        for i, option in enumerate(options):
            colour = "yellow" if i == selected else "white"
            surf = menu_font.render(option, True, colour)
            screen.blit(
                surf,
                (
                    Screen.WIDTH // 2 - surf.get_width() // 2,
                    Screen.HEIGHT // 2 + i * 40,
                ),
            )
        pygame.display.flip()


def run_game_over(screen, clock, score: int) -> str:
    """Display the game-over screen and return the player's choice.

    Parameters
    ----------
    screen:
        The display surface to draw on.
    clock:
        Clock for timing the menu loop.
    score:
        The score achieved in the preceding game.

    Returns
    -------
    str
        ``"retry"`` or ``"menu"`` depending on the player's selection.
    """

    options = ["Retry", "Main Menu"]
    selected = 0
    title_font = pygame.font.SysFont(None, 48)
    menu_font = pygame.font.SysFont(None, 32)

    while True:
        clock.tick(Screen.FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    # Move selection up.
                    selected = (selected - 1) % len(options)
                    SOUNDS["menu_move"].play()
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    # Move selection down.
                    selected = (selected + 1) % len(options)
                    SOUNDS["menu_move"].play()
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    SOUNDS["menu_select"].play()
                    return "retry" if selected == 0 else "menu"

        screen.fill("black")
        title = title_font.render("Game Over", True, "white")
        screen.blit(
            title,
            (
                Screen.WIDTH // 2 - title.get_width() // 2,
                Screen.HEIGHT // 3 - 50,
            ),
        )

        score_surf = menu_font.render(f"Score: {score}", True, "white")
        screen.blit(
            score_surf,
            (
                Screen.WIDTH // 2 - score_surf.get_width() // 2,
                Screen.HEIGHT // 2 - 40,
            ),
        )

        for i, option in enumerate(options):
            colour = "yellow" if i == selected else "white"
            surf = menu_font.render(option, True, colour)
            screen.blit(
                surf,
                (
                    Screen.WIDTH // 2 - surf.get_width() // 2,
                    Screen.HEIGHT // 2 + i * 40,
                ),
            )
        pygame.display.flip()
