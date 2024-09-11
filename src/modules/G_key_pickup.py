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
 