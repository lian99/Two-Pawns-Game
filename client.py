import sys
import pygame
from board import ChessBoard
from UserInterface import UserInterface
import socket
import time
from agent import Agent
import msvcrt  #  Windows-only module for keyboard input
import threading
# Initialize global variables
global game_time
global color
global UI
global window_initialized  # Flag to track if the Pygame window has been initialized
global game_mode
# Create a socket instance
socketObject = socket.socket()

# Connect to the server
socketObject.connect(("localhost", 5000))
print("Connected to the server")

# Set the socket to non-blocking mode
socketObject.setblocking(False)

#  Initialize Pygame here (before the game loop starts)
pygame.init()

# Initialize the ChessBoard
Board = ChessBoard()
UI = None  # Don't initialize UI yet
window_initialized = False  # Pygame window is not created yet
agent = None  # store the agent object
# Main loop
clock = pygame.time.Clock()
running = True
game_over = False  # Game is initially running




running = True  # Global flag for stopping all threads

def listen_for_exit(socketObject):
    """ Continuously check if the player types 'exit' to quit the game without blocking input """
    global running  # Ensure we modify the global variable

    while running:
        #  Use Windows-specific `msvcrt.kbhit()` instead of `select.select()`
        if msvcrt.kbhit():  
            command = sys.stdin.readline().strip().lower()
            if command == "exit":
                print("🚨 Exit requested by player. Sending exit to server...")

                #  Send exit signal to the server
                socketObject.send(str.encode("exit"))

                #  Set running to False to stop all game loops
                running = False

                #  Quit Pygame to close the board
                pygame.quit()

                #  Exit the entire program
                sys.exit()


#  Start the exit listener in a separate thread
exit_thread = threading.Thread(target=listen_for_exit, args=(socketObject,), daemon=True)
exit_thread.start()





