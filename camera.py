from settings import *


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.displaySurface = pygame.display.get_surface()

        self.offset = pygame.Vector2(0, 0)

    def render(self):
        self.displaySurface.fill('Black')

        for sprite in self.sprites():
            sprite.update()

            offsetPos = sprite.rect.topleft - self.offset
            if sprite.drawable:
                self.displaySurface.blit(sprite.image, offsetPos)