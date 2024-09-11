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