from os import system, name
import re

# Clear output on Windows/Linux shell
def clear():
    system('cls' if name == 'nt' else 'clear')

# Display game state
def display_board(board):
    print("")
    print(f" {board[7]} ║ {board[8]} ║ {board[9]} ")
    print("═══╬═══╬═══")
    print(f" {board[4]} ║ {board[5]} ║ {board[6]} ")
    print("═══╬═══╬═══")
    print(f" {board[1]} ║ {board[2]} ║ {board[3]} ")
    print("")

def input_move():
    choice = ''

    # Keep prompting for input 1-9 into an empty space
    while not re.search('^[1-9]$', choice):
        choice = input("Choose a position using numpad 1-9: ")
        if not re.search('^[1-9]$', choice):
            print("Invalid Input.")
        elif not pos[int(choice)].isspace():
            print(f"Position {choice} occupied. Please choose another position.")
            choice = ''
            continue

    return int(choice)

def check_win_condition(pos):
    # 3 'O' in a row
    if ('O','O','O') in ((pos[1],pos[2],pos[3]),(pos[4],pos[5],pos[6]),(pos[7],pos[8],pos[9]),
                         (pos[1],pos[4],pos[7]),(pos[2],pos[5],pos[8]),(pos[3],pos[6],pos[9]),
                         (pos[1],pos[5],pos[9]),(pos[3],pos[5],pos[7])):
        print("O's win!")
        return True
    # 3 'X' in a row
    elif ('X','X','X') in ((pos[1],pos[2],pos[3]),(pos[4],pos[5],pos[6]),(pos[7],pos[8],pos[9]),
                           (pos[1],pos[4],pos[7]),(pos[2],pos[5],pos[8]),(pos[3],pos[6],pos[9]),
                           (pos[1],pos[5],pos[9]),(pos[3],pos[5],pos[7])):
        print("X's win!")
        return True
    # No 3 in a row and 9 turns have passed
    elif turn == 10:
        print("Stalemate!")
        return True
    # Keep playing
    else:
        return False

# Initialize variables. Whitespace occupies each position initially
is_gameover = False
pos = [None,' ',' ',' ',' ',' ',' ',' ',' ',' ']
turn = 1

# Main game loop
clear()
while is_gameover == False:
    print(f"===TURN {turn}===")
    display_board(pos)

    # X goes first
    if turn % 2 != 0:
        print("X's move.")
        pos[input_move()] = 'X'
        clear()
    else:
        print("O's move.")
        pos[input_move()] = 'O'
        clear()
    turn += 1
    is_gameover = check_win_condition(pos)

display_board(pos)
print(f"Game Over in {turn-1} turns.")
