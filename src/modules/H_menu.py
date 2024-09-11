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