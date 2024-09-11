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
