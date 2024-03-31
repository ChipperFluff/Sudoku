import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600

# Create the screen object
screen = pygame.display.set_mode((screen_width, screen_height))

# Title and Icon
pygame.display.set_caption("Pygame Adventure")
icon = pygame.image.load('resources/imgs/icon.png')  # Add your own path to an icon image
pygame.display.set_icon(icon)

# Game loop
running = T
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Screen background color
    screen.fill((0, 0, 0))  # Black background
    
    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()
sys.exit()
