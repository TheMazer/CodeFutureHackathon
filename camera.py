from settings import *

import random
from interactive import mButton


class CameraGroup(pygame.sprite.Group):
    def __init__(self, levelClass):
        super().__init__()
        self.displaySurface = pygame.display.get_surface()
        self.levelClass = levelClass

        # Camera Offset
        self.graduallyOffset = pygame.Vector2(0, 0)
        self.offset = pygame.Vector2(0, 0)

        # Effects Setup
        self.flashingSurf = pygame.Surface(screenSize, pygame.SRCALPHA)
        self.fadingSurf = pygame.Surface(screenSize, pygame.SRCALPHA)
        self.fadeImage = None

        # Time Travel Button & Gui
        self.travelBtn = mButton('Time Travel', 900, self.displaySurface)

    def render(self):
        # Cleaning Display
        self.displaySurface.fill('Black')

        # Calculating Offset
        player = self.levelClass.player.sprite
        target_offset = pygame.Vector2(player.hitbox.center) - pygame.Vector2(screenSize) / 2 - pygame.Vector2(0, 150)
        self.graduallyOffset += round((target_offset - self.graduallyOffset) * 0.05)
        self.offset = self.graduallyOffset

        # Applying Screenshake
        screenshake = round(self.levelClass.screenshake)
        self.offset = self.offset + pygame.Vector2(random.randint(-screenshake, screenshake), random.randint(-screenshake, screenshake))

        # Tiles will Draw only if colliding this Rect
        cameraViewRect = pygame.Rect(self.offset, screenSize)

        # Drawing Sprites
        for sprite in self.sprites():
            sprite.update()

            offsetPos = sprite.rect.topleft - self.offset
            if sprite.drawable and sprite.rect.colliderect(cameraViewRect):
                self.displaySurface.blit(sprite.image, offsetPos)

        # Drawing Balloon Messages
        balloonMessages = self.levelClass.balloonMessages
        for message in balloonMessages:
            if message.done:
                balloonMessages.remove(message)
            else:
                message.draw(self.displaySurface, self.offset)

        # Time Travel Button
        playerControllability = self.levelClass.player.sprite.controllability
        hasTimeMachine = self.levelClass.hasTimeMachine
        if playerControllability and hasTimeMachine:
            if self.travelBtn.checkClick():
                inPast = self.levelClass.timeTravel()
                self.travelBtn.hovered = False

        if hasTimeMachine:
            self.travelBtn.draw()

        # Effects Rendering
        # Flashing
        flashing = self.levelClass.flashing
        if flashing:
            self.flashingSurf.fill((255, 255, 255, min(flashing / 100 * 255, 255)))
            self.displaySurface.blit(self.flashingSurf, (0, 0))

        # Fading
        fading = self.levelClass.fading['current']
        if fading:
            self.fadingSurf.fill((0, 0, 0, min(fading / 100 * 255, 255)))
            self.displaySurface.blit(self.fadingSurf, (0, 0))

        # Transition
        transition = self.levelClass.transition
        if transition:
            transitionSurf = pygame.Surface(screenSize)
            pygame.draw.circle(transitionSurf, (255, 255, 255), (screenSize[0] // 2, screenSize[1] // 2), (60 - abs(transition)) * 32)
            transitionSurf.set_colorkey((255, 255, 255))
            self.displaySurface.blit(transitionSurf, (0, 0))