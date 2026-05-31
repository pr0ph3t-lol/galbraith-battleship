import pygame
import ships as ships_module
import ui
import threading
import json
import time

print("test")
print("testtesttest")
print("mohammad123")

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Battleship") 

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Create buttons for mode selection
server_button = ui.Button(150, 250, 150, 50, "SERVER", font)
client_button = ui.Button(500, 250, 150, 50, "CLIENT", font)

mode = None
network_status = ""
network_socket = None
player_ready = False
opponent_ready = False
game_started = False
incoming_messages = []

def send_message(msg_type, **kwargs): ##sends whether it is a shot or return
    global network_socket
    try:
        if network_socket:
            message = {"type": msg_type, **kwargs}
            network_socket.send(json.dumps(message).encode())
    except Exception:
        pass

def listen_for_messages():
    global opponent_ready, incoming_messages, network_status
    while True:

        try:
            if network_socket:
                data = network_socket.recv(1024)
                if not data:
                    continue
                msg = json.loads(data.decode())
                incoming_messages.append(msg)
                if msg.get("type") == "READY":
                    opponent_ready = True
                    network_status = "Other player ready"
                if msg.get("type") == "SHOT":
                    network_status = f"Shot recieved at {msg.get('x')}, {msg.get('y')}"
                
        except Exception:
            pass
        time.sleep(0.1)

def run_server_thread():
    global network_socket, network_status
    try:
        import server
        conn, addr = server.start_server()
        network_socket = conn
        network_status = f"Connected by {addr[0]}:{addr[1]}"
    except Exception as e:
        network_status = f"Server error: {e}"

def run_client_thread():
    global network_socket, network_status
    try:
        import client
        network_status = "Connecting..."
        network_socket = client.connect_client()
        network_status = "Connected to server"
    except Exception as e:
        network_status = f"Client error: {e}"

# Wait for button click to select mode
selecting = True
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
            threading.Thread(target=run_server_thread, daemon=True).start()

        if client_button.is_clicked(event):
            mode = 'client'
            network_status = 'Connecting to server...'
            selecting = False
            threading.Thread(target=run_client_thread, daemon=True).start()
    screen.fill((125, 125, 125))
    prompt_surf = font.render("Select Mode:", True, (0, 0, 0))
    screen.blit(prompt_surf, (250, 150))
    server_button.draw(screen)
    client_button.draw(screen)
    pygame.display.flip()

print(f"Mode selected: {mode}")
threading.Thread(target=listen_for_messages, daemon=True).start()



# main game loop
running = True
ui_state = ui.UI(screen)
if mode == 'client':
    ui_state.turn = 'enemy'
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            ui_state.toggleOrientation()
        ui_state.mouseClick(event)
    
    if ui_state.ready and not player_ready:
        player_ready = True
        send_message("READY")
        network_status = "You are ready. Waiting for opponent..."


    if player_ready and opponent_ready and not game_started:
        game_started = True
        if mode == 'server':
            ui_state.turn = 'player'
            network_status = "Game started. Your turn."
        else:
            ui_state.turn = 'enemy'
            network_status = "Game started. Waiting for server..."

    if game_started and ui_state.turn == 'player' and ui_state.shot_fired:
        row, col = ui_state.shot_coordinates
        send_message("SHOT", row=row, col=col)
        network_status = f"Shot fired at {row}, {col}. Waiting for opponent..."
        ui_state.shot_fired = False
        ui_state.turn = 'enemy'


    for msg in incoming_messages[:]:
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
        elif msg.get("type") == "SHOT":
            row, col = msg.get("row"), msg.get("col")
            if ui_state.player_board[row][col] == ui_state.SHIP:
                ui_state.updateCell("player", row, col, ui_state.HIT)
                send_message("RESULT", row=row, col=col, result="HIT")
            else:
                ui_state.updateCell("player", row, col, ui_state.MISS)
                send_message("RESULT", row=row, col=col, result="MISS")
            ui_state.turn = "player"
            ui_state.lock_input = False
        elif msg.get("type") == "RESULT":
            row, col, result = msg.get("row"), msg.get("col"), msg.get("result")
            if msg.get("result") == "HIT":
                ui_state.updateCell("enemy", row, col, ui_state.HIT)
            else:
                ui_state.updateCell("enemy", row, col, ui_state.MISS)
            ui_state.turn = "enemy"
            ui_state.lock_input = False
        incoming_messages.remove(msg)


    # draw stuff here
    screen.fill((125, 125, 125))  # background color
    ui_state.updateStatusHeader()
    ui_state.drawGrids()
    
    # display mode text and network status
    mode_text = font.render(f"Mode: {mode}", True, (0, 0, 0))
    screen.blit(mode_text, (50, 520))
    status_text = small_font.render(network_status, True, (0, 0, 0))
    screen.blit(status_text, (50, 560))

    pygame.display.flip()

pygame.quit()

