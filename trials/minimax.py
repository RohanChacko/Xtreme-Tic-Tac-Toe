import sys
from copy import deepcopy
import random
import time

class MinimaxAgent(object):
    def __init__(self, player):
        self.player                 = player
        self.MIN_DEPTH              = 1
        self.MAX_DEPTH              = 6
        self.INIT_ALPHA             = -1*sys.maxint
        self.INIT_BETA              = sys.maxint
        self.TIME_LIMIT             = 20
        self.TIME_ELAPSED           = 0
        self.board                  = None
        self.best_move              = (-1,-1,-1)
        self.best_move_val          = -1 *  sys.maxint
        self.transposition_table    = {}
        self.zobristboard           = []

        # self.small_board_weights    = [
        #     [
        #         [ 9, 10,  9,     8,  7,  8,      9, 10,  9,],
        #         [10, 10,  7,     7,  8,  7,      7, 10, 10,],
        #         [ 9,  7,  9,     8,  7,  8,      9,  7,  9,],
        #
        #         [ 8,  7,  8,     8,  7,  8,      8,  7,  8,],
        #         [ 7,  8,  7,     7,  8,  7,      7,  8,  7,],
        #         [ 8,  7,  8,     8,  7,  8,      8,  7,  8,],
        #
        #         [ 9,  7,  9,     8,  7,  8,      9,  7,  9,],
        #         [10, 10,  7,     7,  8,  7,      7, 10, 10,],
        #         [9 , 10,  9,     8,  7,  8,      9, 10,  9,],
        #     ],
        #     [
        #         [ 9, 10,  9,     8,  7,  8,      9, 10,  9,],
        #         [10, 10,  7,     7,  8,  7,      7, 10, 10,],
        #         [ 9,  7,  9,     8,  7,  8,      9,  7,  9,],
        #
        #         [ 8,  7,  8,     8,  7,  8,      8,  7,  8,],
        #         [ 7,  8,  7,     7,  8,  7,      7,  8,  7,],
        #         [ 8,  7,  8,     8,  7,  8,      8,  7,  8,],
        #
        #         [ 9,  7,  9,     8,  7,  8,      9,  7,  9,],
        #         [10, 10,  7,     7,  8,  7,      7, 10, 10,],
        #         [9 , 10,  9,     8,  7,  8,      9, 10,  9,],
        #     ],
        # ]
        #
        # self.small_board_status_weights = [
        #     [
        #         [20, 15, 20,],
        #         [15, 20, 15,],
        #         [20, 15, 20,],
        #     ],
        #     [
        #         [15, 20, 15,],
        #         [20, 15, 20,],
        #         [15, 20, 15,],
        #     ]
        # ]


        # Populating the Zobrist Hash Table
        for k in range(0,2):
            self.zobristboard.append([])
            for i in range(0,9):
                self.zobristboard[k].append([])
                for j in range(0,9):
                    self.zobristboard[k][i].append( [random.randint(1, 2**64 - 1) for l in range(2)] )

        self.player_smallboard_count = []

        # Setting no. of x's & o's to be zero initially for each smallboard.
        # Each cell [num(x) num(o)]
        for k in range(0,2):
            self.player_smallboard_count.append([])
            for i in range(0,3):
                self.player_smallboard_count[k].append([])
                for j in range(0,3):
                    self.player_smallboard_count[k][i].append(0)

        self.num_moves = 0

        self.good_board_1 = [-1,-1,-1]
        self.good_board_2 = [-1,-1,-1]

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

    def update(self, move, player, tog_update):
        # tog_update: 1 for update | 0 for restore

        if not tog_update:
            player = '-'

        if tog_update:
            self.board.big_boards_status[move[0]][move[1]][move[2]] = player


        x = move[1]/3
        y = move[2]/3
        k = move[0]
        fl = 0
        #checking if a small_board has been won or drawn or not after the current move
        bs = self.board.big_boards_status[k]
        for i in range(3):
            #checking for horizontal pattern(i'th row)
            if (bs[3*x+i][3*y] == bs[3*x+i][3*y+1] == bs[3*x+i][3*y+2]) and (bs[3*x+i][3*y] == player):
                self.board.small_boards_status[k][x][y] = player

                if not tog_update:
                    self.board.small_boards_status[k][x][y] = '-'
                    self.board.big_boards_status[move[0]][move[1]][move[2]] = '-'
                return
			#checking for vertical pattern(i'th column)
            if (bs[3*x][3*y+i] == bs[3*x+1][3*y+i] == bs[3*x+2][3*y+i]) and (bs[3*x][3*y+i] == player):
                self.board.small_boards_status[k][x][y] = player

                if not tog_update:
                    self.board.small_boards_status[k][x][y] = '-'
                    self.board.big_boards_status[move[0]][move[1]][move[2]] = '-'
                return
		#checking for diagonal patterns
		#diagonal 1
		if (bs[3*x][3*y] == bs[3*x+1][3*y+1] == bs[3*x+2][3*y+2]) and (bs[3*x][3*y] == player):
			self.board.small_boards_status[k][x][y] = player

            if not tog_update:
                self.board.small_boards_status[k][x][y] = '-'
                self.board.big_boards_status[move[0]][move[1]][move[2]] = '-'

            return
		#diagonal 2
        if (bs[3*x][3*y+2] == bs[3*x+1][3*y+1] == bs[3*x+2][3*y]) and (bs[3*x][3*y+2] == player):
            self.board.small_boards_status[k][x][y] = player

            if not tog_update:
                self.board.small_boards_status[k][x][y] = '-'
                self.board.big_boards_status[move[0]][move[1]][move[2]] = '-'

            return
		#checking if a small_board has any more cells left or has it been drawn

        if not tog_update:
            self.board.big_boards_status[move[0]][move[1]][move[2]] = '-'
            if self.board.small_boards_status[k][x][y] == 'd':
                self.board.small_boards_status[k][x][y] = '-'

        for i in range(3):
			for j in range(3):
				if bs[3*x+i][3*y+j] =='-':
					return

        if tog_update:
            self.board.small_boards_status[k][x][y] = 'd'

        return

    def minimax(self, depth, old_move, is_maximizing_player, alpha, beta):


        if depth == 0 or self.board.find_terminal_state() != ('CONTINUE', '-'):

            zobhash = self.computeZobHash(self.board.big_boards_status)
            if zobhash in self.transposition_table:
                state_score = self.transposition_table[zobhash]
            else:
                state_score = self.evaluate_heuristic(self.board, old_move, depth, is_maximizing_player)
                self.transposition_table[zobhash] = state_score
            return state_score

        if is_maximizing_player:
            best_heuristic_val = -1 * sys.maxint
            available_moves = self.board.find_valid_move_cells(old_move)
            # if len(available_moves) > 18 and self.num_moves > 0:
            #     available_moves = self.open_move_heuristic(available_moves)


            for current_move in available_moves:

                self.update(current_move, self.player, 1)

                allowed_small_board = [current_move[1]%3, current_move[2]%3]

                current_time = time.time()
                if current_time - self.TIME_ELAPSED > self.TIME_LIMIT:
                    return best_heuristic_val

                if self.board.small_boards_status[0][allowed_small_board[0]][allowed_small_board[1]] != '-' and self.board.small_boards_status[1][allowed_small_board[0]][allowed_small_board[1]] != '-':
                    value = self.minimax(depth-1, current_move, True, alpha, beta)
                else:
                    value = self.minimax(depth-1, current_move, False, alpha, beta)

                best_heuristic_val = max(best_heuristic_val, value)
                alpha = max(alpha, best_heuristic_val)
                self.update(current_move, self.player, 0)
                if beta <= alpha:
                    break

            return best_heuristic_val


        else:
            best_heuristic_val = sys.maxint
            available_moves = self.board.find_valid_move_cells(old_move)
            # if len(available_moves) > 18 and self.num_moves > 0:
            #     available_moves = self.open_move_heuristic(available_moves)

            for current_move in available_moves:

                self.update(current_move, self.opponent, 1)

                allowed_small_board = [current_move[1]%3, current_move[2]%3]

                current_time = time.time()
                if current_time - self.TIME_ELAPSED > self.TIME_LIMIT:
                    return best_heuristic_val


                if self.board.small_boards_status[0][allowed_small_board[0]][allowed_small_board[1]] != '-' and self.board.small_boards_status[1][allowed_small_board[0]][allowed_small_board[1]] != '-':
                    value = self.minimax(depth-1, current_move, False, alpha, beta)
                else:
                    value = self.minimax(depth-1, current_move, True, alpha, beta)

                best_heuristic_val = min(best_heuristic_val, value)
                beta = min(beta, best_heuristic_val)
                self.update(current_move, self.opponent, 0)

                if alpha <= beta:
                    break

            return best_heuristic_val

    def IDS(self, available_moves, old_move, is_player_max):
        # print "Came into IDS"

        for depth in range(self.MIN_DEPTH, self.MAX_DEPTH):
            print "Doing depth " + str(depth)

            for current_move in available_moves:

                # Max Player Made His Move
                self.update(current_move, self.player, 1)
                # self.board.update(old_move, current_move, self.player)

                allowed_small_board = [current_move[1]%3, current_move[2]%3]

                current_time = time.time()
                # print str(depth) + " " + str(current_time - self.TIME_ELAPSED)
                if current_time - self.TIME_ELAPSED > self.TIME_LIMIT:
                    return

                # Get the value of the move the max player made
                if self.board.small_boards_status[0][allowed_small_board[0]][allowed_small_board[1]] != '-' and self.board.small_boards_status[1][allowed_small_board[0]][allowed_small_board[1]] != '-':
                    move_value = self.minimax(depth, current_move, is_player_max, self.INIT_ALPHA, self.INIT_BETA)
                else:
                    move_value = self.minimax(depth, current_move, not is_player_max, self.INIT_ALPHA, self.INIT_BETA)

                # Undo the move
                self.update(current_move, self.player, 0)

                # Update the best move value and best move depending on if the player is Max or Min
                if move_value > self.best_move_val:
                    self.best_move = current_move
                    self.best_move_val = move_value


    def move(self, board, old_move, flag):

        self.board = deepcopy(board)
        self.TIME_ELAPSED = time.time()
        is_player_max = True
        self.best_move_val = -1 *  sys.maxint
        self.best_move = (-1,-1,-1)
        available_moves = self.board.find_valid_move_cells(old_move)

        if old_move != (-1,-1,-1):
            self.num_moves +=1

        if len(available_moves) == 1:
            return available_moves[0]

        # if len(available_moves) > 18 and self.num_moves > 0:
        #     available_moves = self.open_move_heuristic(available_moves)

        self.IDS(available_moves, old_move, is_player_max)

        self.num_moves +=1
        print self.player + str(self.best_move)
        return self.best_move

    def evaluate_heuristic(self, board, old_move, depth, is_maximizing_player):

        state_score = 0

        #################################### Heuristic A ####################################

        if board.find_terminal_state() == (self.player,'WON'):
            return sys.maxint + depth
        elif  board.find_terminal_state() == (self.opponent,'WON'):
            return -1*sys.maxint - depth
        else:
            pass

        #################################### Heuristic B ####################################

        state_score += self.heur_b()
        #################################### Heuristic C ####################################

        # Small Board position weights
        # for k in range(2):
        #     for i in range(9):
        #         for j in range(9):
        #             if self.board.big_boards_status[k][i][j] == self.player:
        #                 state_score += self.small_board_weights[k][i][j]

        state_score += self.evaluate_big_board()

        if self.board.small_boards_status[0][old_move[1]%3][old_move[2]%3] != '-' and self.board.small_boards_status[1][old_move[1]%3][old_move[2]%3] != '-':
            
            if is_maximizing_player:
                state_score += 1000
            else:
                state_score -= 1000
        
        return state_score


    def open_move_heuristic(self, available_moves):
        # Reset values
        for k in range(0,2):
            for i in range(0,3):
                for j in range(0,3):
                    self.player_smallboard_count[k][i][j] = 0

        min_1 = sys.maxint
        min_2 = sys.maxint
        avail = []
        self.good_board_1 = [-1,-1,-1]
        self.good_board_2 = [-1,-1,-1]

        for move in available_moves:
            self.player_smallboard_count[move[0]][move[1]%3][move[2]%3] +=1

        for k in range (0,2):
            for i in range(0,3):
                for j in range(0,3):

                    if min_1 > self.player_smallboard_count[k][i][j] and self.player_smallboard_count[k][i][j] > 0:
                        min_2 = min_1
                        self.good_board_2 = self.good_board_1
                        min_1 = self.player_smallboard_count[k][i][j]
                        self.good_board_1 = [k, i, j]

        for move in available_moves:
            if [move[0], move[1]%3, move[2]%3] == self.good_board_1 or [move[0], move[1]%3, move[2]%3] == self.good_board_2:
                avail.append(move)

        return avail


    def heur_b(self):
        # The Small Board Representations of the Big Board
        # Heuristic for winning Small Board
        # Have to still decide on a score for winning, as in what priority to give
        count = 0
        for k in range(2):
            for i in range(3):
                for j in range(3):
                    if self.board.small_boards_status[k][i][j] == self.player:
                        count += 35
                    if self.board.small_boards_status[k][i][j] == self.opponent:
                        count -= 35

        for k in range(0,2):

            count += 75 * self.eval_smallboard(k, 'x')
            count -= 50 * self.eval_smallboard(k, 'o')

        return count

    def eval_smallboard(self, board_num, player):

        count = 0
        board = [
                [1, 1, 1,],
                [1, 1, 1,],
                [1, 1, 1,],
            ]
        bs = self.board.small_boards_status[board_num]
        for i in range(0,3):
            for j in range(0,3):

                if bs[i][j] == '-':
                    board[i][j] = 0
                elif bs[i][j] != player:
                    board[i][j] = -1


        for i in range(0,3):
            # Horizontal winning pattern
            if board[i][0] + board[i][1] + board[i][2] == 2:
                count+=1

            # Horizontal blocking pattern
            if board[i][0] + board[i][1] + board[i][2] == -1:
                count+=1

            # Vertical winning pattern
            if board[0][i] + board[1][i] + board[2][i] == 2:
                count+=1

            # Vertical blocking pattern
            if board[0][i] + board[1][i] + board[2][i] == -1:
                count+=1

        # Diagnol winning pattern
        if board[0][0] + board[1][1] + board[2][2] == 2:
            count+=1

        # Diagnol winning pattern
        if board[0][2] + board[1][1] + board[2][0] == 2:
            count+=1

        # Diagnol blocking pattern
        if board[0][0] + board[1][1] + board[2][2] == -1:
            count+=1

        # Diagnol blocking pattern
        if board[0][2] + board[1][1] + board[2][0] == -1:
            count+=1

        return count

    def evaluate_big_board(self):

        player_adv_pos_count = self.get_big_board_advantage_positions(self.player)
        opponent_adv_pos_count = self.get_big_board_advantage_positions(self.opponent)

        return player_adv_pos_count - opponent_adv_pos_count

    def get_big_board_advantage_positions(self, flg):
        advantange_pos_count = 0
        big_board_weight = ([[1 for i in range(9)] for j in range(9)], [[1 for i in range(9)] for j in range(9)])
        for k in range(2):
            for i in range(9):
                for j in range(9):
                    if self.board.big_boards_status[k][i][j] == '-':
                        big_board_weight[k][i][j] = 0
                    elif  self.board.big_boards_status[k][i][j] != flg:
                        big_board_weight[k][i][j] = -1

        for k in range(2):
            for i in range(0,9,3):
                for j in range(0,9,3):
                    for l in range(3):
                        if big_board_weight[k][i+l][j] +  big_board_weight[k][i+l][j+1] + big_board_weight[k][i+l][j+2] == 2:
                            advantange_pos_count += 1
                        if big_board_weight[k][i+l][j] +  big_board_weight[k][i+l][j+1] + big_board_weight[k][i+l][j+2] == -1:
                            advantange_pos_count += 1
                        if big_board_weight[k][i][j+l] +  big_board_weight[k][i+1][j+l] + big_board_weight[k][i+2][j+l] == 2:
                            advantange_pos_count += 1
                        if big_board_weight[k][i][j+l] +  big_board_weight[k][i+1][j+l] + big_board_weight[k][i+2][j+l] == -1:
                            advantange_pos_count += 1
                    if big_board_weight[k][i][j] + big_board_weight[k][i+1][j+1] + big_board_weight[k][i+2][j+2] == 2:
                        advantange_pos_count += 1
                    if big_board_weight[k][i][j+2] + big_board_weight[k][i+1][j+1] + big_board_weight[k][i+2][j] == 2:
                        advantange_pos_count += 1

        return advantange_pos_count
