import pygame
import time
import threading
import pygame
import pygame
import msvcrt  # ✅ For Windows keyboard input handling

class UserInterface:
    def __init__(self, surface, chessboard, playerColor, socketObject):
        self.surface = surface
        self.chessboard = chessboard
        self.playerColor = playerColor  # Default player color
        self.firstgame = True
        self.game_time = 0
        self.selected = False
        self.selected_row = -1
        self.selected_col = -1
        self.returned_flag = 0
        self.game_mode = None  # store the game mode

        self.running = True
        self.current_turn = 'W'
        self.flag = False
        self.socketObject = socketObject

        # Load pawn images
        self.black_pawn = pygame.image.load('images/black_pawn.png')
        self.white_pawn = pygame.image.load('images/white_pawn.png')
        # Scale pawn images to fit the slots
        self.black_pawn = pygame.transform.scale(self.black_pawn, (50, 50))
        self.white_pawn = pygame.transform.scale(self.white_pawn, (50, 50))
        self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
        self.timer_thread.start()

    def draw_time(self):
        """Clears the previous time and updates the displayed game time on the UI."""
        font = pygame.font.SysFont('Arial', 30)
        minutes = self.game_time // 60
        seconds = self.game_time % 60
        time_text = font.render(f"Time: {minutes:02}:{seconds:02}", True, (255, 255, 255))

        # Clear previous text by drawing a rectangle over the old text
        pygame.draw.rect(self.surface, (0, 0, 0), (0, 600, 600, 50))  # Black background

        # Draw updated time
        self.surface.blit(time_text, (10, 610))  # Adjust position as needed
        pygame.display.update()  # Refresh the UI

    def run_timer(self):
        """Thread function to update the timer every second."""
        while self.running:
            time.sleep(1)  # Wait for one second
            if self.flag and self.game_time > 0:
                self.game_time -= 1
                self.draw_time()

            # elif self.game_time==0:
            #      self.socketObject.send(str.encode("TIMEOUT"))
            if self.game_time == 0:
                self.running = False  # ✅ Stop the timer thread
                print(f"Time over for {self.playerColor}!")  # Debugging

    def switch_turn(self, new_turn):
        """Switch the turn to update the timer correctly."""
        self.current_turn = new_turn  # Change turn

    def start_timer(self):
        # print("\n\nstart_timer function is envoked\n\n")
        """Starts the countdown timer using pygame's built-in event system."""
        pygame.time.set_timer(pygame.USEREVENT, 1000)  # Fire event every 1 second

    def update_timer(self):
        """Decrease game time by one second and refresh UI."""
        if self.game_time > 0:
            self.game_time -= 1
            self.draw_time()

        # print(f"Turn: {self.current_turn}, Remaining Time: {self.game_time}")  # Debugging
        self.draw_time()  # ✅ Refresh the timer on screen

    def stop_timer(self):
        # print("stop_timer in userinterface is called")
        """Stops the countdown when the game ends."""
        self.running = False

    def drawComponent(self):
        print("Redrawing the board")  # Debugging
        # Draw the chessboard grid
        # Draw the white background for the time display
        pygame.draw.rect(self.surface, (255, 255, 255), (0, 0, 600, 50))  # White rectangle at the top

        for i in range(8):
            for j in range(8):
                color = (255, 223, 186) if (i + j) % 2 == 0 else (139, 69, 19)  # Light and dark squares
                pygame.draw.rect(self.surface, color, (j * 75, i * 75, 75, 75))

        # Draw the pawns
        for i in range(8):
            for j in range(8):
                if self.chessboard.boardArray[i][j] == 'wp':
                    if self.white_pawn:
                        self.surface.blit(self.white_pawn, (j * 75 + 12, i * 75 + 12))
                    else:
                        pygame.draw.circle(self.surface, (255, 255, 255), (j * 75 + 37, i * 75 + 37), 25)
                elif self.chessboard.boardArray[i][j] == 'bp':
                    if self.black_pawn:
                        self.surface.blit(self.black_pawn, (j * 75 + 12, i * 75 + 12))
                    else:
                        pygame.draw.circle(self.surface, (0, 0, 0), (j * 75 + 37, i * 75 + 37), 25)
        # Draw the time
        # print("draw_time function is about to be called in drawcomponent-userinterface")
        self.draw_time()
        # Update the display
        pygame.display.update()


    def getMoveInput(self):
            while True:
                move_str = input("\nEnter your move (e.g., 'e2e4'): ").strip().lower()
                if len(move_str) == 4 and move_str[0] in "abcdefgh" and move_str[1] in "12345678" and \
                move_str[2] in "abcdefgh" and move_str[3] in "12345678":
                    return move_str
                print("\n❌ Invalid format. Use format like 'e2e4'.")

    def clientMove(self, color):
        """
        Handle human player moves via terminal input while keeping the UI responsive.
        Supports both mouse and terminal inputs without freezing.
        """
        self.socketObject.setblocking(False)  #  Ensure socket doesn't freeze

        #  Check for "exit" right away before selecting a move
        try:
            data = self.socketObject.recv(1024).decode()
            if data == "exit":
                print("🚪 Exit received from server. Closing game immediately...")
                exit()
        except BlockingIOError:
            pass  # No exit message, continue as normal

        if self.game_time == 0:
            print(f"🚨 {color} ran out of time before making a move!")
            return ("TIMEOUT", 0, 0)

        print("🎮 [DEBUG] Waiting for player move via terminal or mouse...")

        move_str = None
        move_made = False
        self.selected = False  #  Reset selection at the start
        invalid_format_printed = False  #  Prevent repeated error messages

        while not move_made:
            #  Process Pygame events (Prevents Freezing)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("🚪 Quit event detected! Closing game...")
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # ✅ Handle mouse-based move
                    x, y = pygame.mouse.get_pos()
                    row, col = y // 75, x // 75  # Convert click to board coordinates
                    print(f"🖱️ Click detected at ({row}, {col})")

                    if not self.selected:  # First click - select the pawn
                        piece = self.chessboard.boardArray[row][col]
                        if piece == ('wp' if self.playerColor == 'W' else 'bp'):
                            self.selected = True
                            self.selected_row, self.selected_col = row, col
                            print(f"✅ Selected piece at ({row}, {col})")
                        else:
                            print("❌ You can't move pieces that aren't yours.")
                    else:  # Second click - attempt to move the piece
                        is_valid, capture_flag = self.isLegalMove(self.selected_row, self.selected_col, row, col, self.chessboard.boardArray[self.selected_row][self.selected_col])
                        if is_valid:
                            self.update_piece_status(self.chessboard.boardArray[self.selected_row][self.selected_col], self.selected_row, self.selected_col, row, col)
                            self.selected = False
                            print(f"✅ Move made: ({self.selected_row}, {self.selected_col}) → ({row}, {col})")
                            if ((row==0 and piece=='wp') or (row==7 and piece=='bp')):
                                    self.returned_flag=-1
                            if all(value is False for value in self.chessboard.piece_status[self.chessboard.boardArray[self.selected_row][self.selected_col]][1]):
                                    self.returned_flag=1
                            return ((self.selected_row, self.selected_col, row, col), 0, capture_flag)
                        else:
                            print("❌ Invalid move, try again.")
                            self.selected = False

            # ✅ Check for Terminal Input (Non-blocking)
            if msvcrt.kbhit():
                move_str = input().strip().lower()
                invalid_format_printed = False  # ✅ Reset flag when new input is received

            pygame.time.delay(50)  # ✅ Prevent CPU overuse

            if move_str:
                # print(f"✔ Move received: {move_str}")

                # ✅ Validate move format
                if len(move_str) == 4 and move_str[0] in "abcdefgh" and move_str[1] in "12345678" and move_str[2] in "abcdefgh" and move_str[3] in "12345678":
                    start_col = ord(move_str[0]) - ord('a')
                    start_row = 8 - int(move_str[1])
                    end_col = ord(move_str[2]) - ord('a')
                    end_row = 8 - int(move_str[3])

                    piece = self.chessboard.boardArray[start_row][start_col]
                    print(f"🔍 Chosen piece color: {piece}")

                    if piece == ('wp' if self.playerColor == 'W' else 'bp'):
                        is_valid, capture_flag = self.isLegalMove(start_row, start_col, end_row, end_col, piece)
                        if is_valid:
                            self.update_piece_status(piece, start_row, start_col, end_row, end_col)
                            return ((start_row, start_col, end_row, end_col), 0, capture_flag)
                        else:
                            print("❌ Invalid move, try again.")
                    else:
                        print("❌ You must move your own pawn.")
                else:
                    if not invalid_format_printed:
                        print("❌ Invalid format. Use format like 'e2e4'.")
                        invalid_format_printed = True  # ✅ Ensures error message prints only once per bad input

        return None, 0, 0  # Keep waiting for a valid move


    def update_piece_status(self, player_color, old_row, old_col, new_row, new_col):

        old_pos = f"({old_row}, {old_col})"  # Ensure it's a formatted string
        new_pos = f"({new_row}, {new_col})"  # Ensure it's also a string

        # print(f"\n🔍 [DEBUG] Updating {player_color} piece from {old_pos} to {new_pos}")

        # this loop is responsible for updating the status of each piece:
        # 1: if a piece still has a place to move to
        # 2: if a piece was captures by the other player, we update its status in the
        for i in range(len(self.chessboard.piece_status[player_color][0])):  # Access self.piece_status
            row1, col1 = map(int, self.chessboard.piece_status[player_color][0][i].strip("()").split(", "))

            if (row1 != -1 and col1 != -1):
                # if (row1!=new_row and col1!=new_col):
                if self.chessboard.boardArray[row1][col1] != player_color:
                    self.chessboard.piece_status[player_color][0][i] = "(-1, -1)"
                    self.chessboard.piece_status[player_color][1][i] = False

                    continue

                validity = self.check_upcoming_validity(row1, col1, player_color)

                self.chessboard.piece_status[player_color][1][i] = validity
                # print(f"After: {self.chessboard.piece_status[player_color]}\n")

        for i in range(len(self.chessboard.piece_status[player_color][0])):  # Access self.piece_status

            # if self.chessboard.boardArray
            if self.chessboard.piece_status[player_color][0][i] == old_pos:  # Find old position
                # print(f"✅ [DEBUG] Found piece at index {i}, updating position...")

                # Print before update
                # print(f"Before: {self.chessboard.piece_status[player_color]}")

                self.chessboard.piece_status[player_color][0][i] = new_pos  # Update to new position
                # print("player_color in update_piece_status is:" + player_color)

                break  # Stop searching after updating

    def check_upcoming_validity(self, row1, col1, color):
        if color == 'bp':
            valid1, _ = self.isLegalMove(row1, col1, row1 + 1, col1 - 1, color)

            valid2, _ = self.isLegalMove(row1, col1, row1 + 1, col1, color)

            valid3, _ = self.isLegalMove(row1, col1, row1 + 1, col1 + 1, color)

            # If any of them is valid, set flag to True, otherwise False

        elif color == 'wp':
            valid1, _ = self.isLegalMove(row1, col1, row1 - 1, col1 - 1, color)

            valid2, _ = self.isLegalMove(row1, col1, row1 - 1, col1, color)

            valid3, _ = self.isLegalMove(row1, col1, row1 - 1, col1 + 1, color)

            # If any of them is valid, set flag to True, otherwise False

        # print("valid1 or valid2 or valid3 is: "+str(valid1 or valid2 or valid3))
        return valid1 or valid2 or valid3

    def isLegalMove(self, start_row, start_col, end_row, end_col, player_color):
        # print(f"Checking move from ({start_row}, {start_col}) to ({end_row}, {end_col})")

        # Check if the move is within the board
        if not (0 <= end_row < 8 and 0 <= end_col < 8):
            # print("Move is outside the board")
            return False, 0

        # En passant logic
        if self.chessboard.enpassant_possible == (end_row, end_col):
            if player_color == 'wp' and start_row == 3:
                # White pawn capturing en passant
                return True, 1
            elif player_color == 'bp' and start_row == 4:
                # Black pawn capturing en passant
                return True, 1

        # Existing move validation logic
        if player_color == 'wp':  # White pawn
            if end_row == start_row - 1 and end_col == start_col:  # Move forward by 1
                # print("Valid forward move (1 square)")
                return (self.chessboard.boardArray[end_row][end_col] == '--', 0)
            elif start_row == 6 and end_row == start_row - 2 and end_col == start_col:  # Move forward by 2 (initial move)
                # print("Valid forward move (2 squares)")
                return (self.chessboard.boardArray[end_row][end_col] == '--' and \
                        self.chessboard.boardArray[start_row - 1][start_col] == '--', 0)
            elif end_row == start_row - 1 and abs(end_col - start_col) == 1:  # Capture diagonally
                # print("Valid diagonal capture")
                return (self.chessboard.boardArray[end_row][end_col] == 'bp', 1)
        elif player_color == 'bp':  # Black pawn
            if end_row == start_row + 1 and end_col == start_col:  # Move forward by 1
                # print("Valid forward move (1 square)")
                return (self.chessboard.boardArray[end_row][end_col] == '--', 0)
            elif start_row == 1 and end_row == start_row + 2 and end_col == start_col:  # Move forward by 2 (initial move)
                # print("Valid forward move (2 squares)")
                return (self.chessboard.boardArray[end_row][end_col] == '--' and \
                        self.chessboard.boardArray[start_row + 1][start_col] == '--', 0)
            elif end_row == start_row + 1 and abs(end_col - start_col) == 1:  # Capture diagonally
                # print("Valid diagonal capture")
                return (self.chessboard.boardArray[end_row][end_col] == 'wp', 1)

        print("Invalid move")
        return (False, None)

    def set_game_mode(self, mode):
        """
        Set the game mode (1 for Human vs Human, 2 for Human vs AI, 3 for AI vs AI).
        """
        self.game_mode = mode
        print(f"Game mode set to: {self.game_mode}")
