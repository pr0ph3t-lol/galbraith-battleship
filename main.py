# Ethan Trinh & Sherjil Khan - 6/3/26
# A game of internet battleship with pygame UI and socket networking
# A good amount of AI used (primarily for socket, and debugging)


# import libraries used for pygame ui and network threads
import pygame
import ui
import threading
import json
import time
import os
import sys
import subprocess

# battleship game uses command line flags to select server or client mode

def resolve_mode_from_args():
# read command line arguments and return server or client mode
    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        if idx + 1 < len(sys.argv):
            candidate = sys.argv[idx + 1].lower()
            if candidate in ("server", "client"):
                return candidate
    return None

# if dual mode is requested, launch both server and client locally for testing
# support launching both server and client together for dual mode
if "--dual" in sys.argv:
    script_path = os.path.abspath(__file__)
    python_exe = sys.executable
    subprocess.Popen([python_exe, script_path, "--mode", "server"])
    time.sleep(0.4)
    subprocess.Popen([python_exe, script_path, "--mode", "client"])
    raise SystemExit

# initialize pygame and set up the window for the game
pygame.init()

# ensure window is wide enough for two battle grids side-by-side
GRID_COLS = 10
CELL_SIZE = 40
MARGIN = 20
WINDOW_WIDTH = 2 * GRID_COLS * CELL_SIZE + 3 * MARGIN
screen = pygame.display.set_mode((WINDOW_WIDTH, 600))
pygame.display.set_caption("Battleship") 

# fonts used for rendering status text and mode labels
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# create buttons for selecting server or client mode
server_button = ui.Button(150, 250, 150, 50, "SERVER", font)
client_button = ui.Button(500, 250, 150, 50, "CLIENT", font)

# determine startup mode and initialize network/game state variables
mode = resolve_mode_from_args()
network_status = ""
network_socket = None
player_ready = False
opponent_ready = False
game_started = False
incoming_messages = []
recv_buffer = ""
mode_started = False


# send a json message over the active network socket
def send_message(msg_type, **kwargs):
    global network_socket
    try:
        if network_socket:
            message = {"type": msg_type, **kwargs}
            network_socket.send((json.dumps(message) + "\n").encode())
    except Exception:
        pass

# listen for incoming json messages from the opponent
def listen_for_messages():
    global opponent_ready, incoming_messages, network_status, recv_buffer, network_socket
    while True:

        try:
# read raw bytes from socket and append them to the receive buffer
            if network_socket:
                data = network_socket.recv(1024)
                if not data:
                    network_status = "Connection closed"
                    network_socket = None
                    continue
                recv_buffer += data.decode()
                while "\n" in recv_buffer:
                    raw, recv_buffer = recv_buffer.split("\n", 1)
                    if not raw.strip():
                        continue
                    msg = json.loads(raw)
                    incoming_messages.append(msg)
                    if msg.get("type") == "READY":
                        opponent_ready = True
                        network_status = "Other player ready"
                    if msg.get("type") == "SHOT":
                        row = msg.get("row")
                        col = msg.get("col")
                        if row is not None and col is not None:
                            network_status = f"Shot received at {row}, {col}"
                        else:
                            network_status = "Shot received"
                
        except Exception:
            pass
        time.sleep(0.1)

# thread helper for starting the server and accepting one client
def run_server_thread():
    global network_socket, network_status
    try:
        import server
        conn, addr = server.start_server()
        network_socket = conn
        network_status = f"Connected by {addr[0]}:{addr[1]}"
    except Exception as e:
        network_status = f"Server error: {e}"

# thread helper for connecting to the server as a client
def run_client_thread():
    global network_socket, network_status
    try:
        import client
        network_status = "Connecting..."
        network_socket = client.connect_client()
        network_status = "Connected to server"
    except Exception as e:
        network_status = f"Client error: {e}"

