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
    