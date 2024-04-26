from settings import *

from functions import importFolder


class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, drawable = True):
        super().__init__()
        self.image = pygame.Surface((tileSize, tileSize))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.drawable = drawable


class StaticTile(Tile):
    def __init__(self, x, y, surface, val = False):
        super().__init__(x, y)
        self.image = surface
        self.val = val


class StaticObject(StaticTile):
    def __init__(self, x, y, fileName):
        super().__init__(x, y, pygame.image.load('assets/images/tilesets/objects/' + str(fileName) + '.png').convert_alpha())
        offsetY = y + tileSize
        self.rect = self.image.get_rect(bottomleft = (x, offsetY))

    def trim(self, start, width):
        self.rect.left += start
        self.rect.width = width
        self.image = self.image.subsurface(start, 0, width, self.image.get_height())


class AnimatedTile(Tile):
    def __init__(self, x, y, path):
        super().__init__(x, y)
        self.animationSpeed = 0.15
        self.frames = importFolder('assets/images/tilesets/animatedObjects/' + str(path))
        self.frameIndex = 0
        self.image = self.frames[self.frameIndex]

    def animate(self):
        self.frameIndex += self.animationSpeed
        if self.frameIndex >= len(self.frames):
            self.frameIndex = 0
        self.image = self.frames[int(self.frameIndex)]

    def update(self):
        self.animate()


class Alarm(AnimatedTile):
    def __init__(self, x, y, path):
        super().__init__(x, y, path)
        self.animationSpeed = 0.25
        centerX = x + int(tileSize / 2)
        centerY = y + int(tileSize / 2)
        self.rect = self.image.get_rect(center = (centerX, centerY))