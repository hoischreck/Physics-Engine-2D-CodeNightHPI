import pygame
from PygameCollection.gameObjects import GraphicalObj
from PygameCollection.math import Line2D, Vector2D
import csv


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
    DATA_DELIMITER = ","

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

    def save(self, filepath):
        # saves each wall as a 4 values (start_x, start_y, end_x, end_y)
        with open(f"{filepath}.csv", "w", newline="", encoding="utf8") as f:
            csvWriter = csv.writer(f, delimiter=Map.DATA_DELIMITER)
            csvWriter.writerows([(*w.start.toTuple(), *w.end.toTuple()) for w in self.walls])

    def load(self, filepath):
        with open(f"{filepath}.csv", "r", encoding="utf8") as f:
            csvReader = csv.reader(f, delimiter=Map.DATA_DELIMITER)
            for l in csvReader:
                self.addWall((int(l[0]), int(l[1])), (int(l[2]), int(l[3])))

    def addWallH(self, start, length):
        self.addWall(start, (start[0] + length, start[1]))

    def addWallV(self, start, length):
        self.addWall(start, (start[0], start[1] + length))

    def draw(self, screen=None):
        s = self.screen if screen is None else screen
        for w in self.walls:
            w.draw(s)
