import copy
import time
import sys

global weights


class Agent:
    def __init__(self, chessboard, color):
        """
        Initialize the Agent with the chessboard and the player's color.

        :param chessboard: The current state of the chessboard.
        :param color: The color of the player ('W' for White, 'B' for Black).
        """
        self.chessboard = chessboard
        self.playerColor = color
        self.transposition_table = {}  # To store previously evaluated board states

    def print_board(self, board, message="Board State"):
        print(f"\n[DEBUG] {message}\n\n")
        for row in board:
            print(" ".join(row))

    def getBestMove(self, player, max_depth=5, time_limit=30):
        """
        Get the best move using iterative deepening and alpha-beta pruning.

         player: The player making the move ('W' or 'B').
         max_depth: The maximum depth to search.
         time_limit: The time limit in seconds for the search.
        :return: The best move found.
        """
        
        start_time = time.time()
        best_move = None
        best_value = -float('inf')

        # Iterative deepening: Start with depth 1 and increase until time runs out
        for depth in range(1, max_depth + 1):
            elapsed_time = time.time() - start_time
            if elapsed_time > time_limit:
                break  # Stop searching if time limit is exceeded

            # Perform a minimax search at the current depth
            move, value = self.minimax_search(player, depth, start_time, time_limit)
            # print(f"we are in gteBestMove, printing move and its evaluation: {move}, {value} \n\n")
            # print(f" best move and best value currently in getBestMove is: {best_move}, {best_value}")
            if value > best_value:
                best_value = value
                best_move = move

        return best_move

    def minimax_search(self, player, depth, start_time, time_limit):
        """
        Perform a minimax search with alpha-beta pruning to find the best move.

         player: The player making the move ('W' or 'B').
         depth: The current depth of the search.
         start_time: The time when the search started.
         time_limit: The time limit in seconds for the search.
        :return: The best move and its evaluated score.
        """
        best_move = None
        best_value = -float('inf')
        alpha = -float('inf')
        beta = float('inf')
        # print("\n[DEBUG] Original Board Before Move Simulation:")
        # self.print_board(self.chessboard.boardArray, "Original Board Before Move")

        # Generate all possible moves and sort them for better pruning
        moves = self.getPossibleMoves(player)
        # Print heuristic values of all moves before sorting
        # print("\n[DEBUG] Move evaluations before sorting:")
        # for move in moves:
        #     move_eval = self.heuristic(self.simulateMove([row[:] for row in self.chessboard.boardArray], move), player)
        #     print(f"Move: {move}, Evaluation: {move_eval}")
        # print("\n")

        moves.sort(
            key=lambda move: self.heuristic(self.simulateMove([row[:] for row in self.chessboard.boardArray], move),
                                            player), reverse=True)

        for move in moves:
            # Simulate the move on a copy of the board
            new_board = self.simulateMove([row[:] for row in self.chessboard.boardArray], move)
            # Perform the minimax search
            _, eval = self.minimax(new_board, depth - 1, alpha, beta, False, player, start_time, time_limit)
            

            if eval > best_value:
                best_value = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta cut-off

        # print("\n[DEBUG] Move evaluations AFTER sorting:")
        for move in moves:
            move_eval = self.heuristic(self.simulateMove([row[:] for row in self.chessboard.boardArray], move), player)
            # print(f"Move: {move}, Evaluation: {move_eval}")

        # print(f"\n\n[DEBUG] Best move selected: {best_move}, Evaluation: {best_value}\n\n")
        # Print all move evaluations **only after all are processed**

        return best_move, best_value

  

    def minimax(self, board, depth, alpha, beta, maximizing_player, player, start_time, time_limit):
        """
        Minimax algorithm with alpha-beta pruning and iterative deepening.

         board: The current state of the board.
         depth: The current depth of the search.
         alpha: The alpha value for alpha-beta pruning.
         beta: The beta value for alpha-beta pruning.
         maximizing_player: True if the current player is maximizing, False otherwise.
         player: The player making the move ('W' or 'B').
         start_time: The time when the search started.
         time_limit: The time limit in seconds for the search.
        :return: The best move and its evaluated score.
        """
        # Check for time limit
        if time.time() - start_time > time_limit:
            return None, self.heuristic(board, player)  # Return the current evaluation if time runs out

        # Check transposition table for previously evaluated board states
        board_key = self._hash_board(board)
        if board_key in self.transposition_table:
            stored_depth, stored_value = self.transposition_table[board_key]
            if stored_depth >= depth:
                return None, stored_value  # Use the stored value if the depth is sufficient

        if depth == 0 or self.isGameOver(board):
            return None, self.quiescence_search(board, alpha, beta, player, depth=3)  # Quiescence search

        # if self.isGameOver(board):  
        #     return None, float('-inf') if maximizing_player else float('inf')  # Losing for maximizing, winning for minimizing

        # if depth == 0:
        #     return None, self.quiescence_search(board, alpha, beta, player, depth=3)  # Quiescence search




        if maximizing_player:
            max_eval = -float('inf')
            best_move = None
            moves = self.getPossibleMoves(player)
            moves.sort(key=lambda move: self.heuristic(self.simulateMove(board, move), player), reverse=True)

            for move in moves:
                new_board = self.simulateMove(board, move)
                _, eval = self.minimax(new_board, depth - 1, alpha, beta, False, player, start_time, time_limit)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cut-off
            self.transposition_table[board_key] = (depth, max_eval)  # Store the result in the transposition table
            return best_move, max_eval
        else:
            min_eval = float('inf')
            best_move = None
            opponent = 'B' if player == 'W' else 'W'
            moves = self.getPossibleMoves(opponent)
            moves.sort(key=lambda move: self.heuristic(self.simulateMove(board, move), player))

            for move in moves:
                new_board = self.simulateMove(board, move)
                _, eval = self.minimax(new_board, depth - 1, alpha, beta, True, player, start_time, time_limit)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cut-off
            self.transposition_table[board_key] = (depth, min_eval)  # Store the result in the transposition table
            return best_move, min_eval

    def quiescence_search(self, board, alpha, beta, player, depth=3):
        """
        Quiescence search to avoid the horizon effect by evaluating positions after captures.

        board: The current state of the board.
         alpha: The alpha value for alpha-beta pruning.
         beta: The beta value for alpha-beta pruning.
         player: The player making the move ('W' or 'B').
         depth: The maximum depth for quiescence search.
        :return: The evaluated score of the board.
        """
        if depth == 0:
            return self.heuristic(board, player)  # Stop recursion if depth limit is reached

        stand_pat = self.heuristic(board, player)
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        for move in self.getCaptureMoves(player):
            new_board = self.simulateMove(board, move)
            score = -self.quiescence_search(new_board, -beta, -alpha, player, depth - 1)
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha
        # Weights for the heuristic function might change or add weights

    weights = {
        "win_score": 100000,  # Winning the game
        "diff_pawn": 20,  # Difference in number of pawns
        "promote_pawn": 500,  # # Huge bonus for promoting pawns
        "advanced_row": 40,  # bonus for moving pawns forward
        "passed_pawn": 250,  # bigger bonus for having a passed pawn
        "white_advancement_pawn": 40,  # Penalty for White pawns advanced pawns (as a black player)
        "black_advancement_pawn": 40,  # Penalty for White advanced pawns (as a white player)
        "white_passed_pawn": 180,  # bigger penalty for letting White have a passed pawn
        "black_passed_pawn": 180,  # bigger penalty for letting black have a passed pawn
        "capture_opponent": 50  # Gains for capturing opponent's pawns
    }

    def heuristic(self, board, player):
        """
        Heuristic function to evaluate the board state.

         board: The current state of the board.
        return: The evaluated score of the board.
        """
        # for row in board:
        #     print(row)
        #     print("\n\n")

        white_score = 0
        black_score = 0
        winner = self.checkWinner(board)
        if winner == 'W':
            white_score += self.weights["win_score"]
        elif winner == 'B':
            black_score += self.weights["win_score"]
        # Calculate the difference in number of pawns
        white_pawns = sum(row.count('wp') for row in board)
        black_pawns = sum(row.count('bp') for row in board)
        diff_pawn = white_pawns - black_pawns
        if player == 'W':
            white_score += diff_pawn * self.weights["diff_pawn"]
        else:  # player is black
            black_score += (-1 * diff_pawn) * self.weights["diff_pawn"]
        for i in range(8):
            for j in range(8):
                if player == 'W':  # handle white player
                    if board[i][j] == 'wp':  # White pawn
                        # check if player is so close to promotion
                        if i == 1:
                            white_score += self.weights["promote_pawn"]
                        # give more weight to pawns that are closer to promotion
                        advance_weight = 7 - i  # we are reaching row 0

                        white_score += advance_weight * self.weights["advanced_row"]
                        scaling_factor = 1 + ((7 - i) / 7)  # Moves from 1 to ~2

                        # check if pawn is passed
                        if self.is_passed_pawn(board, i, j, 'W'):
                            white_score += scaling_factor * self.weights["passed_pawn"]  # maybe we should add advance_weight * weights["advanced_row"]

                        if self.is_hanging_pawn(board, i, j, 'W'):
                            white_score -= 70  # Penalize hanging pawns

                        if self.capture_opponent(board, i, j, 'W'):
                            white_score += self.weights["capture_opponent"]


                    elif board[i][j] == 'bp':  # Black pawn
                        # we need to "punish" white score if black are close to promotion
                        advance_weight = i
                        white_score -= advance_weight * self.weights["black_advancement_pawn"]
                        if self.is_passed_pawn(board, i, j, 'B'):
                            white_score -= self.weights["black_passed_pawn"]+ advance_weight * self.weights[
                                "black_advancement_pawn"]

                else:  # handle black player


                    if board[i][j] == 'bp':  # black pawn
                        # check if player is so close to promotion
                        if i == 6:
                            black_score += self.weights["promote_pawn"]
                        # give more weight to pawns that are closer to promotion
                        advance_weight = i  # we are reaching row 7
                        
                        black_score += advance_weight * self.weights["advanced_row"]
                        scaling_factor = 1 + (advance_weight / 7)  # Normalizes from 1 (starting) to ~2 (almost promoted)
                        # check if pawn is passed
                        if self.is_passed_pawn(board, i, j, 'B'):
                            #   print("found a passed pawn on ( "+str(i)+" , "+ str(j)+" ) , of black player")
                            black_score += scaling_factor * self.weights["passed_pawn"]  # maybe we should add advance_weight * weights["advanced_row"]

                        # **NEW: Check if Black's pawn is hanging**
                        if self.is_hanging_pawn(board, i, j, 'B'):
                            black_score -= 70  # Penalize hanging pawns

                        if self.capture_opponent(board, i, j, 'B'):
                            black_score += self.weights["capture_opponent"]

                    elif board[i][j] == 'wp':  # white pawn
                        # we need to "punish" black score if black pawns are close to promotion
                        advance_weight = 7 - i
                        black_score -= advance_weight * self.weights["white_advancement_pawn"]
                        if self.is_passed_pawn(board, i, j, 'W'):
                            black_score -= self.weights["white_passed_pawn"]+ advance_weight * self.weights[
                                "white_advancement_pawn"]
               
        return white_score if player == 'W' else black_score

   

    def is_hanging_pawn(self, board, row, col, player):
        opponent = 'w' if player == 'B' else 'b'

        # Define capture directions based on player color
        capture_directions = [(row - 1, col - 1), (row - 1, col + 1)] if player == 'W' else [(row + 1, col - 1),
                                                                                             (row + 1, col + 1)]

        for r, c in capture_directions:
            if 0 <= r < 8 and 0 <= c < 8 and board[r][c] == f"{opponent}p":
                # print("\nreturning true in is_hanging_pawn for player: "+player+" row and col are: "+str(row)+" , "+ str(col)+ " a diagonal capture was found\n")
                return True  # Pawn is under threat

        return False

    def capture_opponent(self, board, row, col, player):
        opponent = 'w' if player == 'B' else 'b'

        # Define capture directions based on player color
        capture_directions = [(row - 1, col - 1), (row - 1, col + 1)] if player == 'W' else [(row + 1, col - 1),
                                                                                             (row + 1, col + 1)]

        for r, c in capture_directions:
            if 0 <= r < 8 and 0 <= c < 8 and board[r][c] == f"{opponent}p":
                # print("\nreturning true in capture_opponent for player: "+player+" row and col are: "+str(row)+" , "+ str(col)+ " a diagonal capture was found\n")
                return True  # Pawn is under threat

        return False

    def is_passed_pawn(self, board, row, col, color):
        """
        Check if a pawn is a passed pawn (no opposing pawns blocking its path to promotion).

         board: The current state of the board.
         row: The row of the pawn.
         col: The column of the pawn.
         color: The color of the pawn ('W' or 'B').
         True if the pawn is a passed pawn, False otherwise.
        """
        if color == 'W':
            for r in range(row - 1, -1, -1):
                for c in [col - 1, col, col + 1]:
                    if (0 <= c < 8 and board[r][c] == 'bp'):
                        return False
                
                if board[r][col]=='wp':
                    return False

            # print("\nreturning true in function is_passed_pawn for player: "+color+" , in board["+str(r)+"]["+str(c)+"]\n")
            return True
        else:  # color == 'B'
            for r in range(row + 1, 8):
                for c in [col - 1, col, col + 1]:
                    if 0 <= c < 8 and board[r][c] == 'wp':
                        return False
                    
                if board[r][col]=='bp':
                    return False
            # print("\nreturning true in function is_passed_pawn for player: "+color+" , in board["+str(r)+"]["+str(c)+"]\n")
            return True

    def _hash_board(self, board):
        """
        Generate a unique hash for the board state.

         board: The current state of the board.
         A hash value representing the board state.
        """
        return hash(tuple(map(tuple, board)))

    def getPossibleMoves(self, player):
        """
        Get all possible moves for a player.

         player: The player making the move ('W' or 'B').
         return: A list of possible moves.
        """
        moves = []
        for i in range(8):
            for j in range(8):
                if self.chessboard.boardArray[i][j] == ('wp' if player == 'W' else 'bp'):
                    if player == 'W':
                        if i > 0 and self.chessboard.boardArray[i - 1][j] == '--':  # Move forward
                            moves.append((i, j, i - 1, j))
                        if i > 0 and j > 0 and self.chessboard.boardArray[i - 1][j - 1] == 'bp':  # Capture diagonally
                            moves.append((i, j, i - 1, j - 1))
                        if i > 0 and j < 7 and self.chessboard.boardArray[i - 1][j + 1] == 'bp':  # Capture diagonally
                            moves.append((i, j, i - 1, j + 1))
                        if i == 6 and self.chessboard.boardArray[i - 2][j] == '--' and \
                                self.chessboard.boardArray[i - 1][j] == '--':  # Move forward by 2 (initial move)
                            moves.append((i, j, i - 2, j))
                        if i == 3:
                            if j == 0 and self.chessboard.enpassant_possible == (i - 1, j + 1):  # Capture en passant
                                moves.append((i, j, i - 1, j + 1))
                            if j == 7 and self.chessboard.enpassant_possible == (i - 1, j - 1):  # Capture en passant
                                moves.append((i, j, i - 1, j - 1))
                            if self.chessboard.enpassant_possible == (i - 1, j - 1) and 0 < j < 7:  # Capture en passant
                                moves.append((i, j, i - 1, j - 1))
                            if self.chessboard.enpassant_possible == (i - 1, j + 1) and 0 < j < 7:  # Capture en passant
                                moves.append((i, j, i - 1, j + 1))
                    else:
                        if i < 7 and self.chessboard.boardArray[i + 1][j] == '--':  # Move forward
                            moves.append((i, j, i + 1, j))
                        if i < 7 and j > 0 and self.chessboard.boardArray[i + 1][j - 1] == 'wp':  # Capture diagonally
                            moves.append((i, j, i + 1, j - 1))
                        if i < 7 and j < 7 and self.chessboard.boardArray[i + 1][j + 1] == 'wp':  # Capture diagonally
                            moves.append((i, j, i + 1, j + 1))
                        if i == 1 and self.chessboard.boardArray[i + 2][j] == '--' and \
                                self.chessboard.boardArray[i + 1][j] == '--':  # Move forward by 2 (initial move)
                            moves.append((i, j, i + 2, j))
                        if i == 4:
                            if j == 0 and self.chessboard.enpassant_possible == (i + 1, j + 1):  # Capture en passant
                                moves.append((i, j, i + 1, j + 1))
                            if j == 7 and self.chessboard.enpassant_possible == (i + 1, j - 1):  # Capture en passant
                                moves.append((i, j, i + 1, j - 1))
                            if self.chessboard.enpassant_possible == (i + 1, j - 1) and 0 < j < 7:  # Capture en passant
                                moves.append((i, j, i + 1, j - 1))
                            if self.chessboard.enpassant_possible == (i + 1, j + 1) and 0 < j < 7:  # Capture en passant
                                moves.append((i, j, i + 1, j + 1))
        return moves

    def getCaptureMoves(self, player):
        """
        Get all capture moves for a player.

         player: The player making the move ('W' or 'B').
        return: A list of capture moves.
        """
        moves = []
        for i in range(8):
            for j in range(8):
                if self.chessboard.boardArray[i][j] == ('wp' if player == 'W' else 'bp'):
                    if player == 'W':
                        if i > 0 and j in [1, 6]:
                            if self.chessboard.boardArray[i - 1][j - 1] == 'bp':  # Capture diagonally
                                moves.append((i, j, i - 1, j - 1))
                            elif self.chessboard.boardArray[i - 1][j + 1] == 'bp':  # Capture diagonally
                                moves.append((i, j, i - 1, j + 1))
                        if i > 0 and j == 0 and self.chessboard.enpassant_possible == (
                        i - 1, j + 1):  # Capture diagonally
                            moves.append((i, j, i - 1, j + 1))
                        if i > 0 and j == 7 and self.chessboard.enpassant_possible == (
                        i - 1, j - 1):  # Capture diagonally
                            moves.append((i, j, i - 1, j - 1))
                        if i == 3:
                            if j == 0 and self.chessboard.enpassant_possible == (i - 1, j + 1):  # Capture en passant
                                moves.append((i, j, i - 1, j + 1))
                            if j == 7 and self.chessboard.enpassant_possible == (i - 1, j - 1):  # Capture en passant
                                moves.append((i, j, i - 1, j - 1))
                            if self.chessboard.enpassant_possible == (i - 1, j - 1) and 0 < j < 7:  # Capture en passant
                                moves.append((i, j, i - 1, j - 1))
                            if self.chessboard.enpassant_possible == (i - 1, j + 1) and 0 < j < 7:  # Capture en passant
                                moves.append((i, j, i - 1, j + 1))
                    else:
                        if i < 7 and j in [1, 6]:
                            if self.chessboard.boardArray[i + 1][j - 1] == 'wp':  # Capture diagonally
                                moves.append((i, j, i + 1, j - 1))
                            elif self.chessboard.boardArray[i + 1][j + 1] == 'wp':  # Capture diagonally
                                moves.append((i, j, i + 1, j + 1))
                        if i < 7 and j == 0 and self.chessboard.boardArray[i + 1][j + 1] == 'wp':  # Capture diagonally
                            moves.append((i, j, i + 1, j + 1))
                        if i < 7 and j == 7 and self.chessboard.boardArray[i + 1][j - 1] == 'wp':  # Capture diagonally
                            moves.append((i, j, i + 1, j - 1))
                        if i == 4:
                            if j == 0 and self.chessboard.enpassant_possible == (i + 1, j + 1):  # Capture en passant
                                moves.append((i, j, i + 1, j + 1))
                            if j == 7 and self.chessboard.enpassant_possible == (i + 1, j - 1):  # Capture en passant
                                moves.append((i, j, i + 1, j - 1))
                            if self.chessboard.enpassant_possible == (i + 1, j - 1) and 0 < j < 7:  # Capture en passant
                                moves.append((i, j, i + 1, j - 1))
                            if self.chessboard.enpassant_possible == (i + 1, j + 1) and 0 < j < 7:  # Capture en passant
                                moves.append((i, j, i + 1, j + 1))
        return moves

    def simulateMove(self, board, move):
        """
        Simulate a move on the board.

         board: The current state of the board.
         move: The move to simulate.
         return: The new state of the board after the move.
        """
        new_board = copy.deepcopy(board)
        start_row, start_col, end_row, end_col = move
        new_board[end_row][end_col] = new_board[start_row][start_col]
        new_board[start_row][start_col] = '--'
        return new_board

    def checkWinner(self, board):
        for j in range(8):
            if board[0][j] == 'wp':
                return 'W'
            elif board[7][j] == 'bp':
                return 'B'
        return None

    def isGameOver(self, board):
        """
        Check if the game is over.

        board: The current state of the board.
        return: winner if the game is over, False otherwise.
        """
        # Check if a pawn has reached the last row
        for i in range(8):
            if board[7][i] == 'bp' or board[0][i] == 'wp':
                # print("condition of gameOver is true")
                return True

        # Check if either player has no pawns left
        white_pawns = sum(row.count('wp') for row in board)
        black_pawns = sum(row.count('bp') for row in board)
        if white_pawns == 0 or black_pawns == 0:
            return True

        # Check if either player has no legal moves
        if len(self.getPossibleMoves('W')) == 0 or len(self.getPossibleMoves('B')) == 0:
            return True

        return False