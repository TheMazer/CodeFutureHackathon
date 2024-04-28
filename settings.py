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
        'useCameraConstraints': False,
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

    'LevelMusic': 'assets/sounds/music/Cunning Fox R&B Remix.mp3'
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

    'PastBackgroundImage': 'assets/images/background/levels/2/past.png',

    'LevelMusic': 'assets/sounds/music/Arcade Machine Trap Remix.mp3'
}

level_3 = {
    'Parameters': {
        'musicVolume': 0.2,
        'startTime': 'past',
        'focusOnPlayerFirst': True,
        'snow': 'future'
    },

    'VerticalTriggers': [
        'MarcusInit',
        'MarcusQuestComplete'
    ],

    'ScriptedObjects': 'levels/3/level3_ScriptedObjects.csv',
    'Fades': 'levels/3/level3_Fades.csv',
    'FutureFades': 'levels/3/level3_FutureFades.csv',
    'PastFades': 'levels/3/level3_PastFades.csv',
    'ParticleSources': 'levels/3/level3_ParticleSources.csv',
    'PastParticleSources': 'levels/3/level3_PastParticleSources.csv',
    'AnimatedObjects': 'levels/3/level3_AnimatedObjects.csv',
    'PastAnimatedObjects': 'levels/3/level3_PastAnimatedObjects.csv',
    'FutureObjects': 'levels/3/level3_FutureObjects.csv',
    'PastObjects': 'levels/3/level3_PastObjects.csv',
    'Decoration': 'levels/3/level3_Decoration.csv',
    'Bonuses': 'levels/3/level3_Bonuses.csv',
    'Player': 'levels/3/level3_Player.csv',
    'Npcs': 'levels/3/level3_Npcs.csv',
    'Enemies': 'levels/3/level3_Enemies.csv',
    'FutureBg': 'levels/3/level3_FutureBg.csv',
    'PastBg': 'levels/3/level3_PastBg.csv',
    'bgDecoration': 'levels/3/level3_bgDecoration.csv',
    'FuturePlatforms': 'levels/3/level3_FuturePlatforms.csv',
    'PastPlatforms': 'levels/3/level3_PastPlatforms.csv',
    'FutureHelicopters': 'levels/3/level3_FutureHelicopters.csv',
    'PastHelicopters': 'levels/3/level3_PastHelicopters.csv',
    'FutureSaws': 'levels/3/level3_FutureSaws.csv',
    'PastSaws': 'levels/3/level3_PastSaws.csv',
    'Ground': 'levels/3/level3_Ground.csv',
    'FutureGround': 'levels/3/level3_FutureGround.csv',
    'PastGround': 'levels/3/level3_PastGround.csv',
    'Background': 'levels/3/level3_Background.csv',
    'UnderBgDecoration': 'levels/3/level3_UnderBgDecoration.csv',

    'pastGroundTileset': 'assets/images/tilesets/corpsTiles.png',
    'futureGroundTileset': 'assets/images/tilesets/corpsNeoTiles.png',

    'FutureBackgroundImage': 'assets/images/background/levels/3/future.png',
    'CustomCloudsFolder': 'assets/images/background/cloudFades',

    'LevelMusic': 'assets/sounds/music/Cunning Fox R&B Remix.mp3',
    'FutureMusic': 'assets/sounds/music/Pulse of Time.mp3'
}

# Defining Next Levels
level_1['nextLevel'] = level_2
level_2['nextLevel'] = level_3