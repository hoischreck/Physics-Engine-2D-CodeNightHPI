import pygame
from PygameCollection.gameObjects import GraphicalObj
from PygameCollection.math import Line2D, Vector2D


class Wall(GraphicalObj):
    def __init__(self, game, start: Vector2D, end: Vector2D):
        super().__init__(game)
        self.line = Line2D(start, end)
        self.color = (0, 0, 0, 0)
        self.width = 2

    def draw(self, screen=None):
        s = self.screen if screen is None else screen
        pygame.draw.line(s, self.color, self.line.start.toTuple(),
                         self.line.end.toTuple(), self.width)


class Map(GraphicalObj):
    def __init__(self, game):
        super().__init__(game)
        self.walls = list()

    def addWall(self, start, end):
        self.walls.append(Wall(self.game, Vector2D.fromIterable(
            start), Vector2D.fromIterable(end)))

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
