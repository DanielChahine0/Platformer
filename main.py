# import os
# import random
# import math
import pygame
from os import listdir
from os.path import isfile, join

# Initializing pygame
pygame.init()
pygame.display.set_caption("Platformer")

# -------------- VARIABLES --------------
BG_COLOR = (255, 255, 255)
WIDTH, HEIGHT = 1100, 750

FPS = 60

PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))


# Function that flips the character depending on what it looks at
def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    # Path to get a sprite
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size, name):
    # Get the path of the image
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()

    # Different blocks depending on the given name
    if name == "Rock":
        surface = pygame.Surface((64, 64), pygame.SRCALPHA, 32)
        rect = pygame.Rect(96 * 2 + 16, 64 + 16, 32, 32)
        surface.blit(image, (0, 0), rect)

    elif name == "Gold_plate":
        surface = pygame.Surface((64, 64), pygame.SRCALPHA, 32)
        rect = pygame.Rect(96 * 3 - 16, 128, 64, 64)
        surface.blit(image, (0, 0), rect)

    else:
        surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
        rect = pygame.Rect(96, 0, size, size)
        surface.blit(image, (0, 0), rect)

    return pygame.transform.scale2x(surface)


# -------------- CLASSES --------------
class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, True)
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.sprite = None

    def change_char(self, name):
        self.SPRITES = load_sprite_sheets("MainCharacters", name, 32, 32, True)

    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 9
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        # Gravity looking mechanism
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)

        # Movement
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        # Ticks counter
        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.fall_count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

    def die(self):
        self.rect.x = 1500
        self.rect.y = 400
        self.fall_count = 0
        self.hit_count = 0
        self.animation_count = 0
        self.jump_count = 0
        self.x_vel = 0
        self.y_vel = 0


# OBJECT CLASS - for building blocks
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size, name="Terrain"):
        if name == "Gold_plate":
            super().__init__(x, y, size + 64, size)
        else:
            super().__init__(x, y, size, size)
        block = get_block(size, name)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 10

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


