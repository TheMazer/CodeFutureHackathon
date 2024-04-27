from settings import *

import random
from functions import circleSurf, importFolder
from tiles import Tile


class ParticleSource(Tile):
    def __init__(self, x, y, val, surf, cameraClass, lifetime = -1):
        super().__init__(x, y, False)
        self.particleType = val
        self.lifetime = lifetime
        self.surface = surf
        self.cameraClass = cameraClass
        self.frame = 0
        self.x = x
        self.y = y

        self.particles = []

    def animate(self, customOffset):
        glowEffectColor = (20, 20, 20)
        particleBaseDrawable = True
        scalingSpeed = 0.2
        gravity = 0.1

        # Different Particle Types
        if self.particleType == '0':  # Case "Portal" type of Particles
            if self.frame < self.lifetime or self.lifetime == -1:
                self.particles.append([
                    [self.x, self.y],  # Position
                    [random.randint(0, 30) / 10 - 1.5, -1],  # Speed X, Y
                    random.randint(10, 16)  # Scale
                ])
            glowEffectColor = (30, 20, 50)
            particleBaseDrawable = True
            scalingSpeed = 0.2
            gravity = 0.1
        elif self.particleType == '3':  # Case "Red Light" type of Particles
            if self.frame < self.lifetime or self.lifetime == -1:
                self.particles.append([
                    [self.x, self.y],  # Position
                    [0, 0],  # Speed X, Y
                    random.randint(10, 16)  # Scale
                ])
            glowEffectColor = (5, 0, 0)
            particleBaseDrawable = False
            scalingSpeed = 0.5
            gravity = 0
        elif self.particleType == '4':  # Case "Item Glow" type of Particles
            if self.frame < self.lifetime or self.lifetime == -1:
                self.particles.append([
                    [self.x - 32, self.y - 32],  # Position
                    [random.randint(0, 30) / 10 - 1.5,
                     random.randint(0, 30) / 10 - 1.5],  # Speed X, Y
                    random.randint(16, 24)  # Scale
                ])
            glowEffectColor = (60, 50, 20)
            particleBaseDrawable = False
            scalingSpeed = 0.2
            gravity = 0
        elif self.particleType == '5':  # Case "Time Machine" type of Particles
            if self.frame < self.lifetime or self.lifetime == -1:
                self.particles.append([
                    [self.x - 32, self.y - 32],  # Position
                    [random.randint(0, 4) - 2,
                     random.randint(0, 4) - 2],  # Speed X, Y
                    random.randint(2, 8)  # Scale
                ])
            glowEffectColor = (20, 40, 40)
            particleBaseDrawable = True
            scalingSpeed = 0.1
            gravity = 0
        elif self.particleType == '6':  # Case "MidDoor" type of Particles
            if self.frame < self.lifetime or self.lifetime == -1:
                self.particles.append([
                    [self.x - 32, self.y - 32],  # Position
                    [random.randint(0, 3) - 1.5,
                     random.randint(0, 3) - 1.5],  # Speed X, Y
                    random.randint(8, 14)  # Scale
                ])
            glowEffectColor = (10, 20, 20)
            particleBaseDrawable = False
            scalingSpeed = 0.2
            gravity = 0
        elif self.particleType == '7':  # Case "Jump Boost" type of Particles
            if self.frame < self.lifetime or self.lifetime == -1:
                self.particles.append([
                    [self.x - 32, self.y - 32],  # Position
                    [random.randint(0, 2) - 1,
                     random.randint(0, 2) - 1],  # Speed X, Y
                    random.randint(6, 8)  # Scale
                ])
            glowEffectColor = (5, 20, 5)
            particleBaseDrawable = False
            scalingSpeed = 0.2
            gravity = 0
        elif self.particleType == '8':  # Case "Jump Boost" type of Particles
            if self.frame < self.lifetime or self.lifetime == -1:
                self.particles.append([
                    [self.x - 32, self.y - 32],  # Position
                    [random.randint(0, 2) - 1,
                     random.randint(0, 2) - 1],  # Speed X, Y
                    random.randint(6, 8)  # Scale
                ])
            glowEffectColor = (20, 20, 5)
            particleBaseDrawable = False
            scalingSpeed = 0.2
            gravity = 0
        elif self.particleType == '9':  # Case "Jump Boost" type of Particles
            if self.frame < self.lifetime or self.lifetime == -1:
                self.particles.append([
                    [self.x - 32, self.y - 32],  # Position
                    [random.randint(0, 2) - 1,
                     random.randint(0, 2) - 1],  # Speed X, Y
                    random.randint(6, 8)  # Scale
                ])
            glowEffectColor = (5, 5, 20)
            particleBaseDrawable = False
            scalingSpeed = 0.2
            gravity = 0

        camOffset = self.cameraClass.offset if customOffset is None else customOffset
        for particle in self.particles:
            # Moving Particles
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            # Scaling Particles
            particle[2] -= scalingSpeed
            # Applying gravity
            particle[1][1] += gravity
            if particleBaseDrawable:
                pygame.draw.circle(
                    self.surface,
                    (255, 255, 255),
                    (int(particle[0][0]) - camOffset.x + tileSize / 2,
                    int(particle[0][1]) - camOffset.y + tileSize / 2),
                    int(particle[2])
                )

            radius = particle[2] * 2
            self.surface.blit(
                circleSurf(radius, glowEffectColor),
                (int(particle[0][0]) - camOffset.x + tileSize / 2 - radius,
                int(particle[0][1]) - camOffset.y + tileSize / 2 - radius),
                special_flags=pygame.BLEND_RGBA_ADD
            )

            if particle[2] <= 0:
                self.particles.remove(particle)

    def update(self, customOffset = None):
        self.animate(customOffset)
        self.frame += 1


class ParticleSpawner(Tile):
    def __init__(self, x, y, type, surf, cameraClass):
        super().__init__(x, y, False)
        self.isParticleSource = True
        self.particleType = type
        self.surface = surf
        self.cameraClass = cameraClass
        self.x = x
        self.y = y

        self.animationSpeed = 0.1
        self.frames = importFolder('assets/images/tilesets/animatedObjects/particle_textures/' + str(type))
        self.frameIndex = 0
        self.image = self.frames[self.frameIndex]

        self.particles = []

    def animate(self, customOffset):
        if self.particleType == 'leaf' or self.particleType == 'fadeLeaf':
            if random.randint(1, 5) > 4:
                self.particles.append([
                    [self.x + random.randint(-128, 128),
                     self.y + random.randint(-128, 64)],    # Position
                    [random.randint(0, 15) / -10, 0.5],  # Speed X, Y
                    0,                                         # Frame Index
                    self.frames[0]                             # Image
                ])
        else:
            if random.randint(1, 5) > 1:
                self.particles.append([
                    [self.x + random.randint(0, 1920),
                     self.y + random.randint(0, 1080)],  # Position
                    [random.randint(0, 15) / -10, 0.5],  # Speed X, Y
                    0,                                         # Frame Index
                    self.frames[0]                             # Image
                ])

        camOffset = self.cameraClass.offset if customOffset is None else customOffset
        for particle in self.particles:
            # Moving Particles
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            # Applying gravity
            particle[1][1] += 0.01
            # Animating
            particle[2] += self.animationSpeed
            # Removing
            if particle[2] >= len(self.frames):
                self.particles.remove(particle)
            else:
                particle[3] = self.frames[int(particle[2])]

            self.surface.blit(particle[3], (int(particle[0][0]) - camOffset.x + tileSize / 2, int(particle[0][1]) - camOffset.y + tileSize / 2))

    def update(self, customOffset = None):
        self.animate(customOffset)