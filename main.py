import pgzrun
import time
import types

WIDTH = 640
HEIGHT = 700

score = 0
lives = 3
playing = False
paused = False

MUNCHER_START_X = WIDTH / 2
MUNCHER_START_Y = (HEIGHT / 4) * 3
muncher = Actor('muncher', (MUNCHER_START_X, MUNCHER_START_Y))
muncher.images = ['muncher', 'muncher2']
muncher.vx = 150
muncher.vy = 150
muncher.fps = 2

BOUNDS_X1 = 50
BOUNDS_Y1 = 50
BOUNDS_X2 = WIDTH - BOUNDS_X1
BOUNDS_Y2 = HEIGHT - BOUNDS_Y1


def keep_in_bounds(actor):
    if actor.x < BOUNDS_X1:
        actor.x = BOUNDS_X1
    elif actor.x > BOUNDS_X2:
        actor.x = BOUNDS_X2

    if actor.y < BOUNDS_Y1:
        actor.y = BOUNDS_Y1
    elif actor.y > BOUNDS_Y2:
        actor.y = BOUNDS_Y2


Actor.keep_in_bounds = keep_in_bounds


def animate(actor):
    if not hasattr(actor, "images"):
        return
    if not hasattr(actor, "fps"):
        actor.fps = 5
    if not hasattr(actor, "next_frame"):
        actor.next_frame = time.time_ns()
    if not hasattr(actor, "frame"):
        actor.frame = 0

    now = time.time_ns()

    if now > actor.next_frame:
        actor.frame = (actor.frame + 1) % len(actor.images)
        actor.image = actor.images[actor.frame]
        while actor.next_frame < now:
            actor.next_frame += (1_000_000_000 / actor.fps)


Actor.animate = animate

GHOST_START_X = WIDTH / 2
GHOST_START_Y = (HEIGHT / 3)
GHOST_START = (GHOST_START_X, GHOST_START_Y)

blue = Actor('ghost-blue', GHOST_START)
blue.images = ['ghost-blue', 'ghost-blue2']
blue.vx = -60
blue.vy = -60

orange = Actor('ghost-orange', GHOST_START)
orange.images = ['ghost-orange', 'ghost-orange2']
orange.vx = 260
orange.vy = 60

red = Actor('ghost-red', GHOST_START)
red.images = ['ghost-red', 'ghost-red2']
red.vx = 40
red.vy = 280

pink = Actor('ghost-pink', GHOST_START)
pink.images = ['ghost-pink', 'ghost-pink2']
pink.vx = 60
pink.vy = 60

blue2 = Actor('ghost-blue', GHOST_START)
blue2.images = ['ghost-blue', 'ghost-blue2']
blue2.vx = -10
blue2.vy = -60

ghosts = [blue, orange, red, pink, blue2]


def ghost_move(ghost, dt):
    ghost.x += ghost.vx * dt
    ghost.y += ghost.vy * dt

    if ghost.x >= BOUNDS_X2:
        ghost.x = BOUNDS_X2
        ghost.vx *= -1
    elif ghost.x <= BOUNDS_X1:
        ghost.x = BOUNDS_X1
        ghost.vx *= -1

    if ghost.y >= BOUNDS_Y2:
        ghost.y = BOUNDS_Y2
        ghost.vy *= -1
    elif ghost.y <= BOUNDS_Y1:
        ghost.y = BOUNDS_Y1
        ghost.vy *= -1


for ghost in ghosts:
    ghost.move = types.MethodType(ghost_move, ghost)


def unpause():
    global paused
    paused = False


def reset_actors():
    for ghost in ghosts:
        ghost.x = GHOST_START_X
        ghost.y = GHOST_START_Y

    muncher.x = MUNCHER_START_X
    muncher.y = MUNCHER_START_Y

    if lives <= 0:
        exit()

    clock.schedule(unpause, 2)


walls = [
    Actor('wall', (WIDTH / 4, HEIGHT / 2)),
    Actor('wall', ((WIDTH / 4) * 3, HEIGHT / 2)),
    Actor('wall', (WIDTH / 2, HEIGHT / 5)),
    Actor('wall', (WIDTH / 2, (HEIGHT / 5) * 4)),
    Actor('wall2', (WIDTH / 5, HEIGHT / 3)),
    Actor('wall2', ((WIDTH / 5) * 4, HEIGHT / 3)),
    Actor('wall2', (WIDTH / 5, (HEIGHT / 3) * 2)),
    Actor('wall2', ((WIDTH / 5) * 4, (HEIGHT / 3) * 2)),
]


def check_for_wall_collisions(actor):
    for wall in walls:
        if wall.colliderect(actor):
            if actor.top < wall.top and actor.bottom > wall.top:
                actor.bottom = wall.top

            if actor.bottom > wall.bottom and actor.top < wall.bottom:
                actor.top = wall.bottom

            if actor.left < wall.left and actor.right > wall.left:
                actor.right = wall.left

            if actor.right > wall.right and actor.left < wall.right:
                actor.left = wall.right


