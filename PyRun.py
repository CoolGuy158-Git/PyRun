import pygame
import random
import math
import time
import os
from sys import exit

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("PyRun")
clock = pygame.time.Clock()
font = pygame.font.SysFont('jetbrainsmononlextralight', 30)
sfont = pygame.font.SysFont('jetbrainsmononlextrabold', 40)

# --Background Music Source: https://pixabay.com/users/--supracode---50170273/ --
pygame.mixer.init()
pygame.mixer.music.load("bg_music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)
# --Game Over Effect Source: https://pixabay.com/users/alphix-52619918/ --
game_over_sfx = pygame.mixer.Sound("gameover.mp3")
# --Background--
bg_img = pygame.image.load("bg.png").convert()
bg_img = pygame.transform.scale(bg_img, (screen.get_width(), screen.get_height()))
scroll_speed = 6

# --Ground--
tile_width = 200
tile_height = 100
ground_y = screen.get_height() - tile_height
ground_img = pygame.Surface((tile_width, tile_height))
grass_height = 30
pygame.draw.rect(ground_img, (46, 125, 50), (0, 0, tile_width, grass_height))
pygame.draw.rect(ground_img, (139, 69, 19), (0, grass_height, tile_width, tile_height - grass_height))
random.seed(42)
for _ in range(1200):
    x = random.randint(0, tile_width - 1)
    y = random.randint(grass_height, tile_height - 1)
    size = random.randint(1, 3)
    shade_offset = random.randint(-40, 10)
    color = (
        max(0, 139 + shade_offset),
        max(0, 69 + shade_offset),
        max(0, 19 + shade_offset)
    )
    pygame.draw.circle(ground_img, color, (x, y), size)

num_blades = 25
spacing = tile_width // num_blades
for i in range(num_blades + 1):
    x_base = i * spacing
    if x_base >= tile_width:
        break
    sway_amp = 4
    mid_sway = random.randint(-sway_amp, sway_amp)
    top_sway = random.randint(-sway_amp, sway_amp)
    points = [
        (x_base, grass_height - 1),
        (x_base + mid_sway, grass_height // 2),
        (x_base + top_sway, 2)
    ]
    green_offset = random.randint(-20, 5)
    color = (
        max(0, 25 + green_offset),
        max(0, 80 + green_offset),
        max(0, 25 + green_offset)
    )
    blade_width = random.randint(2, 4)
    pygame.draw.lines(ground_img, color, False, points, blade_width)

num_tiles = (screen.get_width() // tile_width) + 2
tiles = [pygame.Rect(i * tile_width, ground_y, tile_width, tile_height) for i in range(num_tiles)]

# --Player--
player_img = pygame.image.load("player.png").convert_alpha()
player_width = 50
player_height = 50
player_img = pygame.transform.scale(player_img, (player_width, player_height))
player_x = 100
player_y = ground_y - player_height
player_vel_y = 0
gravity = 0.8
jump_strength = -15
on_ground = True

# --Spikes--
spike_img = pygame.image.load("bug.png").convert_alpha()
spike_width = 90
spike_height = 50
spike_img = pygame.transform.scale(spike_img, (spike_width, spike_height))
spike_bounce_height = 5

spikes = []
last_spike_x = screen.get_width() + random.randint(100, 300)

# --Score--
score = 0
last_time = time.time()

# --Highscore--
highscore_file = "highscore.txt"
if os.path.exists(highscore_file):
    with open(highscore_file, "r") as f:
        try:
            highscore = int(f.read())
        except:
            highscore = 0
else:
    highscore = 0

game_over = False

# --The Loop--
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
            pygame.mixer.music.play(-1)
            game_over = False
            player_y = ground_y - player_height
            player_vel_y = 0
            on_ground = True
            spikes.clear()
            last_spike_x = screen.get_width() + random.randint(100, 300)
            score = 0
            last_time = time.time()

    if not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and on_ground:
            player_vel_y = jump_strength
            on_ground = False
        player_vel_y += gravity
        player_y += player_vel_y
        if player_y + player_height >= ground_y:
            player_y = ground_y - player_height
            player_vel_y = 0
            on_ground = True

        for tile in tiles:
            tile.x -= scroll_speed
        for tile in tiles:
            if tile.right < 0:
                max_x = max(t.x for t in tiles)
                tile.x = max_x + tile_width

        current_time = time.time()
        if current_time - last_time >= 1:
            score += 1
            last_time = current_time

        if random.randint(1, 80) == 1:
            new_x = last_spike_x + random.randint(60, 350)
            spike_y = ground_y - spike_height
            new_spike_rect = pygame.Rect(new_x, spike_y, spike_width, spike_height)
            new_spike_rect.inflate_ip(-10, -10)
            phase = random.uniform(0, math.pi * 2)
            spikes.append({'rect': new_spike_rect, 'phase': phase})
            last_spike_x = new_x

    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

    for spike in spikes[:]:
        spike['rect'].x -= scroll_speed
        if spike['rect'].right < 0:
            spikes.remove(spike)

    # --Drawing--
    screen.blit(bg_img, (0, 0))
    for tile in tiles:
        screen.blit(ground_img, tile.topleft)
    if not game_over:
        screen.blit(player_img, (player_x, player_y))
        for spike in spikes:
            bounce_offset = math.sin(pygame.time.get_ticks() / 200 + spike['phase']) * spike_bounce_height
            spike_draw_y = spike['rect'].y + bounce_offset
            screen.blit(spike_img, (spike['rect'].x, spike_draw_y))
            spike_hitbox = pygame.Rect(spike['rect'].x, spike_draw_y, spike['rect'].width, spike['rect'].height)
            if player_rect.colliderect(spike_hitbox):
                game_over = True
                pygame.mixer.music.stop()
                game_over_sfx.play()
                if score > highscore:
                    highscore = score
                    with open(highscore_file, "w") as f:
                        f.write(str(highscore))
    else:
        over_text = font.render("You Died, Press 'R' To Restart", True, (255, 0, 0))
        screen.blit(over_text, (screen.get_width() // 2 - over_text.get_width() // 2, screen.get_height() // 2))
        highscore_text = sfont.render(f"Highscore: {highscore}", True, (0, 0, 0))
        hs_rect = highscore_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + -55))
        screen.blit(highscore_text, hs_rect)

    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 60))

    fps = int(clock.get_fps())
    fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))

    pygame.display.update()
    clock.tick(60)
