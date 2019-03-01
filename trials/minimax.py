import sys
from copy import deepcopy
import random
import time 

class MinimaxAgent(object):
    def __init__(self, player):
        self.player         = player
        self.MAX_DEPTH      = 2
        self.INIT_ALPHA     = -1*sys.maxint
        self.INIT_BETA      = sys.maxint
        self.board          = None

        # self.corner_strategic_positions = [ 
        #                         (0, 0, 0) , (0, 0, 1) , (0, 1, 0) , (0, 1, 1),
        #                         (0, 0, 7) , (0, 0, 8) , (0, 1, 7) , (0, 1, 8),
        #                         (0, 7, 0) , (0, 7, 1) , (0, 8, 0) , (0, 8, 1),
        #                         (0, 7, 7) , (0, 7, 8) , (0, 8, 7) , (0, 8, 8),
        #                         ]


        if player == 'x':
            self.opponent = 'o'
        else:
            self.opponent = 'x'

    def minimax(self, depth, old_move, is_maximizing_player, alpha, beta):
        
        board_copy = deepcopy(self.board)

        if depth == 0 or self.board.find_terminal_state() != ('CONTINUE', '-'):
            state_score = self.evaluate_heuristic(self.board)
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

            print(str(current_move))

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
                        state_score += 20

        #################################### Heuristic C ####################################

        # The Special Positions of the Small Board of the Big Board Positions
        for k in range(2):
            for i in range(0,9,3):
                for j in range(0,9,3):
                    # if self.board.big_boards_status[k][i+1][j+1] == self.player:
                    #     state_score += 10

                    # Top Left Block
                    if i == 0 and j == 0:

                        # f x -
                        # x - -
                        # - - -
                        if self.board.big_boards_status[k][i][j+1] == self.player:
                            state_score += 10
                        if self.board.big_boards_status[k][i+1][j] == self.player:
                            state_score += 10

                        # Center block of top left
                        if self.board.big_boards_status[k][i+1][j+1] == self.player:
                            state_score += 10

                        # Favourable Corner
                        if self.board.big_boards_status[k][i][j] == self.player:
                            state_score += 8

                    # Top Center Block
                    if i == 0 and j == 3:
                        pass

                    # Top Right Block
                    if i == 0 and j == 6:

                        # - x f
                        # - - x
                        # - - -
                        if self.board.big_boards_status[k][i][j+1] == self.player:
                            state_score += 10
                        if self.board.big_boards_status[k][i+1][j+2] == self.player:
                            state_score += 10
                        
                        # Center block of top right
                        if self.board.big_boards_status[k][i+1][j+1] == self.player:
                            state_score += 10

                        # Favourable Corner
                        if self.board.big_boards_status[k][i][j+2] == self.player:
                            state_score += 8

                    # Center Left Block
                    if i == 3 and j == 0:
                        pass
                    # Center Center Block
                    if i == 3 and j == 3:
                        pass
                    # Center Right Block
                    if i == 3 and j == 6:
                        pass

                    # Bottom Left Block
                    if i == 6 and j == 0:

                        # - - -
                        # x - -
                        # f x -
                        if self.board.big_boards_status[k][i+1][j] == self.player:
                            state_score += 10
                        if self.board.big_boards_status[k][i+2][j+1] == self.player:
                            state_score += 10

                        # Center block of bottom left
                        if self.board.big_boards_status[k][i+1][j+1] == self.player:
                            state_score += 10

                        # Favourable Corner
                        if self.board.big_boards_status[k][i+2][j] == self.player:
                            state_score += 8

                    # Bottom Center Block
                    if i == 6 and j == 3:
                        pass

                    # Bottom Right Block
                    if i == 6 and j == 6:

                        # - - -
                        # - - x
                        # - x f
                        if self.board.big_boards_status[k][i+1][j+2] == self.player:
                            state_score += 10
                        if self.board.big_boards_status[k][i+2][j+1] == self.player:
                            state_score += 10

                        # Center block of bottom right
                        if self.board.big_boards_status[k][i+1][j+1] == self.player:
                            state_score += 10

                        # Favourable Corner
                        if self.board.big_boards_status[k][i+2][j+2] == self.player:
                            state_score += 8

        return state_score
