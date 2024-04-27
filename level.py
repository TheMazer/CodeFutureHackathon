from settings import *

import threading
from tiles import StaticTile, StaticObject, EnergyExplosion, Alarm
from particles import ParticleSource
from player import Player
from npc import Marcus
from functions import importCutGraphics, importCsvLayout
from interactive import BalloonMessage
from camera import CameraGroup


class Level:
    def __init__(self, levelData, createMenu, createLevel, config):
        self.displaySurface = pygame.display.get_surface()
        self.createMenu = createMenu
        self.createLevel = createLevel
        self.config = config

        # Level Data
        self.levelData = levelData
        self.levelParameters = self.levelData.get('Parameters', {})

        # Screen Effects
        self.screenshake = 0
        self.screenshakeFrozen = False
        self.flashing = 0
        self.transition = 60
        self.fading = {
            'fadeIn': 0,
            'current': 0,
            'delay': 0,
            'fadeOut': 0,
            'totalFadeSeconds': [0, 0]
        }

        # Music
        self.levelMusic = pygame.mixer.Sound(self.levelData['LevelMusic'])
        self.levelMusic.set_volume(self.levelParameters.get('musicVolume', 1) * int(self.config.get('musicVolume', 'Settings')) / 100)

        # Balloon Messages Processing
        self.balloonMessages = []

        # Time Travelling
        self.inPast = True
        self.hasTimeMachine = True  # Todo: Replace with this: self.levelParameters.get('hasTimeMachine', 0)
        self.lastPlayerPositions = {'past': (0.0, 0.0), 'future': (0.0, 0.0), 'init': (0, 0)}

        # Time-based Tilesets
        self.pastGroundTileList = importCutGraphics(self.levelData['pastGroundTileset'])
        self.futureGroundTileList = importCutGraphics(self.levelData['futureGroundTileset'])

        # Level Setup
        self.setupLevel()

        self.levelMusic.play(loops = -1)

    # Game Management Functions
    def startScriptedObject(self, event, destroy = False):
        for sprite in self.scriptedObjectsSprites:
            if isinstance(sprite, EnergyExplosion) and event == 'EnergyExplosion':
                def destruct():
                    if destroy: self.scriptedObjectsSprites.remove(sprite)
                sprite.activate(int(self.config.get('effectsVolume', 'Settings')), destruct)

    def switchPlayerControllability(self, mode: bool = None):
        if mode is not None:
            self.player.sprite.controllability = mode
        else:
            self.player.sprite.controllability = not self.player.sprite.controllability

    def switchTimeMachine(self, mode: bool = None):
        if mode is not None:
            self.hasTimeMachine = mode
        else:
            self.hasTimeMachine = not self.hasTimeMachine

    def setBackgroundMusic(self, path, volume = 0.2, fade = 2, loops = -1):
        if path != 'stop':
            def changingMusic():
                self.levelMusic.stop()
                self.levelMusic = pygame.mixer.Sound(path)
                self.levelMusic.set_volume(volume * int(self.config.get('musicVolume', 'Settings')) / 100)
                self.levelMusic.play(loops=loops)
            self.levelMusic.fadeout(int(fade * 1000))
            threading.Timer(fade, changingMusic).start()
        else:
            self.levelMusic.fadeout(int(fade * 1000))

    def playSound(self, path, volume = 0.2, fade = 0, loops = 0):
        soundEffect = pygame.mixer.Sound(path)
        soundEffect.set_volume(volume * int(self.config.get('effectsVolume', 'Settings')) / 100)
        soundEffect.play(fade_ms=fade * 1000, loops=loops)
        return soundEffect

    def createBalloonMessage(self, messages, pos, speed = 3, color = 'White', callback = None, voice = 'beep'):
        if pos == 'player': pos = self.player.sprite.rect.topleft  # Player Speech
        message = BalloonMessage(messages, pos, speed, color, voice, self.switchPlayerControllability, callback)
        message.speechSound.set_volume(int(self.config.get('effectsVolume', 'Settings')) / 100)  # Beeps Volume
        self.balloonMessages.append(message)

    def screenShakeEffect(self, intensity, stay = False):
        self.screenshake = intensity
        self.screenshakeFrozen = stay

    def screenFlashEffect(self, intensity):
        self.flashing = intensity

    def screenFadeEffect(self, fadeIn, delay, fadeOut):
        self.fading = {
            'fadeIn': fadeIn * fps,
            'current': 0,
            'delay': delay * fps,
            'fadeOut': fadeOut * fps,
            'totalFadeSeconds': [fadeIn * fps, fadeOut * fps]
        }

    # noinspection PyTypeChecker, PyUnboundLocalVariable
    def createTileGroup(self, layout, sType):
        spriteGroup = pygame.sprite.Group()
        if not layout: return spriteGroup

        for rowIndex, row in enumerate(layout):
            for colIndex, val in enumerate(row):
                if val != '-1':
                    x = colIndex * tileSize
                    y = rowIndex * tileSize

                    if sType == 'Ground':
                        if self.inPast: groundTileList = self.pastGroundTileList
                        else: groundTileList = self.futureGroundTileList
                        tileSurface = groundTileList[int(val)]
                        sprite = StaticTile(x, y, tileSurface, int(val))
                    elif sType == 'Fades':
                        fadesTileList = importCutGraphics('assets/images/tilesets/fadeTiles.png')
                        tileSurface = fadesTileList[int(val)]
                        sprite = StaticTile(x, y, tileSurface)
                    elif sType == 'Decoration':
                        sprite = StaticObject(x, y, val)
                    elif sType == 'ScriptedObjects':
                        if val == '0':  # Energy Explosion
                            sprite = EnergyExplosion(x, y)
                    elif sType == 'AnimatedObjects':
                        if val == '0':  # Alarm
                            sprite = Alarm(x, y, val)
                    elif sType == 'ParticleSources':
                        sprite = ParticleSource(x, y, val, self.displaySurface, self.cameraGroup)
                    elif sType == 'Npcs':
                        if val == '0':  # Marcus (Intro)
                            sprite = Marcus((x, y), self)

                    spriteGroup.add(sprite)

        return spriteGroup

    def setupLevel(self):
        # Camera Setup, Level size needed for Background Clipping calculation
        self.cameraGroup = CameraGroup(self)
        self.player = pygame.sprite.GroupSingle()

        # Fades Setup
        fadesLayout = importCsvLayout(self.levelData.get('Fades'))
        self.fadesSprites = self.createTileGroup(fadesLayout, 'Fades')

        # Future Fades Setup
        futureFadesLayout = importCsvLayout(self.levelData.get('FutureFades'))
        self.futureFadesSprites = self.createTileGroup(futureFadesLayout, 'Fades')

        # Past Fades Setup
        pastFadesLayout = importCsvLayout(self.levelData.get('PastFades'))
        self.pastFadesSprites = self.createTileGroup(pastFadesLayout, 'Fades')

        # Particle Sources Setup
        particleSourcesLayout = importCsvLayout(self.levelData.get('ParticleSources'))
        self.particleSourcesSprites = self.createTileGroup(particleSourcesLayout, 'ParticleSources')

        # Past Particle Sources Setup
        pastParticleSourcesLayout = importCsvLayout(self.levelData.get('PastParticleSources'))
        self.pastParticleSourcesSprites = self.createTileGroup(pastParticleSourcesLayout, 'ParticleSources')

        # Scripted Objects Setup
        scriptedObjectsLayout = importCsvLayout(self.levelData['ScriptedObjects'])
        self.scriptedObjectsSprites = self.createTileGroup(scriptedObjectsLayout, 'ScriptedObjects')

        # Background Scripted Objects
        self.bgScriptedObjectsSprites = pygame.sprite.Group()
        for sprite in self.scriptedObjectsSprites:
            if getattr(sprite, 'isBackground', 0):
                self.scriptedObjectsSprites.remove(sprite)
                self.bgScriptedObjectsSprites.add(sprite)

        # Animated Objects Setup
        animatedLayout = importCsvLayout(self.levelData.get('AnimatedObjects'))
        self.animatedSprites = self.createTileGroup(animatedLayout, 'AnimatedObjects')

        # Past Animated Objects Setup
        pastAnimatedLayout = importCsvLayout(self.levelData.get('PastAnimatedObjects'))
        self.pastAnimatedSprites = self.createTileGroup(pastAnimatedLayout, 'AnimatedObjects')

        # Future Objects Setup
        futureObjectsLayout = importCsvLayout(self.levelData.get('FutureObjects'))
        self.futureObjectsSprites = self.createTileGroup(futureObjectsLayout, 'Decoration')

        # Past Objects Setup
        pastObjectsLayout = importCsvLayout(self.levelData.get('PastObjects'))
        self.pastObjectsSprites = self.createTileGroup(pastObjectsLayout, 'Decoration')

        # Decoration Setup
        decorationLayout = importCsvLayout(self.levelData.get('Decoration'))
        self.decorationSprites = self.createTileGroup(decorationLayout, 'Decoration')

        # Player Setup
        playerLayout = importCsvLayout(self.levelData['Player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.playerSetup(playerLayout, self.levelParameters.get('playerFacingRight', True))

        # Npcs Setup
        npcLayout = importCsvLayout(self.levelData.get('Npcs'))
        self.npcSprites = self.createTileGroup(npcLayout, 'Npcs')

        # Future Decoration Setup
        futureBgLayout = importCsvLayout(self.levelData.get('FutureBg'))
        self.futureBgSprites = self.createTileGroup(futureBgLayout, 'Decoration')

        # Past Decoration Setup
        pastBgLayout = importCsvLayout(self.levelData.get('PastBg'))
        self.pastBgSprites = self.createTileGroup(pastBgLayout, 'Decoration')

        # Background Decoration Setup
        bgDecorationLayout = importCsvLayout(self.levelData.get('bgDecoration'))
        self.bgDecorationSprites = self.createTileGroup(bgDecorationLayout, 'Decoration')

        # Future Platforms Setup
        futurePlatformsLayout = importCsvLayout(self.levelData.get('FuturePlatforms'))
        self.futurePlatforms = self.createTileGroup(futurePlatformsLayout, 'Platforms')

        # Past Platforms Setup
        pastPlatformsLayout = importCsvLayout(self.levelData.get('PastPlatforms'))
        self.pastPlatforms = self.createTileGroup(pastPlatformsLayout, 'Platforms')

        # Future Saws Setup
        futureSawsLayout = importCsvLayout(self.levelData.get('FutureSaws'))
        self.futureSaws = self.createTileGroup(futureSawsLayout, 'FutureSaws')

        # Past Saws Setup
        pastSawsLayout = importCsvLayout(self.levelData.get('PastSaws'))
        self.pastSaws = self.createTileGroup(pastSawsLayout, 'PastSaws')

        # Future Helicopters Setup
        futureHelicoptersLayout = importCsvLayout(self.levelData.get('FutureHelicopters'))
        self.futureHelicopters = self.createTileGroup(futureHelicoptersLayout, 'Helicopters')

        # Past Helicopters Setup
        pastHelicoptersLayout = importCsvLayout(self.levelData.get('PastHelicopters'))
        self.pastHelicopters = self.createTileGroup(pastHelicoptersLayout, 'Helicopters')

        # Ground Setup
        groundLayout = importCsvLayout(self.levelData.get('Ground'))
        self.groundSprites = self.createTileGroup(groundLayout, 'Ground')

        # Future Ground Setup
        futureGroundLayout = importCsvLayout(self.levelData.get('FutureGround'))
        self.futureGroundSprites = self.createTileGroup(futureGroundLayout, 'Ground')

        # Past Ground Setup
        pastGroundLayout = importCsvLayout(self.levelData.get('PastGround'))
        self.pastGroundSprites = self.createTileGroup(pastGroundLayout, 'Ground')

        # Background Setup
        backgroundLayout = importCsvLayout(self.levelData.get('Background'))
        self.backgroundSprites = self.createTileGroup(backgroundLayout, 'Ground')

        # Under Background Decoration Setup
        underBgDecoration = importCsvLayout(self.levelData.get('UnderBgDecoration'))
        self.underBgDecorationSprites = self.createTileGroup(underBgDecoration, 'Decoration')

        # Adding Basic Sprites (Pt 1)
        self.cameraGroup.add(self.underBgDecorationSprites)
        self.cameraGroup.add(self.backgroundSprites)
        self.cameraGroup.add(self.groundSprites)
        self.cameraGroup.add(self.bgDecorationSprites)
        self.cameraGroup.add(self.decorationSprites)

        # Adding sprites depending on current time
        if self.inPast:
            self.cameraGroup.add(self.pastGroundSprites)
            self.cameraGroup.add(self.pastBgSprites)
            self.cameraGroup.add(self.pastObjectsSprites)
            self.cameraGroup.add(self.pastAnimatedSprites)
            self.cameraGroup.add(self.pastPlatforms)
            self.cameraGroup.add(self.pastHelicopters)
            self.cameraGroup.add(self.pastSaws)
        else:
            self.cameraGroup.add(self.futureGroundSprites)
            self.cameraGroup.add(self.futureBgSprites)
            self.cameraGroup.add(self.futureObjectsSprites)
            self.cameraGroup.add(self.animatedSprites)
            self.cameraGroup.add(self.futurePlatforms)
            self.cameraGroup.add(self.futureHelicopters)
            self.cameraGroup.add(self.futureSaws)

        # Adding Basic Sprites (Pt 2)
        self.cameraGroup.add(self.npcSprites)
        self.cameraGroup.add(self.player)
        self.cameraGroup.add(self.goal)
        if self.inPast:  # Adding Particles depending on current time
            self.cameraGroup.add(self.pastParticleSourcesSprites)
            self.cameraGroup.add(self.pastFadesSprites)
        else:
            self.cameraGroup.add(self.particleSourcesSprites)
            self.cameraGroup.add(self.futureFadesSprites)
        self.cameraGroup.add(self.fadesSprites)

        self.player.sprite.collideableSprites = self.groundSprites.sprites() + self.decorationSprites.sprites()

    def timeTravel(self, to: str = None):
        for sprite in self.cameraGroup.sprites():
            self.cameraGroup.remove(sprite)

        # Returning Basic Sprites (Pt 1)
        self.cameraGroup.add(self.underBgDecorationSprites)
        self.cameraGroup.add(self.backgroundSprites)
        self.cameraGroup.add(self.groundSprites)
        self.cameraGroup.add(self.bgDecorationSprites)

        # Adding sprites depending on current time
        if (self.inPast and to != 'past') or to == 'future':
            if self.player.sprite.onGround:
                self.lastPlayerPositions['past'] = self.player.sprite.rect.topleft
            if self.lastPlayerPositions['future'] != (0, 0):
                self.player.sprite.hitbox.topleft = self.lastPlayerPositions['future']
            self.inPast = False
            for sprite in self.groundSprites.sprites() + self.futureGroundSprites.sprites() + self.pastGroundSprites.sprites() + self.backgroundSprites.sprites():
                tileSurface = self.futureGroundTileList[sprite.val]
                sprite.image = tileSurface
            self.cameraGroup.add(self.futureGroundSprites)
            self.cameraGroup.add(self.futureBgSprites)
            self.cameraGroup.add(self.futureObjectsSprites)
            self.cameraGroup.add(self.animatedSprites)
            self.cameraGroup.add(self.futurePlatforms)
            self.cameraGroup.add(self.futureHelicopters)
            self.cameraGroup.add(self.futureSaws)
        else:
            if self.player.sprite.onGround:
                self.lastPlayerPositions['future'] = self.player.sprite.rect.topleft
            if self.lastPlayerPositions['past'] != (0, 0):
                self.player.sprite.hitbox.topleft = self.lastPlayerPositions['past']
            self.inPast = True
            for sprite in self.groundSprites.sprites() + self.futureGroundSprites.sprites() + self.pastGroundSprites.sprites() + self.backgroundSprites.sprites():
                tileSurface = self.pastGroundTileList[sprite.val]
                sprite.image = tileSurface
            self.cameraGroup.add(self.pastGroundSprites)
            self.cameraGroup.add(self.pastBgSprites)
            self.cameraGroup.add(self.pastObjectsSprites)
            self.cameraGroup.add(self.pastAnimatedSprites)
            self.cameraGroup.add(self.pastPlatforms)
            self.cameraGroup.add(self.pastHelicopters)
            self.cameraGroup.add(self.pastSaws)

        # What Scripted Objects will add to Camera depends on Time Condition
        timeCondBgScriptedObjects = pygame.sprite.Group([sprite for sprite in self.bgScriptedObjectsSprites if not hasattr(sprite, 'inPast') or sprite.inPast == self.inPast])
        timeCondScriptedObjects = pygame.sprite.Group([sprite for sprite in self.scriptedObjectsSprites if not hasattr(sprite, 'inPast') or sprite.inPast == self.inPast])

        # Returning Basic Sprites (Pt 2)
        self.cameraGroup.add(self.decorationSprites)
        self.cameraGroup.add(timeCondBgScriptedObjects)
        self.cameraGroup.add([
            npc for npc in self.npcSprites if not hasattr(npc, 'timeCond') or
            (npc.timeCond == 'all' or
            (npc.timeCond == 'past' and self.inPast) or
            (npc.timeCond == 'future' and not self.inPast))
        ])
        self.cameraGroup.add(self.player)
        self.cameraGroup.add(self.goal)
        if self.inPast:  # Adding Particles depending on current time and changing Background image
            self.cameraGroup.add(self.pastParticleSourcesSprites)
            self.cameraGroup.add(self.pastFadesSprites)
        else:
            self.cameraGroup.add(self.particleSourcesSprites)
            self.cameraGroup.add(self.futureFadesSprites)
        self.cameraGroup.add(self.fadesSprites)
        self.cameraGroup.add(timeCondScriptedObjects)

        # Resetting Player's Direction to prevent from noclipping
        self.player.sprite.direction = pygame.Vector2()

        # Changing Music
        if self.levelData.get('FutureMusic') and not self.inPast:
            self.setBackgroundMusic(self.levelData.get('FutureMusic'), fade=1)
        elif self.levelData.get('PastMusic') and self.inPast:
            self.setBackgroundMusic(self.levelData.get('PastMusic'), fade=1)
        elif self.levelParameters.get('musicSwitching', True):
            self.setBackgroundMusic(self.levelData.get('LevelMusic'), fade=1)

        self.screenshake = 30
        self.flashing = 100

        return self.inPast

    # noinspection PyTypeChecker
    def playerSetup(self, layout, facingRight):
        for rowIndex, row in enumerate(layout):
            for colIndex, val in enumerate(row):
                x = colIndex * tileSize
                y = rowIndex * tileSize
                if val == '0':
                    sprite = Player((x, y), facingRight)
                    sprite.jumpSound.set_volume(0.2 * int(self.config.get('effectsVolume', 'Settings')) / 100)
                    sprite.landSound.set_volume(0.2 * int(self.config.get('effectsVolume', 'Settings')) / 100)
                    sprite.damageTakenSound.set_volume(int(self.config.get('effectsVolume', 'Settings')) / 100)
                    self.player.add(sprite)
                    self.lastPlayerPositions['init'] = (x, y)
                elif val == '1':
                    goalSurf = pygame.image.load('assets/images/character/goal.png').convert_alpha()
                    sprite = StaticTile(x, y, goalSurf)
                    sprite.drawable = False  # Defining Goal Visibility
                    self.goal.add(sprite)

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pygame.quit()

    def run(self):
        # Keyboard Input
        self.input()

        # Rendering
        self.cameraGroup.render()

        # Screen Effects Processing
        if self.screenshake and not self.screenshakeFrozen:
            self.screenshake -= 0.5

        if self.flashing:
            self.flashing -= (100 - min(self.flashing, 80)) / 20
            self.flashing = max(self.flashing, 0)

        if self.fading['fadeIn'] > 0:
            self.fading['current'] = round((self.fading['totalFadeSeconds'][0] - self.fading['fadeIn']) / self.fading['totalFadeSeconds'][0] * 100)
            self.fading['fadeIn'] -= 1
        elif self.fading['delay'] > 0:
            self.fading['current'] = 100
            self.fading['delay'] -= 1
        elif self.fading['current'] > 0:
            self.fading['current'] = round((1 - (self.fading['totalFadeSeconds'][1] - self.fading['fadeOut']) / self.fading['totalFadeSeconds'][1]) * 100)
            self.fading['fadeOut'] -= 1

        if self.transition:
            self.transition -= 1