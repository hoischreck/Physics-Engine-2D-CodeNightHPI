from __future__ import annotations
from random import random, randrange

from map import Map
from circle import PhysicsCircle
from physics import PhysicsManager

from PygameCollection.game import Base2DGame
from PygameCollection.math import Vector2D
import pygame
pygame.init()


class PhysicsSim2D(Base2DGame):
    def __init__(self):
        super().__init__(windowSize=(1080, 720))
        # self.windowCaption = "2D-Physics-Engine" #todo: implement
        self.physicsManager = None
        self.tps = 60

    def setup(self):
        clock = pygame.time.Clock()
        clock.tick(self.tps)

        self.physicsManager = PhysicsManager(self)

        for _ in range(0, 25):
            radius = randrange(20, 40)
            self.physicsManager.addObj(
                PhysicsCircle(self, pos=Vector2D(
                    random() * self.windowSize[0], random() * self.windowSize[1]), velocity=Vector2D(
                    randrange(-20, 20), randrange(-20, 20)), mass=radius, elasticity=randrange(30, 90) / 100, radius=radius)
            )

        self.physicsManager.addObj(
            PhysicsCircle(self, pos=Vector2D(200, 200), velocity=Vector2D(
                15, 20), mass=500, elasticity=0.7, radius=50)
        )
        self.physicsManager.addObj(
            PhysicsCircle(self, pos=Vector2D(
                300, 300), velocity=Vector2D(-20, -20), mass=200, elasticity=0.7, radius=20)
        )
        self.physicsManager.addObj(
            PhysicsCircle(self, pos=Vector2D(250, 300), velocity=Vector2D(
                1, 0.5), mass=50, elasticity=0.7, radius=5)
        )

        self.map = Map(self)

        self.map.addWallH((0, 0), self.w)
        self.map.addWallH((0, self.h), self.w)
        self.map.addWallV((0, 0), self.h)
        self.map.addWallV((self.w, 0), self.h)

        self.map.addWall((100, 100), (700, 500))

        self.drawingQueue.append(self.physicsManager)
        self.drawingQueue.append(self.map)

    def loop(self):
        self.physicsManager.applyStep()
        self.physicsManager.applyCollisions()
        self.physicsManager.applyCollisionsMap()
        #self.physicsManager.applyGravity()
        self.physicsManager.applyPostCollisions()


if __name__ == "__main__":
    i = PhysicsSim2D()
    i.run()
