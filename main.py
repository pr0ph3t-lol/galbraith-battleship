import pygame
import ships as ships_module
import ui

print("test")
print("testtesttest")
print("mohammad123")

# Ask user for mode
while True:
    mode = input("Choose mode (server/client): ").strip().lower()
    if mode in ('server', 'client'):
        break
    print("Invalid choice. Enter 'server' or 'client'")

# Import the appropriate module
if mode == 'server':
    import server as network_module
else:
    import client as network_module


ships = {"Aircraft_Carrier": ships_module.ship("Aircraft Carrier", 5), 
         "Battle_ship": ships_module.ship("Battleship", 4),
         "Submarine": ships_module.ship("Submarine", 3),
         "Destroyer": ships_module.ship("Destroyer", 3),
         "Patrol_Boat": ships_module.ship("Patrol Boat", 2)}

pygame.init()

screen = pygame.display.set_mode((800, 600))  # window size
pygame.display.set_caption("Battleship")
font = pygame.font.Font(None, 36)

# main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # draw stuff here
    grid = ui.Grid(10, 10, 50, 50)
    screen.fill((125, 125, 125))  # background color
    grid.draw(screen)  # create a grid with 10 rows and 10 columns, each cell is 50x50 pixels
    
    # display mode text
    mode_text = font.render(f"Mode: {mode}", True, (0, 0, 0))
    screen.blit(mode_text, (50, 520))

    pygame.display.flip()

pygame.quit()

