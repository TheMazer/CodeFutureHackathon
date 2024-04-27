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