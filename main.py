from PygameCollection.game import Base2DGame
from PygameCollection.gameObjects import GraphicalObj
from PygameCollection.math import Vector2D, Line2D, Straight2D
from abc import ABC, abstractmethod
from math import sin, pi
import pygame
pygame.init()

from PygameCollection.utils import showVector

class Wall(GraphicalObj):
    def __init__(self, game, start: Vector2D, end: Vector2D):
        super().__init__(game)
        self.line = Line2D(start, end)
        self.color = (0, 0, 0, 0)
        self.width = 2

    def draw(self, screen=None):
        s = self.screen if screen is None else screen
        pygame.draw.line(s, self.color, self.line.start.toTuple(), self.line.end.toTuple(), self.width)


class Map(GraphicalObj):
    def __init__(self, game):
        super().__init__(game)
        self.walls = list()

    def addWall(self, start, end):
        self.walls.append(Wall(self.game, Vector2D.fromIterable(start), Vector2D.fromIterable(end)))

    def addWalls(self, startEndTuples):
        for w in startEndTuples:
            self.addWall(*w)

    def removeWall(self, wall):
        self.walls.remove(wall)

    def removeLast(self, minAmount=0):
        if len(self.walls) > minAmount:
            del self.walls[-1]

    def addWallH(self, start, length):
        self.addWall(start, (start[0] + length, start[1]))

    def addWallV(self, start, length):
        self.addWall(start, (start[0], start[1] + length))

    def draw(self, screen=None):
        s = self.screen if screen is None else screen
        for w in self.walls:
            w.draw(s)


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

    def step(self, dt: float):
        prevPos = self.pos

        self.v = self.v + PhysicsManager.G * dt
        self.pos = self.pos + self.v


        baseLine = Line2D(prevPos, self.pos)
        offsetH = Vector2D.asUnitVector(baseLine.dV) * self.radius
        lineMiddle = Line2D(baseLine.start+offsetH, baseLine.end-offsetH)
        #

        # todo: check against wall glitching
        # todo: edge case: Ball schneidet ein ganzes Vielfaches von (2k-1)*45°

        pointCollision = False
        for w in self.game.map.walls:
            if (p := lineMiddle.intersectsLinePos(w.line)) is not None or (pointCollision := ((w.line.distanceToPoint(*self.pos.toTuple())) <= self.radius)):
                if pointCollision:
                    p = Vector2D.fromIterable(w.line.closestPointOnLine(*self.pos.toTuple()))
                    #pygame.draw.circle(self.screen, (255, 0, 0), p, 5)
                    d = self.pos-p
                    du = Vector2D.asUnitVector(d)
                    self.pos = self.pos + du * (self.radius-d.magnitude())

                else:
                    d = Vector2D.asUnitVector(baseLine.dV)
                    d.toCounter()

                    self.pos = Vector2D.fromIterable(p) + d * self.radius/sin(d.enclosedAngle(w.line.dV))

                self.v = w.line.reflectVector(self.v)

                #todo: more collision possible?
                break


class PhysicsManager:
    G = Vector2D(0, 9.81 / 80)

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
        super().__init__(windowSize=(1080, 720))
        #self.windowCaption = "2D-Physics-Engine" #todo: implement
        self.physicsManager = None
        self.tps = 60

    def setup(self):
        self.physicsManager = PhysicsManager()
        self.map = Map(self)

        #self.map.walls.add(Wall(self, Vector2D(200, 200), Vector2D(700, 210)))
        #self.map.walls.add(Wall(self, Vector2D(100, 400), Vector2D(1000, 300)))

        self.map.addWallH((0, 0), self.w)
        self.map.addWallH((0, self.h), self.w)
        self.map.addWallV((0, 0), self.h)
        self.map.addWallV((self.w, 0), self.h)

        self.drawingQueue.append(self.physicsManager)
        self.drawingQueue.append(self.map)

    def loop(self):
        self.physicsManager.applyStep()
        #showVector(self.screen, self.c.v, *self.c.pos.toTuple())

        if self.mouse.heldDown(1):
            # create circle
            self.physicsManager.addObj(
                PhysicsCircle(game=self, pos=Vector2D.fromIterable(self.mouse.getPos()), velocity=Vector2D(1, 1), mass=10, radius=20)
            )



if __name__ == "__main__":
    i = PhysicsSim2D()
    i.run()