while running:
    try:
        # Receive data from the server
        data = socketObject.recv(1024).decode()
        if not data:
            print("Server disconnected")
            running = False
            break

        print(f"Received data: {data}")

        if data == "Black's turn" or data == "White's turn":
            print(data)
            # UI.current_turn = 'W' if data == "White's turn" else 'B'  # ✅ Fix turn tracking!
            # UI.draw_time()  # ✅ Update UI to show the correct active timer
            socketObject.send(str.encode("OK"))

        if data.startswith("Time"):
            # Set the time limit
            try:
                time_parts = data.split()
                if len(time_parts) == 2 and time_parts[0] == "Time":
                    game_time = int(time_parts[1]) * 60
                    print("game_time that was received in clinet is:" + str(game_time))
                    socketObject.send(str.encode("OK"))
                else:
                    print(f"Invalid Time command received: {data}")
            except ValueError:
                print(f"Invalid time value in Time command: {data}")

        elif data.startswith("Setup"):
            # Initialize the board with pawn positions
            # Clear the board before placing pawns
            for row in range(8):
                for col in range(8):
                    Board.boardArray[row][col] = "--"

            # Reset piece_status
            Board.piece_status["wp"] = [[], []]  # Empty positions & status for white pawns
            Board.piece_status["bp"] = [[], []]  # Empty positions & status for black pawns

            # Parse received pawn positions
            pawn_positions = data.split()[1:]
            for pos in pawn_positions:
                color = pos[0]  # 'W' for White, 'B' for Black
                col = ord(pos[1]) - ord('a')  # Convert letter to column index
                row = 8 - int(pos[2])  # Convert board row index

                piece = 'wp' if color == 'W' else 'bp'
                Board.boardArray[row][col] = piece  # Place pawn on board

                # Store in piece_status dynamically
                if piece == "wp":
                    Board.piece_status["wp"][0].append(f"({row}, {col})")  # Store position
                    Board.piece_status["wp"][1].append(True)  # Mark as active
                else:
                    Board.piece_status["bp"][0].append(f"({row}, {col})")  # Store position
                    Board.piece_status["bp"][1].append(True)  # Mark as active

            # ✅ Set opponent pieces count dynamically based on the player's color
            if color == "W":
                Board.opponent_pieces = len(Board.piece_status["bp"][0])  # White's opponent is Black
            else:
                Board.opponent_pieces = len(Board.piece_status["wp"][0])  # Black's opponent is White

            socketObject.send(str.encode("OK"))  # Confirm setup completion

        elif data == "White":
            color = "W"

            # UI.white_time = game_time  # White's initial time

            socketObject.send(str.encode("OK"))

        elif data == "Black":
            color = "B"

            socketObject.send(str.encode("OK"))



        elif data == "Begin":
            # ✅ Create the Pygame window only when "Begin" is received
            if not window_initialized:
                surface = pygame.display.set_mode([600, 650], 0, 0)
                pygame.display.set_caption('Pawn Game')
                if color == 'B':
                    pygame.display.set_caption('Pawn Game - Black')
                else:
                    pygame.display.set_caption('Pawn Game - White')

                UI = UserInterface(surface, Board, color, socketObject)
                UI.set_game_mode(game_mode)  # Pass the mode to the UI
                UI.playerColor = color
                # UI.white_time = game_time  # White's initial time
                # UI.black_time = game_time  # Black's initial time
                UI.game_time = game_time

                # UI.start_timer()
                window_initialized = True
                UI.drawComponent()  # Draw the initial board
                if game_mode == "2" or game_mode == "3":
                    agent = Agent(UI.chessboard, color)


            socketObject.send(str.encode("OK"))



        elif data == "1" or data == "2" or data == "3" or data == "4":
            print()
            # Store the game mode
            game_mode = data.split()[0]  # Extract the mode (1, 2, or 3)
            print(f"Game mode set to: {game_mode}")
            socketObject.send(str.encode("OK"))



        elif data == "Your turn":

            print("its my turn")
            if UI:
                UI.flag = True
                if (game_mode == "2" and color == "B") or (game_mode == "3" and color == "W" ) or game_mode == "4":  # AI Turn
                    print("AI is making a move...")
                    ai_move = agent.getBestMove(color)

                    if ai_move :  # Ensure it's a valid move:
                    
                        move_str = f"{chr(ord('a') + ai_move[1])}{8 - ai_move[0]}{chr(ord('a') + ai_move[3])}{8 - ai_move[2]}"
                        print(f"AI move: {move_str}")
                        if (color == "W" and ai_move[2]==0) or (color == "B" and ai_move[2]==7):
                                socketObject.send(str.encode("Win"))
                        UI.flag = False
                        socketObject.send(str.encode(move_str))
                    else:
                        print("AI has no move available.")
                       
                        socketObject.send(str.encode("exit"))
                else:  # human turn
                    move, flag, capture_flag = UI.clientMove(color)
                    if capture_flag == 1:
                        # update the captured pieces of the opponent
                        UI.chessboard.opponent_pieces -= 1
                        # current player wins if he captured all the opponent's pieces
                        flag = -1 if UI.chessboard.opponent_pieces == 0 else flag

                    if move is None:
                        print("No valid move available")
                        socketObject.send(str.encode("exit"))
                    elif move == "TIMEOUT":
                        socketObject.send(str.encode("TIMEOUT"))
                    elif flag == -1:
                        socketObject.send(str.encode("Win"))
                    elif flag == 1:
                        socketObject.send(str.encode("Lost"))
                    else:
                        move_str = f"{chr(ord('a') + move[1])}{8 - move[0]}{chr(ord('a') + move[3])}{8 - move[2]}"
                        UI.flag = False
                        socketObject.send(str.encode(move_str))
            else:
                print("UI not initialized")





        elif data == "YOU WON!":
            print(data + " HURRRAY!")
            # running = False
            game_over = True
            socketObject.send(str.encode("OK"))
            break

        elif data == "You lost! good luck next time":
            print(data)
            # running = False
            game_over = True
            socketObject.send(str.encode("OK"))
            break

        elif data == "exit":
            print("Game ended by server")
            game_over = True
            socketObject.send(str.encode("OK"))
            # running = False
            break

        else:
            # Handle the opponent's move
            try:
                if len(data) == 4 and data[0] in 'abcdefgh' and data[2] in 'abcdefgh' and data[1] in '12345678' and \
                        data[3] in '12345678':
                    move = data
                    start_col = ord(move[0]) - ord('a')
                    start_row = 8 - int(move[1])
                    end_col = ord(move[2]) - ord('a')
                    end_row = 8 - int(move[3])
                    if UI:
                        UI.chessboard.computeMove((start_row, start_col, end_row, end_col), 0, color)
                        UI.drawComponent()  # Redraw board after opponent's move
                        socketObject.send(str.encode("OK"))

                    else:
                        print("UI not initialized")
                else:
                    print(f"Invalid move data received: {data}")
            except Exception as e:
                print(f"Error processing move: {e}")

    except BlockingIOError:
        pass  # No data received, continue running the loop

    if window_initialized:
        # print("\n\nthis window is initialized , player is : "+color+"\n\n")
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not game_over:  # Allow mouse clicks only if game is still active
                    print(f"🖱 [DEBUG] Mouse clicked at: {pygame.mouse.get_pos()}")  # 🔴 Log mouse clicks
            # elif event.type == pygame.USEREVENT:  # Timer event triggered every second
            #         UI.update_timer()  # Update timer on UI
        pygame.display.update()
    clock.tick(30)

# Close the connection
socketObject.close()
print("Connection closed")


