import pygame
import sys

# Initialize the engine of your impending disappointment
pygame.init()

# Create a window, a canvas for your masterpiece of mediocrity
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Track the Mouse, If You Can")

# The main loop, a reflection of your life, going round and round
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Here comes the highlight of your day, tracking mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Congrats, you've achieved something! Here's your position
            position = pygame.mouse.get_pos()
            print(f"Look who managed to click a mouse: {position}")
            # And because you asked so nicely, let's throw in a bonus
            if event.button == 1:  # Left click, because right is just too mainstream for you
                print("Wow, you pressed the LEFT button, what an achievement!")

    # Fill your void with black, much like your coffee
    screen.fill((0, 0, 0))
    pygame.display.flip()