# wait on the initial menu until the user picks server or client mode
selecting = mode is None
while selecting:
    mouse_pos = pygame.mouse.get_pos()
    server_button.update(mouse_pos)
    client_button.update(mouse_pos)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if server_button.is_clicked(event):
            mode = 'server'
            network_status = 'Waiting for connection...'
            selecting = False
            mode_started = True
            threading.Thread(target=run_server_thread, daemon=True).start()

        if client_button.is_clicked(event):
            mode = 'client'
            network_status = 'Connecting to server...'
            selecting = False
            mode_started = True
            threading.Thread(target=run_client_thread, daemon=True).start()
# draw the initial mode selection screen
    screen.fill((125, 125, 125))
    prompt_surf = font.render("Select Mode:", True, (0, 0, 0))
    screen.blit(prompt_surf, (250, 150))
    server_button.draw(screen)
    client_button.draw(screen)
    pygame.display.flip()

# if mode was passed by args, start the selected network thread automatically
if not mode_started and mode == 'server':
    network_status = 'Waiting for connection...'
    threading.Thread(target=run_server_thread, daemon=True).start()
elif not mode_started and mode == 'client':
    network_status = 'Connecting to server...'
    threading.Thread(target=run_client_thread, daemon=True).start()

print(f"Mode selected: {mode}")
# start background listener thread for incoming network messages
threading.Thread(target=listen_for_messages, daemon=True).start()



# start the main pygame game loop for event handling and drawing
running = True
ui_state = ui.UI(screen)
if mode == 'client':
    ui_state.turn = 'enemy'
while running:
# process all pending input events each frame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            ui_state.toggleOrientation()
        ui_state.mouseClick(event)
    
# once ships are placed, send READY to the opponent
    if ui_state.ready and not player_ready:
        player_ready = True
        send_message("READY")
        network_status = "You are ready. Waiting for opponent..."


# start the game when both players have signaled readiness
    if player_ready and opponent_ready and not game_started:
        game_started = True
        if mode == 'server':
            ui_state.turn = 'player'
            network_status = "Game started. Your turn."
        else:
            ui_state.turn = 'enemy'
            network_status = "Game started. Waiting for server..."

# if player has fired this turn, send shot coordinates to opponent
    if game_started and ui_state.turn == 'player' and ui_state.shot_fired:
        row, col = ui_state.shot_coordinates
        send_message("SHOT", row=row, col=col)
        if row is not None and col is not None:
            network_status = f"Shot fired at {row}, {col}. Waiting for opponent..."
        else:
            network_status = "Shot missed"
        ui_state.shot_fired = False


# process any network messages received from the opponent
    for msg in incoming_messages[:]:
        if ui_state.game_over and msg.get("type") != "GAME_OVER":
            incoming_messages.remove(msg)
            continue
# opponent is ready to start the game
        if msg.get("type") == "READY":
            opponent_ready = True
            if player_ready and not game_started:
                game_started = True
                if mode == 'server':
                    ui_state.turn = 'player'
                    network_status = "Game started. Your turn."
                else:
                    ui_state.turn = 'enemy'
                    network_status = "Game started. Waiting for server..."
