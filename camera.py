from settings import *

import random, time
from tiles import Cloud
from interactive import TimeTravelButton
from functions import importCutGraphics


class CameraGroup(pygame.sprite.Group):
    def __init__(self, levelClass):
        super().__init__()
        self.displaySurface = pygame.display.get_surface()
        self.levelClass = levelClass

        # Camera Offset
        self.graduallyOffset = pygame.Vector2(0, 0)
        self.offset = pygame.Vector2(0, 0)

        # Camera Borders
        self.useCameraConstraints = levelClass.levelParameters.get('useCameraConstraints', True)
        self.cameraBorders = {
            'left': 0,
            'right': levelClass.levelSize[0] * tileSize - screenSize[0],
            'bottom': levelClass.levelSize[1] * tileSize - screenSize[1],
            'top': 0
        }

        # Effects Setup
        self.flashingSurf = pygame.Surface(screenSize, pygame.SRCALPHA)
        self.fadingSurf = pygame.Surface(screenSize, pygame.SRCALPHA)
        self.fadeImage = None
        self.guiParticles = []
        self.foundItemAnimations = []

        # Boosts Display
        self.boostsIcons = importCutGraphics('assets/images/tilesets/bonuses.png')
        self.boostsColors = ('#78d800', '#f3cb1e', '#b6cef0')

        # Background
        self.backgroundSurface = pygame.Surface((levelClass.levelSize[0] * tileSize, levelClass.levelSize[1] * tileSize))

        # Clouds
        self.clouds = []; levelSize = self.levelClass.levelSize
        customClouds = levelClass.customCloudsPath if levelClass.customCloudsPath else None
        for i in range(
                round((levelSize[0] * tileSize / screenSize[0]) * (levelSize[1] * tileSize / screenSize[1]) * 4)):
            self.clouds.append(Cloud(
                x=random.randint(0, levelSize[0] * tileSize),
                y=random.randint(0, levelSize[1] * tileSize),
                resetX=levelSize[0] * tileSize,
                movingSpeed=random.randint(1, 3),
                cloudSurfaces=customClouds
            ))

        # Time Travel Button & Gui
        self.travelBtn = TimeTravelButton(self.displaySurface, levelClass.inPast, int(levelClass.config.get('interfaceVolume', 'Settings')))
        self.objectivesTitle = pygame.image.load('assets/images/gui/objectivesTitle.png').convert()
        self.timeTravelSound = pygame.mixer.Sound('assets/sounds/effects/TimeTravel.wav')
        self.timeTravelSound.set_volume(int(levelClass.config.get('effectsVolume', 'Settings')) / 100)

    def render(self):
        # Cleaning Display
        self.displaySurface.fill('Black')

        # Calculating Offset
        player = self.levelClass.player.sprite
        target_offset = pygame.Vector2(player.hitbox.center) - pygame.Vector2(screenSize) / 2 - pygame.Vector2(0, 150)
        self.graduallyOffset += round((target_offset - self.graduallyOffset) * 0.05)
        self.offset = self.graduallyOffset

        # Constraint Camera to level Size
        if self.useCameraConstraints:
            self.offset.x = self.offset.x if self.offset.x > self.cameraBorders['left'] else self.cameraBorders['left']
            self.offset.x = self.offset.x if self.offset.x < self.cameraBorders['right'] else self.cameraBorders['right']
            self.offset.y = self.offset.y if self.offset.y < self.cameraBorders['bottom'] else self.cameraBorders['bottom']
            self.offset.y = self.offset.y if self.offset.y > self.cameraBorders['top'] else self.cameraBorders['top']

        # Applying Screenshake
        screenshake = round(self.levelClass.screenshake)
        self.offset = self.offset + pygame.Vector2(random.randint(-screenshake, screenshake), random.randint(-screenshake, screenshake))

        # Tiles will Draw only if colliding this Rect
        cameraViewRect = pygame.Rect(self.offset, screenSize)

        # Background
        bgImage = self.levelClass.bgImage
        if bgImage is not None:
            # Adding Background Images on Background Surface with Parallax Effect
            for mosaicX in range(self.levelClass.levelSize[0] * tileSize // bgImage.get_width()):
                for mosaicY in range(self.levelClass.levelSize[1] * tileSize // bgImage.get_height() + 1):
                    dest = (self.offset.x / 2 + mosaicX * bgImage.get_width(),
                            self.offset.y / 2 + mosaicY * bgImage.get_height())
                    # Checking if Background in Camera's View
                    if pygame.Rect(dest[0], dest[1], bgImage.get_width(), bgImage.get_height()).colliderect(cameraViewRect):
                        self.backgroundSurface.blit(bgImage, dest)

            # Clouds Drawing and Moving
            for cloud in self.clouds:
                cloud.move()  # Move Cloud
                cloudRect = cloud.rect.copy()
                cloudRect.topleft -= self.offset / 10
                if cloudRect.colliderect(cameraViewRect):  # Draw only those Clouds that are in Camera View
                    self.backgroundSurface.blit(cloud.image, (cloud.rect.x, cloud.rect.y) - self.offset / 10)
                if cloudRect.left >= cloud.resetX:  # If Cloud reached end of level
                    cloud.rect.right = 0

            # Drawing Background
            self.displaySurface.blit(self.backgroundSurface.subsurface((0, 0,
                min(self.levelClass.levelSize[0] * tileSize, self.backgroundSurface.get_width()),
                min(self.levelClass.levelSize[1] * tileSize, self.backgroundSurface.get_height())
                )), -self.offset
            )

        # Drawing Sprites
        for sprite in self.sprites():
            sprite.update()

            offsetPos = sprite.rect.topleft - self.offset
            if sprite.drawable and sprite.rect.colliderect(cameraViewRect):
                blendMode = sprite.blendMode if hasattr(sprite, 'blendMode') else 0
                self.displaySurface.blit(sprite.image, offsetPos, special_flags = blendMode)

        # Drawing Balloon Messages
        balloonMessages = self.levelClass.balloonMessages
        for message in balloonMessages:
            if message.done:
                balloonMessages.remove(message)
            else:
                message.draw(self.displaySurface, self.offset)

        # Hints
        for hint in self.levelClass.hints:
            hint.draw(self.displaySurface, self.offset)

        # Boosts Display
        timers = []
        if player.jumpBoost[1] is not None:
            timeLeft = player.jumpBoost[1] - time.time()
            timeLeftFormatted = f"{int(timeLeft // 60):02d}:{int(timeLeft % 60):02d}"
            timers.append((0, timeLeftFormatted))
        if player.speedBoost[1] is not None:
            timeLeft = player.speedBoost[1] - time.time()
            timeLeftFormatted = f"{int(timeLeft // 60):02d}:{int(timeLeft % 60):02d}"
            timers.append((1, timeLeftFormatted))
        if player.invincibility[1] is not None:
            timeLeft = player.invincibility[1] - time.time()
            timeLeftFormatted = f"{int(timeLeft // 60):02d}:{int(timeLeft % 60):02d}"
            timers.append((2, timeLeftFormatted))

        for i, timer in enumerate(timers):
            pos = pygame.Vector2(64, screenSize[1] - 64)
            icon = self.boostsIcons[timer[0]]
            # noinspection PyTypeChecker
            clockSnip = bigFont.render(timer[1], False, self.boostsColors[timer[0]])
            clockShadow = bigFont.render(timer[1], False, '#666666')

            self.displaySurface.blit(icon, pos + (0, -icon.get_height() - 64 * i))
            self.displaySurface.blit(clockShadow, pos + (icon.get_width() + 8 + 3, -icon.get_height() - 64 * i + icon.get_height() / 2 - clockSnip.get_height() / 2 + 3))
            self.displaySurface.blit(clockSnip, pos + (icon.get_width() + 8, -icon.get_height() - 64 * i + icon.get_height() / 2 - clockSnip.get_height() / 2))

        # Objectives
        objectives = self.levelClass.objectives
        if objectives:
            maxWidth = 0
            for id, objective in enumerate(objectives):
                objective.draw(self.displaySurface, id)
                maxWidth = max(objective.maxWidth, maxWidth)

            self.displaySurface.blit(self.objectivesTitle, (screenSize[0] - maxWidth - 70, 24))

        # Time Travel Button
        playerControllability = self.levelClass.player.sprite.controllability
        hasTimeMachine = self.levelClass.hasTimeMachine
        if playerControllability and hasTimeMachine:
            if self.travelBtn.checkClick():
                inPast = self.levelClass.timeTravel()
                self.travelBtn.hovered = False
                self.timeTravelSound.play()
                if inPast:
                    self.travelBtn.changeText('В будущее')
                    self.travelBtn.btnSprite = self.travelBtn.pastSprite
                else:
                    self.travelBtn.changeText('В прошлое')
                    self.travelBtn.btnSprite = self.travelBtn.futureSprite

        if hasTimeMachine:
            self.travelBtn.draw()

        # Effects Rendering
        # Flashing
        flashing = self.levelClass.flashing
        if flashing:
            self.flashingSurf.fill((255, 255, 255, min(flashing / 100 * 255, 255)))
            self.displaySurface.blit(self.flashingSurf, (0, 0))

        # Gui Particles Processing
        for particleSource in self.guiParticles:
            particleSource.update(pygame.Vector2(0, 0))

        # Processing Phone Calls
        phoneCalls = self.levelClass.phoneCalls
        if phoneCalls:
            phoneCall = phoneCalls[0]  # First Phone Call
            if phoneCall.done: phoneCalls.remove(phoneCalls[0])
            else: phoneCall.draw(self.displaySurface)

        # Found Item Animations Processing
        for foundItemAnimation in self.foundItemAnimations:
            foundItemAnimation.draw(self.displaySurface)
            if foundItemAnimation.frame > 360:
                self.foundItemAnimations.remove(foundItemAnimation)

        # Fading
        fading = self.levelClass.fading['current']
        if fading:
            self.fadingSurf.fill((0, 0, 0, min(fading / 100 * 255, 255)))
            self.displaySurface.blit(self.fadingSurf, (0, 0))

        # Fade Image
        if self.fadeImage is not None:
            self.displaySurface.blit(self.fadeImage, (
                screenSize[0] / 2 - self.fadeImage.get_width() / 2,
                screenSize[1] / 2 - self.fadeImage.get_height() / 2
            ))

        # Transition
        transition = self.levelClass.transition
        if transition:
            transitionSurf = pygame.Surface(screenSize)
            pygame.draw.circle(transitionSurf, (255, 255, 255), (screenSize[0] // 2, screenSize[1] // 2), (60 - abs(transition)) * 32)
            transitionSurf.set_colorkey((255, 255, 255))
            self.displaySurface.blit(transitionSurf, (0, 0))