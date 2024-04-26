import pygame


class Level:
    def __init__(self, levelData, createMenu, createLevel):
        self.displaySurface = pygame.display.get_surface()
        self.createMenu = createMenu
        self.createLevel = createLevel

        # Level Data
        self.levelData = levelData
        self.levelParameters = self.levelData.get('Parameters', {})

        # Level Setup
        self.setupLevel()

    def setupLevel(self):
        ...