class Fruit(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fruit")
        self.fruit = load_sprite_sheets("Items", "Fruits", width, height)
        self.image = self.fruit["Apple"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Apple"

    def apple(self):
        self.animation_name = "Apple"

    def banana(self):
        self.animation_name = "Bananas"

    def cherries(self):
        self.animation_name = "Cherries"

    def kiwi(self):
        self.animation_name = "Kiwi"

    def melon(self):
        self.animation_name = "Melon"

    def orange(self):
        self.animation_name = "Orange"

    def pineapple(self):
        self.animation_name = "Pineapple"

    def strawberry(self):
        self.animation_name = "Strawberry"

    def loop(self):
        sprites = self.fruit[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


# -------------- FUNCTIONS --------------
def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)
    return tiles, image


def draw(surface, background, bg_image, player, objects, offset_x):
    for tile in background:
        surface.blit(bg_image, tile)

    for obj in objects:
        obj.draw(surface, offset_x)

    player.draw(surface, offset_x)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy >= 0 and (player.rect.right > obj.rect.left):
                player.rect.bottom = obj.rect.top
                player.landed()
                collided_objects.append(obj)
                break
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
                collided_objects.append(obj)
                break

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()

    collided_object = None

    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    # stop moving the player if there is no key pressed
    player.x_vel = 0

    # Check vertical collision with the fruit
    for fruit in objects:
        if isinstance(fruit, Fruit) and pygame.sprite.collide_mask(player, fruit):
            # Handle collision with fruit
            fruit_rect = fruit.rect
            player_rect = player.rect

            # Check if the collision is from top or bottom
            if (player_rect.bottom > fruit_rect.top and player.y_vel < 0) or \
                    (player_rect.top < fruit_rect.bottom and player.y_vel > 0):
                objects.remove(fruit)

    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)

    to_check = [*vertical_collide, collide_left, collide_right, ]

    # Check horizontal collision
    for obj in to_check:
        if obj and obj.name == "fruit":
            objects.remove(obj)


def add_backdoor_wall(block_size, lista):
    for i in range(15):
        lista.append(Block(-64, HEIGHT - i * block_size, block_size, "Rock"))
        lista.append(Block(-64 * 2, HEIGHT - i * block_size, block_size, "Rock"))
        lista.append(Block(-64 * 3, HEIGHT - i * block_size, block_size, "Rock"))


def generate_floor():
    block_size = 96

    list_of_blocks = []
    GAP = 10
    LEVEL = 3

    # The initial 3 blocks
    for i in range(0, LEVEL):
        list_of_blocks.append(Block(i * block_size, HEIGHT - block_size, block_size))

    for i in range(LEVEL + GAP, LEVEL * 3 + GAP):
        list_of_blocks.append(Block(i * block_size, HEIGHT - block_size, block_size))

    for i in range(17 + 7, 17 + 14):
        list_of_blocks.append(Block(i * block_size, HEIGHT - block_size, block_size))

    for i in range(31 + 7, 31 + 14):
        list_of_blocks.append(Block(i * block_size, HEIGHT - block_size, block_size))

    add_backdoor_wall(64, list_of_blocks)

    return list_of_blocks


def generate_fruits():
    list_of_fruits = []

    apple1 = Fruit(200, 400, 32, 32)
    banana2 = Fruit(200, 500, 32, 32)

    list_of_fruits.append(apple1)
    list_of_fruits.append(banana2)

    return list_of_fruits


def generate_obstacles():
    pass


def generate_gold_plates1():
    gold_plates = []

    f = open("assets/txtfiles/Gold_plates.txt", "r")
    for x in f:
        numbers = x.split(",")
        x = int(numbers[0])
        y = int(numbers[1])
        gold_plates.append(Block(x, y, 32, "Gold_plate"))

    return gold_plates


def reset():
    print("LOST")


def loose():
    reset()


def main(win):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    offset_x = 0
    scroll_area_width = 250

    # Creating a player
    player = Player(100, 500, 50, 50)

    # Structure
    floor = generate_floor()

    # Jumping Plates
    gold_plates = generate_gold_plates1()

    # Edibles
    fruits = generate_fruits()

    objects = [
        *floor,
        *gold_plates,
        *fruits,
    ]

    offset_x = 1500
    player.die()
    
    # Event loop
    run = True
    while run:

        # Set a fixed number of frames per second
        clock.tick(FPS)

        # Check the events of the user
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and player.jump_count < 2:
                    player.jump()
                elif event.key == pygame.K_d:
                    offset_x += 300
                elif event.key == pygame.K_a:
                    offset_x -= 300
                elif event.key == pygame.K_u:
                    floor = generate_floor()
                    gold_plates = generate_gold_plates1()
                    fruits = generate_fruits()
                    objects = [*floor,
                               *gold_plates,
                               *fruits
                               ]
                elif event.key == pygame.K_KP1:
                    background, bg_image = get_background("Blue.png")
                elif event.key == pygame.K_KP2:
                    background, bg_image = get_background("Brown.png")
                elif event.key == pygame.K_KP3:
                    background, bg_image = get_background("Gray.png")
                elif event.key == pygame.K_KP4:
                    background, bg_image = get_background("Green.png")
                elif event.key == pygame.K_KP5:
                    background, bg_image = get_background("Pink.png")
                elif event.key == pygame.K_KP6:
                    background, bg_image = get_background("Purple.png")
                elif event.key == pygame.K_KP7:
                    background, bg_image = get_background("Yellow.png")
                elif event.key == pygame.K_1:
                    player.change_char("MaskDude")
                elif event.key == pygame.K_2:
                    player.change_char("NinjaFrog")
                elif event.key == pygame.K_3:
                    player.change_char("PinkMan")
                elif event.key == pygame.K_4:
                    player.change_char("VirtualGuy")
                elif event.key == pygame.K_s:
                    offset_x = 1500
                    player.die()

        # We handle movement before we draw
        player.loop(FPS)

        handle_move(player, objects)

        # Handle the animation of the fruits
        for fruit in fruits:
            fruit.loop()

        # Drawing methods
        draw(win, background, bg_image, player, objects, offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) \
                or ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

        if player.rect.top > HEIGHT + 20:
            offset_x = 1500
            player.die()
            loose()

    # Quit the program
    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)
