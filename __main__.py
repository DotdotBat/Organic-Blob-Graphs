import simulation
import pygame
import draw as draw_module
from draw import draw
import state

def main():
    pygame.init()
    draw_module.screen = pygame.display.set_mode((state.width, state.height))
    clock = pygame.time.Clock()
    running = True
    dt = 0

    simulation.setup()
    
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        simulation.simulate(dt)
        draw()
        #wrap up
        pygame.display.flip()
        dt = clock.tick(60) / 1000

    pygame.quit()

if __name__ == "__main__":
    main()



