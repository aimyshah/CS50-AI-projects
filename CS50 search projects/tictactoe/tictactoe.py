"""
Tic Tac Toe Player
"""


import copy
import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    countX = 0
    countY = 0
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == X:
                countX += 1
            elif board[row][col] == O:
                countY += 1
            elif board[row][col] == EMPTY:
                countX += 0
    if countX > countY:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    AllPossibleActions = set()
    for row in range(len(board)):
        for col in range(len(board)):
            if board[row][col] == EMPTY:
                AllPossibleActions.add((row, col))
    return AllPossibleActions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action not in actions(board):
        raise Exception("Invalid move")
    row, col = action
    board_copy = copy.deepcopy(board)
    board_copy[row][col] = player(board)
    return board_copy


def checkRows(board, player):
    for row in board:
        if row[0] == player and row[1] == player and row[2] == player:
            return True

    return False


def checkCols(board, player):
    for col in range(len(board)):
        if board[0][col] == player and board[1][col] == player and board[2][col] == player:
            return True

    return False


def checkFirstDig(board, player):
    return board[0][0] == player and board[1][1] == player and board[2][2] == player


def checkSecondDig(board, player):
    return board[0][2] == player and board[1][1] == player and board[2][0] == player


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    if checkRows(board, X) or checkCols(board, X) or checkFirstDig(board, X) or checkSecondDig(board, X):
        return X
    elif checkRows(board, O) or checkCols(board, O) or checkFirstDig(board, O) or checkSecondDig(board, O):
        return O
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    for row in range(len(board)):
        for col in range(len(board)):
            if board[row][col] == EMPTY:
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def max_value(board):
    v = -math.inf
    if terminal(board):
        return utility(board)
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v


def min_value(board):
    v = math.inf
    if terminal(board):
        return utility(board)
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    elif player(board) == X:
        plays = []
        for action in actions(board):
            plays.append([min_value(result(board, action)), action])
        return sorted(plays, key=lambda x: x[0], reverse=True)[0][1]

    elif player(board) == O:
        plays = []
        for action in actions(board):
            plays.append([max_value(result(board, action)), action])
        return sorted(plays, key=lambda x: x[0])[0][1]
