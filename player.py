from settings import *

from functions import importFolder
from tiles import Helicopter


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, facingRight = True):
        super().__init__()
        self.importCharacterAssets()
        self.frameIndex = 0
        self.animationSpeed = 0.10
        self.transparency = 0
        self.image = self.animations['idle'][self.frameIndex]
        self.rect = self.image.get_rect(topleft = pos)
        self.drawable = True

        # Sound Effects
        self.jumpSound = pygame.mixer.Sound('assets/sounds/effects/player/jump.mp3')
        self.landSound = pygame.mixer.Sound('assets/sounds/effects/player/land.mp3')
        self.damageTakenSound = pygame.mixer.Sound('assets/sounds/effects/player/damageTaken.wav')

        # Player movement
        self.collideableSprites = None
        self.onTopCollideableSprites = None
        self.direction = pygame.Vector2(0, 0)
        self.playerSpeed = 8
        self.playerGravity = 0.8
        self.playerJumpSpeed = -16
        self.hitbox = pygame.Rect(
            self.rect.topleft,
            (40, self.rect.height)
        )  # (pos, size)

        # Player status
        self.status = 'idle'
        self.controllability = True
        self.facingRight = facingRight
        self.passPlatforms = -1
        self.invulnerability = 0
        self.onGround = False

    def importCharacterAssets(self):
        charPath = 'assets/images/character/'
        self.animations = {
            'idle': [],
            'run': [],
            'jump': [],
            'fall': [],
        }

        for animation in self.animations.keys():
            fullPath = charPath + animation
            self.animations[animation] = importFolder(fullPath)

    def animate(self):
        animation = self.animations[self.status]

        # Loop Frame Index
        self.frameIndex += self.animationSpeed if self.status != 'run' else self.animationSpeed * 3
        if self.frameIndex >= len(animation):
            self.frameIndex = 0

        image = animation[int(self.frameIndex)]
        if self.facingRight:
            self.image = image
            self.rect.bottomleft = self.hitbox.bottomleft
        else:
            flippedImage = pygame.transform.flip(image, True, False)
            self.image = flippedImage
            self.rect.bottomright = self.hitbox.bottomright

        if self.transparency:
            self.image.set_alpha(255 - round(255 * self.transparency / 100))

        self.rect = self.image.get_rect(midbottom = self.rect.midbottom)

    def horizontalMovementCollision(self):
        self.hitbox.x += self.direction.x * self.playerSpeed

        for sprite in self.collideableSprites:
            if sprite.rect.colliderect(self.hitbox):
                if self.direction.x < 0:
                    self.hitbox.left = sprite.rect.right
                elif self.direction.x > 0:
                    self.hitbox.right = sprite.rect.left

    def verticalMovementCollision(self):
        self.applyGravity()

        for sprite in self.collideableSprites:
            if sprite.rect.colliderect(self.hitbox):
                if self.direction.y > 0:
                    self.hitbox.bottom = sprite.rect.top
                    self.direction.y = 0
                    if not self.onGround:
                        self.landSound.play()
                        self.onGround = True
                elif self.direction.y < 0:
                    self.hitbox.top = sprite.rect.bottom
                    self.direction.y = 0

        if self.onGround and self.direction.y < 0 or self.direction.y > self.playerGravity:
            self.onGround = False

    def onTopMovementCollision(self):
        for sprite in self.onTopCollideableSprites:
            if sprite.rect.colliderect(self.hitbox):
                if self.direction.y > 0 and sprite.rect.top >= self.oldRect.bottom:
                    if self.passPlatforms < 1:
                        self.hitbox.bottom = sprite.rect.top
                        self.direction.y = 0
                        self.onGround = True
            if isinstance(sprite, Helicopter) and self.passPlatforms < 1:
                bottomRect = pygame.Rect(self.hitbox.bottomleft, (self.hitbox.width, 2))
                if sprite.rect.colliderect(bottomRect) and self.hitbox.bottom >= sprite.rect.top >= self.oldRect.bottom - sprite.speed:
                    self.hitbox.bottom = sprite.rect.top
                    self.hitbox.topleft += sprite.direction * sprite.speed
                    if sprite.directionType == 'vertical' and (sprite.endPos[1] - sprite.rect.bottom < 16 or sprite.rect.top - sprite.startPos[1] < 16):
                        self.playerOnGround = True

    def applyGravity(self):
        self.direction.y += self.playerGravity
        self.hitbox.y += self.direction.y

    def jump(self):
        self.direction.y = self.playerJumpSpeed
        self.jumpSound.play()

    def applyDamage(self):
        if self.invulnerability <= 0:
            self.invulnerability = 20  # Invulnerability for some time
            self.passPlatforms = 1  # Balance loss on Saw Impact
            self.damageTakenSound.play()

    def hitAnimation(self):
        if self.invulnerability > 0:
            self.transparency = self.invulnerability * 4
            self.invulnerability -= 1

    def getInput(self):
        if self.controllability:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_d]:
                self.direction.x = 1
                self.facingRight = True
            elif keys[pygame.K_a]:
                self.direction.x = -1
                self.facingRight = False
            else:
                self.direction.x = 0

            if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.onGround:
                self.jump()

            if keys[pygame.K_s] and self.passPlatforms == -1:
                self.passPlatforms = 16  # Interval when Player will pass through platforms
            elif keys[pygame.K_s] and self.passPlatforms > 0:
                self.passPlatforms -= 1
            elif not keys[pygame.K_s] and self.invulnerability < 10:  # Balance loss on Saw Impact
                self.passPlatforms = -1
        else:
            self.direction.x = 0

    def getStatus(self):
        if self.direction.y < 0:
            self.status = 'jump'
        elif self.direction.y > self.playerGravity:
            self.status = 'fall'
        else:
            if self.direction.x != 0:
                self.status = 'run'
            else:
                self.status = 'idle'

    def update(self):
        self.getInput()
        self.getStatus()
        self.animate()
        self.hitAnimation()
        self.oldRect = self.hitbox.copy()
        self.horizontalMovementCollision()
        self.verticalMovementCollision()
        self.onTopMovementCollision()