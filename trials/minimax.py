import sys
from copy import deepcopy
import random
import time
from multiprocessing import Process

class MinimaxAgent(object):
    def __init__(self, player):
        self.player                 = player
        self.MIN_DEPTH              = 3
        self.MAX_DEPTH              = 8
        self.INIT_ALPHA             = -1*sys.maxint
        self.INIT_BETA              = sys.maxint
        self.TIME_LIMIT             = 20
        self.TIME_ELAPSED           = 0
        self.board                  = None
        self.best_move              = (-1,-1,-1)
        self.best_move_val          = -1 *  sys.maxint
        self.transposition_table    = {}
        self.zobristboard           = []

        self.small_board_weights    = [
            [
                [9, 10, 9,     8,  7,  8,      9, 10,  9,],
                [10,10, 7,     7,  8,  7,      7, 10, 10,],
                [9, 7,  9,     8,  7,  8,      9,  7,  9,],

                [ 8,  7,  8,     8,  7,  8,      8,  7,  8,],
                [ 7,  8,  7,     7,  8,  7,      7,  8,  7,],
                [ 8,  7,  8,     8,  7,  8,      8,  7,  8,],

                [ 9,  7,  9,     8,  7,  8,      9,  7,  9,],
                [10, 10,  7,     7,  8,  7,      7, 10, 10,],
                [9 , 10,  9,     8,  7,  8,      9, 10,  9,],
            ],
            [
                [9, 10, 9,     8,  7,  8,      9, 10,  9,],
                [10,10, 7,     7,  8,  7,      7, 10, 10,],
                [9, 7,  9,     8,  7,  8,      9,  7,  9,],

                [ 8,  7,  8,     8,  7,  8,      8,  7,  8,],
                [ 7,  8,  7,     7,  8,  7,      7,  8,  7,],
                [ 8,  7,  8,     8,  7,  8,      8,  7,  8,],

                [ 9,  7,  9,     8,  7,  8,      9,  7,  9,],
                [10, 10,  7,     7,  8,  7,      7, 10, 10,],
                [9 , 10,  9,     8,  7,  8,      9, 10,  9,],
            ],
        ]

        self.small_board_status_weights = [
            [
                [20, 15, 20,],
                [15, 20, 15,],
                [20, 15, 20,],
            ],
            [
                [15, 20, 15,],
                [20, 15, 20,],
                [15, 20, 15,],
            ]
        ]


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

        # board_copy = deepcopy(self.board)

        if depth == 0 or self.board.find_terminal_state() != ('CONTINUE', '-'):

            zobhash = self.computeZobHash(self.board.big_boards_status)
            if zobhash in self.transposition_table:
                state_score = self.transposition_table[zobhash]
            else:
                state_score = self.evaluate_heuristic(self.board, old_move)
                self.transposition_table[zobhash] = state_score
            return state_score

        if is_maximizing_player:
            best_heuristic_val = -1 * sys.maxint
            available_moves = self.board.find_valid_move_cells(old_move)
            if len(available_moves) > 18 and self.num_moves > 0:
                available_moves = self.open_move_heuristic(available_moves)


            for current_move in available_moves:
                # self.board.big_boards_status[current_move[0]][current_move[1]][current_move[2]] = self.player
                # print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&'
                # print '-------------------------------------------'
                # print self.board.print_board()

                self.update(current_move, self.player, 1)

                allowed_small_board = [current_move[1]%3, current_move[2]%3]

                current_time = time.time()
                # print current_time - self.TIME_ELAPSED
                # print str(depth) + " " + str(current_time - self.TIME_ELAPSED)
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

                # self.board.big_boards_status[current_move[0]][current_move[1]][current_move[2]] = '-'
                # print self.board.print_board()
                # print '-------------------------------------------'
                # print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&'
                # print
                # print

            return best_heuristic_val


        else:
            best_heuristic_val = sys.maxint
            available_moves = self.board.find_valid_move_cells(old_move)
            if len(available_moves) > 18 and self.num_moves > 0:
                available_moves = self.open_move_heuristic(available_moves)

            for current_move in available_moves:

                # print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&'
                # print '-------------------------------------------'
                # print self.board.print_board()


                # copy_board.big_boards_status[current_move[0]][current_move[1]][current_move[2]] = self.opponent
                self.update(current_move, self.opponent, 1)
                
                allowed_small_board = [current_move[1]%3, current_move[2]%3]

                current_time = time.time()
                # print current_time - self.TIME_ELAPSED
                # print str(depth) + " " + str(current_time - self.TIME_ELAPSED)
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

                # copy_board.big_boards_status[current_move[0]][current_move[1]][current_move[2]] = '-'

            return best_heuristic_val

    def IDS(self, available_moves, old_move, is_player_max):
        # print "Came into IDS"

        for depth in range(self.MIN_DEPTH, self.MAX_DEPTH):
            # print "Doing depth " + str(depth)

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

        if len(available_moves) > 18 and self.num_moves > 0:
            available_moves = self.open_move_heuristic(available_moves)


        # Some Issue: Timeout not Happening After the Required Number of Seconds In the case of MultiProcessing
        # action_process = Process(target=self.IDS(available_moves, old_move, is_player_max))
        # action_process.start()
        # action_process.join(1)

        # if action_process.is_alive():
        #     print "Its still running time to kill"
        #     action_process.terminate()
        #     action_process.join()

        self.IDS(available_moves, old_move, is_player_max)

        # for current_move in available_moves:

        #     # Max Player Made His Move
        #     board_copy = deepcopy(self.board)
        #     self.board.update(old_move, current_move, self.player)

        #     allowed_small_board = [current_move[1]%3, current_move[2]%3]

        #     # Get the value of the move the max player made
        #     if self.board.small_boards_status[0][allowed_small_board[0]][allowed_small_board[1]] != '-' and self.board.small_boards_status[1][allowed_small_board[0]][allowed_small_board[1]] != '-':
        #         move_value = self.minimax(self.MAX_DEPTH, current_move, is_player_max, self.INIT_ALPHA, self.INIT_BETA)
        #     else:
        #         move_value = self.minimax(self.MAX_DEPTH, current_move, not is_player_max, self.INIT_ALPHA, self.INIT_BETA)

        #     # Undo the move
        #     self.board = deepcopy(board_copy)

        #     # Update the best move value and best move depending on if the player is Max or Min
        #     if move_value > self.self.best_move_val:
        #         self.best_move = current_move
        #         self.best_move_val = move_value

        self.num_moves +=1
        print self.player + str(self.best_move)
        return self.best_move

    def evaluate_heuristic(self, board, old_move):

        state_score = 0

        #################################### Heuristic A ####################################

        if board.find_terminal_state() == (self.player,'WON'):
            return sys.maxint
        elif  board.find_terminal_state() == (self.opponent,'WON'):
            return -1*sys.maxint
        else:
            pass

        #################################### Heuristic B ####################################

        # The Small Board Representations of the Big Board
        # Heuristic for winning Small Board
        # Have to still decide on a score for winning, as in what priority to give
        for k in range(2):
            for i in range(3):
                for j in range(3):
                    if self.board.small_boards_status[k][i][j] == self.player:
                        state_score += self.small_board_status_weights[k][i][j]
                    if self.board.small_boards_status[k][i][j] == self.opponent:
                        state_score -= self.small_board_status_weights[k][i][j]
        #################################### Heuristic C ####################################

        # Small Board position weights
        for k in range(2):
            for i in range(9):
                for j in range(9):
                    if self.board.big_boards_status[k][i][j] == self.player:
                        state_score += self.small_board_weights[k][i][j]


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

        # print self.good_board_1
        # print self.good_board_2
        return avail
