# title:   Završni igrica
# author:  Nimaj Dupanović
# desc:    short description
# site:    https://ai.foi.hr
# license: GPLv3
# version: 0.1
# script:  python

state = 'menu'
level = 0
timer_start = 60
timer_current = timer_start

def reset_space_pressed():
    menu.space_pressed = False

def TIC():
    update_keys()
    Final()

    global state
    if state == 'game':
        PlayLevel()
        if level_manager.level == 0:
            print("Keys (<- ->) for moving left and right", 0, 16)
            print("Key (X) for jump", 0, 24)
            print("Key (Y) for attacking with the sword", 0, 32)

        level_manager.timer_current -= 1 / 60
        if level_manager.timer_current <= 0:
            level_manager.timer_current = 0
            sfx(8, "C-4", 30, 0, 5, 0)
            state = 'over'

    elif state == 'menu':
        menu.show_menu()
    elif state == 'over':
        menu.show_game_over()
    elif state == 'win':
        menu.show_win_screen()

    

def Final():
    cls(13)
prev_key_space = False

def update_keys():
    global key_space, key_left, key_right, key_up, key_down, key_attack, key_y
    global prev_key_space

    current_key_space = btn(5)

    key_space = current_key_space and not prev_key_space

    key_left = btn(2) 
    key_right = btn(3) 
    key_up = btn(0) 
    key_down = btn(1)
    key_attack = btn(4)

    prev_key_space = current_key_space
    
def move_towards(start, end, step):
    if step == 0:
        return start
    elif start < end:
        return min(start + step, end)
    else:
        return max(start - step, end)

class Character:
    x = 96
    y = 24
    width = 14
    height = 14
    h_speed = 0
    v_speed = 0
    facing_right = False
    is_moving = False
    current_frame = 256
    attack_timer = 0
    jump_power = 0
    colliders = []
    sprite_timer = 0
    attack_duration = 20
    attack_timer = 0
    attacking = False
    sword_sprite = 298

    min_y = 120
    min_x = 10000

    accel_normal = 0.25
    acceleration = 0.25
    max_speed = 2
    gravity = 0.24

    jump_strength = 4.4

    coyote_time = 8
    coyote_counter = 0
    has_jumped = False

    health = 10
    hit_cooldown = 10
    hit_counter = 0
    hit_by_enemy = False

    knockback_strength = 2
    knockback_duration = 10
    knockback_timer = 0

    def __init__(self):
        self.current_frame = self.sword_sprite

    def check_collisions(self, x_offset, y_offset):
        self.x += x_offset
        self.y += y_offset
        for obj in self.colliders:
            if obj.check_collision(self):
                self.x -= x_offset
                self.y -= y_offset
                return True
        self.x -= x_offset
        self.y -= y_offset
        return False
    
    def apply_knockback(self, direction):
        self.h_speed = direction * self.knockback_strength
        self.v_speed = -self.knockback_strength
        self.knockback_timer = self.knockback_duration

    def player_controller(self, colliders):
        self.colliders = colliders
        if self.knockback_timer > 0:
            self.knockback_timer -= 1
        else:
            self.check_enemy_collisions(Character, enemies)


        if key_space and self.v_speed == 0:
            sfx(9, "C-4", 10, 0, 2, 0)
            if self.check_collisions(self, 0, 1) or self.y >= self.min_y or self.coyote_counter < self.coyote_time:
                self.v_speed = -self.jump_strength
                self.has_jumped = True

        if self.check_collisions(self, 0, 1):
            self.coyote_counter = 0
            self.has_jumped = False
        else:
            self.coyote_counter += 1

        if key_left:
            self.h_speed = move_towards(self.h_speed, -self.max_speed, self.acceleration)
            self.facing_right = False
            self.is_moving = True
        elif key_right:
            self.h_speed = move_towards(self.h_speed, self.max_speed, self.acceleration)
            self.is_moving = True
            self.facing_right = True
        else:
            self.h_speed = move_towards(self.h_speed, 0, self.acceleration)
            self.is_moving = False

        if self.y + self.v_speed >= self.min_y or self.check_collisions(self, 0, self.v_speed + 1):
            if self.v_speed > 0:
                while self.y < self.min_y and not self.check_collisions(self, 0, 1):
                    self.y += 1
            self.v_speed = 0
        else:
            self.v_speed += self.gravity
            if self.check_collisions(self, 0, self.v_speed):
                self.v_speed = 0

        if self.v_speed < 0:
            if self.check_collisions(self, 0, self.v_speed - 1):
                self.v_speed = 0

        if self.knockback_timer > 0:
            self.x += self.h_speed
            self.y += self.v_speed

        if self.x > (view.restriction_x - self.width) or self.check_collisions(self, 1 + self.h_speed, 0):
            self.h_speed = 0
            while self.x > (view.restriction_x - self.width):
                self.x -= 1

        if self.x < 0 or self.check_collisions(self, -1 + self.h_speed, 0):
            self.h_speed = 0
            while self.x < 0:
                self.x += 1

        self.x += self.h_speed
        self.y += self.v_speed

        if self.is_moving:
            self.sprite_timer += 0.1

        if key_attack and not self.attacking:
            self.attacking = True
            self.attack_timer = self.attack_duration
        if self.attacking:
            self.attack_timer -= 0.5
            if self.attack_timer <= 0:
                self.attacking = False

        if self.attacking:
            attack_sprites = [294, 296, 298]
            current_attack_sprite = attack_sprites[int(self.sprite_timer / 1) % len(attack_sprites)]
            spr(current_attack_sprite, int(self.x) - int(view.x), int(self.y) - int(view.y), 6, 1, int(not self.facing_right), 0, 2, 2)
            sfx(0, "C-4", 30, 0, 5, 0)
        else:
            if self.facing_right and self.is_moving:
                walk_sprites = [260, 262, 264]
                current_walk_sprite = walk_sprites[int(self.sprite_timer / 2) % len(walk_sprites)]
                spr(current_walk_sprite, int(self.x) - int(view.x), int(self.y) - int(view.y), 6, 1, 0, 0, 2, 2)
            elif not self.facing_right and self.is_moving:
                walk_sprites = [260, 262, 264]
                current_walk_sprite = walk_sprites[int(self.sprite_timer / 2) % len(walk_sprites)]
                spr(current_walk_sprite, int(self.x) - int(view.x), int(self.y) - int(view.y), 6, 1, 1, 0, 2, 2)
            else:
                spr(256, int(self.x) - int(view.x), int(self.y) - int(view.y), 6, 1, int(not self.facing_right), 0, 2, 2)

        if self.hit_cooldown > self.hit_counter:
            self.hit_counter += 1
            if self.facing_right and self.is_moving:
                spr(266 + 2*(round(self.sprite_timer) % 2 == 0), int(self.x) - int(view.x), int(self.y) - int(view.y), 6, 1, 0, 0, 2, 2)
            elif not self.facing_right and self.is_moving:
                spr(266 + 2*(round(self.sprite_timer) % 2 == 0), int(self.x) - int(view.x), int(self.y) - int(view.y), 6, 1, 1, 0, 2, 2)
            else:
                spr(266, int(self.x) - int(view.x), int(self.y) - int(view.y), 6, 1, int(not self.facing_right), 0, 2, 2)

        self.unstuck(self)


    def take_damage(self, dmg):
        global state
        self.health -= dmg
        self.hit_counter = 0
        if self.health == 0:
            sfx(8, "C-4", 30, 0, 5, 0)
            state = 'over'
        else:
            direction = -1 if self.facing_right else 1
            self.apply_knockback(self, direction) 


    def unstuck(self):
        if self.check_collisions(self, 0, 0):
            for jump in range(1, 3):
                for i in range(-jump, jump, jump):
                    for j in range(-jump, jump, jump):
                        if i == 0 and j == 0:
                            continue
                        if not self.check_collisions(self, i, j):
                            self.x += i
                            self.y += j
                            return

    def check_enemy_collisions(self, enemies):
        hitt = False
        attack_box_active = self.attacking

        for Enemys in enemies:
            for Enemy in Enemys:
                enemy_box = (Enemy.x, Enemy.y, Enemy.width, Enemy.height)

                if attack_box_active:
                    attack_box = (self.x - 8, self.y - 8, 48, 32) 
                    if self.check_collision(self, attack_box, enemy_box):
                        if not self.hit_by_enemy and not Enemy.dead:
                            Enemy.take_damage(1)  
                        self.hit_by_enemy = True
                        hitt = True
                else:
                    if self.check_collision(self, (self.x, self.y, self.width, self.height), enemy_box):
                        if not self.hit_by_enemy and not Enemy.dead:
                            self.take_damage(self, 1)
                        self.hit_by_enemy = True
                        hitt = True

        if not hitt:
            self.hit_by_enemy = False

    def check_collision(self, box1, box2):
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2
import random

