from settings import *

import math
import textwrap


class Button:
    def __init__(self, text, y, surface, interfaceVolume = 100, x=-1):
        self.pressed = False
        self.hovered = False

        self.y = y
        self.x = x
        self.surface = surface

        if self.x == -1:
            self.x = self.surface.get_width() / 2

        self.sprite = pygame.image.load('assets/images/gui/holoButton.png').convert_alpha()
        self.hoverSprite = pygame.image.load('assets/images/gui/holoButtonHover.png').convert_alpha()
        self.clickSprite = pygame.image.load('assets/images/gui/holoButtonPressed.png').convert_alpha()

        self.hoverSound = pygame.mixer.Sound('assets/sounds/gui/buttonHover.wav')
        self.releaseSound = pygame.mixer.Sound('assets/sounds/gui/buttonRelease.wav')
        self.interfaceVolume = interfaceVolume / 100

        self.btnSprite = self.sprite
        self.btnRect = pygame.Rect(
            (self.x - self.btnSprite.get_width() / 2, self.y),
            (self.btnSprite.get_width(), self.btnSprite.get_height())
        )

        self.textColor = 'White'
        self.textShadowColor = '#666666'
        self.text = text
        self.textRect = mainFont.render(self.text, False, self.textColor).get_rect(center=self.btnSprite.get_rect().center)

    def changeText(self, newText):
        self.text = newText
        self.textRect = mainFont.render(newText, False, self.textColor).get_rect(center=self.btnSprite.get_rect().center)

    def draw(self):
        self.surface.blit(self.btnSprite, self.btnRect)
        # self.surface.blit(self.surface, self.btnRect)
        self.surface.blit(mainFont.render(self.text, False, self.textShadowColor), (self.textRect.x + self.x - self.btnSprite.get_width() / 2 + 3, self.textRect.y + self.y + 3))
        self.surface.blit(mainFont.render(self.text, False, self.textColor), (self.textRect.x + self.x - self.btnSprite.get_width() / 2, self.textRect.y + self.y))

    def checkClick(self):
        self.hoverSound.set_volume(0.5 * self.interfaceVolume)
        self.releaseSound.set_volume(0.5 * self.interfaceVolume)

        mousePos = pygame.mouse.get_pos()
        if self.btnRect.collidepoint(mousePos):
            self.btnSprite = self.hoverSprite
            self.textColor = 'Yellow'
            self.textShadowColor = '#666600'
            if not self.hovered:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.hoverSound.play()
                self.hovered = True
            if pygame.mouse.get_pressed()[0]:
                self.textColor = '#B2B200'
                self.textShadowColor = '#474700'
                self.btnSprite = self.clickSprite
                self.pressed = True
            else:
                if self.pressed:
                    pygame.mouse.set_cursor(0)
                    self.releaseSound.play()
                    self.pressed = False
                    return True
        else:
            if self.hovered:
                pygame.mouse.set_cursor(0)
            self.hovered = False
            self.pressed = False
            self.btnSprite = self.sprite
            self.textColor = 'White'
            self.textShadowColor = '#666666'


