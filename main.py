import pygame
import time
import random

pygame.font.init()

WIDTH, HEIGHT = 1900, 1000

PLAYER_WIDTH = 100
PLAYER_HEIGHT = 100
PLAYER_VEL = 5

FONT = pygame.font.SysFont("comicsans", 30)

PRO_WIDTH = 79
PRO_HEIGHT = 79
PRO_VEL = 3

WIN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("karapuz")

background = pygame.image.load("background.jpg")

player_img = pygame.image.load("player.png")
player_img = pygame.transform.scale(player_img, (PLAYER_WIDTH, PLAYER_HEIGHT))

pro_img = pygame.image.load("bullet.png")
pro_img = pygame.transform.scale(pro_img, (PRO_WIDTH, PRO_HEIGHT))


def draw(player, elapsed_time, pros):
    WIN.blit(background, (0, 0))

    time_text = FONT.render(f"Tme: {round(elapsed_time)}s", 1, "white")
    WIN.blit(time_text, (10, 10))

    WIN.blit(player_img, (player.x, player.y))

    for pro in pros:
        WIN.blit(pro_img, (pro.x, pro.y))

    pygame.display.update()


def main():
    run = True

    player = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT,
                         PLAYER_WIDTH, PLAYER_HEIGHT)
    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0

    pro_add_increment = 2000
    pro_count = 0

    pros = []
    hit = False

    while run:
        pro_count += clock.tick(1000)
        elapsed_time = time.time() - start_time

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
                run = False
                break

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - PLAYER_VEL >= 0:
            player.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and player.x + PLAYER_VEL + player.width <= WIDTH:
            player.x += PLAYER_VEL

        for pro in pros[:]:
            pro.y += PRO_VEL
            if pro.y > HEIGHT:
                pros.remove(pro)
            elif pro.y + pro.height >= player.y and pro.colliderect(player):
                pros.remove(pro)
                hit = True
                break

        if hit:
            lost_text = FONT.render("You lost (((", 1, (255, 255, 255))
            WIN.blit(lost_text, (WIDTH / 2 - lost_text.get_width() / 2, HEIGHT / 2 - lost_text.get_height() / 2))
            pygame.display.update()
            pygame.time.delay(1500)
            break

        draw(player, elapsed_time, pros)
    pygame.quit()


if __name__ == "__main__":
    main()
