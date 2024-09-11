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
