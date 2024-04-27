from settings import *

import threading
from functions import importFolder


class Npc(pygame.sprite.Sprite):
    def __init__(self, npc_type, pos, levelClass):
        super().__init__()
        self.npcType = npc_type
        self.pos = pos
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

        # Level Management
        self.switchPlayerControllability = levelClass.switchPlayerControllability
        self.createBalloonMessage = levelClass.createBalloonMessage

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
        self.storytelling()

    def storytelling(self):
        self.preparingDialogue()

    def preparingDialogue(self):
        self.createBalloonMessage(
            ['Вроде, всё готово, Алексей!', 'Я смогу переместится во временной петле прямо сегодня!'],
            self.pos, 3, voice='synth', callback=self.alexeyQuestion)

    def alexeyQuestion(self):
        self.createBalloonMessage(['Даже и не верится, а что вы там будите делать?'], 'player',
                                  callback=self.educationMethods)

    def educationMethods(self):
        self.createBalloonMessage(['Как что? Внедрю новые методы обучения и воспитания в первые кадетские корпуса!'],
                                  self.pos, voice='synth', callback=self.alexeyWantTogether)

    def alexeyWantTogether(self):
        self.createBalloonMessage(['Вау! А можно с вами?'], 'player', callback=self.declining)

    def declining(self):
        self.createBalloonMessage(['Нет, это слишком опасно!'], self.pos, 2, voice='synth', callback=self.alone)

    def alone(self):
        self.createBalloonMessage(['Лучше я пойду один...'], self.pos, 7, voice='synth', callback=self.alexeyAskingBack)

    def alexeyAskingBack(self):
        self.createBalloonMessage(['А вернуться вы сможете? Профессор?'], 'player', callback=self.calm)

    def calm(self):
        self.createBalloonMessage(['После перемещения, машина времени свяжется с моим портативным устройством.',
                                   'C его помощью, я смогу вернуться назад.'], self.pos, voice='synth',
                                  callback=self.goodLuck)

    def goodLuck(self):
        self.createBalloonMessage(['Удачи, профессор!'], 'player', callback=self.moving)

    def moving(self):
        self.switchPlayerControllability(False)
        self.facingRight = False
        pygame.mouse.set_visible(False)
        threading.Timer(0.5, self.moving2).start()

    def moving2(self):
        self.speed = -3
        threading.Timer(1, self.moving3).start()

    def moving3(self):
        self.speed = 0
        self.facingRight = True