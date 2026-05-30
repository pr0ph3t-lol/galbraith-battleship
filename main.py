import pygame
import network
import ships
import ui

print("test")
print("testtesttest")
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
    screen.fill((0, 0, 255))  # background color
    pygame.display.flip()

pygame.quit()