class TimeTravelButton(Button):
    def __init__(self, surface, inPast = True, interfaceVolume = 100):
        super().__init__('В будущее' if inPast else 'В прошлое', screenSize[1] - 256, surface, interfaceVolume, screenSize[0] - 192)

        self.pastSprite = pygame.image.load('assets/images/gui/travelButtonInPast.png').convert_alpha()
        self.futureSprite = pygame.image.load('assets/images/gui/travelButtonInFuture.png').convert_alpha()
        self.rotating = 0

        self.hoverSound.set_volume(0.5 * self.interfaceVolume)
        self.releaseSound.set_volume(0.5 * self.interfaceVolume)

        self.btnSprite = self.pastSprite if inPast else self.futureSprite
        self.btnRect = pygame.Rect(
            (self.x - self.btnSprite.get_width() / 2, self.y),
            (self.btnSprite.get_width(), self.btnSprite.get_height())
        )
        self.btnRect.y += 32
        self.btnRect.height -= 64
        self.textRect = dialogueFont.render(self.text, False, self.textColor).get_rect(center=self.btnSprite.get_rect().midbottom)
        self.textRect.y += 24

    def changeText(self, newText):
        self.text = newText
        self.textRect = dialogueFont.render(newText, False, self.textColor).get_rect(center=self.btnSprite.get_rect().midbottom)
        self.textRect.y += 24

    def draw(self):
        rotatedSprite = pygame.transform.rotate(self.btnSprite, -self.rotating)
        rotatedRect = rotatedSprite.get_rect(center=self.btnRect.center)
        self.surface.blit(rotatedSprite, rotatedRect)
        self.surface.blit(dialogueFont.render(self.text, False, self.textShadowColor), (self.textRect.x + self.x - self.btnSprite.get_width() / 2 + 3, self.textRect.y + self.y + 3 - 32))
        self.surface.blit(dialogueFont.render(self.text, False, self.textColor), (self.textRect.x + self.x - self.btnSprite.get_width() / 2, self.textRect.y + self.y - 32))

    def checkClick(self):
        mousePos = pygame.mouse.get_pos()
        if self.btnRect.collidepoint(mousePos):
            self.textColor = 'Yellow'
            self.textShadowColor = '#666600'
            if self.rotating < 30:
                self.rotating += max(1, (30 - self.rotating) // 4)
            if not self.hovered:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.hoverSound.play()
            self.hovered = True
            if pygame.mouse.get_pressed()[0]:
                self.textColor = '#B2B200'
                self.textShadowColor = '#474700'
                self.pressed = True
            else:
                if self.pressed:
                    pygame.mouse.set_cursor(0)
                    self.releaseSound.play()
                    self.pressed = False
                    return True
        else:
            if self.rotating > 0:
                self.rotating -= max(1, self.rotating // 4)
            if self.hovered:
                pygame.mouse.set_cursor(0)
            self.hovered = False
            self.pressed = False
            self.textColor = 'White'
            self.textShadowColor = '#666666'


class Slider:
    def __init__(self, surface: pygame.Surface, x, y, initialValue: float, label = '', min: int = 0,
                 max: int = 100, interfaceVolume = 100, editingFunc = None, doneFunc = None, type = None):
        self.surface = surface
        self.label = label
        self.x = x
        self.y = y
        self.min = min
        self.max = max

        self.editingFunction = editingFunc
        self.doneFunction = doneFunc
        self.type = type

        self.base = pygame.image.load('assets/images/gui/sliderBase.png')
        self.button = pygame.image.load('assets/images/gui/sliderButton.png')
        self.buttonHover = pygame.image.load('assets/images/gui/sliderButtonHover.png')
        self.buttonPressed = pygame.image.load('assets/images/gui/sliderButtonPressed.png')

        self.buttonRect = pygame.Rect((
            self.x + self.base.get_width() / 100 * initialValue - self.button.get_width() / 2,
            self.y + self.base.get_height() / 2 - self.button.get_height() / 2
        ), self.button.get_size())
        self.buttonSprite = self.button

        self.hoverSound = pygame.mixer.Sound('assets/sounds/gui/buttonHover.wav')
        self.releaseSound = pygame.mixer.Sound('assets/sounds/gui/buttonRelease.wav')
        self.interfaceVolume = interfaceVolume / 100
        self.effectsVolume = None

        self.value = initialValue
        self.hovered = False
        self.pressed = False

    def update(self):
        mousePos = pygame.mouse.get_pos()
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSprite = self.buttonHover
            if not self.hovered:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.hoverSound.set_volume(0.5 * self.interfaceVolume)
                self.hoverSound.play()
                self.hovered = True
            if pygame.mouse.get_pressed()[0]:
                self.buttonSprite = self.buttonPressed
                self.pressed = True
                newCenterX = min(max(mousePos[0], self.x + 39), self.x + self.base.get_width() - 39)
                self.buttonRect.centerx = newCenterX
                self.value = ((self.buttonRect.centerx - (self.x + 39)) / (self.base.get_width() - 39 * 2)) * (self.max - self.min) + self.min
                if self.editingFunction is not None:
                    self.editingFunction(self.type, self.value)
            else:
                if self.pressed:
                    if self.doneFunction is not None:
                        self.doneFunction(self.type, self.value)
                    if self.type != 'musicVolume':
                        self.releaseSound.set_volume(
                            0.5 * (self.interfaceVolume if self.effectsVolume is None else self.effectsVolume))
                        self.releaseSound.play()
                    self.pressed = False
        else:
            if pygame.mouse.get_pressed()[0] and self.pressed:
                newCenterX = min(max(mousePos[0], self.x + 39), self.x + self.base.get_width() - 39)
                self.buttonRect.centerx = newCenterX
                self.value = ((self.buttonRect.centerx - (self.x + 39)) / (self.base.get_width() - 39 * 2)) * (self.max - self.min) + self.min
                if self.editingFunction is not None:
                    self.editingFunction(self.type, self.value)
            elif self.pressed:
                if self.doneFunction is not None:
                    self.doneFunction(self.type, self.value)
                if self.type != 'musicVolume':
                    self.releaseSound.set_volume(
                        0.5 * (self.interfaceVolume if self.effectsVolume is None else self.effectsVolume))
                    self.releaseSound.play()
                self.pressed = False
            elif self.hovered:
                pygame.mouse.set_cursor(0)
                self.hovered = False
                self.buttonSprite = self.button

    def draw(self):
        self.surface.blit(self.base, (self.x, self.y))
        self.surface.blit(self.buttonSprite, self.buttonRect)

        snip = mainFont.render(str(int(self.value)), False, '#006600' if int(self.value) > 0 else '#660000')
        self.surface.blit(snip, pygame.Vector2(self.x, self.y + self.base.get_height() / 2) - pygame.Vector2(snip.get_size()) / 2 + pygame.Vector2(-29, 3))
        self.surface.blit(mainFont.render(str(int(self.value)), False, '#aaffaa' if int(self.value) > 0 else '#ffaaaa'),
                          pygame.Vector2(self.x, self.y + self.base.get_height() / 2) - pygame.Vector2(snip.get_size()) / 2 + pygame.Vector2(-32, 0))

        textX = self.x + self.base.get_width() + 16
        textY = self.y + self.base.get_height() / 2 - 10
        self.surface.blit(mainFont.render(self.label, False, '#666666'), (textX + 3, textY + 3))
        self.surface.blit(mainFont.render(self.label, False, 'White'), (textX, textY))


# Balloon Backgrounds Preloading
balloonBackgrounds = []
for i in range(1, 7):
    balloonBackgrounds.append(pygame.image.load('assets/images/npcs/messageBalloon' + str(i) + '.png'))


class BalloonMessage:
    def __init__(self, messages: list, pos, speed = 3, color = 'White', voice = 'beep', switchPlayerControllability = None, callback = None):
        self.messages = messages
        self.messagePosition = 0
        self.currentMessage = 0
        self.printingSpeed = speed
        self.color = color

        for s in range(len(messages)):
            messages[s] = messages[s][:87] + '...' if len(messages[s]) > 90 else messages[s]

        self.speechSound = pygame.mixer.Sound('assets/sounds/speech/' + voice + '.mp3')

        self.done = False
        self.lastMessage = ''
        self.snips = []
        self.pos = pos

        pygame.mouse.set_visible(False)
        self.switchPlayerControllability = switchPlayerControllability
        if self.switchPlayerControllability is not None:
            self.switchPlayerControllability(False)

        self.callback = callback

    def draw(self, surface, offset):
        self.messagePosition += 1
        slicedMessage = self.messages[self.currentMessage][0:self.messagePosition // self.printingSpeed]

        lines = textwrap.wrap(slicedMessage, width=18)

        if slicedMessage != self.lastMessage:
            self.lastMessage = slicedMessage

            # Playing Speech Sound
            if slicedMessage and slicedMessage[-1] not in [' ', '.', ',', ';', '!', '?']:
                self.speechSound.play(maxtime=self.printingSpeed * fps)

            self.snips = []
            for line in lines:
                self.snips.append(dialogueFont.render(line.lstrip(), False, self.color))

        wrapped_lines = textwrap.wrap(self.messages[self.currentMessage], width=18)
        lineOffset = max(0, len(wrapped_lines) - 1)
        surface.blit(balloonBackgrounds[lineOffset], self.pos - offset - (64, 64) - (0, lineOffset * 18))
        for n, snip in enumerate(self.snips):
            surface.blit(snip, self.pos - offset - (64, 64) + (16, 16) + (0, n * 18) - (0, lineOffset * 18))

        # Checking if Mouse button has pressed, then printing next message
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP or (event.type == pygame.KEYUP and event.key == pygame.K_SPACE):
                if self.messagePosition // self.printingSpeed < len(self.messages[self.currentMessage]):
                    self.messagePosition = len(self.messages[self.currentMessage]) * self.printingSpeed
                elif self.currentMessage < len(self.messages) - 1:
                    self.messagePosition = 0
                    self.currentMessage += 1
                else:
                    self.done = True
                    pygame.mouse.set_visible(True)
                    if self.switchPlayerControllability is not None:
                        self.switchPlayerControllability(True)
                    if self.callback is not None:
                        self.callback()


class PhoneCall:
    def __init__(self, messages: list, speed = 3, color = 'White', voice = 'beep', name = 'Неизвестный', switchTimeMachine = None, callback = None):
        self.messages = messages
        self.messagePosition = 0
        self.currentMessage = 0
        self.name = name
        self.printingSpeed = speed
        self.color = color
        self.inPastCond = False

        for s in range(len(messages)):
            messages[s] = messages[i][:177] + '...' if len(messages[s]) > 180 else messages[s]

        self.speechSound = pygame.mixer.Sound('assets/sounds/speech/' + voice + '.mp3')
        self.callingBackground = pygame.image.load('assets/images/gui/marcusCalling.png')
        self.callingPhone = pygame.image.load('assets/images/gui/callingPhone.png')
        self.callingRingtone = pygame.mixer.Sound('assets/sounds/effects/PhoneCall.wav')
        self.acceptSound = pygame.mixer.Sound('assets/sounds/effects/PhoneAccept.wav')
        self.declineSound = pygame.mixer.Sound('assets/sounds/effects/PhoneDecline.wav')

        self.done = False
        self.waitingAnswer = True
        self.frame = 0
        self.lastMessage = ''
        self.snips = []

        pygame.mouse.set_visible(False)
        self.switchTimeMachine = switchTimeMachine
        if self.switchTimeMachine is not None:
            self.switchTimeMachine(False)

        self.callback = callback

    def draw(self, surface):
        if self.waitingAnswer:
            pos = (screenSize[0] / 2 - self.callingBackground.get_width() / 2, screenSize[1] - self.callingBackground.get_height() - 128)
            surface.blit(self.callingBackground, pos)
            nameSnip = bigFont.render(self.name, False, 'White')
            tipSnip = dialogueFont.render('Входящий вызов', False, '#cccccc')
            answerTipSnip = mainFont.render('[E] — Ответить', False, '#aaffaa')
            declineTipSnip = mainFont.render('[Y] — Сбросить', False, '#ff6666')

            # Phone Rotation Animation
            if self.frame % 60 < 30: angle = 5 - self.frame % 60 / 3
            else: angle = -5 + (self.frame % 60 - 30) / 3
            rotatedPhone = pygame.transform.rotate(self.callingPhone, angle)

            # Incoming Call text Blinking
            if self.frame < 60: alpha = 100 + int(self.frame / 60 * 155)
            else: alpha = 255 - int((self.frame - 60) / 60 * 155)
            tipSnip.set_alpha(alpha)

            surface.blit(nameSnip, pos + pygame.Vector2(256, 64))
            surface.blit(tipSnip, pos + pygame.Vector2(256, 96))
            surface.blit(answerTipSnip, pos + pygame.Vector2(256, 180))
            surface.blit(declineTipSnip, pos + pygame.Vector2(256, 212))
            surface.blit(rotatedPhone, pos - pygame.Vector2(156, 168) + self.callingBackground.get_size())

            self.frame = 0 if self.frame >= 120 else self.frame + 1

            # Checking if key has pressed, then answering or declining
            for event in pygame.event.get():
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_e:
                        self.acceptSound.play()
                        self.callingRingtone.stop()
                        self.callingPhone = pygame.image.load('assets/images/gui/activePhone.png')
                        self.waitingAnswer = False
                    elif event.key == pygame.K_y:
                        self.declineSound.play()
                        self.callingRingtone.stop()
                        self.done = True
                        pygame.mouse.set_visible(True)
                        if self.switchTimeMachine is not None:
                            self.switchTimeMachine(True)
                        if self.callback is not None:
                            self.callback()

        else:
            self.messagePosition += 1
            slicedMessage = self.messages[self.currentMessage][0:self.messagePosition // self.printingSpeed]

            lines = textwrap.wrap(slicedMessage, width=30)

            if slicedMessage != self.lastMessage:
                self.lastMessage = slicedMessage

                # Playing Speech Sound
                if slicedMessage and slicedMessage[-1] not in [' ', '.', ',', ';', '!', '?']:
                    self.speechSound.play(maxtime=self.printingSpeed * fps)

                self.snips = []
                for line in lines:
                    self.snips.append(bigFont.render(line.lstrip(), False, self.color))

            pos = (screenSize[0] / 2 - self.callingBackground.get_width() / 2, screenSize[1] - self.callingBackground.get_height() - 128)
            surface.blit(self.callingBackground, pos)
            surface.blit(self.callingPhone, pos - pygame.Vector2(156, 168) + self.callingBackground.get_size())
            for y, snip in enumerate(self.snips):
                surface.blit(snip, pos + pygame.Vector2(256, 64) + (0, y * 24) + (0, y * 2))

            # Checking if Mouse button has pressed, then printing next message
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP or (event.type == pygame.KEYUP and event.key == pygame.K_e):
                    if self.messagePosition // self.printingSpeed < len(self.messages[self.currentMessage]):
                        self.messagePosition = len(self.messages[self.currentMessage]) * self.printingSpeed
                    elif self.currentMessage < len(self.messages) - 1:
                        self.messagePosition = 0
                        self.currentMessage += 1
                    else:
                        self.done = True
                        self.declineSound.set_volume(self.declineSound.get_volume() * 0.5)
                        self.declineSound.play()
                        pygame.mouse.set_visible(True)
                        if self.switchTimeMachine is not None:
                            self.switchTimeMachine(True)
                        if self.callback is not None:
                            self.callback()


class Hint:
    def __init__(self, pos, parent, text, key = None):
        self.parent = parent
        self.text = text
        self.key = key
        self.color = 'White'
        self.shadowColor = '#333333'

        self.pos = pygame.Vector2(pos[0] - 16 * len(self.text) // 2, pos[1] - (32 if key is not None else 8))
        self.printingSound = pygame.mixer.Sound('assets/sounds/speech/typing.mp3')

        if key is not None:
            self.keyImage = pygame.image.load('assets/images/gui/keyboard_keys/' + str.lower(key) + '.png').convert_alpha()
        else:
            self.keyImage = None

        self.lastText = ''
        self.textPosition = 0
        self.printingSpeed = 3

        self.snip = pygame.Surface((0, 0))
        self.shadowSnip = pygame.Surface((0, 0))

    def draw(self, surface, offset):
        self.textPosition += 1
        slicedText = self.text[0:self.textPosition // self.printingSpeed]

        if slicedText != self.lastText:
            self.lastText = slicedText

            # Playing Printing Sound
            if slicedText and slicedText[-1] not in [' ', '.', ',', ';', '!', '?']:
                self.printingSound.play(maxtime=self.printingSpeed * fps)

            self.snip = dialogueFont.render(slicedText, False, self.color)
            self.shadowSnip = dialogueFont.render(slicedText, False, self.shadowColor)

        surface.blit(self.shadowSnip, self.pos - offset + (2, 2))
        surface.blit(self.snip, self.pos - offset)
        if self.keyImage:
            self.keyImage.set_alpha(255 * ((self.textPosition // self.printingSpeed) / len(self.text)))
            surface.blit(self.keyImage, self.pos - offset + (16 * len(self.text) / 2 - 12, 20))


class Objective:
    def __init__(self, text):
        self.text = text
        self.checkBox = pygame.image.load('assets/images/gui/objectiveCheckbox.png').convert()
        self.check = pygame.image.load('assets/images/gui/objectiveCheck.png')
        self.addSound = pygame.mixer.Sound('assets/sounds/gui/questAdd.wav')
        self.completeSound = pygame.mixer.Sound('assets/sounds/gui/questComplete.wav')
        self.snip = mainFont.render(self.text, False, 'White')
        self.textShadow = mainFont.render(self.text, False, '#666666')
        self.maxWidth = self.snip.get_width()
        self.frame = 0
        self.completeFrame = None

    def draw(self, surface, id):
        # Animation Processing
        if self.frame < 20:
            scaleFactor = 1.0 + math.cos(math.pi * self.frame / 40) * 2
            pos = (screenSize[0] - self.maxWidth - 24, id * (self.snip.get_height() + 16) + 96)
            scaledCheckBox = pygame.transform.scale(self.checkBox, ( self.checkBox.get_width() * scaleFactor, self.checkBox.get_height() * scaleFactor ))
            surface.blit(scaledCheckBox, (pos[0] - 48, pos[1] - 8))
            self.frame += 1
        else:
            pos = (screenSize[0] - self.maxWidth - 24, id * (self.snip.get_height() + 16) + 96)
            surface.blit(self.checkBox, (pos[0] - 48, pos[1] - 8))
            surface.blit(self.textShadow, (pos[0] + 3, pos[1] + 3))
            surface.blit(self.snip, pos)
        if self.completeFrame is not None:
            scaleFactor = 1.0 + math.cos(math.pi * min(self.frame - self.completeFrame, 20) / 40) * 2
            scaledCheck = pygame.transform.scale(self.check, (self.check.get_width() * scaleFactor, self.check.get_height() * scaleFactor))
            surface.blit(scaledCheck, (pos[0] - 48, pos[1] - 8))

            alpha = max(80, 255 * 3 - (self.frame - self.completeFrame) * 6)
            self.checkBox.set_alpha(alpha)
            self.snip.set_alpha(alpha)
            self.textShadow.set_alpha(alpha)

            self.frame += 1

    def complete(self):
        self.completeFrame = self.frame
        self.completeSound.set_volume(self.addSound.get_volume() * 2)
        self.completeSound.play()


class FoundItemAnimation:
    def __init__(self, type, label):
        self.type = type
        self.label = label

        self.image = pygame.image.load('assets/images/gui/items/' + type + '.png')
        self.mask = pygame.mask.from_surface(self.image).to_surface()
        self.mask.set_colorkey('Black')

        self.heading = mainFont.render('Получен предмет', False, 'White')
        self.label = dialogueFont.render(label, False, 'White')

        self.foundItemSound = pygame.mixer.Sound('assets/sounds/gui/foundItem.wav')
        self.frame = 0

    def draw(self, surf):
        self.mask.set_alpha(255 * 2 - self.frame * 3)
        self.image.set_alpha(255 * 4 - self.frame * 3)
        self.heading.set_alpha(255 * 4 - self.frame * 3)
        self.label.set_alpha(min(255 / 100 * self.frame, 255 * 4 - self.frame * 3))

        surf.blit(self.heading, (screenSize[0] / 2 - self.heading.get_width() / 2, screenSize[1] / 3 - 128))
        surf.blit(self.image, (screenSize[0] / 2 - self.image.get_width() / 2, screenSize[1] / 3 - self.image.get_height() / 2))
        surf.blit(self.mask, (screenSize[0] / 2 - self.image.get_width() / 2, screenSize[1] / 3 - self.image.get_height() / 2))
        surf.blit(self.label, (screenSize[0] / 2 - self.label.get_width() / 2, screenSize[1] / 3 + 128))

        self.frame += 1