class Enemy:
    x = 80
    y = 80
    width = 16
    height = 16
    sprite = 1
    dx = -0.5
    vsp = 0
    gravity = 0.3
    jump_strength = 3
    min_y = 120
    facing_right = False
    coll = []
    health = 1
    dead = False

    change_direction_timer = random.randint(300, 600)
    jump_timer = random.randint(200, 400)
    state = "walking" 
    wait_timer = 0
    sprite_timer = 0

    def __init__(self, x, y):
        tile_size = 8
        self.x = x * tile_size
        self.y = y * tile_size

    def update(self, collision_objects):
        self.collision_objects = collision_objects
        if self.dead:
            return

        if not self.check_collision(self.dx, 0):
            self.x += self.dx
        else:
            self.dx = -self.dx
            self.facing_right = not self.facing_right

        self.sprite_timer += 0.1 

        self.change_direction_timer -= 1
        if self.change_direction_timer <= 0:
            self.dx = -self.dx
            self.facing_right = not self.facing_right
            self.change_direction_timer = random.randint(300, 600)

        self.jump_timer -= 1
        if self.jump_timer <= 0:
            self.vsp = -self.jump_strength
            self.jump_timer = random.randint(200, 400)

        if self.y + self.vsp >= self.min_y or self.check_collision(0, self.vsp + 1):
            self.vsp = 0
            while self.y < self.min_y and not self.check_collision(0, 1):
                self.y += 1
        else:
            self.vsp += self.gravity

        if self.vsp < 0:
            if self.check_collision(0, self.vsp - 1):
                self.vsp = 0

        self.y += self.vsp

        if self.state == "walking":
            walk_sprites = [320, 322]
            current_walk_sprite = walk_sprites[int(self.sprite_timer / 5) % len(walk_sprites)]
            spr(current_walk_sprite, int(self.x) - int(view.x), int(self.y) - int(view.y), 6, 1, int(not self.facing_right), 0, 2, 2)
        else:
            spr(300, int(self.x) - int(view.x), int(self.y) - int(view.y), 6, 1, int(not self.facing_right), 0, 2, 2)

    def check_collision(self, x_offset, y_offset):
        self.x += x_offset
        self.y += y_offset
        collision = False
        for obj in self.collision_objects:
            if obj.check_collision(self):
                collision = True
        self.x -= x_offset
        self.y -= y_offset
        return collision

    def take_damage(self, dmg):
        if not self.dead:
            self.health -= dmg
            if self.health <= 0:
                self.dead = True
                self.die()

    def die(self):
        sfx(8, "C-4", 30, 0, 5, 0)

class Enemy2(Enemy):
    x = 80
    y = 80
    width = 16
    height = 16
    sprite = 1
    dx = -0.5
    vsp = 0
    gravity = 0.3
    jump_strength = 3
    min_y = 120
    facing_right = False
    collision_objects = []
    health = 2
    dead = False

    change_direction_timer = random.randint(300, 600)
    jump_timer = random.randint(200, 400)
    state = "walking"
    wait_timer = 0
    sprite_timer = 0

    def __init__(self, x, y):
        tile_size = 8
        self.x = x * tile_size
        self.y = y * tile_size

    def update(self, collision_objects):
        self.collision_objects = collision_objects
        if self.dead:
            return

        if not self.check_collision(self.dx, 0):
            self.x += self.dx
        else:
            self.dx = -self.dx
            self.facing_right = not self.facing_right

        self.sprite_timer += 0.1 

        self.change_direction_timer -= 1
        if self.change_direction_timer <= 0:
            self.dx = -self.dx
            self.facing_right = not self.facing_right
            self.change_direction_timer = random.randint(300, 600)

        self.jump_timer -= 1
        if self.jump_timer <= 0:
            self.vsp = -self.jump_strength
            self.jump_timer = random.randint(200, 400)

        if self.y + self.vsp >= self.min_y or self.check_collision(0, self.vsp + 1):
            self.vsp = 0
            while self.y < self.min_y and not self.check_collision(0, 1):
                self.y += 1
        else:
            self.vsp += self.gravity

        if self.vsp < 0:
            if self.check_collision(0, self.vsp - 1):
                self.vsp = 0

        self.y += self.vsp

        if self.state == "walking":
            walk_sprites = [326, 328]
            current_walk_sprite = walk_sprites[int(self.sprite_timer / 5) % len(walk_sprites)]
            spr(current_walk_sprite, int(self.x) - int(view.x), int(self.y) - int(view.y), 6, 1, int(not self.facing_right), 0, 2, 2)
        else:
            spr(324, int(self.x) - int(view.x), int(self.y) - int(view.y), 6, 1, int(not self.facing_right), 0, 2, 2)

    def check_collision(self, x_offset, y_offset):
        self.x += x_offset
        self.y += y_offset
        collision = False
        for obj in self.collision_objects:
            if obj.check_collision(self):
                collision = True
        self.x -= x_offset
        self.y -= y_offset
        return collision

    def take_damage(self, dmg):
        if not self.dead:
            self.health -= dmg
            if self.health <= 0:
                self.dead = True
                self.die()

    def die(self):
        sfx(8, "C-4", 30, 0, 5, 0)
class View:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 240
        self.height = 136
        self.is_restricted = False
        self.restriction_x = 0
        self.set_restriction(240 * 8)

    def follow(self, obj):
        self.x = round(obj.x - (self.width - obj.width) / 2)

        if self.is_restricted:
            self.x = min(max(0, self.x), self.restriction_x - self.width)

    def set_restriction(self, max_x):
        self.is_restricted = True
        self.restriction_x = max_x

    def follow_player(self):
        if Character.is_moving:
            self.follow(Character)

view = View()
class CollisionObject:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def check_collision(self, other):
        return rects_overlap(self.x, self.y, self.width, self.height, other.x, other.y, other.width, other.height)

    def check_collision_rectangle(self, x_left, y_top, x_right, y_bottom):
        return rects_overlap(self.x, self.y, self.width, self.height, x_left, y_top, x_right - x_left, y_bottom - y_top)

    def draw(self):
        rect(self.x - int(view.x), self.y - int(view.y), self.width, self.height, 15)


def rects_overlap(x1, y1, w1, h1, x2, y2, w2, h2):
    return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2


def define_collisions(object_list, level, LEVEL_HEIGHT):
    collision_objects = {}
    tile_size = 8
    collision_width = 8
    for obj in object_list:
        obj_list = obj if isinstance(obj, list) else [obj]
        
        for o in obj_list:
            px = min(max(int(o.x / tile_size) - round(collision_width / 2), 0), 239)
            py = min(max(int(o.y / tile_size) - round(collision_width / 2), 0), 135)

            for xx in range(collision_width):
                for yy in range(collision_width):
                    tile_here = mget(xx + px, yy + py + level * LEVEL_HEIGHT)
                    if tile_here != 0 and tile_here not in level_finish_tile_indexes and tile_here not in background_tile_indexes:
                        pos_key = (xx + px, yy + py)
                        if pos_key not in collision_objects:
                            collision_objects[pos_key] = CollisionObject((xx + px) * tile_size, (yy + py) * tile_size, tile_size, tile_size)

    return list(collision_objects.values())
class KeyPickup:
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sprite = 362
        self.sprite_timer = 0

    def reset_position(self, level_height, tile_size):
        while self.y > level_height * tile_size:
            self.y -= level_height * tile_size

    def update(self):
        spr(362, int(self.x) - int(view.x), int(self.y) - int(view.y), 6, 1, 0, 0, 2, 2)

    def check_collision_with_player(self, player):
        if abs(self.x - player.x) < 8 and abs(self.y - player.y) < 8:
            level_manager.has_key = True
            print("Key acquired!")
            self.x = -100 

class CrownPickup:
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sprite = 360
        self.sprite_timer = 0

    def reset_position(self, level_height, tile_size):
        while self.y > level_height * tile_size:
            self.y -= level_height * tile_size

    def update(self):
        spr(360, int(self.x) - int(view.x), int(self.y) - int(view.y), 6, 1, 0, 0, 2, 2)

    def check_collision_with_player(self, player):
        if abs(self.x - player.x) < 8 and abs(self.y - player.y) < 8:
            level_manager.has_crown = True
            print("Crown acquired!")
            self.x = -100 
 
