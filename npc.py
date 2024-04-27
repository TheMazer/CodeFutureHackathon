from settings import *

from functions import importFolder


class Npc(pygame.sprite.Sprite):
    def __init__(self, npc_type, pos, levelClass):
        super().__init__()
        self.npcType = npc_type
        self.importNpcAssets(self.npcType)
        self.frameIndex = 0
        self.animationSpeed = 0.15
        self.image = self.animations['idle'][self.frameIndex]
        self.rect = self.image.get_rect(topleft=pos)
        self.drawable = True

        # Npc Status
        self.status = 'idle'
        self.facingRight = True

        # Movement
        self.direction = pygame.Vector2(0, 0)
        self.speed = 4

    def importNpcAssets(self, npc_type):
        charPath = 'assets/images/npcs/' + npc_type + '/'
        self.animations = {
            'idle': [],
            'pointingRight': []
        }

        for animation in self.animations.keys():
            fullPath = charPath + animation
            self.animations[animation] = importFolder(fullPath)

    def move(self):
        self.rect.x += self.speed

    def animate(self):
        animation = self.animations[self.status]

        # Loop Frame Index
        self.frameIndex += self.animationSpeed
        if self.frameIndex >= len(animation):
            self.frameIndex = 0

        image = animation[int(self.frameIndex)]
        if self.facingRight:
            self.image = image
        else:
            flippedImage = pygame.transform.flip(image, True, False)
            self.image = flippedImage

        self.rect = self.image.get_rect(midbottom = self.rect.midbottom)

    def update(self):
        self.animate()
        self.move()


class Marcus(Npc):
    def __init__(self, pos, levelClass):
        super().__init__('Marcus', pos, levelClass)
        self.animationSpeed = 0.05
        self.speed = 0