import random

# Initialize the board
def create_board():
    return [[" " for _ in range(3)] for _ in range(3)]

# Display the board
def print_board(board):
    for row in board:
        print("|".join(row))
        print("-" * 5)

# Check for a winner
def check_winner(board, player):
    for row in board:  # Check rows
        if all(cell == player for cell in row):
            return True
    for col in range(3):  # Check columns
        if all(board[row][col] == player for row in range(3)):
            return True
    if all(board[i][i] == player for i in range(3)):  # Diagonal \
        return True
    if all(board[i][2-i] == player for i in range(3)):  # Diagonal /
        return True
    return False

# Check if board is full
def is_draw(board):
    return all(cell != " " for row in board for cell in row)

# Get player's move
def get_move(board):
    while True:
        try:
            row, col = map(int, input("Enter row and column (0-2): ").split())
            if board[row][col] == " ":
                return row, col
            else:
                print("That spot is already taken!")
        except (ValueError, IndexError):
            print("Invalid input! Please enter two numbers between 0 and 2.")

# Minimax Algorithm for AI
def minimax(board, depth, is_maximizing):
    if check_winner(board, "O"):
        return 1
    if check_winner(board, "X"):
        return -1
    if is_draw(board):
        return 0
    
    if is_maximizing:
        best_score = -float("inf")
        for row in range(3):
            for col in range(3):
                if board[row][col] == " ":
                    board[row][col] = "O"
                    score = minimax(board, depth + 1, False)
                    board[row][col] = " "
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = float("inf")
        for row in range(3):
            for col in range(3):
                if board[row][col] == " ":
                    board[row][col] = "X"
                    score = minimax(board, depth + 1, True)
                    board[row][col] = " "
                    best_score = min(score, best_score)
        return best_score

# AI Move
def get_ai_move(board):
    best_score = -float("inf")
    best_move = None
    for row in range(3):
        for col in range(3):
            if board[row][col] == " ":
                board[row][col] = "O"
                score = minimax(board, 0, False)
                board[row][col] = " "
                if score > best_score:
                    best_score = score
                    best_move = (row, col)
    return best_move

# Play the game
def play_game():
    board = create_board()
    human_player = "X"
    ai_player = "O"
    
    print("Welcome to Tic-Tac-Toe!")
    print("You are X and the AI is O")
    print("Enter moves as row column (e.g., '0 0' for top-left)")
    
    while True:
        print_board(board)
        row, col = get_move(board)
        board[row][col] = human_player
        
        if check_winner(board, human_player):
            print_board(board)
            print("You win!")
            break
        elif is_draw(board):
            print_board(board)
            print("It's a draw!")
            break
        
        print("AI is thinking...")
        ai_row, ai_col = get_ai_move(board)
        board[ai_row][ai_col] = ai_player
        
        if check_winner(board, ai_player):
            print_board(board)
            print("AI wins!")
            break
        elif is_draw(board):
            print_board(board)
            print("It's a draw!")
            break

if __name__ == "__main__":
    play_game() 