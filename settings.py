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
        'musicVolume': 0.2,
        'finishTime': 'past',
        'musicSwitching': False
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

level_2 = {
    'Parameters': {
        'musicVolume': 0.2,
        'startTime': 'past'
    },

    'StartQuests': [
        ['Найти профессора', 2],
        ['Понять, что произошло', 2.5]
    ],

    'ScriptedObjects': 'levels/2/level2_ScriptedObjects.csv',
    'Fades': 'levels/2/level2_Fades.csv',
    'ParticleSources': 'levels/2/level2_ParticleSources.csv',
    'PastParticleSources': 'levels/2/level2_PastParticleSources.csv',
    'AnimatedObjects': 'levels/2/level2_AnimatedObjects.csv',
    'PastAnimatedObjects': 'levels/2/level2_PastAnimatedObjects.csv',
    'FutureObjects': 'levels/2/level2_FutureObjects.csv',
    'PastObjects': 'levels/2/level2_PastObjects.csv',
    'Decoration': 'levels/2/level2_Decoration.csv',
    'Player': 'levels/2/level2_Player.csv',
    'Npcs': 'levels/2/level2_Npcs.csv',
    'Enemies': 'levels/2/level2_Enemies.csv',
    'FutureBg': 'levels/2/level2_FutureBg.csv',
    'PastBg': 'levels/2/level2_PastBg.csv',
    'bgDecoration': 'levels/2/level2_bgDecoration.csv',
    'Ground': 'levels/2/level2_Ground.csv',
    'Background': 'levels/2/level2_Background.csv',
    'UnderBgDecoration': 'levels/2/level2_UnderBgDecoration.csv',

    'pastGroundTileset': 'assets/images/tilesets/streetTiles.png',
    'futureGroundTileset': 'assets/images/tilesets/streetTiles.png',

    'FutureBackgroundImage': 'assets/images/background/levels/2/future.png',
    'PastBackgroundImage': 'assets/images/background/levels/2/past.png',

    'LevelMusic': 'assets/sounds/music/Arcade Machine.mp3'
}

# Defining Next Levels
level_1['nextLevel'] = level_2