class menu:
    m_ind = 0
    options = ['Start', 'Credits', 'Quit'] 
    key_pressed = False 
    space_pressed = False 

    def show_menu():
        global state
        cls(0)
        menu.animate_frame()
        menu.animate_title()

        for i, option in enumerate(menu.options):
            rect(50, 48 + 15 * i, 140, 13, 2 if i == menu.m_ind else 0)  
            print(option, 100, 50 + 15 * i, 13, False, 1, False) 

        if not menu.key_pressed:
            if key_down and menu.m_ind < len(menu.options) - 1:
                menu.m_ind += 1
                menu.key_pressed = True
            elif key_up and menu.m_ind > 0:
                menu.m_ind -= 1
                menu.key_pressed = True

        if not key_down and not key_up:
            menu.key_pressed = False

        if key_space and not menu.space_pressed:
            menu.space_pressed = True 
            if menu.m_ind == 0: 
                state = 'game'
                level = 0
                StartLevel(level)
            elif menu.m_ind == 1: 
                menu.show_credits()  
            elif menu.m_ind == 2: 
                exit()

        if not key_space:
            menu.space_pressed = False 

    def show_credits():
        global state
        cls(0)
        menu.animate_frame()
        print("CREDITS", 90, 20, 13, False, 2, False)
        print("Game by: Nimaj Dupanović", 50, 50, 12, False, 1, False)
        print("Powered by: TIC-80", 50, 70, 12, False, 1, False)
        print("Press (Y) to return to menu", 50, 100, 13, False, 1, False)

        if key_attack:
            state = 'menu' 

    def animate_title():
        colors = [12, 13, 14, 15]
        color_index = int(time() % 500 // 125) 
        print('KNIGHT\'S QUEST', 57, 20, colors[color_index], False, 2, False)

    def animate_frame():
        colors = [12, 13, 14, 15]
        color_index = int(time() % 500 // 125) 
        rectb(0, 0, 240, 136, colors[color_index])

    def animate_win_title():
            print('VICTORY!', 80, 50, 6, False, 2, False)

    def show_win_screen():
        global state
        cls(0)
        menu.animate_frame()
        menu.animate_win_title()
        print('START (x) for exit', 75, 70, 13, False, 1, False)

        if key_space:
            exit()

    def show_game_over():
        cls(0)
        menu.animate_frame() 
        print('GAME OVER', 75, 50, 2, False, 2, False)
        print('START (x) for restart', 75, 70, 13, False, 1, False)

        if key_space:
            reset()
player_starting_positions = [ # Starting Character positions for each level:
    [2, 12], # Level 0
    [5, 28], # Level 1
    [9, 44], # Level 2 (doesn't exist but kept for consistency)
]

level_finish_tile_indexes = [ # Tile indexes for level exit doors
    80, 81, 82, 
    96, 97, 98, 
    112, 113, 114, #vrata na kraju levela 0
    128, 129, 130,
    144, 145, 146, 
    160, 161, 162, #tron na kraju levela 1
]

background_tile_indexes = [ # Background tiles that don't have collision
    #vani
    44, #nebo
    75, 76, 77, 78, 79, 91, 92, 93, 94, 95, 107, 108, 109, 110, 111, 124, 125, 126, #drvo
    69, 70, 71, 72, 83, 84, 85, 86, 87, 88, 99, 100, 101, 102, 103, 104, 116, 117, 118, 119, 120, # kuća sa prozorom, vratima i krovom
    9, 10, 25, 26, 41, 42, 17, #zidovi dvorca
    39, 55, #zastava horizontalna
    64, 65, #zastava vodoravna
    40, 56, #svijeća
    7, 8, 23, 24, #bunar
    #vani zavrseno

    #unutrasnjos dvorca
    131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 147, 148, 149, 150, 151, 
    152, 153, 154, 155, 156, 157, 158, 159, 163, 164, 165, 166, 167, 168, 169, 170, 
    176, 177, 179, 180, 185, 186, 192, 193, 195, 196, 201, 202, 209, 210, 211, 212, 217, 218,
    #unutrasnjos zavrsena
]

enemies = [ # Starting positions for enemies on each level
    [Enemy(40, 35), Enemy(125, 35), Enemy(192, 35)], # Level 0
    [Enemy2(58, 46), Enemy2(139, 46), Enemy2(184, 46),] # Level 1
]

pickups = [ # Starting positions for pickups (only key pickup for now)
    [KeyPickup(620, 28)], # Level 0
    [CrownPickup(1210, 32)], # Level 1
    [], # Level 2
]

LEVEL_HEIGHT = 17

class LevelManager:
    def __init__(self):
        self.level = 0
        self.has_key = False
        self.has_crown = False
        self.timer_current = 0
        self.tile_size = 8

    def start_level(self):
        self.timer_current = timer_start
        self.has_key = False
        self.has_crown = False
        starting_pos = player_starting_positions[self.level]
        Character.x = starting_pos[0] * self.tile_size
        Character.y = (starting_pos[1] - LEVEL_HEIGHT * self.level) * self.tile_size
        view.x = max(0, Character.x - (view.width - Character.width) / 2)
        Character.h_speed = 0
        Character.v_speed = 0

        levelPickups = pickups[self.level]
        for pickup in levelPickups:
            pickup.reset_position(LEVEL_HEIGHT, self.tile_size)

    def play_level(self):
        cls(0)
        map(0, self.level * LEVEL_HEIGHT, 240, 18, -int(view.x), -int(view.y), 0)
        HUD()
        
        levelEnemies = enemies[self.level]
        for Enemy in levelEnemies:
            while Enemy.y > LEVEL_HEIGHT * self.tile_size:
                Enemy.y -= LEVEL_HEIGHT * self.tile_size

        collidables = define_collisions([Character] + levelEnemies, self.level, LEVEL_HEIGHT)
        
        for Enemy in levelEnemies:
            Enemy.update(collidables)

        Character.player_controller(Character, collidables)
        view.follow_player()
        
        levelPickups = pickups[self.level]
        for pickup in levelPickups:
            pickup.update()
            pickup.check_collision_with_player(Character)
        
        self.check_player_at_door()

    def check_player_at_door(self):
        tile_index = mget(round(Character.x / self.tile_size), round(Character.y / self.tile_size) + self.level * LEVEL_HEIGHT)
        if tile_index in level_finish_tile_indexes:
            if (self.level == 0 and self.has_key) or (self.level == 1 and self.has_crown):
                sfx(6, "C-4", 15, 0, 2, 1)
                self.end_level()
            else:
                print("You need the key/crown to proceed!", 0, 8, 2)

    def end_level(self):
        self.level += 1
        self.has_key = False
        self.has_crown = False
        if self.level <= 1:
            self.start_level()
        else:
            global state
            state = 'win'

level_manager = LevelManager()

def StartLevel(level):
    level_manager.level = level
    level_manager.start_level()

def PlayLevel():
    level_manager.play_level()

def CheckPlayerAtDoor():
    level_manager.check_player_at_door()

def EndLevel():
    level_manager.end_level()

def HUD():
    rect(0, 0, 240, 8, 0)
    print("Level:" + str(level_manager.level), 1, 1, 12, True, 1, False)
    
    print("Time Left: " + str(round(level_manager.timer_current)) + "s", 150, 1, 12, True, 1, False)

    spr(364, 50, 0, 6, 1, 0, 0, 1, 1)
    rect(60, 1, Character.health * 5, 5, 6)
    if Character.health > 0:
        print(str(Character.health) + "HP", 120, 1, 12, True, 1, False)
    else: 
        print("0HP", 120, 1, 12, True, 1, False)

# <TILES>
# 000:000000000ddddddd0deeeeee0deeeeee000000000dde0ddd0eee0dee0eee0dee
# 001:000000000ddddddd0eeeeeee0eeeeeee00000000ddde0dddeeee0deeeeee0dee
# 002:00000000d0ddddd0e0eeeed0e0eeeed000000000dddde0e0eeeee0e0eeeee0e0
# 003:aaaaaaaaaaaaaaaaaaaaa6a6aaaa6666aaaaa666aa666666aa666666a6666666
# 004:aaaaaaaa6aa6a6a66a6666a66666666666666666666666666666666666666666
# 005:aaaaaaaa6aa6a6a66a6666a66666666666666666666666666666666666666666
# 006:aaaaaaaa66aaaaaa6aaaaaaa6666aaaa6666aaaa666666aa6666666a666666aa
# 007:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa3303330320220220
# 008:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa3033033002202202
# 009:000000000dde0ddd0dee0eee0dee0eee000000000dde0ddd0dee0dee0dee0dee
# 010:00000000dddd0ddeeeee0deeeeee0dee00000000ddde0ddeeeee0deeeeee0dee
# 012:1111111111111111111111111111111111111111111111111111111111111111
# 013:3333333333333333333333333333333333333333333333333333333333333333
# 014:2222222222222222222222222222222222222222222222222222222222222222
# 015:4444444444444444444444444444444444444444444444444444444444444444
# 016:0eee0dee000000000dddddde0deeeeee0deeeeee000000000dde0ddd0eee0eee
# 017:eeee0dee00000000e0dddddde0deeeeee0deeeee00000000ddde0dddeeee0dee
# 018:eeeee0d000000000ee0ddde0ee0deee0ee0deee000000000dddde0d0eeeee0d0
# 019:a6666666aa666666aa666666aaaaa666aaaa6666aaaaa6a6aaaaaa66aaaaa444
# 020:6666666666666666666666666666666666666666646666266246264644444444
# 021:6666666666666666666666666666666666666666646666266246264644444444
# 022:666666aa6666666a666666aa6666aaaa6666aaaa6aaaaaaa66aaaaaa444aaaaa
# 023:2aaaaaa20aaaaaa22aaaaaa22aaaaaa20aaaaaa22aaaaaa22aaaaaa20aaaaaa2
# 024:2aaaaaa22aaaaaa02aaaaaa22aaaaaa02aaaaaa22aaaaaa22aaaaaa22aaaaaa0
# 025:0dee0dee0dee00000dee0dde0dee0eee0dee0eee0dee00000dee0ddd0dee0eee
# 026:eeee0dee00000deee0de0deee0de0deee0de0dee00000deeddde0deeeeee0dee
# 027:5555555555555555555555555555555555555555555555555555555555555555
# 028:6666666666666666666666666666666666666666666666666666666666666666
# 029:7777777777777777777777777777777777777777777777777777777777777777
# 030:8888888888888888888888888888888888888888888888888888888888888888
# 031:7777777777777777777777777777777777777777777777777777777777777777
# 032:0eee0eee00000000000000000dddddde0deeeeee0deeeeee000000000ddddddd
# 033:eeee0dee0000000000000000e0dddddde0deeeeee0deeeee000000000ddddddd
# 034:eeeee0d00000000000000000ee0ddde0ee0deee0ee0deee000000000d0ddddd0
# 035:000000000bbbbbbb0000bbbb0230000002332244023322440233224402332244
# 036:00000000bbbbbbb0bbbb00000000024022332240223322402233224022332240
# 039:aaaaaaaaaaaaaaaaaaaaaaaaacc22222acc42424acc44444acc22222accaaaaa
# 040:eeee3dee00033000e03223dde332233ee332233e00333300ddddddddee4444ee
# 041:0dee0eee0dee0eee0dee00000dee0dde0dee0eee00000eee0ddd00000dee0ddd
# 042:eeee0deeeeee0dee00000deee0de0deee0de0deee0de000000000ddedddd0dee
# 043:9999999999999999999999999999999999999999999999999999999999999999
# 044:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
# 045:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
# 046:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
# 047:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd
# 048:0deeeeee0000000000000000000000000ddddddd0deeeeee0deeeeee00000000
# 049:0eeeeeee0000000000000000000000000ddddddd0eeeeeee0eeeeeee00000000
# 050:e0eeeed0000000000000000000000000d0dddde0e0eeeee0e0eeeee000000000
# 051:0233224402332244023322440233224402332244023322440233224400000000
# 052:2233224022332240223322402233224022332240223322402233224000000000
# 055:accaaaaaaccaaaaaaccaaaaaaccaaaaaaccaaaaaaccaaaaaaccaaaaaaccaaaaa
# 056:ee4444ee00444400e04444ddf04444fffecdcedffecdced0ffeddefdeffedffe
# 057:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddeeeeeed
# 060:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
# 061:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
# 064:eeee0dee02222222e2442224e2442224e244444402444444d2222222eeee0dee
# 065:eeee0dee222222204222442d4222442e4444442e444444202222222deeee0dee
# 066:cccccccccccccccccccccccccccccccccaaccccccaacccaaaaaaaaaaaaaaaaaa
# 067:acccccccaaccccccaaacccccaaaaccccaaaaacccaaaaaaccaaaaaaacaaaaaaaa
# 068:cccccccaccccccaacccccaaaccccaaaacccaaaaaccaaaaaacaaaaaaaaaaaaaaa
# 069:aaaaaaa2aaaaaa22aaaaa223aaaa2232aaa22322aa223223a223223222322322
# 070:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa32232232223223222322322332232232
# 071:2aaaaaaa32aaaaaa223aaaaa2322aaaa32232aaa223223aa2322322a32232232
# 072:2322322332232232223223222322322332232232223223222322322332232232
# 073:dfffdffddfdfffdddddddddddeeeeeeddfdfffdddfffdffddddddddddeeeeeed
# 074:3333333344444444444444445555555505050505505050500505050550505050
# 075:aaaaaaaaaaaaaaaaaaaaa6a6aaaa6666aaaaa666aa666666aa666666a6666666
# 076:aaaaaaaa6aa6a6a66a6666a66666666666666666666666666666666666666666
# 077:aaaaaaaa6aa6a6a66a6666a66666666666666666666666666666666666666666
# 078:aaaaaaaa6aa6a6a66a6666a66666666666666666666666666666666666666666
# 079:aaaaaaaa66aaaaaa6aaaaaaa6666aaaa6666aaaa666666aa6666666a666666aa
# 080:eeeeddddeeeddf0feedd0f0feddf0f0fed0f0f0fed0f0f0fed0f0f0fed0f0f0f
# 081:dddddddd0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f
# 082:ddddeeee0f0ddeee0f0fddee0f0f0dde0f0f0fde0f0f0fde0f0f0fde0f0f0fde
# 083:0c0cceeecccceebec0ceebce0ceebcbeceebcbbeeebcbbceeecbbcbeeebbcbbe
# 084:eee0c0c0ebeeccccecbee0ccebbbeec0ebbcbeecebcbbbeeecbbbceeebbbcbee
# 085:ccc0cc0c0c0cc222cccc2222c0c222220c222222cc2222220c222222c0222222
# 086:c0c0c0c022200222222002222220022222200222222002222220022222200222
# 087:c0cc0ccc222cc0c02222cccc22222c0c222222c0222222cc222222c02222220c
# 088:ccccccccc0c0cccccccccc0ccccccccccc0ccc0cc0cc0ccccccccc0ccc0ccccc
# 089:dfffdffddfdffdfddddddddddeeeeeedddfffdfddffdfffddddddddddddddddd
# 090:0505555055555055505055050555555050505055555555500505050550505550
# 091:aa666666a6666666aa666666aaa6666666666666a6666666a6666666aa666666
# 092:6666666666666666666666666666666666666666666666666666666666666666
# 093:6666666666666666666666666666666666666666666666666666666666666666
# 094:6666666666666666666666666666666666666666666666666666666666666666
# 095:666666aa6666666a666666aa66666aaa666666666666666a6666666a666666aa
# 096:ed0f0f0fed0f0f0fed0f0f0fed0f0f0fed0f0f0fed0f0f0fed0f0f0fed0f0f0f
# 097:0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f
# 098:0f0f0fde0f0f0fde0f0f0fde0f0f0fde0f0f0fde0f0f0fde0f0f0fde0f0f0fde
# 099:eebcbbbeeecbbbceeebbbcbeeebbcbbeeebcbbbeeecbbbceeeeeeeeeeeeeeeee
# 100:ebbcbbeeebcbbbeeecbbbceeebbbcbeeebbcbbeeebcbbbeeeeeeeeeeeeeeeeee
# 101:c02222220c222222cc2222220c222222c0222222cc2222220c222222cc222222
# 102:2220022222200222222002220020020000200200222002222220022222200222
# 103:2222220c222222c0222222cc222222c02222220c222222cc222222c0222222cc
# 104:ccccccccc0c0cccccccccc0ccccccccccc0ccc0cc0cc0ccccccccc0c33333333
# 105:0d0de222efed22b2d0d22bc20e22bcb2e22bcbb2d2bcbbc202cbbcb2e2bbcbb2
# 106:2220d0d02b22feee2cb220ed2bbb22d02bbcb22e2bcbbb2d2cbbbc2f2bbbcb2e
# 107:a6666666aa666666aa666666aaaaa666aaaa6666aaaaa6a6aaaaaaaaaaaaaaaa
# 108:66666666666666666666666666666666666666666a6666a66aa6a6a6aaaaaaaa
# 109:6666666666666666666666666666666666666666646666266246264623234232
# 110:66666666666666666666666666666666666666666a6666a66aa6a6a6aaaaaaaa
# 111:666666aa6666666a666666aa6666aaaa6666aaaa6aaaaaaa66aaaaaaaaaaaaaa
# 112:ed0f0f0fed0f0f0fed0f0f0fed0f0f0fed0f0f0fed0f0f0fed0f0f0feeeeeeee
# 113:0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0feeeeeeee
# 114:0f0f0fde0f0f0fde0f0f0fde0f0f0fde0f0f0fde0f0f0fde0f0f0fdeeeeeeeee
# 116:ccccccc3c0c0ccc3cccccc03ccccccc3cc0ccc03c0cc0cc3cccccc03cc0cccc3
# 117:c02222220c222222cc2222220c222222c0222222cc2222220c22222233333333
# 118:2220022222200222222002222220022222200222222002222220022233333333
# 119:2222220c222222c0222222cc222222c02222220c222222cc222222c033333333
# 120:3ccccccc3ccc0c0c30cccccc3ccccccc30ccc0cc3cc0cc0c30cccccc3cccc0cc
# 121:02bcbbb2d2cbbbc202bbbcb2f2bbcbb2e2bcbbb202cbbbc2d22222220e0ded0d
# 122:2bbcbb2f2bcbbb202cbbbc2e2bbbcb202bbcbb2f2bcbbb2d2222222eed0ffd0d
# 124:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa223
# 125:2432422332232432424232422324232424232432324232422432423232242324
# 126:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa242aaaaa
# 127:6666666666666666666aa6a66a6aa6666a666aa666a666666666a6a66aa6a6a6
# 128:eeee0dee00000000e0dddddde0deeeeee0deeeee00000000ddde0d22eeee0d22
# 129:eeee0dee400440044dd44dd44444444444444444444444442222222244444444
# 130:eeee0dee00000000e0dddddde0deeeeee0deeeee0000000022de0ddd22ee0dee
# 131:eeee0dee000000c2e0ddddc2e0deeec2e0deeec2000000c2ddde0dc2eeee0dc2
# 132:eeee0dee22222222222222224224422442244224444444444444444422222222
# 133:2eee0dee2000000020dddddd20deeeee20deeeee200000002dde0ddd2eee0dee
# 134:eeee0dee00000bbbe0dddbbbe0deeebee0deeebe0ccc0bbb2222222222222222
# 135:eee33dee000cc000e0dccddde0d44eeee0d44eee004444002222222222222222
# 136:eeee0deebbb00000bbbdddddebdeeeeeebdeeeeebbb0ccc02222222222222222
# 137:eeee0dee00000000e0dddddde0deeeeee0deeeee00000000ddde4444eeee2222
# 138:eeee042200000422e0ddd422e0dee422e0dee422000004224444442222222222
# 139:2240eeee22400000224ddd0e224eed0e224eed0e224000002244444422222222
# 140:eed0eeee00000000dddddd0eeeeeed0eeeeeed0e000000004444eddd2222eeee
# 142:eee0cdee000cc000e0dc0ddde0dcceeee0d0ceee000cc000dddc0dddeee0cdee
# 144:eeee0d2200000022e0dddd22e0deee22e0de444400002222ddde2222eeee2222
# 145:4444444444444444440440444444444444444444440440444444444444444444
# 146:22ee0dee2200000022dddddd22deeeee4444eeee2222000022220ddd22220dee
# 147:eeee0dc2000000c0e0ddddcde0deeccee0deccee00dcc000ddcc0ddddcce0dee
# 148:2222222200000000e0dddddde0deeeeee0deeeee00000000ddde0dddeeee0dee
# 149:2eee0dee00000000e0dddddde0deeeeee0deeeee00000000ddde0dddeeee0dee
# 150:eeee0dee00000000e0dddddde0deeeeee0deeeee000000002222222222222222
# 151:eeee0dee00000000e0dddddde0deeeeee0deeeee000000002222222222222222
# 152:eeee0dee00000000e0dddddde0deeeeee0deeeee000000002222222222222222
# 153:eeee222200002002e0dd2dd2e0de2ee2e0de2ee200002002ddde2dd2eeee2de2
# 154:2222222200002002e0dd2dd2e0de2ee2e0de2ee200002002ddde2dd2eeee2de2
# 155:22222222200200002dd2dd0e2ee2ed0e2ee2ed0e200200002dd2eddd2ed2eeee
# 156:2222eeee200200002dd2dd0e2ee2ed0e2ee2ed0e200200002dd2eddd2ed2eeee
# 157:eeee0dee00000000303d3d3dc0cecece404e4e4e40404040444444444e4e4d4e
# 158:eee44dee0004400030d44dd3c0d44eec40d44ee440444404444444444ee44de4
# 159:eeee0dee00000000e3d3d3d3ecdcecece4d4e4e40404040444444444e4e404e4
# 160:eeee0d2200000022e0dddd22e0deee22e0deee2200003333ddde3333eeee3333
# 161:2222222222222222222222222222222222222222333333333333333333333333
# 162:22ee0dee2200000022dddddd22deeeee22deeeee3333000033330ddd33330dee
# 163:eeee0dee00000000e0dddddde0333333e0cccccc00c22222ddc22222eec22222
# 164:eeee0dee00000000dddddddd333333eeccccccee22222c0022222cdd22222cee
# 166:222222222302300023d23ddd23d23eee23d23eee2302300023d23ddd23e23dee
# 167:2222222200000000e0dddddde0deeeeee0deeeee00000000ddde0dddeeee0dee
# 168:2222222200032032e0d32d32e0d32e32e0d32e3200032032ddd32d32eee32d32
# 169:eeee0dee00222222e0222222e022a4a4e022a4440022a444dd22adddee22add4
# 170:eeee0dee22222200222222dda4aa22ee44aa22ee44aa2200ddaa22dd04aa22ee
# 176:222e0dee22202200e2222edd2222deee20ddddee000dddd0dddeddddeeee0ddd
# 177:eeee0dee00000000e0dddddde0deeeeee0deeeee00000000ddde0ddddeee0dee
# 179:eec2244400c22444e0c22444e0c22442e0c2244200c22442ddc22444eec22444
# 180:44422cee44422c0044422cdd22222cee22222cee22222c0044422cdd44422cee
# 181:eeee0dee00000000e0dddddde0deeeeee0deeeee00000000ddde0dddeeee0dee
# 182:eeee0dee00000000e0dddddde0deeeeee0deeeee00000000ddde0dddeeee0dee
# 183:eeee0dee00000000e0dddddde0deeeeee0deeeee00000000ddde0dddeeee0dee
# 184:eeee0dee00000000e0dddddde0deeeeee0deeeee00000000ddde0dddeeee0dee
# 185:ee22add40022add4e022addde022a777e022a7770022a777dd22a777ee220477
# 186:44aa22ee44aa2200ddaa22dd77aa22ee77aa22ee77aa220077aa22dd720422ee
# 192:eeee00dd0000000de0dddddde0deeeeee0deeeee00000000ddde0dddeeee0dee
# 193:ddee0deeddd00000ddddddddedddeeeee0dddeee00eddd00ddeedddeeeeeeddd
# 195:eec2244400c22444e0c22442e0c22442e0c2244200c22444ddc22444eec22444
# 196:44422cee44422c0022222cdd22222cee22222cee44422c0044422cdd44422cee
# 197:e22e022e0220022022222222eddeeddeeddeedde0dd00dd022222222e222222e
# 198:eeee0dee00000000e0dddddde0deeeeee0deeeee00000000ddde0dddeeee0dee
# 199:0000000000324232020242320230423202320232023240320232420202324230
# 200:0000000042324200423240304232023042304230420242304032423002324230
# 201:ee22a7770022a77de022a7dde022add7e022ad770022dd0add22da0aee22aa0a
# 202:22aa22eed7aa220077aa22dd77aa220077aa220e0aaa22000aaa220d0aaa220e
# 209:eeee00dd0000000de0dddddee0deeeeee0deeeee00000000ddde0dddeeee0dee
# 210:deee0deedde00000dddeeeddedddeeeee0ddeeee00000000ddde0dddeeee0dee
# 211:eec2222200c22222e0c22222e0cccccce0ceecee00c00c00ddde0dddeeee0dee
# 212:22222cee22222c0022222cddcccccceec0dceceec00c0c00ddde0dddeeee0dee
# 213:e222222e02222220e222222de222222ee222222e02222220d222222de222222e
# 214:eeee0dee00000000e0dddddde0deeeeee0deeeee00000000ddde0dddeeee0dee
# 215:0232423002324202023240320232023202304232020242320032423200000000
# 216:0232423040324230420242304230423042320230423240304232420000000000
# 217:ee22a00a00226656e0226566e0226665e022222200222222ddde0dddeeee0dee
# 218:00aa22ee65662200565622dd666522ee222222ee22222200ddde0dddeeee0dee
# </TILES>

# <SPRITES>
# 000:226226006222600f226200ff6260ffdd6660ffd466600fd4666000d46600ffd4
# 001:00066666ff006666fff00666ddddd66644040666440406664444066644440666
# 002:226226006222600f226200ff6260ffdd6660ffd46660ffd4666000d46660ffd4
# 003:00066666ff006666fff00666ddddd66644040666440406664444066644440666
# 004:226226006222600f226200ff6260ffdd6660ffd46660ffd4666000d46660ffd4
# 005:00066666ff006666fff00666ddddd66644040666440406664444066644440666
# 006:226226006222600f226200ff6260ffdd6660ffd46660ffd4666000d46660ffd4
# 007:00066666ff006666fff00666ddddd66644040666440406664444066644440666
# 008:226226006222600f226200ff6260ffdd6660ffd46660ffd4666000d46600ffd4
# 009:00066666ff006666fff00666ddddd66644040666440406664444066644440666
# 010:2262260062226003226200336260333366600333666003336660003366003333
# 011:0006666633006666333006663333066633030666330306663333066633330666
# 012:2262260062226003226200336260333366603333666033336660003366603333
# 013:0006666633006666333006663333066633030666330306663333066633330666
# 016:660fffdd600ff0f260dd0ff26044000060000fff6660ff00660dd00666000066
# 017:ddd006662ff006662f0f066600ffd066fff040660ff0066660dd066660000666
# 018:6660ff0d6600d0f2660440f2660000006660fff0660dd0066600006666666666
# 019:ddd000662ff040662f0dd066000006660fff0066600dd0666600006666666666
# 020:6660ff0d6600f0f2660dd0f266044000660000ff6660ff00660ddd0666000066
# 021:ddd000662ff040662f0dd06600fff066fff006660ff0066660dd066660000666
# 022:660fff0d660ff00f660ffd406660fd40666000006660fff06660dd0066600006
# 023:ddd0666622f06666220f666600ff6666fff06666ff0066660dd0666600006666
# 024:66000f0d60ff0ff060dd0ff260440ff26600ffff6660ff00660ddd0666000066
# 025:ddd00066000040662f0d40662ffd4066000006660ff0066660dd066660000666
# 026:6603333360033033603303336033000060000333666033006603300666000066
# 027:3330066633300666330306660033306633303066033006666033066660000666
# 028:6660330366003033660330336603300066000033666033006603330666000066
# 029:3330006633303066330330660033306633300666033006666033066660000666
# 032:2262260062226003226200336260333366603333666033336660003366603333
# 033:0006666633006666333006663333066633030666330306663333066633330666
# 034:666666626666662f666660ff66660ff260060ffe0440fffe0dd0fffe0ffffffe
# 035:022266662f2066662ff0666622ff0666eeff0666eeff0666eeff0666eeff0006
# 036:666666626666662f666660ff66660ff266660ffe6660fffe6000fffe0440fffe
# 037:022266662f2066662ff0666622ff0666eeff0666eeff0006eeff0440eeff0dd0
# 038:26226000222600ff26200fff260ffddd6600fd446600fd4466000d44600ffd44
# 039:00666666f0066666ff006666dddd666640406666404066664440666644406666
# 040:26226000222600ff26200fff260ffddd6600fd446600fd4466000d44600ffd44
# 041:00666666f0066666ff006666dddd666640406666404066664440666644406666
# 042:26226000222600ff26200fff260ffddd6600ffd46600ffd466000fd4660fffd4
# 043:00666666f0066666ff006666dddd666640406666404066664440666644406666
# 044:6666dddd6666feed6666feed6666ffed66666fee666666fe66600e0066feeeee
# 045:ddd66666d4d666664046666640466666d4d66666d66666660e006666eeeed666
# 048:6660330366003033660330336600000066603330660330066600006666666666
# 049:3330006633303066330330660000066603330066600330666600006666666666
# 050:600ffffe660ff0fe66000ffe6666000e66600fff6660fff0660dd00666000066
# 051:eef00440eef0ddd0ee0fff00eeff0066fff0066600dd06666000066666666666
# 052:0ddffffe600ff0fe660ffffe6660000e6660ffff660dd0006600006666666666
# 053:eef0fff0eef0ff06ee0ff006eeff0666fff066660ff0066660dd066660000666
# 054:60fffddd00ff0fff0dd2eeee2442eeee0002eeee660ff00060dd006660000666
# 055:dd066666f0000466eeeee466eeeee666eeeee666ff0666660dd0666600006666
# 056:60fffddd60ff0fff60d02eee62442eee60002eee660ff00060dd006660000666
# 057:dd006666f0066666eeeeee66eeeeee66eeeeee66ff0666660dd0666600006666
# 058:660fffdd660d0fff6600ff2e6602442e6600ff2e660ff00060dd006660000666
# 059:dd006666f0066666eeeeeeeeeeeeeeeeeeeeeeeeff0066660dd0666600006666
# 060:6feeeeee6feef0e06fee6fee2eeddddd2eeddddd6666fe66666fee66666ffee6
# 061:eeefed660eefee66eef6eed6ddddddddddddddddffed66666ffd666666fed666
# 064:6666dddd6666eeed6666feed6666ffed66666fee666666fe66600e0066feeeee
# 065:ddd66666d4d666664046666640466666d4d66666e66666660e006666eeeed666
# 066:6666dddd6666feed6666feed6666ffed66666fee666666fe6666fee06666feee
# 067:ddd66666d4d666664046666640466666d4d66666ee666666ee666666e0666666
# 068:6666dddd6666eccd6666fccd6666ffcd66666fcc666666fc66600c0066fccccc
# 069:ddd66666d4d666664046666640466666d4d66666c66666660c006666ccccd666
# 070:6666dddd6666eccd6666fccd6666ffcd66666fcc666666fc66600c0066fccccc
# 071:ddd66666d4d666664046666640466666d4d66666c66666660c006666ccccd666
# 072:6666dddd6666fccd6666fccd6666ffcd66666fcc666666fc6666fcc06666fccc
# 073:ddd66666d4d666664046666640466666d4d66666cc666666cc666666c0666666
# 074:6666666666666666666666666666666666666666666666666666666666666666
# 075:6666666666666666666666666666666666666666666666666666666666666666
# 076:6666666666666666666666666666666666666666666666666666666666666666
# 077:6666666666666666666666666666666666666666666666666666666666666666
# 080:6feeeeee6fe6f0e06fee6fee22ffdddd22ffdddd6666fe66666fee66666ffee6
# 081:eeeeed660eeeee66eef6eed6ddddddddddddddddffed66666ffd666666fed666
# 082:666feeee666feefe662feefd662ffffd66666fee6666fee66666fe6666666ff6
# 083:e0666666e0666666ddddddddddddddddfe666666ffe66666fee66666ffe66666
# 084:6fcccccc6fc6f0c06fcc6fcc22ffdddd22ffdddd6666fc66666fcc66666ffcc6
# 085:cccecd660ccecc66ccf6ccd6ddddddddddddddddffcd66666ffd666666fcd666
# 086:6fcccccc6fc6f0c06fcc6fcc22ffdddd22ffdddd6666fc66666fcc66666ffcc6
# 087:cccecd660ccecc66ccf6ccd6ddddddddddddddddffcd66666ffd666666fcd666
# 088:666fcccc666fcfcc662fcfdd662fffdd66666fcc6666fcc66666fc6666666ff6
# 089:c0666666c0666666ddddddddddddddddfc666666ffc66666fcc66666ff666666
# 090:6666666666666666666666666666666666666666666666666666666666666666
# 091:6666666666666666666666666666666666666666666666666666666666666666
# 092:6666666666666666666666666666666666666666666666666666666666666666
# 093:6666666666666666666666666666666666666666666666666666666666666666
# 104:eeee0dee00000000e0ddddddcc4eeeccc44eeec4c44000c4c44e0dc4c44e0dc4
# 105:eeee0dee00000000e0dddddd44deecc444deec4444000c4444de0c4444ee0c44
# 106:aaaaaaaaaaaaa333aaaaa3aaaaaaa3aaaaaaa3aaaaaaa333aaaaaaa3aaaaaaa3
# 107:aaaaaaaa333aaaaaaa3aaaaaaa3aaaaaaa3aaaaa333aaaaa3aaaaaaa3aaaaaaa
# 108:0000000002200220222222222222222202222220002222000002200000000000
# 120:c44444c4c44444c4c44444c4c44444c4e0deeeee00000000ddde0dddeeee0dee
# 121:44444c4444444c4444444c4444444c44e0deeeee00000000ddde0dddeeee0dee
# 122:aaaaaaa3aaaaaaa3aaaaaaa3aaaaaaa3aaaaaaa3aaaaaaaaaaaaaaaaaaaaaaaa
# 123:3aaaaaaa33aaaaaa3aaaaaaa3aaaaaaa33aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
# </SPRITES>

# <MAP>
# 000:c2c2c234e2e2e2e244c2c2c2c234e2e2e244c2c234e2e2e244c2c234e2e2e244c2c234e2e2e2e244c2c234e2e2e2e244c2c2c234e2e2e2e244c2c2342444c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c234e2e2e2e2e2e2e2e244c2c2c2c2c234e2e2e2e2e2e244c2c2c2342424242444c2c2c234e2e2e2e2e2e2e244c2c2c2c2342424242444c2c234e2e2e2e2e2e2e244c2c2c2c2342424242444c2c234e2e2e2e2e2e2e244c2c2c2c2342424242444c2c2c2c234e2e2e2e2e2e2e244c2c2342424242444c2342424242444c23424242424449073907390c2c2
# 001:c2c2c2c234242444c2c2c2c2c2c2242424c2c2c2c2242424c2c2c2c2242424c2c2c2c234242444c2c2c2c234242444c2c2c2c2c234242444c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c23424242424242444c2c2c2c2c2c2c2342424242444c2c2c2c2c2c2c2c2c2c2c2c2c2c234242424242444c2c2c2c2c2c2c2c2c2c2c2c2c2c234242424242444c2c2c2c2c2c2c2c2c2c2c2c2c2c234242424242444c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c234242424242444c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c290101010a0c2c2
# 002:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c272c272c291111111a1c2c2
# 003:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c26464646464c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c26464646464c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2909073907390c390c390c39090
# 004:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c254848484848474c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c254848484848474c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2909090909090909090909090a0
# 005:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2548484848484848474c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2548484848484848474c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c29196a61104141104141196a6a1
# 006:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c25484848484848484848474c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c25484848484848484848474c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c29197a71111111111111197a7a1
# 007:c2c2c2c2c2c2c2c2c2c2c2c2c2b4c4d4e4f4c28785858585858585858547c2c2c2c2c2c2c2c2c2c2b4c4d4e4f4c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2a4a4a4a4a4a4a4a4a4a4a4a4a4c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2b4c4d4e4f4c2c2c2c2c2c2c2c2c2c2c2c2c2b4c4d4e4f4c28785858585858585858547c2b4c4d4e4f4c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2b4c4d4e4f4c2c2c2c2c2c2c2c2c2b4c4d4e4f4c2c2c2c2c2c2c2c2c2c2c2c2c2b4c4d4e4f4c2c2c2c2c2c2c2c2c2c2c2c2c2b4c4d4e4f4911111111111111111111111a1
# 008:c2c2c2c2c2c2c2c2c2c2c2c2c2b5c5d5e5f5c28785858585858585858547c2c2c2c2c2c2c2c2c2c2b5c5d5e5f5c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2a5a5a5a5a5a5a5a5a5a5a5a5a5c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2b5c5d5e5f5c2c2c2c2c2c2c2c2c2c2c2c2c2b5c5d5e5f5c28785858585858585858547c2b5c5d5e5f5c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2b5c5d5e5f5c2c2c2c2c2c2c2c2c2b5c5d5e5f5c2c2c2c2c2c2c2c2c2c2c2c2c2b5c5d5e5f5c2c2c2c2c2c2c2c2c2c2c2c2c2b5c5d5e5f59196a61111111111111196a6a1
# 009:c2c2c2c2c2c2c2c2c2c2c2c2c2b5c5d5e5f5c28785858585858585858547c2c2c2c2c2c2c2c2c2c2b5c5d5e5f5c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2a5a5a5a5a5a5a5a5a5a5a5a5a5c2c2c2c2c2a4a4a4a4a4a4c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2b5c5d5e5f5c2c2c2c2c2c2c2c2c2c2c2c2c2b5c5d5e5f5c28785858585858585858547c2b5c5d5e5f5c2c2c2707070c2c2c2c2c2c2c2c2c2c2b5c5d5e5f5c2c2c2c2c2c2c2c2c2b5c5d5e5f5c2c2c2c2c2c2c2c2c2c2c2c2c2b5c5d5e5f5c2c2c2c2c2c2c2c2c2c2c2c2c2b5c5d5e5f59197a71111111111111197a7a1
# 010:c2c2c2c2c2c2c2c2c2c2c2c2c2b6c6d6e6f6c28735458585858585354547c2c2c2c2c2c2707080c2b6c6d6e6f6c2c2c2c2c2c2c2c2c2c2c2c2c2a4a4a4a4a4a4a4a4a4c2c2c2c2c2a5a5a5a5a5a5a5a5a5a5a5a5a5c2c2c2c2c2a5a5a5a5a5a5c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2b6c6d6e6f6c2c2c2c2c2c2c2c2c2c2c2c2c2b6c6d6e6f6c28735458585858585354547c2b6c6d6e6f6c2c2c271c281c2c2c2c2c2c2c2c2c2c2b6c6d6e6f6c2c2c2c2c2c2c2c2c2b6c6d6e6f6c2c2c2c2c2c2c2c2c2c2c2c2c2b6c6d6e6f6c2c2c2c2c2c2c2c2c2c2c2c2c2b6c6d6e6f6911111111111111111111111a1
# 011:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2d7c2c2c28736468555657585364647c2c2c2c2c2c271c281c2c2c2d7c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2a5a5a5a5a5a5a5a5a5c2c2c2c2c2a5a5a5a5a5a5a5a5a5a5a5a5a5c2c2c2c2a4a5a5a5a5a5a5c2c2c2c2a4a4a4a4a4c2c2c2c2c2c2c2c2c2c2c2c2d7c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2d7c2c2c28736468555657585364647c2c2c2d7c2c2c2c2c271c281c2c2c2c2c2c2c2c2c2c2c2c2d7c2c2c2c2c2c2c2c2c2c2c2c2c2d7c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2d7c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2d7c2c2911182111105152511118211a1
# 012:c2c2c2c2c2c2c2c2c2c2c2c23242c2d7c2c2c28785858556667685858547c2c2c2c2c2c271c281c2c2c2d7c23060a4a4a4a4a4a4a4c2c2c2c2c2a5a5a5a5a5a5a5a5a5a4c2c2c2c2a5a5a5a5a5a5a5a5a5a5a5a5a5c2c2c2a4a5a5a5a5a5a5a5c2c2c2c2a5a5a5a5a5c2c2c2c2c23060c2c2c2c2c2d7c230405060c2c2c2c2c2c2c2c2c2c2c2c2d7c2c2c28785858556667685858547c2c2c2d7c23242c2c2001020c2c2c2c2c2c2c2c23060c2c2d7c2c2c2c2c230405060c2c2c2c2d7c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2d7c2c2c2c2c230405060c2c2c2c2c2c23060d7c2c2911183111106162611118311a1
# 013:c2c2c2c2c2c2c2c2c2c2c2c23343c7d7e7c2c28786868657677786868647c2c2c2c2c2c290a0a0c2c2c7d7e73161a5a5a5a5a5a5a5c2c2c2c2c2a5a5a5a5a5a5a5a5a5a5c2c2c2c2a5a5a5a5a5a5a5a5a5a5a5a5a5c2c2c2a5a5a5a5a5a5a5a5c2c2c2c2a5a5a5a5a5c2c2c2c2c23161c2c2c2c2c7d7e731415161c2c2c2c2c2c2c2c2c2c2c2c7d7e7c2c28786868657677786868647c2c2c7d7e73343c2c2011121c2c2c2c2c2c2c2c23161c2c7d7e7c2c2c2c231415161c2c2c2c7d7e7c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c7d7e7c2c2c2c231415161c2c2c2c2c2c23161d7e7c2921111111107172711111111a2
# 014:a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a5a5a5a5a5a5a5a4a4a4a4a4a5a5a5a5a5a5a5a5a5a5a4a4a4a4a5a5a5a5a5a5a5a5a5a5a5a5a5a4a4a4a5a5a5a5a5a5a5a5a4a4a4a4a5a5a5a5a5a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4
# 015:a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5
# 016:a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5
# 017:1111111111111111111111111111e8111111111111111111111111111111111111111111e811111111111111111111111111111111111111111111e8111111111111111111111111111111e81111111111111111111111e811111111111111111111111111111111e81111111111111111111111111111111111e811111111111111111111e81111111111111111111111111111111111111111111111111111111111111111111111111111111111111111e811111111111111111111111111111111111111111111111111111111111111111111111111e8111111111111111111111111111111e811111111111111
# 018:1111111111111111111111111111e8111111111111111111111111111111111111111111e811111111111111111111111111111111111111111111e8111111111111111111111111111111e81111111111111111111111e811111111111111111111111111111111e81111111111111111111111111111111111e811111111111111111111e81111111111111111111111111111111111111111111111111111111111111111111111111111111111111111e811111111111111111111111111111111111111111111111111111111111111111111111111e8111111111111111111111111111111e811111111111111
# 019:1111111111111111111111111111e8111111111111111111111111111111111111111111e811111111111111111111111111111111111111111111e8111111111111111111111111111111e81111111111111111111111e811111111111111111111111111111111e81111111111111111111111111111111111e811111111111111111111e811111111111111111111111111118211111111111111821111111111111111111111111111111111111111d9e9f91111111111111111111111111111111111111111111111111111111111111111111111d9e9f911111111111111111111111111d9e9f9111111111111
# 020:11111111111111111111111111d9e9f91111111111111111111111111111111111111111e8111111111111111111111111111111111111111111d9e9f911111111111111111111111111d9e9f9111111111111111111d9e9f9111111111111111111111111111111e811111111111111111111111111111111d9e9f91111111111111111d9e9f9111111111111111111111111118311111111111111831111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
# 021:1111111111111111111111111111111111111111111111111111111111111111111111d9e9f91111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111d9e9f911111111111111111111111111111111111111113a4a1111111111111111111111111111119aaa11111111111111111111111111111111111111111111119aaa11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111113a4a1111113a4a11111111
# 022:11113a4a111111111111111111111111111111111111111111113a4a11111111111111111111111111111111111111111111111111113a4a111111111111113a4a11111111111111111111111111111111111111111111111111111111113a4a111111111111111111111111111111113a4a1111111111111111111111113b4b1111111111111138481111111111119bab11111111111111111111111111111111111111118211119bab1111110b1b11111111111111111111111111111111111111111111111111111111111111111111111111111111119aaa1111111111110b1b1111113b4b1111113b4b110b1b11
# 023:11113b4b111111111111111111111111111111111111111111113b4b111111111111111111111111111111110b1b11111111111111113b4b111111111111113b4b1111111111111111110b1b111111111111111111110b1b1111111111113b4b111111111111111111111111111111113b4b1111111111111111111111113c4c1111111111111139491111111111119cac1111111111d3d3d3d3d3111111111111111111118311119cac1111110c1c11111111111138481111118211111138481111118211113848111111118211111138481111111111119bab1111111111110c1c1111113c4c1111113c4c110c1c11
# 024:11113c4c118211111111111111111111111111111111111182113c4c118211111111111111111111118211110c1c11111111821111113c4c111111384811113c4c1111118211111111110c1c111111111182111111110c1c1111118211113c4c111138481111111104141111113848113c4c1111118211111111111111113d4d1111111111111111111111111111119dad11111111111111111111111111111111041411111111119dad111111111d2d111111111139491111118311111139491111118311113949111111118311111139491111111111119cac111111111111111d2d11113d4d1111113d4d11111d2d
# 025:11113d4d118311111111111111111111111111111111111183113d4d11831111111111111111111111831111111d2d111111831111113d4d111111394911113d4d111111831111111111111d2d111111118311111111111d2d11118311113d4d111139491111111111111111113949113d4d1111118311111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111119dad11111111111111111111111111111111111111111111
# 026:111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111d3d3d3d3d3d3111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
# 027:111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111081828111111111111
# 028:111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111091929111111111111
# 029:1111111111111111111111115c111111116979891111115c1111111111111111115c5c111111111111b8c81168788898a81111111111111111111111111111111111117c8c111111111111111111111169798911111111111111111111116979891111111111111111697989111111117c8c111111111111111111111111111111111111b8c868788898a8111111115c5c11111111111111111111111111111111111111111111111111111111687888111111115c5c111111111111b8c81111111111111111111111111198a81111111111115c5c11b8c868788898a8111111111111111111110a1a2a111111111111
# 030:1111111111111111111111115d111111116a7a8a1111115d1111111111111111115d5d111111111111b9c9116a7a8a99a91111111111111111111111111111111111117d8d11111111111111111111116a7a8a11111111111111111111116a7a8a11111111111111116a7a8a111111117d8d111111111111111111111111111111111111b9c96a7a8a99a9111111115d5d1111111111d3d3d3d3d31111111111111111111111111111111111116a7a8a111111115d5d111111111111b9c91111111111111111111111111199a91111111111115d5d11b9c96a7a8a99a91111111111111111d3d3d3d3d3d3d311111111
# 031:d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3
# 032:d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3
# 033:d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3
# 034:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 035:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 036:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 037:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 038:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 039:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 040:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 041:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 042:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 043:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 044:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 045:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 046:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 047:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 048:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 049:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 050:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 051:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 052:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 053:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 054:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 055:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 056:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 057:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 058:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 059:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 060:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 061:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 062:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 063:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 064:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 065:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 066:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 067:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 068:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 069:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 070:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 071:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 072:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 073:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 074:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 075:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 076:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 077:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 078:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 079:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 080:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 081:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 082:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 083:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 084:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 085:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 086:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 087:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 088:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 089:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 090:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 091:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 092:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 093:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 094:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 095:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 096:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 097:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 098:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 099:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 100:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 101:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 102:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 103:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 104:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 105:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 106:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 107:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 108:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 109:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 110:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 111:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 112:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 113:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 114:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 115:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 116:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 117:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 118:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 119:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 120:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 121:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 122:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 123:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 124:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 125:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 126:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 127:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 128:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 129:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 130:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 131:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 132:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 133:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 134:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# 135:c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2
# </MAP>

# <WAVES>
# 000:00000000ffffffff00000000ffffffff
# 001:0123456789abcdeffedcba9876543210
# 002:0123456789abcdef0123456789abcdef
# </WAVES>

# <SFX>
# 000:77727773777377747774777477747774777477747774777477707773777377837783778277817780779f679d679c679b679b679b679b678b67806780304000000000
# 006:c6077604060416013600460f560e760d860ca60bb60ac609c609d600d600d600e600e600e600f600f600f600f600f600f600f600f600f600f600f600b6000000000d
# 008:3748873837188748476897485708a70867099709470a970b670b970c770db70e670fb70f8701d7029703d703c704d705d706d706d707d707e707f700360000000000
# 009:e700970f670ed70df700e70dc70ca70b570cf700f700f700f700f700f700f700f700f700f700f700f700f700f700f700f700f700f700f700f700f700b60000000000
# </SFX>

# <TRACKS>
# 000:100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# </TRACKS>

# <PALETTE>
# 000:1a1c2c5d275db13e53ef7d57ffcd75a7f07038b76425717929366f3b5dc941a6f673eff7f4f4f494b0c2566c86333c57
# </PALETTE>

