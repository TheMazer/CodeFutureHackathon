from settings import *

import random, time
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


class Bonus(StaticTile):
    def __init__(self, x, y, surface, val, glowParticles):
        super().__init__(x, y, surface, val)
        self.rect.center = (x + tileSize / 2, y + tileSize / 2)
        self.glowParticles = glowParticles
        self.val = val
        self.up = True
        self.offsetY = 0
        self.y = y + tileSize / 2

    def collect(self, player):
        endTime = time.time() + 20 + 1
        if self.val == '0':
            player.jumpBoost = [1.5, endTime]
        elif self.val == '1':
            player.speedBoost = [1.5, endTime]
        elif self.val == '2':
            player.invincibility = [1, endTime]
        player.collectSound.play()
        self.glowParticles.kill()
        self.kill()

    def update(self):
        if self.up:
            self.offsetY += 0.25
            if self.offsetY >= 8:
                self.up = False
        else:
            self.offsetY -= 0.25
            if self.offsetY <= -8:
                self.up = True
        self.rect.centery = self.y + self.offsetY
        self.glowParticles.y = self.y + self.offsetY


class Platform(StaticTile):
    def __init__(self, x, y, surface):
        super().__init__(x, y, surface)
        self.rect = self.image.get_bounding_rect()
        self.rect.topleft = (x, y)


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


class Helicopter(AnimatedTile):
    def __init__(self, x, y, direction, distance, speed = 2, reverse = False):
        super().__init__(x, y, 'helicopter')
        self.startPos = (x, y)
        self.endPos = (x + distance, y + distance)
        self.direction = pygame.Vector2(1, 0) if direction == 'horizontal' else pygame.Vector2(0, 1)
        self.directionType = direction
        self.speed = speed
        if reverse:  # Reverse Start Position
            if self.directionType == 'horizontal':
                self.rect.right = self.endPos[0]
                self.reverseDirection()
            else:  # Vertical
                self.rect.bottom = self.endPos[1]
                self.reverseDirection()

    def reverseDirection(self):
        self.direction *= -1

    def update(self):
        self.animate()
        self.rect.topleft += self.direction * self.speed
        if self.directionType == 'horizontal':
            if self.rect.right > self.endPos[0] and self.direction.x == 1:
                self.rect.right = self.endPos[0]
                self.reverseDirection()
            elif self.rect.left < self.startPos[0] and self.direction.x == -1:
                self.rect.left = self.startPos[0]
                self.reverseDirection()
        else:
            if self.rect.bottom > self.endPos[1] and self.direction.y == 1:
                self.rect.bottom = self.endPos[1]
                self.reverseDirection()
            elif self.rect.top < self.startPos[1] and self.direction.y == -1:
                self.rect.top = self.startPos[1]
                self.reverseDirection()


class Saw(AnimatedTile):
    def __init__(self, x, y, direction, distance, speed = 3, reverse = False):
        super().__init__(x, y, 'saw')
        self.animationSpeed = 0.5
        self.frames.reverse()
        self.startPos = (x, y)
        self.endPos = (x + distance, y + distance)
        self.direction = pygame.Vector2(1, 0) if direction == 'horizontal' else pygame.Vector2(0, 1)
        self.directionType = direction
        self.speed = speed
        if reverse:  # Reverse Start Position
            if self.directionType == 'horizontal':
                self.rect.right = self.endPos[0]
                self.reverseDirection()
            else:  # Vertical
                self.rect.bottom = self.endPos[1]
                self.reverseDirection()

    def reverseDirection(self):
        self.direction *= -1

    def update(self):
        self.animate()
        self.rect.topleft += self.direction * self.speed
        if self.directionType == 'horizontal':
            if self.rect.right > self.endPos[0] and self.direction.x == 1:
                self.rect.right = self.endPos[0]
                self.reverseDirection()
            elif self.rect.left < self.startPos[0] and self.direction.x == -1:
                self.rect.left = self.startPos[0]
                self.reverseDirection()
        else:
            if self.rect.bottom > self.endPos[1] and self.direction.y == 1:
                self.rect.bottom = self.endPos[1]
                self.reverseDirection()
            elif self.rect.top < self.startPos[1] and self.direction.y == -1:
                self.rect.top = self.startPos[1]
                self.reverseDirection()


# Clouds Preloading
cloudImages = []
for i in range(1, 5):
    cloudImages.append(pygame.image.load('assets/images/background/clouds/' + str(i) + '.png'))


class Cloud(StaticTile):
    def __init__(self, x, y, resetX, movingSpeed = 10, cloudSurfaces = None):
        if not cloudSurfaces: cloudSurfaces = cloudImages
        super().__init__(x, y, random.choice(cloudSurfaces).convert_alpha())
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


class VerticalTrigger(Tile):
    def __init__(self, x, height, id):
        super().__init__(x, height, False)
        self.isBackground = True
        self.val = 'VerticalTrigger'
        self.id = id
        self.rect.y = 0
        self.rect.height = height
        # self.image = pygame.Surface((64, height))
        # self.image.fill('Red')


class MidDoor(AnimatedTile):
    def __init__(self, x, y):
        super().__init__(x, y, 'midDoor')
        self.rect = self.image.get_rect(topleft=(x, y))
        self.outlines = importFolder('assets/images/tilesets/animatedObjects/midDoorOutline')
        self.outline = self.outlines[0]
        self.highlighted = 0
        self.isBackground = True
        self.inPast = False
        self.stage = 0
        self.val = 'MidDoor'

    def changeOutline(self, type = None):
        if type is not None: self.highlighted = type
        else: self.highlighted = not self.highlighted
        self.outline = self.outlines[0] if not self.highlighted else self.outlines[1]

    def animate(self):
        self.frameIndex += self.animationSpeed
        if self.frameIndex >= len(self.frames):
            self.frameIndex = 0
        self.image = self.frames[int(self.frameIndex)]
        self.image.blit(self.outline, (0, 0))


class WasdGuide(StaticObject):
    def __init__(self, x, y):
        super().__init__(x, y, '189')
        self.image.set_alpha(0)
        self.appear = True
        self.frame = 0
        self.wait = 0

    def update(self):
        if self.wait <= 1000:
            self.wait += 1
        else:
            if self.appear:
                self.image.set_alpha(self.frame)
                self.frame += 2
                if self.frame >= 255:
                    self.appear = False
            else:
                self.image.set_alpha(self.frame)
                self.frame -= 2
                if self.frame <= 100:
                    self.appear = True


class Alarm(AnimatedTile):
    def __init__(self, x, y, path):
        super().__init__(x, y, path)
        self.animationSpeed = 0.25
        centerX = x + int(tileSize / 2)
        centerY = y + int(tileSize / 2)
        self.rect = self.image.get_rect(center = (centerX, centerY))