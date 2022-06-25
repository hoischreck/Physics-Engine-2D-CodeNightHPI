from __future__ import annotations
from random import random, randrange

from numpy import true_divide

from map import Map
from circle import PhysicsCircle
from physics import PhysicsManager

from PygameCollection.game import Base2DGame
from PygameCollection.math import Vector2D
import pygame, os
pygame.init()


class PhysicsSim2D(Base2DGame):
    def __init__(self):
        super().__init__(windowSize=(1080, 720))
        # self.windowCaption = "2D-Physics-Engine" #todo: implement
        self.physicsManager = None
        self.tps = 60
        self.gravityGobal = True
        self.objectGravity = False
        self.collisionActive = True
        self.spawnDelay = 5
        self.lastSpawn = 0

        self.startPos, endPos = None, None
        self.spawnSpeed = 10

    def setup(self):
        clock = pygame.time.Clock()
        clock.tick(self.tps)

        self.physicsManager = PhysicsManager(self)

        # for _ in range(0, 25):
        #     radius = randrange(20, 40)
        #     self.physicsManager.addObj(
        #         PhysicsCircle(self, pos=Vector2D(
        #             random() * self.windowSize[0], random() * self.windowSize[1]), velocity=Vector2D(
        #             randrange(-20, 20), randrange(-20, 20)), mass=radius, elasticity=randrange(30, 90) / 100, radius=radius)
        #     )
        #
        # self.physicsManager.addObj(
        #     PhysicsCircle(self, pos=Vector2D(200, 200), velocity=Vector2D(
        #         15, 20), mass=500, elasticity=0.7, radius=50)
        # )
        # self.physicsManager.addObj(
        #     PhysicsCircle(self, pos=Vector2D(
        #         300, 300), velocity=Vector2D(-20, -20), mass=200, elasticity=0.7, radius=20)
        # )
        # self.physicsManager.addObj(
        #     PhysicsCircle(self, pos=Vector2D(250, 300), velocity=Vector2D(
        #         1, 0.5), mass=50, elasticity=0.7, radius=5)
        # )

        self.map = Map(self)
        self.map.load(os.path.join("Map", "base"))

        # self.map.addWallH((0, 0), self.w)
        # self.map.addWallH((0, self.h), self.w)
        # self.map.addWallV((0, 0), self.h)
        # self.map.addWallV((self.w, 0), self.h)

        #self.map.save(os.path.join("Map", "base"))

        #
        # self.map.addWall((100, 100), (700, 500))

        self.drawingQueue.append(self.physicsManager)
        self.drawingQueue.append(self.map)

    def handelInput(self):
        if(self.key.keyUp(pygame.K_o)):
            self.objectGravity= not self.objectGravity
            print("Object Gravity",self.objectGravity)
        if(self.key.keyUp(pygame.K_g)):
            self.gravityGobal= not self.gravityGobal
            print("Golbal Gravity",self.gravityGobal)
        if(self.key.keyUp(pygame.K_c)):
            self.collisionActive= not self.collisionActive
            print("Collisions",self.collisionActive)

        if self.key.heldDown(pygame.K_UP):
            self.spawnSpeed += 1
            print("speed:", self.spawnSpeed)

        if self.key.heldDown(pygame.K_DOWN):
            self.spawnSpeed -= 1
            print("speed:", self.spawnSpeed)

        if self.mouse.mouseUp(1):
            if self.startPos is None:
                self.startPos = self.mouse.getPos()
            else:
                self.endPos = self.mouse.getPos()
                self.physicsManager.addObj(
                    PhysicsCircle(self,
                              pos=Vector2D.fromIterable(self.startPos),
                              velocity=Vector2D.asUnitVector(Vector2D.fromIterable(self.endPos)-Vector2D.fromIterable(self.startPos)) * self.spawnSpeed,
                              mass=50,
                              elasticity=0.7,
                              radius=20
                    )
                )


                self.startPos, self.endPos = None, None

        if self.mouse.heldDown(3) and self.lastSpawn <= 0:
            self.physicsManager.addObj(
                PhysicsCircle(self, pos=Vector2D.fromIterable(self.mouse.getPos()), velocity=Vector2D(
                    0, 0), mass=50, elasticity=0.7, radius=20)
            )
            self.lastSpawn = self.spawnDelay
        self.lastSpawn -= 1

            
    def loop(self):
        self.handelInput()
        self.physicsManager.applyStep()
        if(self.collisionActive):
            self.physicsManager.applyCollisions()
        self.physicsManager.applyCollisionsMap()
        if(self.objectGravity):
             self.physicsManager.applyGravity()
        self.physicsManager.applyPostCollisions()


if __name__ == "__main__":
    i = PhysicsSim2D()
    i.run()
