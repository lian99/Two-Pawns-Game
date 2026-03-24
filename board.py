class ChessBoard:
    def __init__(self):
        # Initialize an 8x8 board with empty spaces
        self.boardArray = [
            ["--"] * 8,  # Row 0: Empty
            ["bp"] * 8,  # Row 1: Black pawns
            ["--"] * 8,  # Row 2: Empty
            ["--"] * 8,  # Row 3: Empty
            ["--"] * 8,  # Row 4: Empty
            ["--"] * 8,  # Row 5: Empty
            ["wp"] * 8,  # Row 6: White pawns
            ["--"] * 8  # Row 7: Empty
        ]
        self.round = 0  # Current round
        self.enpassant = False  # En passant flag
        self.enpassant_possible = ()
        self.enpassantCol = -1  # En passant column
        self.opponent_pieces = 8
        self.color = "none"
        print("🛠 [DEBUG] Board initialized with pawns:")
        for row in self.boardArray:
            print(row)

            # Dictionary to track pawn positions dynamically
        self.piece_status = {
            "wp": [[], []],  # White pawns (positions, active status)
            "bp": [[], []]  # Black pawns (positions, active status)
        }

    def computeMove(self, move, flag, client_color):

        start_row, start_col, end_row, end_col = move
        moving_piece = self.boardArray[start_row][start_col]
        # print("enpassant is: " + str(
            # self.enpassant_possible) + " for player of color: " + moving_piece + ", end_row and end_col are " + str(
            # end_row) + ", " + str(end_col))
        # Check if the move is a two-shquare pawn advance
        if client_color == 'B':
            if moving_piece == 'wp' and start_row == 6 and end_row == 4:
                # Mark the square behind the pawn as the en passant target
                self.enpassant_possible = (end_row + 1, end_col)  # Row 5 (behind the pawn)
                self.boardArray[end_row][end_col] = moving_piece
                self.boardArray[start_row][start_col] = '--'
                return
            elif moving_piece == 'wp' and start_row == 3 and end_row == 2 and abs(start_col - end_col) == 1 and \
                    self.boardArray[start_row][end_col] == 'bp':
                # print("\n condition of line 48 is true\n")
                self.boardArray[end_row][end_col] = moving_piece
                self.boardArray[start_row][start_col] = '--'
                self.boardArray[start_row][end_col] = '--'
                for row in self.boardArray:
                    print(row)

                return

        elif client_color == 'W':
            if moving_piece == 'bp' and start_row == 1 and end_row == 3:
                # Mark the square behind the pawn as the en passant target
                self.enpassant_possible = (end_row - 1, end_col)  # Row 2 (behind the pawn)
                self.boardArray[end_row][end_col] = moving_piece
                self.boardArray[start_row][start_col] = '--'
                return
            elif moving_piece == 'bp' and start_row == 4 and end_row == 5 and abs(start_col - end_col) == 1 and \
                    self.boardArray[start_row][end_col] == 'wp':
                self.boardArray[end_row][end_col] = moving_piece
                self.boardArray[start_row][start_col] = '--'
                self.boardArray[start_row][end_col] = '--'
                for row in self.boardArray:
                    print(row)

                return

        self.boardArray[end_row][end_col] = moving_piece
        self.boardArray[start_row][start_col] = '--'

        # print(f"enpassant_possible: {self.enpassant_possible} (Type: {type(self.enpassant_possible)})")
        # print(f"Checking against: ({end_row}, {end_col}) (Type: {type((end_row, end_col))})")

        if (client_color == 'W'):
            if moving_piece == 'wp':
                if self.enpassant_possible == (end_row, end_col):
                    self.boardArray[end_row + 1][end_col] = '--'
                    self.enpassant_possible = ()
                    return
                self.enpassant_possible = ()

        # Handle en passant capture

        elif (client_color == 'B'):
            if moving_piece == 'bp':
                if self.enpassant_possible == (end_row, end_col):
                    self.boardArray[end_row - 1][end_col] = '--'
                    self.enpassant_possible = ()
                    return
                self.enpassant_possible = ()

        for row in self.boardArray:
            print(row)

    def changePerspective(self):
        """
        Flip the board for the opponent's perspective.
        """
        self.boardArray = [row[::-1] for row in self.boardArray[::-1]]