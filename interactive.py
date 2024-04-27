from settings import *

import textwrap


class mButton:
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


class TimeTravelButton(mButton):
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