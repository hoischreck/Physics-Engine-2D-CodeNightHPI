from PygameCollection.game import Base2DGame
from PygameCollection.gameObjects import GraphicalObj
from PygameCollection.math import Vector2D
from abc import ABC, abstractmethod
import pygame
pygame.init()


class PhysicsObj(GraphicalObj): #ABC
    def __init__(self, game, pos: Vector2D, mass: float, velocity: Vector2D = Vector2D(0, 0)):
        super().__init__(game)
        self.pos = pos
        self.mass = mass

        #self.v0 = Vector2D(0, 0)

        self.v = velocity
        self.color = (0, 0, 0, 0)

    def step(self, dt: float):
        self.v = self.v + PhysicsManager.G * dt

        self.pos = self.pos + self.v


class PhysicsCircle(PhysicsObj):
    def __init__(self, game, pos, mass, velocity, radius):
        super().__init__(game, pos, mass, velocity)
        self.radius = radius


    #todo: flip
    def draw(self, screen=None):
        s = self.screen if screen is None else screen
        pygame.draw.circle(s, self.color, self.pos.toTuple(), self.radius)


class PhysicsManager:
    G = Vector2D(0, 9.81 / 10)

    def __init__(self):
        self.physicObjs = set()

    def addObj(self, obj: PhysicsObj):
        self.physicObjs.add(obj)

    def removeObj(self, obj: PhysicsObj):
        self.physicObjs.remove(obj)

    def draw(self):
        for o in self.physicObjs:
            o.draw()

    def applyStep(self):
        for o in self.physicObjs:
            o.step(0.1)


class PhysicsSim2D(Base2DGame):
    def __init__(self):
        super().__init__()
        #self.windowCaption = "2D-Physics-Engine" #todo: implement
        self.windowSize = (1080, 720)
        self.physicsManager = None

    def setup(self):
        self.physicsManager = PhysicsManager()
        self.physicsManager.addObj(
            PhysicsCircle(self, pos=Vector2D(100, 100), mass=100, radius=10, velocity=Vector2D(2, 2))
        )

        self.drawingQueue.append(self.physicsManager)

    def loop(self):
        self.physicsManager.applyStep()


if __name__ == "__main__":
    i = PhysicsSim2D()
    i.run()