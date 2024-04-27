from settings import *

from csv import reader
from os import walk
import configparser


class Config:
    def __init__(self, path = 'config.ini'):
        self.path = path
        self.config = configparser.ConfigParser()
        self.config.read(self.path)

    def load(self, path = None):
        self.path = path if path is not None else self.path
        self.config.read(self.path)

    def get(self, key, section = None):
        if section is not None:
            try: value = self.config[section][key]
            except KeyError: value = 0
            return value
        else:
            try: value = self.config[key]
            except KeyError: value = 0
            return value

    def set(self, key, value, section = None):
        if section is not None:
            if section not in self.config:
                self.config[section] = {}
            self.config[section][key] = value
        else:
            self.config[key] = value

    def save(self):
        with open(self.path, 'w') as configfile:
            self.config.write(configfile)


def importFolder(path):
    surfaceList = []

    for _, __, imgFiles in walk(path):
        for image in imgFiles:
            fullPath = path + '/' + image
            imageSurf = pygame.image.load(fullPath).convert_alpha()
            surfaceList.append(imageSurf)

    return surfaceList


def importCsvLayout(path):
    if path is not None:
        groundMap = []
        with open(path) as map:
            level = reader(map, delimiter = ',')
            for row in level:
                groundMap.append(list(row))
            return groundMap
    else:
        return []


def getLevelSize(path):
    width = 0
    height = 0

    with open(path) as map:
        level = reader(map, delimiter = ',')
        for row in level:
            height += 1
            if len(row) > width:
                width = len(row)

    return width, height


def importCutGraphics(path):
    surface = pygame.image.load(path).convert_alpha()
    tileNumX = int(surface.get_size()[0] / tileSize)
    tileNumY = int(surface.get_size()[1] / tileSize)

    cutTiles = []
    for row in range(tileNumY):
        for col in range(tileNumX):
            x = col * tileSize
            y = row * tileSize
            newSurf = pygame.Surface((tileSize, tileSize), pygame.SRCALPHA)
            newSurf.blit(surface, (0, 0), pygame.Rect(x, y, tileSize, tileSize))
            cutTiles.append(newSurf)

    return cutTiles


def circleSurf(radius, color):
    surf = pygame.surface.Surface((radius * 2, radius * 2))
    pygame.draw.circle(surf, color, (radius, radius), radius)
    surf.set_colorkey((0, 0, 0))
    return surf