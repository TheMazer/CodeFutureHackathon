from settings import *

import time
from level import Level
from menu import Menu
from functions import Config


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(screenSize, flags=screenFlags)
        pygame.display.set_caption('Tempus Corp')
        pygame.display.set_icon(pygame.image.load('assets/images/gui/icon.png'))

        self.clock = pygame.time.Clock()
        self.config = Config('config.ini')
        self.showFPS = self.config.get('showFPS', 'Settings') == 'True'

        self.menu = None
        self.level = None
        self.currentStage = None
        self.createMenu()
        # self.createLevel(level_2)

    def createMenu(self):
        self.menu = Menu(self.createLevel, self.config, self.switchFPS)
        self.currentStage = self.menu

    def createLevel(self, currentLevel):
        self.level = Level(currentLevel, self.createMenu, self.createLevel, self.config)
        self.currentStage = self.level

    def switchFPS(self, mode: bool = None):
        self.showFPS = mode if mode is not None else not self.showFPS
        return self.showFPS

    def run(self):
        fpsCounter = 0
        fpsUpdateInterval = 0

        running = True
        while running:
            start_time = time.time()
            self.clock.tick(fps)
            self.currentStage.run()

            if self.showFPS:
                fpsColor = 'White' if fpsCounter >= 50 else 'Red'
                self.screen.blit(mainFont.render('FPS: ' + str(fpsCounter), False, fpsColor), (32, 32))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()

            timeDiff = round(1.0 / (time.time() - start_time))
            if fpsUpdateInterval >= 20:
                fpsCounter = timeDiff
                fpsUpdateInterval = 0
            else:
                fpsUpdateInterval += 1


if __name__ == '__main__':
    game = Game()
    game.run()