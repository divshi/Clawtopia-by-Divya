import pygame
import sys
import random
import time

pygame.init()

# Screen setup
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Clawtopia by Divya")
clock = pygame.time.Clock()

# Colors
LIGHT_LILAC = (200, 180, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Load images
claw_img = pygame.image.load('assets/claw.png')
claw_img = pygame.transform.scale(claw_img, (35, 60))

toy_images = [
    (pygame.transform.scale(pygame.image.load('assets/toy1.png'), (60, 60)), 10),
    (pygame.transform.scale(pygame.image.load('assets/toy2.png'), (60, 60)), 20),
    (pygame.transform.scale(pygame.image.load('assets/toy3.png'), (60, 60)), 30),
    (pygame.transform.scale(pygame.image.load('assets/toy4.png'), (60, 60)), 40),
    (pygame.transform.scale(pygame.image.load('assets/toy5.png'), (60, 60)), 50)
]

# Claw variables
claw_x = 0
claw_y = 80
claw_speed = 5
claw_dropping = False
claw_direction = 1
claw_original_y = claw_y

# Toys setup
num_toys = 100

def spawn_toys():
    toys_list = []
    for _ in range(num_toys):
        img, points = random.choice(toy_images)
        x = random.randint(0, WIDTH - 60)
        y = random.randint(HEIGHT // 2, HEIGHT - 60)
        toy_rect = pygame.Rect(x, y, 60, 60)
        toys_list.append({'rect': toy_rect, 'img': img, 'points': points})
    return toys_list

toys = spawn_toys()
toy_caught = False
caught_toy = None
ready_to_drop = False
toy_collected_text_time = 0

# Score and font
score = 0
high_score = 0
font = pygame.font.SysFont(None, 40)
big_font = pygame.font.SysFont(None, 70)

# Game timer
GAME_DURATION = 30
start_time = None
game_active = False

def draw_text_center(text, font, color, surface, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect(center=(WIDTH // 2, y))
    surface.blit(textobj, textrect)

def reset_game():
    global toys, score, claw_x, claw_y, claw_dropping, toy_caught, caught_toy
    global start_time, game_active, ready_to_drop, claw_direction
    global toy_collected_text_time
    toys = spawn_toys()
    score = 0
    claw_x = 0
    claw_y = claw_original_y
    claw_direction = 1
    claw_dropping = False
    toy_caught = False
    caught_toy = None
    ready_to_drop = False
    toy_collected_text_time = 0
    start_time = time.time()
    game_active = True

# Main loop
while True:
    screen.fill(LIGHT_LILAC)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if not game_active:
        draw_text_center("Clawtopia by Divya", big_font, BLACK, screen, HEIGHT // 3)
        draw_text_center(f"High Score: {high_score}", font, BLACK, screen, HEIGHT // 3 + 80)
        draw_text_center("Press SPACE to Start", font, BLACK, screen, HEIGHT // 3 + 140)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            reset_game()
    else:
        elapsed = time.time() - start_time
        time_left = max(0, int(GAME_DURATION - elapsed))
        if time_left == 0:
            game_active = False
            if score > high_score:
                high_score = score

        keys = pygame.key.get_pressed()

        # Auto claw movement before drop
        if not claw_dropping and not toy_caught and not ready_to_drop:
            claw_x += claw_direction * claw_speed
            if claw_x <= 0 or claw_x >= WIDTH - 60:
                claw_direction *= -1
            if keys[pygame.K_SPACE]:
                claw_dropping = True

        # Drop claw
        if claw_dropping:
            claw_y += 5
            claw_rect = pygame.Rect(claw_x, claw_y, 60, 20)
            if not toy_caught:
                for toy in toys:
                    if claw_rect.colliderect(toy['rect']):
                        toy_caught = True
                        caught_toy = toy
                        break
            if toy_caught or claw_y >= HEIGHT - 100:
                claw_dropping = False

        # Move caught toy with claw
        if toy_caught and caught_toy:
            caught_toy['rect'].x = claw_x + 10
            caught_toy['rect'].y = claw_y + 20

        # Return claw
        if not claw_dropping and claw_y > claw_original_y and not ready_to_drop:
            claw_y -= 5
            if claw_y <= claw_original_y:
                claw_y = claw_original_y
                if toy_caught:
                    ready_to_drop = True

        # Drop collected toy on Enter
        if ready_to_drop and caught_toy:
            if keys[pygame.K_RETURN]:
                score += caught_toy['points']
                toys.remove(caught_toy)
                caught_toy = None
                toy_caught = False
                ready_to_drop = False
                toy_collected_text_time = time.time()

        # Draw timer & score with new layout
        screen.blit(font.render(f"Score: {score}", True, BLACK), (10, 10))
        screen.blit(font.render(f"High Score: {high_score}", True, BLACK), (10, 50))
        screen.blit(font.render(f"Time Left: {time_left}s", True, BLACK), (WIDTH - 200, 10))

        # Draw toys
        for toy in toys:
            screen.blit(toy['img'], (toy['rect'].x, toy['rect'].y))

        # Draw claw (gameplay position)
        screen.blit(claw_img, (claw_x, claw_y))

        # Draw held toy
        if ready_to_drop and caught_toy:
            screen.blit(caught_toy['img'], (caught_toy['rect'].x, caught_toy['rect'].y))

        # Show "Toy Collected!" message for 1 second
        if time.time() - toy_collected_text_time < 1:
            draw_text_center("Toy Collected!", font, BLACK, screen, 100)

    pygame.display.update()
    clock.tick(60)
