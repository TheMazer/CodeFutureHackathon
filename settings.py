import pygame

# Screen Setup
screenSize = (1920, 1080)
screenFlags = pygame.NOFRAME | pygame.HWSURFACE | pygame.DOUBLEBUF

# Game Properties
tileSize = 64
fps = 60

# Level Dictionaries
level_1 = {
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
    'Enemies': 'levels/1/level1_Enemies.csv',
    'FutureBg': 'levels/1/level1_FutureBg.csv',
    'PastBg': 'levels/1/level1_PastBg.csv',
    'bgDecoration': 'levels/1/level1_bgDecoration.csv',
    'Ground': 'levels/1/level1_Ground.csv',
    'Background': 'levels/1/level1_Background.csv'
}