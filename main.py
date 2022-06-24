from __future__ import annotations

from numpy import tan

from PygameCollection.game import Base2DGame
from PygameCollection.gameObjects import GraphicalObj
from PygameCollection.math import Line2D, Vector2D
from abc import ABC, abstractmethod
import pygame
pygame.init()


class PhysicsObj(GraphicalObj):  # ABC
    def __init__(self, game, pos: Vector2D, velocity: Vector2D, mass: float, elasticity: float):
        super().__init__(game)
        self.pos = pos
        self.prev_pos = self.pos
        self.step_movement = Vector2D(0, 0)
        self.step_acc = Vector2D(0, 0)

        self.mass = mass
        self.elasticity = elasticity

        self.v = velocity
        self.color = (0, 0, 0, 0)

    def step(self, dt: float):
        self.v = self.v + Vector2D(0, 0)  # todo acceleration

        self.prev_pos = self.pos
        self.pos = self.pos + (self.v * dt)

    def collide(self, dt: float, other: PhysicsObj):
        distance = self.pos - other.pos
        if distance.magnitude() < (self.radius + other.radius):
            # move back
            speed_factor = 0
            if self.v.magnitude() > 0:
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
            diff = tangentLine.reflectVector(diff)

            self.step_acc = self.step_acc + diff

    def postCollide(self, dt: float):
        self.pos = self.pos + self.step_movement
        self.step_movement = Vector2D(0, 0)

        self.v = self.v + self.step_acc
        if self.step_acc.magnitude() > 0:
            self.v = self.v * self.elasticity
        self.step_acc = Vector2D(0, 0)


class PhysicsCircle(PhysicsObj):
    def __init__(self, game, pos, velocity, mass, elasticity, radius):
        super().__init__(game, pos, velocity, mass, elasticity)
        self.radius = radius

    #todo: flip

    def draw(self, screen=None):
        s = self.screen if screen is None else screen
        pygame.draw.circle(s, self.color, self.pos.toTuple(), self.radius, 1)


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
        self.tps = 30

    def setup(self):
        clock = pygame.time.Clock()
        clock.tick(self.tps)

        self.physicsManager = PhysicsManager()

        self.physicsManager.addObj(
            PhysicsCircle(self, pos=Vector2D(200, 200), velocity=Vector2D(
                15, 20), mass=500, elasticity=0.3, radius=50)
        )
        self.physicsManager.addObj(
            PhysicsCircle(self, pos=Vector2D(
                400, 400), velocity=Vector2D(-20, -20), mass=200, elasticity=0.8, radius=20)
        )
        self.physicsManager.addObj(
            PhysicsCircle(self, pos=Vector2D(450, 300), velocity=Vector2D(
                1, 0.5), mass=50, elasticity=0.9, radius=5)
        )

        self.drawingQueue.append(self.physicsManager)

    def loop(self):
        self.physicsManager.applyStep()
        self.physicsManager.applyCollisions()
        self.physicsManager.applyPostCollisions()


if __name__ == "__main__":
    i = PhysicsSim2D()
    i.run()
