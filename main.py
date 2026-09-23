import pygame
import time
import random
import sys
import os

pygame.font.init()

WIDTH, HEIGHT = 1900, 1000

PLAYER_WIDTH = 100
PLAYER_HEIGHT = 100
PLAYER_VEL = 5

FONT = pygame.font.SysFont("comicsans", 30)
BIG_FONT = pygame.font.SysFont("comicsans", 60)
TITLE_FONT = pygame.font.SysFont("comicsans", 90)

PRO_WIDTH = 79
PRO_HEIGHT = 79

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("karapuz")

# --- Load images, with safe fallbacks so the menu still works if a file is missing ---
def resource_path(filename):
    """Get the correct path to an asset, whether running as a plain script
    or as a PyInstaller-built exe (where bundled files land in a temp folder)."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def safe_load(path, size=None, fallback_color=(40, 40, 60)):
    try:
        full_path = resource_path(path)
        img = pygame.image.load(full_path)
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception as e:
        log_error(f"Failed to load '{path}' (tried: {resource_path(path)}): {e}")
        surf = pygame.Surface(size if size else (WIDTH, HEIGHT))
        surf.fill(fallback_color)
        return surf


def log_error(message):
    """Write errors to a log file next to the exe, since --windowed hides the console."""
    try:
        log_path = os.path.join(os.path.dirname(settings_file_path()), "error_log.txt")
        with open(log_path, "a") as f:
            f.write(message + "\n")
    except Exception:
        pass

background = safe_load("background.jpg", (WIDTH, HEIGHT), (30, 30, 40))
menu_background = safe_load("menu_background.jpg", (WIDTH, HEIGHT), (20, 20, 35))
player_img = safe_load("player.png", (PLAYER_WIDTH, PLAYER_HEIGHT))
pro_img = safe_load("bullet.png", (PRO_WIDTH, PRO_HEIGHT))

def settings_file_path():
    """Settings should live next to the exe/script itself (not in PyInstaller's
    temp bundle folder), so they actually persist between runs."""
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "settings.txt")


SETTINGS_FILE = settings_file_path()

# --- Settings that persist between menu visits (and between runs, via settings.txt) ---
settings = {
    "fall_speed": 3,     # PRO_VEL
    "survive_time": 30,  # seconds, chosen on Play screen (default)
}


def load_settings():
    """Read settings.txt if it exists and update the settings dict with any values found."""
    try:
        with open(SETTINGS_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if key in settings:
                    try:
                        settings[key] = int(value)
                    except ValueError:
                        pass
    except FileNotFoundError:
        pass  # No saved settings yet, just use the defaults above


def save_settings():
    """Write the current settings dict to settings.txt."""
    try:
        with open(SETTINGS_FILE, "w") as f:
            for key, value in settings.items():
                f.write(f"{key}={value}\n")
    except OSError:
        pass  # If we can't write for some reason, just keep going in-memory


load_settings()


class Button:
    def __init__(self, x, y, w, h, text, base_color=(70, 70, 90), hover_color=(110, 110, 140)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.base_color = base_color
        self.hover_color = hover_color

    def draw(self, win):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.base_color
        pygame.draw.rect(win, color, self.rect, border_radius=10)
        pygame.draw.rect(win, (255, 255, 255), self.rect, 2, border_radius=10)
        label = FONT.render(self.text, 1, (255, 255, 255))
        win.blit(label, (self.rect.centerx - label.get_width() / 2,
                          self.rect.centery - label.get_height() / 2))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


def main_menu():
    clock = pygame.time.Clock()

    btn_w, btn_h = 300, 80
    center_x = WIDTH / 2 - btn_w / 2

    play_btn = Button(center_x, 400, btn_w, btn_h, "Play")
    settings_btn = Button(center_x, 500, btn_w, btn_h, "Settings")
    exit_btn = Button(center_x, 600, btn_w, btn_h, "Exit")

    while True:
        clock.tick(60)
        WIN.blit(menu_background, (0, 0))

        title = TITLE_FONT.render("karapuz", 1, (255, 255, 255))
        WIN.blit(title, (WIDTH / 2 - title.get_width() / 2, 200))

        play_btn.draw(WIN)
        settings_btn.draw(WIN)
        exit_btn.draw(WIN)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.is_clicked(event.pos):
                    return "choose_time"
                if settings_btn.is_clicked(event.pos):
                    return "settings"
                if exit_btn.is_clicked(event.pos):
                    return "exit"


def settings_menu():
    clock = pygame.time.Clock()

    minus_btn = Button(WIDTH / 2 - 150, 450, 80, 80, "-")
    plus_btn = Button(WIDTH / 2 + 70, 450, 80, 80, "+")
    back_btn = Button(WIDTH / 2 - 150, 600, 300, 80, "Back")

    while True:
        clock.tick(60)
        WIN.blit(menu_background, (0, 0))

        title = BIG_FONT.render("Settings", 1, (255, 255, 255))
        WIN.blit(title, (WIDTH / 2 - title.get_width() / 2, 200))

        label = FONT.render("Fall speed of objects:", 1, (255, 255, 255))
        WIN.blit(label, (WIDTH / 2 - label.get_width() / 2, 350))

        value_text = FONT.render(str(settings["fall_speed"]), 1, (255, 255, 255))
        WIN.blit(value_text, (WIDTH / 2 - value_text.get_width() / 2, 470))

        minus_btn.draw(WIN)
        plus_btn.draw(WIN)
        back_btn.draw(WIN)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if minus_btn.is_clicked(event.pos):
                    settings["fall_speed"] = max(1, settings["fall_speed"] - 1)
                    save_settings()
                if plus_btn.is_clicked(event.pos):
                    settings["fall_speed"] = min(15, settings["fall_speed"] + 1)
                    save_settings()
                if back_btn.is_clicked(event.pos):
                    return "menu"


def choose_time_menu():
    clock = pygame.time.Clock()

    minus_btn = Button(WIDTH / 2 - 150, 450, 80, 80, "-")
    plus_btn = Button(WIDTH / 2 + 70, 450, 80, 80, "+")
    start_btn = Button(WIDTH / 2 - 150, 600, 300, 80, "Start")
    back_btn = Button(WIDTH / 2 - 150, 700, 300, 80, "Back")

    while True:
        clock.tick(60)
        WIN.blit(menu_background, (0, 0))

        title = BIG_FONT.render("Survive how long?", 1, (255, 255, 255))
        WIN.blit(title, (WIDTH / 2 - title.get_width() / 2, 200))

        value_text = FONT.render(f"{settings['survive_time']} seconds", 1, (255, 255, 255))
        WIN.blit(value_text, (WIDTH / 2 - value_text.get_width() / 2, 470))

        minus_btn.draw(WIN)
        plus_btn.draw(WIN)
        start_btn.draw(WIN)
        back_btn.draw(WIN)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if minus_btn.is_clicked(event.pos):
                    settings["survive_time"] = max(5, settings["survive_time"] - 5)
                    save_settings()
                if plus_btn.is_clicked(event.pos):
                    settings["survive_time"] = settings["survive_time"] + 5
                    save_settings()
                if start_btn.is_clicked(event.pos):
                    return "play"
                if back_btn.is_clicked(event.pos):
                    return "menu"


def draw(player, elapsed_time, pros, survive_time):
    WIN.blit(background, (0, 0))

    remaining = max(0, round(survive_time - elapsed_time))
    time_text = FONT.render(f"Time left: {remaining}s", 1, "white")
    WIN.blit(time_text, (10, 10))

    WIN.blit(player_img, (player.x, player.y))

    for pro in pros:
        WIN.blit(pro_img, (pro.x, pro.y))

    pygame.display.update()


def show_end_screen(text):
    end_text = BIG_FONT.render(text, 1, (255, 255, 255))
    WIN.blit(end_text, (WIDTH / 2 - end_text.get_width() / 2, HEIGHT / 2 - end_text.get_height() / 2))
    pygame.display.update()
    pygame.time.delay(1800)


def play_game():
    run = True

    player = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT,
                          PLAYER_WIDTH, PLAYER_HEIGHT)
    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0

    survive_time = settings["survive_time"]
    pro_vel = settings["fall_speed"]

    pro_add_increment = 2000
    pro_count = 0

    pros = []
    hit = False
    won = False

    while run:
        pro_count += clock.tick(1000)
        elapsed_time = time.time() - start_time

        if elapsed_time >= survive_time:
            won = True
            break

        if pro_count > pro_add_increment:
            for _ in range(2):
                pro_x = random.randint(0, WIDTH - PRO_WIDTH)
                pro = pygame.Rect(pro_x, -PRO_HEIGHT,
                                   PRO_WIDTH, PRO_HEIGHT)
                pros.append(pro)

            pro_add_increment = max(200, pro_add_increment - 50)
            pro_count = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - PLAYER_VEL >= 0:
            player.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and player.x + PLAYER_VEL + player.width <= WIDTH:
            player.x += PLAYER_VEL

        for pro in pros[:]:
            pro.y += pro_vel
            if pro.y > HEIGHT:
                pros.remove(pro)
            elif pro.y + pro.height >= player.y and pro.colliderect(player):
                pros.remove(pro)
                hit = True
                break

        if hit:
            break

        draw(player, elapsed_time, pros, survive_time)

    if won:
        show_end_screen("You survived! You win! :)")
    elif hit:
        show_end_screen("You lost (((")

    return "menu"


def main():
    state = "menu"

    while True:
        if state == "menu":
            state = main_menu()
        elif state == "settings":
            state = settings_menu()
        elif state == "choose_time":
            state = choose_time_menu()
        elif state == "play":
            state = play_game()
        elif state == "exit":
            break

    pygame.quit()


if __name__ == "__main__":
    main()
