from settings import *

import textwrap


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