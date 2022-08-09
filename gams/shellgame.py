from random import randint
from time import sleep
from os import system

pos = ["   O                     ",
       "            O            ",
       "                     O   "]

def display_game(cur_pos, hidden):
    system('cls')
    print("  ___      ___      ___  ")
    print(" /   \    /   \    /   \ ")
    print("/  0  \  /  1  \  /  2  \ ")
    print("¯¯¯¯¯¯¯  ¯¯¯¯¯¯¯  ¯¯¯¯¯¯¯")
    print('') if hidden else print(cur_pos)

def cup_choice(correct_pos):
    guess = ''

    while guess not in ['0','1','2']:
        guess = input("Guess which cup! (0, 1, or 2): ")
        print(f'Cup {guess} was chosen.')
        sleep(2)
    
    return int(guess) == correct_pos

def play_ball(iters):
    for i in range(iters):
        if i < (iters - 1):
            val = randint(0,2)
            display_game(pos[val], False)
        else:
            display_game(pos[val], True)
    
    return val

# The Game
cor_val = play_ball(50)
if cup_choice(cor_val):
    display_game(pos[cor_val], False)
    print(f"Ball was under Cup {cor_val}. YOU WIN!")
else:
    display_game(pos[cor_val], False)
    print(f"Ball was under Cup {cor_val}. YOU LOSE!")
