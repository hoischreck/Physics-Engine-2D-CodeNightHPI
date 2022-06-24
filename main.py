from __future__ import annotations

from PygameCollection.game import Base2DGame
from PygameCollection.gameObjects import GraphicalObj
from PygameCollection.math import Vector2D
from abc import ABC, abstractmethod
import pygame
pygame.init()


class PhysicsObj(GraphicalObj): #ABC
    def __init__(self, game, pos: Vector2D, velocity: Vector2D, mass: float):
        super().__init__(game)
        self.pos = pos
        self.prev_pos = self.pos
        self.step_movement = Vector2D(0, 0)
        self.step_acc = Vector2D(0, 0)

        self.mass = mass

        self.v = velocity
        self.color = (0, 0, 0, 0)

    def step(self, dt: float):
        self.v = self.v + Vector2D(0, 0) # todo accelation

        self.prev_pos = self.pos
        self.pos = self.pos + (self.v * dt)

    def collide(self, dt: float, other: PhysicsObj):
        distance = self.pos - other.pos
        if distance.magnitude() < (self.radius + other.radius):
            # calculate the new speed
            v = (
                self.v * self.mass + 
                (other.v * 2 - self.v) * other.mass
            ) / (
                self.mass + other.mass
            )

            # calculate difference between new pseed and current speed
            diff = v - self.v

            self.step_acc = self.step_acc + diff
            #print("collision")
    
    def postCollide(self, dt: float):
        self.pos = self.pos + self.step_movement
        self.step_movement = Vector2D(0, 0)

        self.v = self.v + self.step_acc
        self.step_acc = Vector2D(0, 0)

class PhysicsCircle(PhysicsObj):
    def __init__(self, game, pos, velocity, mass, radius):
        super().__init__(game, pos, velocity, mass)
        self.radius = radius


    #todo: flip
    def draw(self, screen=None):
        s = self.screen if screen is None else screen
        pygame.draw.circle(s, self.color, self.pos.toTuple(), self.radius)


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
        #self.windowCaption = "2D-Physics-Engine" #todo: implement
        self.windowSize = (1080, 720)
        self.physicsManager = None

    def setup(self):
        self.physicsManager = PhysicsManager()
        self.physicsManager.addObj(
            PhysicsCircle(self, pos=Vector2D(100, 100), velocity=Vector2D(20, 0), mass=500, radius=20)
        )
        self.physicsManager.addObj(
            PhysicsCircle(self, pos=Vector2D(200, 100), velocity=Vector2D(1, 0), mass=50, radius=15)
        )
        self.physicsManager.addObj(
            PhysicsCircle(self, pos=Vector2D(500, 100), velocity=Vector2D(-20, 0), mass=500, radius=15)
        )

        self.drawingQueue.append(self.physicsManager)

    def loop(self):
        self.physicsManager.applyStep()
        self.physicsManager.applyCollisions()
        self.physicsManager.applyPostCollisions()


if __name__ == "__main__":
    i = PhysicsSim2D()
    i.run()