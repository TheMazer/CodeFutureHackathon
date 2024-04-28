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
        self.setBackgroundMusic = levelClass.setBackgroundMusic
        self.playSound = levelClass.playSound
        self.switchPlayerControllability = levelClass.switchPlayerControllability
        self.switchTimeMachine = levelClass.switchTimeMachine
        self.screenShakeEffect = levelClass.screenShakeEffect
        self.screenFlashEffect = levelClass.screenFlashEffect
        self.screenFadeEffect = levelClass.screenFadeEffect
        self.changeFadeImage = levelClass.changeFadeImage
        self.startScriptedObject = levelClass.startScriptedObject
        self.triggerNpc = levelClass.triggerNpc
        self.createPhoneCall = levelClass.createPhoneCall
        self.addObjective = levelClass.addObjective
        self.completeObjective = levelClass.completeObjective
        self.createBalloonMessage = levelClass.createBalloonMessage
        self.createFoundItemAnimation = levelClass.createFoundItemAnimation
        self.timeTravel = levelClass.timeTravel

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

        self.gameLogo = pygame.image.load('assets/images/gui/logo.png').convert_alpha()

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
        self.setBackgroundMusic('assets/sounds/music/Danger.mp3', volume=1, loops = 0)
        self.screenShakeEffect(1, True)

        threading.Timer(5, self.screenShakeEffect, [3, True]).start()  # Screen Shake Start

        threading.Timer(12, self.energyExplosion, [5, 50]).start()  # Energy Explosion with Screen Effects
        threading.Timer(16, self.energyExplosion, [7, 70]).start()  # Energy Explosion with Screen Effects
        threading.Timer(23, self.energyExplosion, [10, 100]).start()  # Energy Explosion with Screen Effects

        threading.Timer(35, self.playSound, ['assets/sounds/effects/Whoosh Hit.wav', 0.5]).start()
        threading.Timer(36, self.storyBegin).start()

    def energyExplosion(self, shaking=None, flashing=None, destroy=None):
        self.startScriptedObject('EnergyExplosion', destroy)
        if shaking is not None: threading.Timer(0.2, self.screenShakeEffect, [shaking, True]).start()
        if flashing is not None: threading.Timer(0.2, self.screenFlashEffect, [flashing]).start()

    def setVisibility(self, visibility):
        self.drawable = visibility

    def storyBegin(self):
        pygame.mouse.set_visible(False)
        self.setBackgroundMusic('stop', fade=0.4)
        self.energyExplosion(15, 50, True)
        self.screenFadeEffect(0.2, 12, 3)
        threading.Timer(1, self.screenShakeEffect, [15, False]).start()
        threading.Timer(1, self.timeTravel, ['past']).start()
        threading.Timer(1, self.setVisibility, [False]).start()
        threading.Timer(4, self.changeFadeImage, [self.gameLogo]).start()
        threading.Timer(3.2, self.playSound, ['assets/sounds/effects/Whoosh Hit.wav', 0.5]).start()
        threading.Timer(10, self.changeFadeImage, [None]).start()
        threading.Timer(12.2, self.setBackgroundMusic, ['assets/sounds/music/Washy Noise.mp3', 0.5]).start()
        threading.Timer(13, self.createBalloonMessage, [['Профессор!?'], 'player', 10, (255, 50, 50)]).start()


