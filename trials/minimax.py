import sys
from copy import deepcopy
import random

class MinimaxAgent(object):
    def __init__(self, player):
        self.player = player
        self.MAX_DEPTH = 2

        if player == 'x':
            self.opponent = 'o'
        else:
            self.opponent = 'x'

    def minimax(self, board, depth, old_move, is_maximizing_player):
        
        copy_board = deepcopy(board)

        if depth == 0 or copy_board.find_terminal_state() != ('CONTINUE', '-'):
            state_score = self.evaluate_heuristic(copy_board)
            return state_score

        if is_maximizing_player:
            best_heuristic_val = -1 * sys.maxint
            available_moves = copy_board.find_valid_move_cells(old_move)
            for current_move in available_moves:
                copy_board.big_boards_status[current_move[0]][current_move[1]][current_move[2]] = self.player

                allowed_small_board = [current_move[1]%3, current_move[2]%3]
                if copy_board.small_boards_status[0][allowed_small_board[0]][allowed_small_board[1]] != '-' and copy_board.small_boards_status[1][allowed_small_board[0]][allowed_small_board[1]] != '-':
                    value = self.minimax(copy_board, depth-1, current_move, True)
                else:
                    value = self.minimax(copy_board, depth-1, current_move, False)

                best_heuristic_val = max(best_heuristic_val, value)

                copy_board.big_boards_status[current_move[0]][current_move[1]][current_move[2]] = '-'
            return best_heuristic_val


        else:
            best_heuristic_val = sys.maxint
            available_moves = copy_board.find_valid_move_cells(old_move)
            for current_move in available_moves:
                copy_board.big_boards_status[current_move[0]][current_move[1]][current_move[2]] = self.opponent


                allowed_small_board = [current_move[1]%3, current_move[2]%3]
                if copy_board.small_boards_status[0][allowed_small_board[0]][allowed_small_board[1]] != '-' and copy_board.small_boards_status[1][allowed_small_board[0]][allowed_small_board[1]] != '-':
                    value = self.minimax(copy_board, depth-1, current_move, False)
                else:
                    value = self.minimax(copy_board, depth-1, current_move, True)

                best_heuristic_val = min(best_heuristic_val, value)

                copy_board.big_boards_status[current_move[0]][current_move[1]][current_move[2]] = '-'
            return best_heuristic_val





    def move(self, board, old_move, flag):

        copy_board = deepcopy(board)
        is_player_max = True
        best_move_val = -1 *  sys.maxint
        best_move = (-1,-1,-1)
        available_moves = copy_board.find_valid_move_cells(old_move)

        
        
        for current_move in available_moves:

            # Max Player Made His Move
            copy_board.big_boards_status[current_move[0]][current_move[1]][current_move[2]] = self.player

            allowed_small_board = [current_move[1]%3, current_move[2]%3]

            # Get the value of the move the max player made
            if copy_board.small_boards_status[0][allowed_small_board[0]][allowed_small_board[1]] != '-' and copy_board.small_boards_status[1][allowed_small_board[0]][allowed_small_board[1]] != '-':
                move_value = self.minimax(copy_board, self.MAX_DEPTH, current_move, is_player_max)
            else:
                move_value = self.minimax(copy_board, self.MAX_DEPTH, current_move, not is_player_max)

            # Undo the move
            copy_board.big_boards_status[current_move[0]][current_move[1]][current_move[2]] = '-'

            # Update the best move value and best move depending on if the player is Max or Min
            if move_value > best_move_val:
                best_move = current_move
                best_move_val = move_value


        print self.player + str(best_move)
        return best_move

    def evaluate_heuristic(self, board):
        return random.randint(0,5)
