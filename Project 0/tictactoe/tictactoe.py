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
    # If more Xs than Os, it's Os turn
    x_count = 0
    o_count = 0
    for i in range(0, len(board)):
        for j in range(0, len(board[i])):
            if(board[i][j] == X):
                x_count += 1
            elif(board[i][j] == O):
                o_count += 1

    if(x_count > o_count):
        return O
    # otherwise it's Xs turn
    else:
        return X

    raise NotImplementedError


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()
    # iterate through board and find empty squares
    for i in range(len(board)):
        for j in range(len(board[i])):
            if(board[i][j] == EMPTY):
                possible_actions.add((i, j))
    return possible_actions

    raise NotImplementedError


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # figure out whose turn it is
    player_turn = player(board)
    i, j = action

    # make sure square to be played in is blank
    if(board[i][j] == EMPTY):
        new_board = copy.deepcopy(board)
        new_board[i][j] = player_turn
        return new_board

    # return an error otherwise
    else:
        raise NotImplementedError


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range(0, len(board)):
        if(board[i].count(X) == 3 or column(board, i).count(X) == 3):
            return X
        if(board[i].count(O) == 3 or column(board, i).count(O) == 3):
            return O
    if(board[0][0] == board[1][1] == board[2][2] or board[0][2] ==
       board[1][1] == board[2][0]):
        if(board[1][1] == X):
            return X
        elif(board[1][1] == O):
            return O
    return None


def column(matrix, i):
    return [row[i] for row in matrix]


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if(winner(board) or not actions(board)):
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if(not terminal(board)):
        raise NotImplementedError

    victor = winner(board)
    if(victor == X):
        return 1
    elif(victor == O):
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # ensure that the game isn't over
    if(terminal(board)):
        return None

    v = float('inf')
    optimal_action = None
    for action in actions(board):
        temp_val = max_value(result(board, action))
        if(temp_val < v):
            v = temp_val
            optimal_action = action
    return optimal_action


def maximax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    null_board = initial_state()
    if(board == null_board):
        return (0, 1)

    # ensure that the game isn't over
    if(terminal(board)):
        return None

    v = -1 * float('inf')
    optimal_action = None
    for action in actions(board):
        temp_val = min_value(result(board, action))
        if(temp_val > v):
            v = temp_val
            optimal_action = action
    return optimal_action


def max_value(board):
    if(terminal(board)):
        return utility(board)

    v = -1 * float('inf')
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v


def min_value(board):
    if(terminal(board)):
        return utility(board)

    v = float('inf')
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v
