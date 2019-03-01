import sys
from copy import deepcopy
import random
import time

class MinimaxAgent(object):
    def __init__(self, player):
        self.player         = player
        self.MAX_DEPTH      = 3
        self.INIT_ALPHA     = -1*sys.maxint
        self.INIT_BETA      = sys.maxint
        self.board          = None

        self.small_board_weights = [
            [
                [10, 10,  0,     6,  0,  6,      0, 10, 10,],
                [10,  8,  0,     0,  0,  0,      0,  8, 10,],
                [ 0,  0,  0,     6,  0,  6,      0,  0,  0,],

                [ 6,  0,  6,     6,  0,  6,      6,  0,  6,],
                [ 0,  0,  0,     0,  0,  0,      0,  0,  0,],
                [ 6,  0,  6,     6,  0,  6,      6,  0,  6,],

                [ 0,  0,  0,     6,  0,  6,      0,  0,  0,],
                [10,  8,  0,     0,  0,  0,      0,  8, 10,],
                [10, 10,  0,     6,  0,  6,      0, 10, 10,],
            ],
            [
                [10, 10,  0,     6,  0,  6,      0, 10, 10,],
                [10,  8,  0,     0,  0,  0,      0,  8, 10,],
                [ 0,  0,  0,     6,  0,  6,      0,  0,  0,],

                [ 6,  0,  6,     6,  0,  6,      6,  0,  6,],
                [ 0,  0,  0,     0,  0,  0,      0,  0,  0,],
                [ 6,  0,  6,     6,  0,  6,      6,  0,  6,],

                [ 0,  0,  0,     6,  0,  6,      0,  0,  0,],
                [10,  8,  0,     0,  0,  0,      0,  8, 10,],
                [10, 10,  0,     6,  0,  6,      0, 10, 10,],
            ],
        ]

        self.small_board_status_weights = [
            [
                [20, 15, 20,],
                [15, 15, 15,],
                [20, 15, 20,],
            ],
            [
                [20, 15, 20,],
                [15, 15, 15,],
                [20, 15, 20,],
            ]
        ]

        self.transposition_table = {}
        self.zobristboard = []

        # Populating the Zobrist Hash Table
        for k in range(0,2):
            self.zobristboard.append([])
            for i in range(0,9):
                self.zobristboard[k].append([])
                for j in range(0,9):
                    self.zobristboard[k][i].append( [random.randint(1, 2**64 - 1) for l in range(2)] )

        if player == 'x':
            self.opponent = 'o'
        else:
            self.opponent = 'x'

    def computeZobHash(self, board):

        hash = 0

        for k in range(0,2):
            for i in range(0,9):
                for j in range(0,9):
                    if board[k][i][j] == 'x':
                        hash ^= self.zobristboard[k][i][j][0]
                    elif board[k][i][j] == 'o':
                        hash ^= self.zobristboard[k][i][j][1]
        return str(hash)

    def minimax(self, depth, old_move, is_maximizing_player, alpha, beta):

        board_copy = deepcopy(self.board)

        if depth == 0 or self.board.find_terminal_state() != ('CONTINUE', '-'):

            zobhash = self.computeZobHash(self.board.big_boards_status)
            if zobhash in self.transposition_table:
                state_score = self.transposition_table[zobhash]
            else:
                state_score = self.evaluate_heuristic(self.board)
                self.transposition_table[zobhash] = state_score
            return state_score

        if is_maximizing_player:
            best_heuristic_val = -1 * sys.maxint
            available_moves = deepcopy(self.board.find_valid_move_cells(old_move))
            for current_move in available_moves:
                # self.board.big_boards_status[current_move[0]][current_move[1]][current_move[2]] = self.player
                self.board.update(old_move, current_move, self.player)

                allowed_small_board = [current_move[1]%3, current_move[2]%3]
                if self.board.small_boards_status[0][allowed_small_board[0]][allowed_small_board[1]] != '-' and self.board.small_boards_status[1][allowed_small_board[0]][allowed_small_board[1]] != '-':
                    value = self.minimax(depth-1, current_move, True, alpha, beta)
                else:
                    value = self.minimax(depth-1, current_move, False, alpha, beta)

                best_heuristic_val = max(best_heuristic_val, value)
                alpha = max(alpha, best_heuristic_val)
                if beta <= alpha:
                    break

                # self.board.big_boards_status[current_move[0]][current_move[1]][current_move[2]] = '-'
                self.board = deepcopy(board_copy)

            return best_heuristic_val


        else:
            best_heuristic_val = sys.maxint
            available_moves = deepcopy(self.board.find_valid_move_cells(old_move))
            for current_move in available_moves:


                # copy_board.big_boards_status[current_move[0]][current_move[1]][current_move[2]] = self.opponent
                self.board.update(old_move, current_move, self.opponent)


                allowed_small_board = [current_move[1]%3, current_move[2]%3]
                if self.board.small_boards_status[0][allowed_small_board[0]][allowed_small_board[1]] != '-' and self.board.small_boards_status[1][allowed_small_board[0]][allowed_small_board[1]] != '-':
                    value = self.minimax(depth-1, current_move, False, alpha, beta)
                else:
                    value = self.minimax(depth-1, current_move, True, alpha, beta)

                best_heuristic_val = min(best_heuristic_val, value)
                beta = min(beta, best_heuristic_val)
                if alpha <= beta:
                    break

                # copy_board.big_boards_status[current_move[0]][current_move[1]][current_move[2]] = '-'
                self.board = deepcopy(board_copy)

            return best_heuristic_val





    def move(self, board, old_move, flag):

        self.board = deepcopy(board)
        is_player_max = True
        best_move_val = -1 *  sys.maxint
        best_move = (-1,-1,-1)
        available_moves = deepcopy(self.board.find_valid_move_cells(old_move))

        if len(available_moves) == 1:
            return available_moves[0]



        for current_move in available_moves:

            # print(str(current_move))

            # Max Player Made His Move
            board_copy = deepcopy(self.board)
            self.board.update(old_move, current_move, self.player)
            # copy_board.big_boards_status[current_move[0]][current_move[1]][current_move[2]] = self.player

            allowed_small_board = [current_move[1]%3, current_move[2]%3]

            # Get the value of the move the max player made
            if self.board.small_boards_status[0][allowed_small_board[0]][allowed_small_board[1]] != '-' and self.board.small_boards_status[1][allowed_small_board[0]][allowed_small_board[1]] != '-':
                move_value = self.minimax(self.MAX_DEPTH, current_move, is_player_max, self.INIT_ALPHA, self.INIT_BETA)
            else:
                move_value = self.minimax(self.MAX_DEPTH, current_move, not is_player_max, self.INIT_ALPHA, self.INIT_BETA)

            # Undo the move
            self.board = deepcopy(board_copy)
            # copy_board.big_boards_status[current_move[0]][current_move[1]][current_move[2]] = '-'

            # Update the best move value and best move depending on if the player is Max or Min
            if move_value > best_move_val:
                best_move = current_move
                best_move_val = move_value


        print self.player + str(best_move)
        return best_move

    def evaluate_heuristic(self, board):

        state_score = 0

        #################################### Heuristic A ####################################

        if board.find_terminal_state() == ('x','WON') and self.player == 'x':
            state_score += 100
        elif  board.find_terminal_state() == ('o','WON') and self.player == 'o':
            state_score += 100
        elif board.find_terminal_state() == ('x','WON') and self.player == 'o':
            state_score -= 100
        elif board.find_terminal_state() == ('o','WON') and self.player == 'x':
            state_score -= 100


        #################################### Heuristic B ####################################

        # The Small Board Representations of the Big Board
        # Heuristic for winning for Small Board
        # Have to still decide on a score for winning, as in what priority to give
        for k in range(2):
            for i in range(3):
                for j in range(3):
                    if self.board.small_boards_status[k][i][j] == self.player:
                        state_score += self.small_board_status_weights[k][i][j]

        #################################### Heuristic C ####################################

        # The Special Positions of the Small Board of the Big Board Positions
        for k in range(2):
            for i in range(9):
                for j in range(9):
                    if self.board.big_boards_status[k][i][j] == self.player:
                        state_score += self.small_board_weights[k][i][j]

        return state_score
