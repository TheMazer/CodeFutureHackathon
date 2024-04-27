from settings import *

import threading
from tiles import StaticTile, StaticObject, EnergyExplosion, FenceGateController, VerticalTrigger, Bonus, Platform, Helicopter, Saw, MidDoor, Alarm
from particles import ParticleSource, ParticleSpawner
from player import Player
from npc import Marcus, MarcusAtCorps, HistoryTeacher, FranceTeacher, MathsTeacher
from functions import importFolder, importCutGraphics, importCsvLayout, getLevelSize
from interactive import BalloonMessage, PhoneCall, Hint, Objective, FoundItemAnimation
from camera import CameraGroup


class Level:
    def __init__(self, levelData, createMenu, createLevel, config, objectives: list = None):
        self.displaySurface = pygame.display.get_surface()
        self.createMenu = createMenu
        self.createLevel = createLevel
        self.config = config

        # Level Changing
        self.forceFinish = False
        self.death = False
        self.finishProgress = 0

        # Level Data
        self.levelData = levelData
        self.levelParameters = self.levelData.get('Parameters', {})
        self.disableFades = self.config.get('disableFades', 'Settings') == 'True'

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

        # Balloon Messages & Hints & Objectives Processing
        self.balloonMessages = []
        self.phoneCalls = []
        self.hints = []
        self.objectives = []
        # Load Previous Level and Progress Saved Objectives
        if objectives is None:
            if titles := self.config.get('objectives', 'Progress'):
                titles = titles.split(' | ')
                for title in titles:
                    self.addObjective(title, False)
        else:
            self.objectives = objectives

        # Vertical Triggers
        self.triggerId = 0
        self.triggerActions = self.levelData.get('VerticalTriggers')

        # Time Travelling
        self.inPast = True if self.levelParameters.get('startTime', 'future') == 'past' else False
        self.hasTimeMachine = self.levelParameters.get('hasTimeMachine', False)
        self.lastPlayerPositions = {'past': (0.0, 0.0), 'future': (0.0, 0.0), 'init': (0, 0)}
        self.playerInventory = []

        # Time-based Tilesets
        self.pastGroundTileList = importCutGraphics(self.levelData['pastGroundTileset'])
        self.futureGroundTileList = importCutGraphics(self.levelData['futureGroundTileset'])

        # Background Image
        self.levelSize = getLevelSize(self.levelData['Ground'])
        self.futureBgImage = pygame.image.load(self.levelData['FutureBackgroundImage']).convert() if 'FutureBackgroundImage' in self.levelData else None
        self.pastBgImage = pygame.image.load(self.levelData['PastBackgroundImage']).convert() if 'PastBackgroundImage' in self.levelData else None
        self.bgImage = self.pastBgImage if self.inPast else self.futureBgImage
        self.customCloudsPath = importFolder(self.levelData.get('CustomCloudsFolder')) if self.levelData.get('CustomCloudsFolder') else None

        # Level Setup
        self.reversedObjects = {'helicopters': 0, 'saws': 0}
        self.setupLevel()

        # Focus Camera on Player if it says in Level Parameters
        if self.levelParameters.get('focusOnPlayerFirst'):
            self.cameraGroup.graduallyOffset = pygame.Vector2(self.player.sprite.hitbox.center) - pygame.Vector2(screenSize) / 2 - pygame.Vector2(0, 150)

        # Level Initial Objectives
        for text, delay in self.levelData.get('StartQuests', ()):
            threading.Timer(delay, self.addObjective, [text]).start()

        self.levelMusic.play(loops=-1)
        pygame.mouse.set_cursor(0)

    # Game Management Functions
    def startScriptedObject(self, event, destroy = False):
        if event == 'QuitToMenu':
            for thread in threading.enumerate():
                if isinstance(thread, threading.Timer):
                    thread.cancel()
            pygame.mouse.set_visible(True)
            self.levelMusic.stop()
            self.config.set('level', '0', 'Progress')
            self.config.set('objectives', '', 'Progress')
            self.config.save()
            self.createMenu()
            return

        for sprite in self.scriptedObjectsSprites:
            if isinstance(sprite, EnergyExplosion) and event == 'EnergyExplosion':
                def destruct():
                    if destroy: self.scriptedObjectsSprites.remove(sprite)
                sprite.activate(int(self.config.get('effectsVolume', 'Settings')), destruct)

    def triggerNpc(self, npcType, method = 'storytelling', args = None):
        for sprite in self.npcSprites:
            if sprite.npcType == npcType:
                method = getattr(sprite, method)
                if args is not None:
                    method(*args)
                else:
                    method()

    def switchPlayerControllability(self, mode: bool = None):
        if mode is not None:
            self.player.sprite.controllability = mode
        else:
            self.player.sprite.controllability = not self.player.sprite.controllability

    def switchTimeMachine(self, mode: bool = None, particles=False):
        if mode is not None:
            self.hasTimeMachine = mode
        else:
            self.hasTimeMachine = not self.hasTimeMachine
        if self.hasTimeMachine and particles:
            self.createGuiParticles('5', x=screenSize[0] - 192, y=screenSize[1] - 152, lifetime=20)

    def setBackgroundMusic(self, path, volume=0.2, fade=2, loops=-1):
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

    def createGuiParticles(self, type, variant = 'source', x = screenSize[0] / 2, y = screenSize[1] / 3, lifetime = 240):
        if variant.lower() == 'source':
            sprite = ParticleSource(x, y, type, self.displaySurface, self.cameraGroup, lifetime)
        else:
            sprite = ParticleSpawner(x, y, type, self.displaySurface, self.cameraGroup)
        self.cameraGroup.guiParticles.append(sprite)

    def createFoundItemAnimation(self, type, label = ''):
        self.createGuiParticles('4')
        foundItemAnimation = FoundItemAnimation(type, label)
        foundItemAnimation.foundItemSound.set_volume(0.5 * int(self.config.get('effectsVolume', 'Settings')) / 100)
        foundItemAnimation.foundItemSound.play()
        self.cameraGroup.foundItemAnimations.append(foundItemAnimation)

    def createBalloonMessage(self, messages, pos, speed = 3, color = 'White', callback = None, voice = 'beep'):
        if pos == 'player': pos = self.player.sprite.rect.topleft  # Player Speech
        message = BalloonMessage(messages, pos, speed, color, voice, self.switchPlayerControllability, callback)
        message.speechSound.set_volume(int(self.config.get('effectsVolume', 'Settings')) / 100)  # Beeps Volume
        self.balloonMessages.append(message)

    def createPhoneCall(self, messages: list, speed = 3, color = 'White', voice = 'beep', name = 'Неизвестный', callback = None):
        call = PhoneCall(messages, speed, color, voice, name, self.switchTimeMachine, callback)
        call.callingRingtone.set_volume(int(self.config.get('effectsVolume', 'Settings')) / 100 / 2)  # Ringtone Volume
        call.acceptSound.set_volume(int(self.config.get('effectsVolume', 'Settings')) / 100 / 2)  # Accept Volume
        call.declineSound.set_volume(int(self.config.get('effectsVolume', 'Settings')) / 100 / 2)  # Decline Volume
        call.speechSound.set_volume(int(self.config.get('effectsVolume', 'Settings')) / 100)  # Beeps Volume
        call.callingRingtone.play(loops=-1)
        self.phoneCalls.append(call)

    def addObjective(self, text, animation = True):
        objective = Objective(text)
        objective.addSound.set_volume(0.2 * int(self.config.get('effectsVolume', 'Settings')) / 100)
        if animation: objective.addSound.play()
        else: objective.frame = 20
        self.objectives.append(objective)

        maxWidth = max(self.objectives, key=lambda x: x.snip.get_width()).snip.get_width()
        for objective in self.objectives:
            objective.maxWidth = maxWidth

    def completeObjective(self, text):
        for objective in self.objectives:
            if objective.text == text:
                objective.complete()

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

    def changeFadeImage(self, imageSurface):
        self.cameraGroup.fadeImage = imageSurface

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
                    elif sType == 'Platforms':
                        platformsTileList = importCutGraphics('assets/images/tilesets/platforms.png')
                        tileSurface = platformsTileList[int(val)]
                        sprite = Platform(x, y, tileSurface)
                    elif 'Helicopters' in sType or 'Saws' in sType:
                        spriteData = {
                            '0': ['horizontal', 192],
                            '1': ['horizontal', 320],
                            '2': ['horizontal', 512],
                            '3': ['vertical', 192],
                            '4': ['vertical', 320],
                            '5': ['vertical', 512]
                        }
                        currentSpriteData = spriteData[val]
                        if sType == 'Helicopters':
                            sprite = Helicopter(x, y, currentSpriteData[0], currentSpriteData[1], reverse = self.reversedObjects['helicopters'] % 2)
                            self.reversedObjects['helicopters'] += 1
                        else:
                            sprite = Saw(x, y, currentSpriteData[0], currentSpriteData[1], reverse = self.reversedObjects['saws'] % 2)
                            self.reversedObjects['saws'] += 1
                            if sprite.directionType == 'horizontal':
                                y = sprite.startPos[1] - 20
                                left, right = int(sprite.startPos[0]) + 36, int(sprite.endPos[0]) - 36
                                for x in range(left, right, 16):
                                    chainSprite = StaticObject(x, y, '188')
                                    if 'Future' in sType:
                                        self.futureBgSprites.add(chainSprite)
                                    else:
                                        self.pastBgSprites.add(chainSprite)
                            else:  # Vertical
                                x = sprite.startPos[0] + 36
                                top, bottom = int(sprite.startPos[1]) - 20, int(sprite.endPos[1]) - 84
                                for y in range(top, bottom, 16):
                                    chainSprite = StaticObject(x, y, '188')
                                    if 'Future' in sType:
                                        self.futureBgSprites.add(chainSprite)
                                    else:
                                        self.pastBgSprites.add(chainSprite)
                    elif sType == 'Decoration':
                        sprite = StaticObject(x, y, val)

                        # Special Objects
                        if val == '179':
                            sprite.trim(31, 62)  # Trimming
                        elif val == '180':
                            particleSpawner = ParticleSpawner(x + 2 * tileSize, y - 3 * tileSize, 'leaf', self.displaySurface, self.cameraGroup)
                            self.particleSpawnersSprites.add(particleSpawner)  # Leaf Particles
                        elif val == '187':
                            particleSpawner = ParticleSpawner(x + 2 * tileSize, y - 3 * tileSize, 'fadeLeaf', self.displaySurface, self.cameraGroup)
                            self.futureParticleSpawnersSprites.add(particleSpawner)  # Fade Leaf Particles

                    elif sType == 'Bonuses':
                        bonusesTileList = importCutGraphics('assets/images/tilesets/bonuses.png')
                        tileSurface = bonusesTileList[int(val)]
                        if val == '0':  # Jump Boost
                            particleSource = ParticleSource(x + tileSize / 2, y + tileSize / 2, '7', self.displaySurface, self.cameraGroup)
                            self.particleSourcesSprites.add(particleSource)
                            sprite = Bonus(x, y, tileSurface, val, particleSource)
                        elif val == '1':  # Speed Boost
                            particleSource = ParticleSource(x + tileSize / 2, y + tileSize / 2, '8', self.displaySurface, self.cameraGroup)
                            self.particleSourcesSprites.add(particleSource)
                            sprite = Bonus(x, y, tileSurface, val, particleSource)
                        elif val == '2':  # Shield
                            particleSource = ParticleSource(x + tileSize / 2, y + tileSize / 2, '9', self.displaySurface, self.cameraGroup)
                            self.particleSourcesSprites.add(particleSource)
                            sprite = Bonus(x, y, tileSurface, val, particleSource)
                    elif sType == 'ScriptedObjects':
                        if val == '0':  # Energy Explosion
                            sprite = EnergyExplosion(x, y)
                        elif val == '1':
                            sprite = FenceGateController(x, y)
                        elif val == '2':
                            sprite = VerticalTrigger(x, self.levelSize[1] * tileSize, self.triggerId)
                            self.triggerId += 1
                        elif val == '3':
                            sprite = MidDoor(x, y)
                            particleSource = ParticleSource(x + 96, y + 96, '6', self.displaySurface, self.cameraGroup)
                            self.particleSourcesSprites.add(particleSource)
                    elif sType == 'AnimatedObjects':
                        if val == '0':  # Alarm
                            sprite = Alarm(x, y, val)
                    elif sType == 'ParticleSources':
                        sprite = ParticleSource(x, y, val, self.displaySurface, self.cameraGroup)
                    elif sType == 'Npcs':
                        if val == '0':  # Marcus (Intro)
                            sprite = Marcus((x, y), self)
                        elif val == '1':  # Marcus (At Corps)
                            sprite = MarcusAtCorps((x, y), self)
                        elif val == '2':  # History Teacher
                            sprite = HistoryTeacher((x, y), self)
                        elif val == '3':  # France Teacher
                            sprite = FranceTeacher((x, y), self)
                        elif val == '4':  # Maths Teacher
                            sprite = MathsTeacher((x, y), self)

                    spriteGroup.add(sprite)

        return spriteGroup

    def setupLevel(self):
        # Camera Setup, Level size needed for Background Clipping calculation
        self.cameraGroup = CameraGroup(self)
        self.player = pygame.sprite.GroupSingle()

        # Fades Setup
        if not self.disableFades:
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

        # Particle Spawners Setup
        self.particleSpawnersSprites = pygame.sprite.Group()

        # Future Particle Spawners Setup
        self.futureParticleSpawnersSprites = pygame.sprite.Group()

        # Past Particle Spawners Setup
        self.pastParticleSpawnersSprites = pygame.sprite.Group()

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

        # Bonuses Setup
        bonusesLayout = importCsvLayout(self.levelData.get('Bonuses'))
        self.bonusesSprites = self.createTileGroup(bonusesLayout, 'Bonuses')

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

        # What Scripted Objects will add to Camera depends on Time Condition
        timeCondBgScriptedObjects = pygame.sprite.Group([sprite for sprite in self.bgScriptedObjectsSprites if not hasattr(sprite, 'inPast') or sprite.inPast == self.inPast])
        timeCondScriptedObjects = pygame.sprite.Group([sprite for sprite in self.scriptedObjectsSprites if not hasattr(sprite, 'inPast') or sprite.inPast == self.inPast])

        # Adding Basic Sprites (Pt 1)
        self.cameraGroup.add(self.underBgDecorationSprites)
        self.cameraGroup.add(self.backgroundSprites)
        self.cameraGroup.add(self.groundSprites)
        self.cameraGroup.add(self.bgDecorationSprites)
        self.cameraGroup.add(self.decorationSprites)
        self.cameraGroup.add(timeCondBgScriptedObjects)

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
            self.cameraGroup.add(self.bonusesSprites)
            self.cameraGroup.add(self.futurePlatforms)
            self.cameraGroup.add(self.futureHelicopters)
            self.cameraGroup.add(self.futureSaws)

        # Adding Basic Sprites (Pt 2)
        self.cameraGroup.add(self.npcSprites)
        self.cameraGroup.add(self.player)
        self.cameraGroup.add(self.goal)
        self.cameraGroup.add(self.particleSpawnersSprites)
        if self.inPast:  # Adding Particles depending on current time
            self.cameraGroup.add(self.pastParticleSpawnersSprites)
            self.cameraGroup.add(self.pastParticleSourcesSprites)
            self.cameraGroup.add(self.pastFadesSprites)
        else:
            self.cameraGroup.add(self.futureParticleSpawnersSprites)
            self.cameraGroup.add(self.particleSourcesSprites)
            self.cameraGroup.add(self.futureFadesSprites)
        if not self.disableFades:
            self.cameraGroup.add(self.fadesSprites)
        self.cameraGroup.add(timeCondScriptedObjects)

        # Defining Collideable Sprites
        if self.inPast:
            self.player.sprite.collideableSprites = self.groundSprites.sprites() + self.pastGroundSprites.sprites() + \
                                                    self.decorationSprites.sprites() + self.pastObjectsSprites.sprites()
            self.player.sprite.onTopCollideableSprites = self.pastPlatforms.sprites() + self.pastHelicopters.sprites()
        else:
            self.player.sprite.collideableSprites = self.groundSprites.sprites() + self.futureGroundSprites.sprites() + \
                                                    self.decorationSprites.sprites() + self.futureObjectsSprites.sprites()
            self.player.sprite.onTopCollideableSprites = self.futurePlatforms.sprites() + self.futureHelicopters.sprites()

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
                self.lastPlayerPositions['past'] = self.player.sprite.hitbox.topleft
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
            self.cameraGroup.add(self.bonusesSprites)
            self.cameraGroup.add(self.futurePlatforms)
            self.cameraGroup.add(self.futureHelicopters)
            self.cameraGroup.add(self.futureSaws)
        else:
            if self.player.sprite.onGround:
                self.lastPlayerPositions['future'] = self.player.sprite.hitbox.topleft
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
            self.cameraGroup.add(self.pastParticleSpawnersSprites)
            self.cameraGroup.add(self.pastParticleSourcesSprites)
            self.cameraGroup.add(self.pastFadesSprites)
            self.bgImage = self.pastBgImage
        else:
            self.cameraGroup.add(self.futureParticleSpawnersSprites)
            self.cameraGroup.add(self.particleSourcesSprites)
            self.cameraGroup.add(self.futureFadesSprites)
            self.bgImage = self.futureBgImage
        if not self.disableFades:
            self.cameraGroup.add(self.fadesSprites)
        self.cameraGroup.add(timeCondScriptedObjects)

        # Defining Collideable Sprites
        if self.inPast:
            self.player.sprite.collideableSprites = self.groundSprites.sprites() + self.pastGroundSprites.sprites() + \
                                                    self.decorationSprites.sprites() + self.pastObjectsSprites.sprites()
            self.player.sprite.onTopCollideableSprites = self.pastPlatforms.sprites() + self.pastHelicopters.sprites()
        else:
            self.player.sprite.collideableSprites = self.groundSprites.sprites() + self.futureGroundSprites.sprites() + \
                                                    self.decorationSprites.sprites() + self.futureObjectsSprites.sprites()
            self.player.sprite.onTopCollideableSprites = self.futurePlatforms.sprites() + self.futureHelicopters.sprites()

        # Resetting Player's Direction to prevent from noclipping
        self.player.sprite.direction = pygame.Vector2()

        # Changing Music
        if self.levelData.get('FutureMusic') and not self.inPast:
            self.setBackgroundMusic(self.levelData.get('FutureMusic'), fade=1)
        elif self.levelData.get('PastMusic') and self.inPast:
            self.setBackgroundMusic(self.levelData.get('PastMusic'), fade=1)
        elif self.levelParameters.get('musicSwitching', True):
            self.setBackgroundMusic(self.levelData.get('LevelMusic'), fade=1)

        # Snow Particles
        for particleSpawner in self.cameraGroup.guiParticles:
            if isinstance(particleSpawner, ParticleSpawner):
                self.cameraGroup.guiParticles.remove(particleSpawner)
        addSnow = self.levelParameters.get('snow')
        if (addSnow == 'all') or (addSnow == 'past' and self.inPast) or (addSnow == 'future' and not self.inPast):
            self.createGuiParticles('snow', 'spawner', 0, 0)

        # Inform Marcus about Player used PTTD
        for npc in self.npcSprites:
            if isinstance(npc, MarcusAtCorps) and npc.readyToCall and not self.inPast:
                npc.phoneCall()

        # PTTD Use Particles
        if self.hasTimeMachine:
            self.createGuiParticles('5', x = screenSize[0] - 192, y = screenSize[1] - 152, lifetime = 20)

        # Screen Shake & Flash Effect
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
                    sprite.collectSound.set_volume(0.2 * int(self.config.get('effectsVolume', 'Settings')) / 100)
                    self.player.add(sprite)
                    self.lastPlayerPositions['init'] = (x, y)
                elif val == '1':
                    goalSurf = pygame.image.load('assets/images/character/goal.png').convert_alpha()
                    sprite = StaticTile(x, y, goalSurf)
                    sprite.drawable = False  # Defining Goal Visibility
                    self.goal.add(sprite)

    def checkBgScriptedObjectsCollision(self):
        for obj in self.bgScriptedObjectsSprites:
            if isinstance(obj, FenceGateController):
                if pygame.sprite.collide_rect(self.player.sprite, obj):
                    obj.changeOutline(1)
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_e]:
                        self.forceFinish = True
                    if not any(hint.parent == obj for hint in self.hints):
                        hint = Hint(obj.rect.midtop, obj, 'Войти', 'e')
                        hint.printingSound.set_volume(int(self.config.get('interfaceVolume', 'Settings')) / 100 * 0.5)
                        self.hints.append(hint)
                else:
                    obj.changeOutline(0)
                    for hint in self.hints:
                        if hint.parent == obj:
                            self.hints.remove(hint)
            elif isinstance(obj, VerticalTrigger) and self.triggerActions:
                if pygame.sprite.collide_rect(self.player.sprite, obj):
                    if self.triggerActions[obj.id] == 'MarcusInit':
                        for sprite in self.npcSprites:
                            if isinstance(sprite, MarcusAtCorps):
                                sprite.storytelling()
                                # noinspection PyTypeChecker
                                self.bgScriptedObjectsSprites.remove(obj)
                    elif self.triggerActions[obj.id] == 'MarcusQuestComplete' and self.inPast:
                        if 'Notebook' in self.playerInventory:
                            for sprite in self.npcSprites:
                                if isinstance(sprite, MarcusAtCorps):
                                    sprite.questComplete()
                                    self.player.sprite.facingRight = True
                                    self.playerInventory.remove('Notebook')
                                    # noinspection PyTypeChecker
                                    self.bgScriptedObjectsSprites.remove(obj)
            elif isinstance(obj, MidDoor):
                if pygame.sprite.collide_rect(self.player.sprite, obj) and obj.inPast == self.inPast and not obj.stage:
                    obj.changeOutline(1)
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_e]:
                        self.screenFadeEffect(2, 3, 2)
                        self.playerControllability = False
                        self.playerInventory.append('Notebook')
                        threading.Timer(6, self.createFoundItemAnimation, ['Notebook', 'Тетрадь профессора']).start()
                        threading.Timer(6, self.completeObjective, ['Найти Тетрадь профессора']).start()
                        threading.Timer(8, self.switchPlayerControllability, [True]).start()
                        obj.stage = 1
                    if not any(hint.parent == obj for hint in self.hints):
                        hint = Hint(obj.rect.midtop, obj, 'Войти', 'e')
                        hint.printingSound.set_volume(int(self.config.get('interfaceVolume', 'Settings')) / 100 * 0.5)
                        self.hints.append(hint)
                else:
                    obj.changeOutline(0)
                    for hint in self.hints:
                        if hint.parent == obj:
                            self.hints.remove(hint)

    def checkBonusCollect(self):
        for bonus in self.bonusesSprites:
            if bonus.rect.colliderect(self.player.sprite.hitbox):
                bonus.collect(self.player.sprite)

    def constraintsCheck(self):
        playerCollisionRect = self.player.sprite.collisionRect
        if playerCollisionRect.left <= 0:
            playerCollisionRect.left = 0
        elif playerCollisionRect.right >= self.levelSize[0] * tileSize:
            playerCollisionRect.right = self.levelSize[0] * tileSize

        if playerCollisionRect.bottom >= self.levelSize[1] * tileSize:
            self.death = True

    def damageObjectsCollisionCheck(self):
        if self.inPast: damageObjects = self.pastSaws
        else: damageObjects = self.futureSaws

        for obj in damageObjects:
            if obj.rect.colliderect(self.player.sprite.hitbox):
                self.player.sprite.applyDamage()

    def checkFinish(self):
        if self.finishProgress > 0:
            self.finishProgress += 1
            self.transition = self.finishProgress
            self.player.sprite.direction = pygame.Vector2(0, 0)
            self.player.sprite.transparency = min(100, round(300 * self.finishProgress / 70))
            if self.finishProgress >= 70:
                for thread in threading.enumerate():
                    if isinstance(thread, threading.Timer):
                        thread.cancel()
                pygame.mouse.set_visible(True)
                if not self.death:
                    # Saving Current Progress to Config
                    nextLevelId = int(self.config.get('level', 'Progress')) + 1
                    self.config.set('level', str(nextLevelId), 'Progress')
                    self.config.set('objectives', ' | '.join([objective.text for objective in self.objectives]), 'Progress')
                    self.config.save()
                    self.createLevel(self.levelData['nextLevel'], self.objectives)
                else:
                    # Moving Player to Last coordinates
                    if self.inPast and self.lastPlayerPositions['past'] != (0, 0):
                        pos = self.lastPlayerPositions['past']
                    elif not self.inPast and self.lastPlayerPositions['future'] != (0, 0):
                        pos = self.lastPlayerPositions['future']
                    else:
                        pos = self.lastPlayerPositions['init']

                    self.player.sprite.reset(pos)
                    self.playerControllability = True
                    self.death = False
                    self.finishProgress = 0
                    self.transition = 60
        else:
            if not self.levelParameters:
                timeCond = 1
            elif self.levelParameters.get('finishTime') == 'past':
                timeCond = self.inPast
            else:
                timeCond = not self.inPast

            player_sprite = self.player.sprite
            goal_collided = pygame.sprite.spritecollide(player_sprite, self.goal, False)

            if (goal_collided and timeCond) or self.forceFinish or self.death:
                if not self.death: self.levelMusic.fadeout(2000)
                else: self.player.sprite.damageTakenSound.play()
                self.switchPlayerControllability(False)
                self.player.sprite.playerGravity = 0
                self.finishProgress = 1

    def run(self):
        # Keyboard Input
        self.input()

        # Rendering
        self.cameraGroup.render()

        # Checking Collisions
        self.checkBgScriptedObjectsCollision()
        self.checkBonusCollect()
        self.damageObjectsCollisionCheck()
        self.checkFinish()

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

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            for thread in threading.enumerate():
                if isinstance(thread, threading.Timer):
                    thread.cancel()
            pygame.mouse.set_visible(True)
            self.levelMusic.stop()
            self.createMenu()