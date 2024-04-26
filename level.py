from settings import *

from tiles import StaticTile, StaticObject
from functions import importCutGraphics, importCsvLayout
from camera import CameraGroup


class Level:
    def __init__(self, levelData, createMenu, createLevel):
        self.displaySurface = pygame.display.get_surface()
        self.createMenu = createMenu
        self.createLevel = createLevel

        # Level Data
        self.levelData = levelData
        self.levelParameters = self.levelData.get('Parameters', {})

        # Time Travelling
        self.inPast = False
        
        # Tilesets
        self.groundTileList = importCutGraphics('assets/images/tilesets/auditoriumTiles.png')

        # Level Setup
        self.setupLevel()

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
                        groundTileList = self.groundTileList
                        tileSurface = groundTileList[int(val)]
                        sprite = StaticTile(x, y, tileSurface, int(val))
                    elif sType == 'Fades':
                        fadesTileList = importCutGraphics('assets/images/tilesets/fadeTiles.png')
                        tileSurface = fadesTileList[int(val)]
                        sprite = StaticTile(x, y, tileSurface)
                    elif sType == 'Decoration':
                        sprite = StaticObject(x, y, val)

                    spriteGroup.add(sprite)

        return spriteGroup

    def setupLevel(self):
        # Camera Setup, Level size needed for Background Clipping calculation
        self.cameraGroup = CameraGroup()
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
        # self.playerSetup(playerLayout, self.levelData['Parameters'].get('playerFacingRight', True))

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
            self.cameraGroup.add(self.pastPlatforms)
            self.cameraGroup.add(self.pastHelicopters)
            self.cameraGroup.add(self.pastSaws)
        else:
            self.cameraGroup.add(self.futureGroundSprites)
            self.cameraGroup.add(self.futureBgSprites)
            self.cameraGroup.add(self.futureObjectsSprites)
            self.cameraGroup.add(self.futurePlatforms)
            self.cameraGroup.add(self.futureHelicopters)
            self.cameraGroup.add(self.futureSaws)

        # Adding Basic Sprites (Pt 2)
        self.cameraGroup.add(self.player)
        self.cameraGroup.add(self.goal)
        if self.inPast:  # Adding Particles depending on current time
            self.cameraGroup.add(self.pastFadesSprites)
        else:
            self.cameraGroup.add(self.futureFadesSprites)
        self.cameraGroup.add(self.fadesSprites)

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.cameraGroup.offset.x += 4
        elif keys[pygame.K_a]:
            self.cameraGroup.offset.x -= 4
        if keys[pygame.K_w]:
            self.cameraGroup.offset.y -= 4
        elif keys[pygame.K_s]:
            self.cameraGroup.offset.y += 4

    def run(self):
        # Keyboard Input
        self.input()

        # Rendering
        self.cameraGroup.render()