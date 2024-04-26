from settings import *


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