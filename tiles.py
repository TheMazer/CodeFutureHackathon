from settings import *

import random
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


# Clouds Preloading
cloudImages = []
for i in range(1, 5):
    cloudImages.append(pygame.image.load('assets/images/background/clouds/' + str(i) + '.png'))


class Cloud(StaticTile):
    def __init__(self, x, y, resetX, movingSpeed = 10):
        super().__init__(x, y, random.choice(cloudImages).convert_alpha())
        self.rect = self.image.get_rect(topleft=(x, y))
        self.resetX = resetX
        self.movingSpeed = movingSpeed
        self.movingTimer = 0

    def move(self):
        if self.movingTimer >= self.movingSpeed:
            self.rect.x += 1
            self.movingTimer = 0
        else:
            self.movingTimer += 1


class EnergyExplosion(AnimatedTile):
    def __init__(self, x, y):
        super().__init__(x, y, 'energyExplosion')
        self.animationSpeed = 0.5
        centerX = x + int(tileSize)
        centerY = y + int(tileSize)
        self.rect = self.image.get_rect(center=(centerX, centerY))
        self.blendMode = pygame.BLEND_RGBA_ADD
        self.drawable = False
        self.stage = 0

        self.sound = pygame.mixer.Sound('assets/sounds/effects/Shock.wav')

    def activate(self, volume, destructMethod):
        self.drawable = True
        self.stage = 1  # Start Explosion

        # Object Destruction
        self.destruct = destructMethod

        # Sound Effect
        self.sound.set_volume(volume / 100 * 0.5)
        self.sound.play()

    def animate(self):
        if self.stage == 1:  # Check if Explosion running
            self.frameIndex += self.animationSpeed
            if self.frameIndex >= len(self.frames):
                self.drawable = False
                self.stage = 2  # Explosion Completed
                self.frameIndex = 0
                self.destruct()
            self.image = self.frames[int(self.frameIndex)]


class FenceGateController(StaticObject):
    def __init__(self, x, y):
        super().__init__(x, y, '../animatedObjects/fenceGateOutline/black')
        self.outlines = importFolder('assets/images/tilesets/animatedObjects/fenceGateOutline')
        self.highlighted = 0
        self.isBackground = True
        self.val = 'FenceGate'

    def changeOutline(self, type = None):
        if type is not None: self.highlighted = type
        else: self.highlighted = not self.highlighted
        self.image = self.outlines[0] if not self.highlighted else self.outlines[1]


class Alarm(AnimatedTile):
    def __init__(self, x, y, path):
        super().__init__(x, y, path)
        self.animationSpeed = 0.25
        centerX = x + int(tileSize / 2)
        centerY = y + int(tileSize / 2)
        self.rect = self.image.get_rect(center = (centerX, centerY))