import pygame, sys, random
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.init()

# ---------- FUNCTIONS ----------

def draw_floor():
    screen.blit(floor, (floor_x_pos, 650))
    screen.blit(floor, (floor_x_pos + 432, 650))

def create_pipe():
    # choose center of gap
    random_pipe_pos = random.choice(pipe_height)
    gap_size = 300  # bigger gap than before
    bottom_pipe = pipe_surface.get_rect(midtop=(500, random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom=(500, random_pipe_pos - gap_size))
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 3  # slower pipes
    # remove off-screen pipes
    pipes = [p for p in pipes if p.right > -50]
    return pipes

def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 600:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)

pipe_height = [250, 275, 300, 325, 350]

def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            hit_sound.play()
            return False
    if bird_rect.top <= -75 or bird_rect.bottom >= 650:
        return False
    return True 

def rotate_bird(bird1):
    new_bird = pygame.transform.rotozoom(bird1, -bird_movement * 3, 1)
    return new_bird        

def bird_animation():
    new_bird = bird_list[bird_index]
    new_bird_rect = new_bird.get_rect(center=(100, bird_rect.centery))
    return new_bird, new_bird_rect

def score_display(game_state):
    if game_state == 'main game':
        score_surface = game_font.render(str(int(score)), True, (255,255,255))
        score_rect = score_surface.get_rect(center=(216, 100))
        screen.blit(score_surface, score_rect)
    if game_state == 'game_over':
        score_surface = game_font.render(f'Score: {int(score)}', True, (255,255,255))
        score_rect = score_surface.get_rect(center=(216, 100))
        screen.blit(score_surface, score_rect)

        high_score_surface = game_font.render(f'High Score: {int(high_score)}', True, (255,255,255))
        high_score_rect = high_score_surface.get_rect(center=(216, 630))
        screen.blit(high_score_surface, high_score_rect) 

def update_score(score, high_score):
    if score > high_score:
        high_score = score
    return high_score

# NEW: per-pipe scoring
def score_update():
    global score, score_ready
    for pipe in pipe_list:
        # when bird passes pipe center
        if 95 < pipe.centerx < 105 and score_ready:
            score += 1
            score_sound.play()
            score_ready = False
        # once pipe has moved left of bird, allow scoring again
        if pipe.centerx < 0:
            score_ready = True

# ---------- SETUP ----------

screen = pygame.display.set_mode((432, 768))
clock = pygame.time.Clock()
game_font = pygame.font.Font('04B_19.ttf', 35)

# Game variables
gravity = 0.17
bird_movement = 0
game_active = True
score = 0
high_score = 0
score_ready = True

# Background
background = pygame.image.load('assess/background-night.png').convert()
background = pygame.transform.scale2x(background)

# Floor
floor = pygame.image.load('assess/floor.png')
floor = pygame.transform.scale2x(floor)
floor_x_pos = 0

# Bird
bird_down = pygame.image.load('assess/yellowbird-downflap.png').convert_alpha()
bird_mid = pygame.image.load('assess/yellowbird-midflap.png').convert_alpha()
bird_up = pygame.image.load('assess/yellowbird-upflap.png').convert_alpha()
bird_list = [bird_down, bird_mid, bird_up] # 0,1,2
bird_index = 0
bird = bird_list[bird_index]
bird_rect = bird.get_rect(center=(100, 384))

# Bird flap timer
birdflap = pygame.USEREVENT + 1
pygame.time.set_timer(birdflap, 200)

# Pipes
pipe_surface = pygame.image.load('assess/pipe-green.png').convert()
pipe_surface = pygame.transform.scale2x(pipe_surface)
pipe_list = []

spawnpipe = pygame.USEREVENT
pygame.time.set_timer(spawnpipe, 1800)  # further apart

# Game over screen
game_over_surface = pygame.transform.scale2x(
    pygame.image.load('assess/message.png').convert_alpha()
)
game_over_rect = game_over_surface.get_rect(center=(216, 384))

# Sounds
flap_sound = pygame.mixer.Sound('sounds/sfx_wing.wav')
hit_sound = pygame.mixer.Sound('sounds/sfx_hit.wav')
score_sound = pygame.mixer.Sound('sounds/sfx_point.wav')

# ---------- GAME LOOP ----------

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active: 
                bird_movement = 0
                bird_movement -= 7   # same as “good” code
                flap_sound.play()
            if event.key == pygame.K_SPACE and game_active == False:
                game_active = True
                pipe_list.clear()
                bird_rect.center = (100, 384)
                bird_movement = 0
                score = 0
                score_ready = True
        if event.type == spawnpipe:
            pipe_list.extend(create_pipe())
        if event.type == birdflap:
            if bird_index < 2:
                bird_index += 1
            else:
                bird_index = 0
            bird, bird_rec = bird_animation()

    screen.blit(background, (0, 0))

    if game_active:
        # Bird
        bird_movement += gravity      
        rotated_bird = rotate_bird(bird)
        bird_rect.centery += bird_movement
        screen.blit(rotated_bird, bird_rect)
        game_active = check_collision(pipe_list)

        # Pipes
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        # Score
        score_update()
        score_display('main game')
    else:
        screen.blit(game_over_surface, game_over_rect)
        high_score = update_score(score, high_score)
        score_display('game_over')

    # Floor
    floor_x_pos -= 1
    draw_floor()
    if floor_x_pos <= -432:
        floor_x_pos = 0

    pygame.display.update()
    clock.tick(120)