class MarcusAtCorps(Npc):
    def __init__(self, pos, levelClass):
        super().__init__('Marcus', pos, levelClass)
        self.readyToCall = False
        self.timeCond = 'past'
        self.animationSpeed = 0.05
        self.speed = 0

        self.logo = pygame.image.load('assets/images/gui/logo.png')
        self.credits1 = pygame.image.load('assets/images/gui/credits1.png')
        self.credits2 = pygame.image.load('assets/images/gui/credits2.png')

    def storytelling(self):
        self.noticing()

    def noticing(self):
        self.createBalloonMessage(['...и тогда... !?'], self.pos, speed = 7, voice = 'synth', callback = self.surprising)
        self.completeObjective('Найти профессора')

    def surprising(self):
        self.facingRight = False
        self.createBalloonMessage(['Алексей!?', 'Ты что тут делаешь?'], self.pos, voice = 'synth', callback=self.uhm)

    def uhm(self):
        self.createBalloonMessage(['Эхм...'], self.pos, speed = 5, voice = 'synth', callback = self.presenting)

    def presenting(self):
        self.facingRight = True
        self.status = 'pointingRight'
        self.createBalloonMessage(['Это Алексей — мой помощник, вместе мы прибыли из будущего!'], self.pos, speed = 5, voice = 'synth', callback = self.ourMission)

    def ourMission(self):
        self.status = 'idle'
        self.createBalloonMessage(['И хотим улучшить методы обучения и воспитания в кадетских корпусах вашего времени!'],
            self.pos, speed = 5, voice = 'synth', callback = self.triggerHistoryTeacher)

    def triggerHistoryTeacher(self):
        self.triggerNpc('HistoryTeacher', 'storytelling', [self.justification])

    def justification(self):
        self.createBalloonMessage([
            'Тем не менее, у нас методы развиты также отлично!',
            'Почему бы не обменяться опытом и вспомнить историю кадетского образования?'
        ], self.pos, voice = 'synth', callback = self.triggerFranceTeacher)

    def triggerFranceTeacher(self):
        self.triggerNpc('FranceTeacher', 'storytelling')

    def portableTimeTravellingDevice(self):
        self.facingRight = False
        self.createBalloonMessage([
            'Алексей, можно тебе поручить задание?',
            'Возьми моё портативное устройство перемещения',
            'Оно позволит тебе путешествовать по временной линии.'
        ], self.pos, voice = 'synth', callback = self.givePTTDevice)

    def givePTTDevice(self):
        threading.Timer(6, self.quest).start()
        self.createFoundItemAnimation('PTTD', 'Портативная машина времени')
        self.switchPlayerControllability(False)

    def quest(self):
        self.createBalloonMessage([
            'Найди мою тетрадку с записями об основных нововведениях в истории кадетских корпусов.',
            'А мы ещё поговорим'
        ], self.pos, voice = 'synth', callback = self.givingQuest)

    def givingQuest(self):
        self.facingRight = True
        self.completeObjective('Понять, что произошло')
        self.addObjective('Найти Тетрадь профессора')
        threading.Timer(1, self.switchTimeMachine, [True, True]).start()
        self.readyToCall = True

    def phoneCall(self):
        threading.Timer(5, self.createPhoneCall, [[
            'И снова здравствуй, Алексей! Место, в котором ты находишься, называется Мидтайм, это межвременной карман, где временные потоки переплетаются.',
            'Тебе нужно найти дверь, ведущую в мой кабинет, чтобы найти тетрадь с важными записями. Будь осторожен!'
        ]], {'speed': 3, 'color': 'White', 'voice': 'synth', 'name': 'Профессор'}).start()
        self.readyToCall = False

    def questComplete(self):
        self.facingRight = False
        self.createBalloonMessage([
            'Ты справился, Алексей!',
            'А теперь нам предстоит ещё много работы!'
        ], self.pos, voice='synth', callback = self.finish)

    def finish(self):
        self.switchPlayerControllability(False)
        self.screenFadeEffect(3, 1000, 1)
        self.setBackgroundMusic('stop', fade = 3)
        pygame.mouse.set_visible(False)
        threading.Timer(3.2, self.playSound, ['assets/sounds/effects/Whoosh Hit.wav', 0.5]).start()
        threading.Timer(4, self.changeFadeImage, [self.logo]).start()
        threading.Timer(10, self.changeFadeImage, [self.credits1]).start()
        threading.Timer(20, self.changeFadeImage, [self.credits2]).start()
        threading.Timer(32, self.changeFadeImage, [None]).start()
        threading.Timer(40, self.startScriptedObject, ['QuitToMenu']).start()


class HistoryTeacher(Npc):
    def __init__(self, pos, levelClass):
        super().__init__('HistoryTeacher', pos, levelClass)
        self.callback = None
        self.facingRight = False
        self.timeCond = 'past'
        self.animationSpeed = 0.025
        self.speed = 0

    def storytelling(self, callback = None):
        self.callback = callback
        self.surprising()

    def surprising(self):
        self.createBalloonMessage([
            'Даже и не верится, у Алексея и правда интересная форма!'
        ], self.pos, voice = 'man', callback = self.ourMethods)

    def ourMethods(self):
        self.status = 'pointingRight'
        self.createBalloonMessage([
            'Но наши методы и так довольно хороши, они передаются из поколения в поколение!'
        ], self.pos, voice = 'man', callback = self.asking)

    def asking(self):
        self.status = 'idle'
        self.createBalloonMessage(['Зачем что-то менять?'], self.pos, voice = 'man', callback = self.callback)


class FranceTeacher(Npc):
    def __init__(self, pos, levelClass):
        super().__init__('FranceTeacher', pos, levelClass)
        self.facingRight = False
        self.timeCond = 'past'
        self.animationSpeed = 0.025
        self.speed = 0

    def storytelling(self):
        self.soundsGreat()

    def soundsGreat(self):
        self.createBalloonMessage(['Звучит отлично! Давайте же начнём нашу programme по обмену опыта!'], self.pos, voice = 'woman', callback = self.triggerProfessor)

    def triggerProfessor(self):
        self.triggerNpc('Marcus', 'portableTimeTravellingDevice')


class MathsTeacher(Npc):
    def __init__(self, pos, levelClass):
        super().__init__('MathsTeacher', pos, levelClass)
        self.facingRight = False
        self.timeCond = 'past'
        self.animationSpeed = 0.05
        self.speed = 0