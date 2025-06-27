import pygame
import sys
from .constants import WIDTH, HEIGHT, FPS


def run_menu(screen: pygame.Surface, clock: pygame.time.Clock) -> None:
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
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT // 3 - 50))
        for i, option in enumerate(options):
            color = "yellow" if i == selected else "white"
            surf = menu_font.render(option, True, color)
            screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, HEIGHT // 2 + i * 40))

        pygame.display.flip()
        clock.tick(FPS)


def run_game_over(screen: pygame.Surface, clock: pygame.time.Clock, score: int) -> str:
    options = ["Retry", "Main Menu"]
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
                    return "retry" if selected == 0 else "menu"

        screen.fill("black")
        title_surf = title_font.render("Game Over", True, "white")
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT // 3 - 50))
        score_surf = menu_font.render(f"Score: {score}", True, "white")
        screen.blit(score_surf, (WIDTH // 2 - score_surf.get_width() // 2, HEIGHT // 2 - 40))
        for i, option in enumerate(options):
            color = "yellow" if i == selected else "white"
            surf = menu_font.render(option, True, color)
            screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, HEIGHT // 2 + i * 40))

        pygame.display.flip()
        clock.tick(FPS)
