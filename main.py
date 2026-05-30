import pygame
import ships as ships_module
import ui

print("test")
print("testtesttest")
print("mohammad123")

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Battleship")
font = pygame.font.Font(None, 36)

# Create buttons for mode selection
server_button = ui.Button(150, 250, 150, 50, "SERVER", font)
client_button = ui.Button(500, 250, 150, 50, "CLIENT", font)

mode = None
network_module = None

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
            selecting = False
        if client_button.is_clicked(event):
            mode = 'client'
            selecting = False

    screen.fill((125, 125, 125))
    prompt_surf = font.render("Select Mode:", True, (0, 0, 0))
    screen.blit(prompt_surf, (250, 150))
    server_button.draw(screen)
    client_button.draw(screen)
    pygame.display.flip()

# Import appropriate module after mode is selected
if mode == 'server':
    import server as network_module
else:
    import client as network_module

print(f"Mode selected: {mode}")

ships = {"Aircraft_Carrier": ships_module.ship("Aircraft Carrier", 5), 
         "Battle_ship": ships_module.ship("Battleship", 4),
         "Submarine": ships_module.ship("Submarine", 3),
         "Destroyer": ships_module.ship("Destroyer", 3),
         "Patrol_Boat": ships_module.ship("Patrol Boat", 2)}

# main game loop
running = True
ui_state = ui.UI(screen)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            ui_state.toggleOrientation()
        ui_state.mouseClick(event)
    
    # draw stuff here
    screen.fill((125, 125, 125))  # background color
    ui_state.updateStatusHeader()
    ui_state.drawGrids()
    
    # display mode text
    mode_text = font.render(f"Mode: {mode}", True, (0, 0, 0))
    screen.blit(mode_text, (50, 520))

    pygame.display.flip()

pygame.quit()