# opponent fired at our board; update player board state
        elif msg.get("type") == "SHOT":
            row, col = msg.get("row"), msg.get("col")
            if row is None or col is None or not (0 <= row < ui_state.rows and 0 <= col < ui_state.cols):
                send_message("RESULT", row=row, col=col, result="MISS")
            elif ui_state.player_board[row][col] == ui_state.SHIP:
                ui_state.updateCell("player", row, col, ui_state.HIT)
                sunk_ship = ui_state.register_hit(row, col)
                if sunk_ship:
                    border_cells = ui_state.surrounding_cells(sunk_ship["cells"])
                    for b_row, b_col in border_cells:
                        if ui_state.player_board[b_row][b_col] == ui_state.EMPTY:
                            ui_state.updateCell("player", b_row, b_col, ui_state.MISS)
                    network_status = f"Your {sunk_ship['name']} was sunk!"
                    send_message(
                        "RESULT",
                        row=row,
                        col=col,
                        result="SUNK",
                        ship_name=sunk_ship["name"],
                        ship_cells=sunk_ship["cells"],
                        border_cells=border_cells,
                    )
                    if ui_state.all_ships_sunk():
                        network_status = "All your ships are sunk! You lose!"
                        ui_state.game_over = True
                        ui_state.winner_text = "YOU LOSE!"
                        ui_state.lock_input = True
                        game_started = False
                        send_message("GAME_OVER", result="LOSE")
                    else:
                        ui_state.turn = "enemy"
                        ui_state.lock_input = True
                else:
                    send_message("RESULT", row=row, col=col, result="HIT")
                    ui_state.turn = "enemy"
                    ui_state.lock_input = True
            else:
                ui_state.updateCell("player", row, col, ui_state.MISS)
                send_message("RESULT", row=row, col=col, result="MISS")
                ui_state.turn = "player"
                ui_state.lock_input = False
# handle the opponent's result for the shot we fired
        elif msg.get("type") == "RESULT":
            row, col, result = msg.get("row"), msg.get("col"), msg.get("result")
            if result == "HIT":
                ui_state.updateCell("enemy", row, col, ui_state.HIT)
                ui_state.totalhits += 1
                ui_state.turn = "player"
            elif result == "SUNK":
                if row is not None and col is not None:
                    ui_state.updateCell("enemy", row, col, ui_state.HIT)
                ship_cells = msg.get("ship_cells") or []
                for cell in ship_cells:
                    if not cell or len(cell) != 2:
                        continue
                    s_row, s_col = cell
                    ui_state.updateCell("enemy", s_row, s_col, ui_state.HIT)
                border_cells = msg.get("border_cells") or []
                for cell in border_cells:
                    if not cell or len(cell) != 2:
                        continue
                    b_row, b_col = cell
                    if ui_state.enemy_board[b_row][b_col] == ui_state.EMPTY:
                        ui_state.updateCell("enemy", b_row, b_col, ui_state.MISS)
                ui_state.totalhits += 1
                network_status = f"You sunk the enemy's {msg.get('ship_name')}!"
                ui_state.turn = "player"
            else:
                ui_state.updateCell("enemy", row, col, ui_state.MISS)
                ui_state.turn = "enemy"

# check win condition
            if ui_state.totalhits >= ui_state.totalcells:
                network_status = "All enemy ships sunk! You win!"
                ui_state.game_over = True
                ui_state.winner_text = "YOU WIN!"
                game_started = False
                send_message("GAME_OVER", result="WIN")
                ui_state.lock_input = True
            elif not ui_state.game_over:
                ui_state.lock_input = False
# handle the final game over message from the opponent
        elif msg.get("type") == "GAME_OVER":
            if not ui_state.game_over:
                if msg.get("result") == "WIN":
                    network_status = "YOU LOSE!"
                    ui_state.winner_text = "YOU LOSE!"
                elif msg.get("result") == "LOSE":
                    network_status = "YOU WIN!"
                    ui_state.winner_text = "YOU WIN!"
                ui_state.lock_input = True
                ui_state.game_over = True
                game_started = False
                
        incoming_messages.remove(msg)


        
# draw everything in 
# clear the screen with a gray background before drawing the game boards
    screen.fill((125, 125, 125))
    ui_state.updateStatusHeader()
    ui_state.drawGrids()
    
# display mode text and network status
    mode_text = font.render(f"Mode: {mode}", True, (0, 0, 0))
    screen.blit(mode_text, (50, 520))
    status_text = small_font.render(network_status, True, (0, 0, 0))
    screen.blit(status_text, (50, 560))

    pygame.display.flip()

# close pygame and exit cleanly when the game loop ends
pygame.quit()

