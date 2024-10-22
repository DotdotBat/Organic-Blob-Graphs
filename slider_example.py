import pygame_widgets
import pygame
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox

pygame.init()
win = pygame.display.set_mode((1000, 600))

slider = Slider(win, 100, 100, 800, 20, min=0, max=255, step=1)
sliderY = Slider(win, 100, 200, 800, 20, min=0, max=255, step=1, color = (0,100, 255))

output = TextBox(win, 475, 200, 65, 50, fontSize=30)

output.disable()  # Act as label instead of textbox

run = True
while run:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            run = False
            quit()

    win.fill((255, 255, 255))
    pygame.draw.rect(win, (slider.getValue(), sliderY.getValue(), 0), (slider.getValue(), sliderY.getValue(), 50, 60))

    output.setText(slider.getValue())

    pygame_widgets.update(events)
    pygame.display.update()