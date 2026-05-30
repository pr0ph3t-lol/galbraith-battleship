import pygame
import network
import ships
import ui

print("test")
print("testtesttest")
ships = {"Aircraft_Carrier": ships.ship("Aircraft Carrier", 5), 
         "Battle_ship": ships.ship("Battleship", 4),
         "Submarine": ships.ship("Submarine", 3),
         "Destroyer": ships.ship("Destroyer", 3),
         "Patrol_Boat": ships.ship("Patrol Boat", 2)}

pygame.init()

screen = pygame.display.set_mode((800, 600))  # window size
pygame.display.set_caption("Battleship")

# main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # draw stuff here
    grid = ui.Grid(10, 10, 50, 50)
    grid.draw(screen)  # create a grid with 10 rows and 10 columns, each cell is 50x50 pixels
    screen.fill((255, 0, 0))  # background color
    pygame.display.flip()

pygame.quit()

