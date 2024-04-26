from settings import *

from csv import reader
from os import walk


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