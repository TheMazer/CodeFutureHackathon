from settings import *

import random
from functions import circleSurf
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

    def animate(self):
        glowEffectColor = (20, 20, 20)
        particleBaseDrawable = True
        scalingSpeed = 0.2
        gravity = 0.1

        # Different Particle Types
        if self.particleType == '0':  # Case "Portal" type of Particles
            if self.frame < self.lifetime or self.lifetime == -1:
                self.particles.append([
                    [self.x, self.y],                              # Position
                    [random.randint(0, 30) / 10 - 1.5, -1],  # Speed X, Y
                    random.randint(10, 16)                   # Scale
                ])
            glowEffectColor = (30, 20, 50)
            particleBaseDrawable = True
            scalingSpeed = 0.2
            gravity = 0.1
        elif self.particleType == '3':  # Case "Red Light" type of Particles
            if self.frame < self.lifetime or self.lifetime == -1:
                self.particles.append([
                    [self.x, self.y],                              # Position
                    [0, 0],                                        # Speed X, Y
                    random.randint(10, 16)                   # Scale
                ])
            glowEffectColor = (5, 0, 0)
            particleBaseDrawable = False
            scalingSpeed = 0.5
            gravity = 0

        camOffset = self.cameraClass.offset
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

    def update(self):
        self.animate()
        self.frame += 1