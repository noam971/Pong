import pygame

WHITE = (255, 255, 255)


class Paddle:
    VEL = 4
    WIDTH = 20
    HEIGHT = 100
    COLOR = WHITE

    def __init__(self, x, y):
        self.x = x
        self.y = self.original_y = y


    def draw(self, win):
        pygame.draw.rect(win, self.COLOR, (self.x, self.y, self.WIDTH, self.HEIGHT))

    def move(self, up=False):
        if up:
            self.y -= self.VEL
        else:
            self.y += self.VEL

    def reset(self):
        self.y = self.original_y
