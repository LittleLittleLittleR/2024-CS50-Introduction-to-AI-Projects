"""
Tic Tac Toe Player
"""

import math
import copy

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
    xcount = 0
    ocount = 0

    for row in board:
        for cell in row:
            if cell == X:
                xcount += 1
            if cell == O:
                ocount += 1

    if xcount <= ocount:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    moveset = set()
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == EMPTY:
                moveset.add((i, j))

    return moveset


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    if action not in actions(board):
        raise Exception("Invalid Move")

    row, column = action
    newboard = copy.deepcopy(board)
    newboard[row][column] = player(board)

    return newboard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # Horizontal
    for row in board:
        if len(set(row)) == 1 and row[0] != EMPTY:
            return row[0]

    # Vertical
    for i in range(len(board[0])):
        tempset = set()
        for row in board:
            tempset.add(row[i])
        if len(tempset) == 1 and EMPTY not in tempset:
            return tempset.pop()

    # diagonal
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != EMPTY:
        return board[0][2]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board):
        return True
    else:
        for row in board:
            if EMPTY in row:
                return False
        return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    dic = {"X": 1, "O": -1, None: 0}
    return dic[winner(board)]


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    if terminal(board):
        return None

    def max_value(board):
        if terminal(board):
            return utility(board)
        v = -100
        for action in actions(board):
            v = max(v, min_value(result(board, action)))
        return v

    def min_value(board):
        if terminal(board):
            return utility(board)
        v = 100
        for action in actions(board):
            v = min(v, max_value(result(board, action)))
        return v

    turn = player(board)
    lst = []
    output_act = None
    if turn == X:
        output_val = -100
        for action in actions(board):
            value = min_value(result(board, action))
            lst.append([action, value])
            if value > output_val:
                output_val = value
                output_act = action
    else:
        output_val = 100
        for action in actions(board):
            value = max_value(result(board, action))
            lst.append([action, value])
            if value < output_val:
                output_val = value
                output_act = action
    return output_act




