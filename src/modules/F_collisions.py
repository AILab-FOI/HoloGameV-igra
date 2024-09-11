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