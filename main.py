from settings import *

from level import Level
from functions import Config


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(screenSize, flags=screenFlags)
        pygame.display.set_caption('Tempus Corp')
        self.clock = pygame.time.Clock()
        self.config = Config('config.ini')

        self.menu = None
        self.level = None
        self.currentStage = None
        self.createLevel(level_1)

    def createMainMenu(self):
        self.menu = None
        self.currentStage = self.menu

    def createLevel(self, currentLevel):
        self.level = Level(currentLevel, self.createMainMenu, self.createLevel, self.config)
        self.currentStage = self.level

    def run(self):
        running = True
        while running:
            self.clock.tick(fps)
            self.currentStage.run()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()