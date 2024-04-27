import pygame
pygame.init()

# Screen Setup
screenSize = (1920, 1080)
screenFlags = pygame.NOFRAME | pygame.HWSURFACE | pygame.DOUBLEBUF

# Game Properties
tileSize = 64
fps = 60

# Fonts
mainFont = pygame.font.Font('assets/fonts/PressStart2P.ttf', 20)
bigFont = pygame.font.Font('assets/fonts/PressStart2P.ttf', 24)
dialogueFont = pygame.font.Font('assets/fonts/PressStart2P.ttf', 16)

# Level Dictionaries
level_1 = {
    'Parameters': {
        'playerFacingRight': False,
        'musicVolume': 0.2
    },

    'ScriptedObjects': 'levels/1/level1_ScriptedObjects.csv',
    'Fades': 'levels/1/level1_Fades.csv',
    'ParticleSources': 'levels/1/level1_ParticleSources.csv',
    'PastParticleSources': 'levels/1/level1_PastParticleSources.csv',
    'AnimatedObjects': 'levels/1/level1_AnimatedObjects.csv',
    'PastAnimatedObjects': 'levels/1/level1_PastAnimatedObjects.csv',
    'FutureObjects': 'levels/1/level1_FutureObjects.csv',
    'PastObjects': 'levels/1/level1_PastObjects.csv',
    'Decoration': 'levels/1/level1_Decoration.csv',
    'Player': 'levels/1/level1_Player.csv',
    'Npcs': 'levels/1/level1_Npcs.csv',
    'FutureBg': 'levels/1/level1_FutureBg.csv',
    'PastBg': 'levels/1/level1_PastBg.csv',
    'bgDecoration': 'levels/1/level1_bgDecoration.csv',
    'Ground': 'levels/1/level1_Ground.csv',
    'Background': 'levels/1/level1_Background.csv',

    'pastGroundTileset': 'assets/images/tilesets/auditoriumTiles.png',
    'futureGroundTileset': 'assets/images/tilesets/auditoriumTiles.png',

    'LevelMusic': 'assets/sounds/music/Cunning Fox.mp3'
}