power_pellets = []
muncher.power = 0


def create_pellets():
    global pellets
    pellets = []
    for y in range(12):
        for x in range(12):
            pos = (50 + (50 * x), 100 + (50 * y))
            collide = False
            for wall in walls:
                if wall.collidepoint(pos):
                    collide = True

            if not collide:
                pellets.append(Actor('pellet', pos))

    global power_pellets
    power_pellets = [
        Actor('power-pellet', (WIDTH / 5, HEIGHT / 6)),
        Actor('power-pellet', ((WIDTH / 5) * 4, HEIGHT / 6)),
        Actor('power-pellet', (WIDTH / 5, (HEIGHT / 6) * 5)),
        Actor('power-pellet', ((WIDTH / 5) * 4, (HEIGHT / 6) * 5)),
    ]


pellets = []
create_pellets()


def chase(ghost, dt):
    if ghost.vx < 0:
        ghost.vx *= -1

    if ghost.vy < 0:
        ghost.vy *= -1

    if muncher.power:
        ghost.vx *= -1
        ghost.vy *= -1

    if ghost.x < muncher.x:
        ghost.x += ghost.vx * dt
    else:
        ghost.x -= ghost.vx * dt

    if ghost.y < muncher.y:
        ghost.y += ghost.vy * dt
    else:
        ghost.y -= ghost.vy * dt


blue.move = types.MethodType(chase, blue)

fruits = [
    Actor('apple', (WIDTH / 2, HEIGHT / 2)),
    Actor('lemon', (WIDTH / 2, HEIGHT / 2)),
    Actor('strawberry', (WIDTH / 2, HEIGHT / 2)),
]

fruit = None


def show_fruit():
    import random
    global fruit
    fruit = fruits[random.randint(0, len(fruits) - 1)]
    clock.schedule(hide_fruit, 3)


def hide_fruit():
    global fruit
    fruit = None
    clock.schedule(show_fruit, 5)


clock.schedule(show_fruit, 5)

next_life = 10000

scared_images = ['ghost-scared', 'ghost-scared2']


def draw():
    screen.clear()
    screen.draw.text(f"{score}", (WIDTH / 2, 15), color="red", fontsize=24)

    for i in range(lives):
        screen.blit('muncher', (5 + (37 * i), 5))

    muncher.animate()
    muncher.draw()

    for ghost in ghosts:
        ghost.animate()
        ghost.draw()

    for wall in walls:
        wall.draw()

    for pellet in pellets:
        pellet.draw()

    if fruit is not None:
        fruit.draw()

    for pellet in power_pellets:
        pellet.draw()


def update(dt):
    global lives, paused

    if paused:
        return

    if keyboard.left:
        muncher.x -= muncher.vx * dt
    if keyboard.right:
        muncher.x += muncher.vx * dt
    if keyboard.up:
        muncher.y -= muncher.vy * dt
    if keyboard.down:
        muncher.y += muncher.vy * dt

    muncher.keep_in_bounds()

    for ghost in ghosts:
        ghost.move(dt)
        ghost.keep_in_bounds()

    if muncher.power <= 0:
        for ghost in ghosts:
            if ghost.colliderect(muncher):
                lives -= 1
                sounds.lose_life.play()
                paused = True
                clock.schedule(reset_actors, 2)

    check_for_wall_collisions(muncher)

    global score, pellets
    before = len(pellets)
    pellets = [pellet for pellet in pellets if not pellet.colliderect(muncher)]
    after = len(pellets)
    score += (before - after) * 100
    if after < before:
        sounds.eat_pellet.play()

    if len(pellets) <= 0:
        paused = True
        sounds.new_level.play()
        create_pellets()
        reset_actors()

    global fruit
    if fruit is not None:
        if fruit.colliderect(muncher):
            sounds.eat_fruit.play()
            index = fruits.index(fruit) + 1
            score += (1000 * index)
            fruit = None

    global next_life
    if score >= next_life:
        sounds.new_life.play()
        lives += 1
        next_life += 10000

    muncher.power -= dt
    if muncher.power < 0:
        muncher.power = 0

    global power_pellets
    before = len(power_pellets)
    power_pellets = [pellet for pellet in power_pellets if not pellet.colliderect(muncher)]
    after = len(power_pellets)
    score += (before - after) * 500
    if after < before:
        muncher.power = 5

    global scared_images
    if muncher.power > 0:
        for ghost in ghosts:
            if ghost.images != scared_images:
                ghost.original_images = ghost.images
                ghost.images = scared_images
                ghost.frame = 0
    else:
        for ghost in ghosts:
            if ghost.images == scared_images:
                ghost.images = ghost.original_images
                ghost.frame = 0

    if muncher.power > 0:
        for ghost in ghosts:
            if ghost.colliderect(muncher):
                sounds.eat_ghost.play()
                score += 500
                ghost.pos = GHOST_START


pgzrun.go()
