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