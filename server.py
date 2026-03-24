import socket
import sys
# Create a server socket
# serverSocket = socket.socket()
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # ✅ Allow port reuse

print("Server socket created")

# Associate the server socket with the IP and Port
ip = "127.0.0.1"
port = 5000
serverSocket.bind((ip, port))
print(f"Server socket bound with ip {ip} port {port}")

# Make the server listen for incoming connections
serverSocket.listen()
print("Waiting for clients to connect...")

clients = []

# Wait for two clients to connect
for _ in range(2):
    clientConnection, clientAddress = serverSocket.accept()
    clients.append(clientConnection)
    print(f"Client {len(clients)} connected")

# Send initial connection message
msg = str.encode("Connected to the server")
clients[0].send(msg)
clients[1].send(msg)

# # Send Time command
# time_limit = input("Enter time limit (in minutes): ")
# time_msg = str.encode(f"Time {time_limit}")
# clients[0].send(time_msg)
# clients[1].send(time_msg)


print("Enter time limit (in minutes): ", end="", flush=True)
time_limit = sys.stdin.readline().strip()
time_msg = str.encode(f"Time {time_limit}")
clients[0].send(time_msg)
clients[1].send(time_msg)

# Wait for OK responses
for client in clients:
    data = client.recv(1024)
    if data.decode() != "OK":
        print("Client did not respond with OK to Time command")
        exit()

# Send Setup command
setup = input("Enter Setup command(Setup Wa2 Wb2 Wc2 Wd2 We2 Wf2 Wg2 Wh2 Ba7 Bb7 Bc7 Bd7 Be7 Bf7 Bg7 Bh7) :")
setup_msg = str.encode(setup)
clients[0].send(setup_msg)
clients[1].send(setup_msg)

# Wait for OK responses
for client in clients:
    data = client.recv(1024)
    if data.decode() != "OK":
        print("Client did not respond with OK to Setup command")
        exit()
# Choose game mode
mode = input("Enter game mode (1 for Human vs Human, 2 for Human vs black agent, 3 for human vs white agent, 4 for white agent vs black agent):")
mode_msg = str.encode(f"{mode}")
clients[0].send(mode_msg)
clients[1].send(mode_msg)

# Wait for OK responses
for client in clients:
    data = client.recv(1024)
    if data.decode() != "OK":
        print("Client did not respond with OK to Mode command")
        exit()

# Assign colors
white_msg = str.encode("White")
black_msg = str.encode("Black")
clients[0].send(white_msg)
clients[1].send(black_msg)

#  3OFT ALLAH AND ADDED THE FOLLOWING 5
for client in clients:
    data = client.recv(1024)
    if data.decode() != "OK":
        print("Client did not respond with OK to Begin command")
        exit()

# Send Begin command
begin_msg = str.encode("Begin")
clients[0].send(begin_msg)
clients[1].send(begin_msg)

# Wait for OK responses
for client in clients:
    data = client.recv(1024)
    if data.decode() != "OK":
        print("Client did not respond with OK to Begin command")
        exit()

# Game loop
game_over = False
player_index = 0  # 0 for White, 1 for Black
while True:
    try:
        # Notify clients whose turn it is
        if player_index == 0:
            clients[1].send(str.encode("White's turn"))

        else:
            clients[0].send(str.encode("Black's turn"))

        data = clients[1 - player_index].recv(1024)
        if data.decode() != "OK":
            print("Client did not respond with OK to Begin command")
            exit()
        # Send "Your turn" to the current player
        clients[player_index].send(str.encode("Your turn"))
        # Notify the correct player

        # Receive move from the current player
        data = clients[player_index].recv(1024)

        if not data:
            print("Client disconnected")
            break

        # print("\n did we get anything from client?\n")
        data = data.decode()
        print(f"Received move: {data}")

      

        if data == "Win":
            winner = player_index
            loser = 1 - player_index  # The other player

            clients[winner].send(str.encode("YOU WON!"))
            clients[loser].send(str.encode("You lost! good luck next time"))

            winner_color = "White" if winner == 0 else "Black"  # Determine winner's color
            print(f"Game ended by defeat. Winner: {winner_color}")
            game_over = True
            for client in clients:
                data = client.recv(1024)
                if data.decode() != "OK":
                    print("Client did not respond with OK to Begin command")
                    exit()

            break
            # print("Game over. Keeping connections open until clients close.")

        if data == "Lost" or data == "TIMEOUT":
            loser = player_index
            winner = 1 - player_index  # The other player

            clients[loser].send(str.encode("You lost! good luck next time"))
            clients[winner].send(str.encode("YOU WON!"))

            winner_color = "White" if loser == 1 else "Black"  # Determine winner's color

            if data == "TIMEOUT":
                print(f"Game ended by timeout. Winner: {winner_color}")
            else:
                print(f"Game ended by defeat. Winner: {winner_color}")
            game_over = True
            for client in clients:
                data = client.recv(1024)
                if data.decode() != "OK":
                    print("Client did not respond with OK to Begin command")
                    exit()

            break
            # print("Game over. Keeping connections open until clients close.")
        if data == "exit":
                print("Game ended by client")
                # clients[0].send(str.encode("exit"))
                # clients[1].send(str.encode("exit"))
                # game_over = True
                # for client in clients:
                #     data = client.recv(1024)
                #     if data.decode() != "OK":
                #         print("Client did not respond with OK to Begin command")
                #         exit()
                for client in clients:
                    client.close()
                serverSocket.close()

                break

        if game_over:
            print("Game is over. No more moves processed.")
            continue  # Skip move processing

        # Validate the move format (e.g., e2e4)
        if len(data) == 4 and data[0] in 'abcdefgh' and data[2] in 'abcdefgh' and data[1] in '12345678' and data[
            3] in '12345678':
            # Send the move to the other player
            # print("data is:" + data)
            other_player_index = 1 - player_index
            # print("\n nw ba3deen? player_index=" + str(player_index) + "\n")
            clients[player_index].send(str.encode(data))
            # print("\nsending to second client, other_player_index=" + str(other_player_index) + "\n")
            clients[other_player_index].send(str.encode(data))

            for client in clients:
                data = client.recv(1024)
                if data.decode() != "OK":
                    print("Client did not respond with OK to Begin command")
                    exit()
            # Switch turns
            player_index = other_player_index
        else:
            print(f"Invalid move received: {data}")

    except ConnectionResetError:
        print("Client disconnected unexpectedly")
        break

# Close connections
for client in clients:
    client.close()
serverSocket.close()
print("Server closed")
