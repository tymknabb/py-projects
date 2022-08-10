from os import system, name
import numpy as np
import re

# Clear output on Windows/Linux shell
def clear():
    system('cls' if name == 'nt' else 'clear')

# Display game state
def display(grid):
    print("")
    print(f" {grid[0][0]} ║ {grid[0][1]} ║ {grid[0][2]} ")
    print("═══╬═══╬═══")
    print(f" {grid[1][0]} ║ {grid[1][1]} ║ {grid[1][2]} ")
    print("═══╬═══╬═══")
    print(f" {grid[2][0]} ║ {grid[2][1]} ║ {grid[2][2]} ")
    print("")

def input_move(grid, char):
    choice = ''
    flat_grid = np.flipud(grid).flatten()

    # Keep prompting for input 1-9 into an empty space
    while not re.search('^[1-9]$', choice):
        try:
            choice = input("Choose a position using numpad 1-9: ")
            if choice == '0':
                raise ValueError("Numbers 1-9 only.")
            if flat_grid[int(choice) - 1].isspace():
                flat_grid[int(choice) - 1] = char
            else:
                print(f"Position {choice} occupied. Please choose another position.")
                choice = ''
                continue
        except:
            print("Invalid Input.")
            choice = ''

    # Reverse our changes to the grid and return modified grid
    return np.flipud(flat_grid.reshape(3, 3))

def check_win_condition(grid, turn):
    
    O_ROW = ['O','O','O']
    X_ROW = ['X','X','X']

    # Every time...
    if turn == 10:
        print("Stalemate!")
        return True

    # Search matrix, transposed matrix, and diagonals for 3 X/Os
    diagonals = [ grid.diagonal(), np.fliplr(grid).diagonal() ]
    for matrix in [ grid, grid.T, diagonals ]:
        for arr in matrix:
            if np.array_equal(arr, O_ROW):
                print("O's win!")
                return True
            elif np.array_equal(arr, X_ROW):
                print("X's win!")
                return True

    # No wins, keep playing
    return False

# Initialize variables. Whitespace occupies each gridition initially
is_gameover = False
grid = np.array([[' ',' ',' '],
                 [' ',' ',' '],
                 [' ',' ',' ']])
turn = 1

# Main game loop
clear()
while is_gameover == False:
    print(f"===TURN {turn}===")
    display(grid)

    # X goes first
    if turn % 2 != 0:
        print("X's move.")
        grid = input_move(grid, 'X')
        clear()
    else:
        print("O's move.")
        grid = input_move(grid, 'O')
        clear()
    turn += 1
    is_gameover = check_win_condition(grid, turn)

display(grid)
print(f"Game Over in {turn-1} turns.")
