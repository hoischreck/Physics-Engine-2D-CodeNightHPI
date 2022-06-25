from __future__ import annotations

from abc import ABC, abstractmethod

from PygameCollection.gameObjects import GraphicalObj
from PygameCollection.math import Vector2D

from map import Wall


class PhysicsObj(GraphicalObj):  # ABC
    def __init__(self, game, pos: Vector2D, velocity: Vector2D, mass: float, elasticity: float):
        super().__init__(game)
        self.game = game

        self.pos = pos
        self.prev_pos = self.pos
        self.step_movement = Vector2D(0, 0)
        self.step_acc = Vector2D(0, 0)

        self.mass = mass
        self.elasticity = elasticity
        self.apply_elasticity = False

        self.v = velocity
        self.color = (0, 0, 0, 0)

    @abstractmethod
    def draw(self, screen=None):
        pass

    @abstractmethod
    def step(self, dt: float):
        pass

    @abstractmethod
    def collide(self, dt: float, other: PhysicsObj):
        pass

    @abstractmethod
    def collideMap(self, dt: float, wall: Wall):
        pass

    @abstractmethod
    def postCollide(self, dt: float):
        pass


class PhysicsManager:
    G = Vector2D(0, 9.81 / 10)
    dt = 0.1

    def __init__(self, game):
        self.game = game
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

    def applyCollisionsMap(self):
        for obj in self.physicObjs:
            for wall in self.game.map.walls:
                obj.collideMap(self.dt, wall)

    def applyPostCollisions(self):
        for obj in self.physicObjs:
            obj.postCollide(self.dt)
