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