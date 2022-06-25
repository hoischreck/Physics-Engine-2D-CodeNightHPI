from PygameCollection.math import Line2D, Vector2D
from math import sin
import pygame
from physics import PhysicsManager, PhysicsObj
from map import Wall


class PhysicsCircle(PhysicsObj):
    def __init__(self, game, pos, velocity, mass, elasticity, radius):
        super().__init__(game, pos, velocity, mass, elasticity)
        self.game = game

        self.radius = radius

    #todo: flip
    def draw(self, screen=None):
        s = self.screen if screen is None else screen
        pygame.draw.circle(s, self.color, self.pos.toTuple(), self.radius, 1)

    def step(self, dt: float):
        # gravity
        self.v = self.v + PhysicsManager.G * dt

        self.prev_pos = self.pos
        self.pos = self.pos + (self.v * dt)

    def collide(self, dt: float, other: PhysicsObj):
        # check for collision
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
            move_back = dist_vec * (distance_intersecting * speed_factor + 0.1)

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

    def collideMap(self, dt: float, wall: Wall):

        base_line = Line2D(self.prev_pos, self.pos)
        offset_h = Vector2D.asUnitVector(base_line.dV) * self.radius

        line_middle = Line2D(base_line.start + offset_h,
                             base_line.end - offset_h)

        # todo: check against wall glitching
        # todo: edge case: Ball schneidet ein ganzes Vielfaches von (2k-1)*45°

        point_collision = False

        if (collision_pos := line_middle.intersectsLinePos(wall.line)) is not None or (point_collision := ((wall.line.distanceToPoint(*self.pos.toTuple())) <= self.radius)):
            if point_collision:
                collision_pos = Vector2D.fromIterable(wall.line.closestPointOnLine(*self.pos.toTuple()))
                #pygame.draw.circle(self.screen, (255, 0, 0), p, 5)
                d = self.pos-collision_pos
                du = Vector2D.asUnitVector(d)

                # self.pos = self.pos + du * (self.radius-d.magnitude())
                self.step_movement = self.step_movement + (du * (self.radius-d.magnitude()))

            else:
                d = Vector2D.asUnitVector(base_line.dV)
                d.toCounter()

                # todo
                self.pos = Vector2D.fromIterable(collision_pos) + d * self.radius/sin(d.enclosedAngle(wall.line.dV))

            self.step_acc = self.step_acc - self.v
            self.step_acc = self.step_acc + wall.line.reflectVector(self.v)

            self.apply_elasticity = True

    def gravity(self, dt, other: PhysicsObj):
        G = 1
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

        # damping
        self.v = self.v * 0.999

        if self.pos.x > 1000000 or self.pos.y > 1000000:
            self.v = Vector2D(0, 0)
