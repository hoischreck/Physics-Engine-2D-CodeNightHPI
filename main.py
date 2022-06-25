from __future__ import annotations
from random import random, randrange

from numpy import tan
from numpy.core.multiarray import may_share_memory

from PygameCollection.game import Base2DGame
from PygameCollection.gameObjects import GraphicalObj
from PygameCollection.math import Line2D, Straight2D, Vector2D
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


class PhysicsObj(GraphicalObj):  # ABC
    def __init__(self, game, pos: Vector2D, velocity: Vector2D, mass: float, elasticity: float):
        super().__init__(game)
        self.pos = pos
        self.prev_pos = self.pos
        self.step_movement = Vector2D(0, 0)
        self.step_acc = Vector2D(0, 0)

        self.mass = mass
        self.elasticity = elasticity
        self.apply_elasticity = False

        self.v = velocity
        self.color = (0, 0, 0, 0)

    def step(self, dt: float):
        # gravity
        self.v = self.v + PhysicsManager.G * dt

        self.v = self.v + Vector2D(0, 0)  # todo acceleration

        self.prev_pos = self.pos
        self.pos = self.pos + (self.v * dt)

    def collide(self, dt: float, other: PhysicsObj):
        distance = self.pos - other.pos
        if distance.magnitude() < (self.radius + other.radius):
            # move back
            speed_factor = 0
            if not self.v.isZero():
                speed_factor = self.v.magnitude() / (self.v.magnitude() + other.v.magnitude())

            distance_intersecting = (
                self.radius + other.radius) - distance.magnitude()

            dist_vec = self.pos - other.pos
            dist_vec.toUnitVec()
            move_back = dist_vec * (distance_intersecting * speed_factor)

            self.step_movement = self.step_movement + move_back

            # calculate the new speed
            v = (
                self.v * self.mass +
                (other.v * 2 - self.v) * other.mass
            ) / (
                self.mass + other.mass
            )
            tangentLine = Line2D(self.pos, other.pos)

            # calculate difference between new speed and current speed
            diff = v - self.v

            if diff.magnitude() > 0 and diff.magnitude() < 1000000:
                diff = tangentLine.reflectVector(diff)

            self.step_acc = self.step_acc + diff

            if not diff.isZero():
                self.apply_elasticity = True

    def gravity(self, dt, other: PhysicsObj):
        G = 6.6743 * 10 ** -11
        distance = other.pos - self.pos
        gravityForce = G * (self.mass * other.mass) / \
            (distance.magnitude() ** 2)
        distance.toUnitVec()
        distance = distance * gravityForce
        self.step_acc = self.step_acc + distance

    def postCollide(self, dt: float):
        self.pos = self.pos + self.step_movement
        self.step_movement = Vector2D(0, 0)

        self.v = self.v + self.step_acc
        if self.apply_elasticity:
            self.v = self.v * self.elasticity
            self.apply_elasticity = False
        self.step_acc = Vector2D(0, 0)

        if self.pos.x > 1000000 or self.pos.y > 1000000:
            self.v = Vector2D(0, 0)


class PhysicsCircle(PhysicsObj):
    def __init__(self, game, pos, velocity, mass, elasticity, radius):
        super().__init__(game, pos, velocity, mass, elasticity)
        self.radius = radius

    #todo: flip

    def draw(self, screen=None):
        s = self.screen if screen is None else screen
        pygame.draw.circle(s, self.color, self.pos.toTuple(), self.radius, 1)

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
                    p = w.line.closestPointOnLine(*self.pos.toTuple())
                    #pygame.draw.circle(self.screen, (255, 0, 0), p, 5)

                d = Vector2D.asUnitVector(baseLine.dV)
                d.toCounter()

                self.pos = Vector2D.fromIterable(p) + d * self.radius/sin(d.enclosedAngle(w.line.dV))

                self.v = w.line.reflectVector(self.v)

                #todo: more collision possible?
                break




class PhysicsManager:
    G = Vector2D(0, 9.81 / 10)
    dt = 0.1

    def __init__(self):
        self.physicObjs = set()

    def addObj(self, obj: PhysicsObj):
        self.physicObjs.add(obj)

    def removeObj(self, obj: PhysicsObj):
        self.physicObjs.remove(obj)

    def draw(self):
        for obj in self.physicObjs:
            obj.draw()

    def applyStep(self):
        for obj in self.physicObjs:
            obj.step(self.dt)

    def applyGravity(self):
        for obj in self.physicObjs:
            for other in self.physicObjs:
                if obj is not other:
                    obj.gravity(self.dt, other)

    def applyCollisions(self):
        for obj in self.physicObjs:
            for other in self.physicObjs:
                if obj is not other:
                    obj.collide(self.dt, other)

    def applyPostCollisions(self):
        for obj in self.physicObjs:
            obj.postCollide(self.dt)


class PhysicsSim2D(Base2DGame):
    def __init__(self):
        super().__init__()
        # self.windowCaption = "2D-Physics-Engine" #todo: implement
        self.windowSize = (1080, 720)
        self.physicsManager = None
        self.tps = 60

    def setup(self):
        clock = pygame.time.Clock()
        clock.tick(self.tps)

        self.physicsManager = PhysicsManager()

        # for _ in range(0, 100):
        #     radius = randrange(20, 80)
        #     self.physicsManager.addObj(
        #         PhysicsCircle(self, pos=Vector2D(
        #             random() * self.windowSize[0], random() * self.windowSize[1]), velocity=Vector2D(
        #             randrange(-20, 20), randrange(-20, 20)), mass=radius, elasticity=randrange(10, 99) / 100, radius=radius)
        #     )

        self.physicsManager.addObj(
            PhysicsCircle(self, pos=Vector2D(200, 200), velocity=Vector2D(
                15, 20), mass=(5.972 * (10 ** 12)), elasticity=0.1, radius=50)
        )
        self.physicsManager.addObj(
            PhysicsCircle(self, pos=Vector2D(
                400, 400), velocity=Vector2D(-20, -20), mass=200, elasticity=0.1, radius=20)
        )
        self.physicsManager.addObj(
            PhysicsCircle(self, pos=Vector2D(450, 300), velocity=Vector2D(
                1, 0.5), mass=50, elasticity=0.1, radius=5)
        )
        
        
        self.map = Map(self)
        #self.map.walls.add(Wall(self, Vector2D(200, 200), Vector2D(700, 210)))
        #self.map.walls.add(Wall(self, Vector2D(100, 400), Vector2D(1000, 300)))

        self.map.addWallH((100, 100), 800)
        self.map.addWallH((100, 400), 800)
        self.map.addWallV((100, 100), 300)
        self.map.addWallV((900, 100), 300)

        self.drawingQueue.append(self.physicsManager)
        self.drawingQueue.append(self.map)

    def loop(self):
        self.physicsManager.applyStep()
        self.physicsManager.applyCollisions()
        self.physicsManager.applyPostCollisions()
        self.physicsManager.applyGravity()

        #showVector(self.screen, self.c.v, *self.c.pos.toTuple())

if __name__ == "__main__":
    i = PhysicsSim2D()
    i.run()
