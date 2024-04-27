from settings import *


class CameraGroup(pygame.sprite.Group):
    def __init__(self, levelClass):
        super().__init__()
        self.displaySurface = pygame.display.get_surface()
        self.levelClass = levelClass

        # Camera Offset
        self.graduallyOffset = pygame.Vector2(0, 0)
        self.offset = pygame.Vector2(0, 0)

    def render(self):
        # Cleaning Display
        self.displaySurface.fill('Black')

        # Calculating Offset
        player = self.levelClass.player.sprite
        target_offset = pygame.Vector2(player.hitbox.center) - pygame.Vector2(screenSize) / 2 - pygame.Vector2(0, 150)
        self.graduallyOffset += round((target_offset - self.graduallyOffset) * 0.05)
        self.offset = self.graduallyOffset

        # Tiles will Draw only if colliding this Rect
        cameraViewRect = pygame.Rect(self.offset, screenSize)

        for sprite in self.sprites():
            sprite.update()

            offsetPos = sprite.rect.topleft - self.offset
            if sprite.drawable and sprite.rect.colliderect(cameraViewRect):
                self.displaySurface.blit(sprite.image, offsetPos)