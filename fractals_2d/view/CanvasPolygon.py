from model.Point import *
from view.Settings import *
from view.CanvasLine import *
from view.CanvasSegment import *
from view.Point_2d import *
import time


class CanvasPolLine:
    def __init__(self, points, color=Settings.COLOR_LINE, width=2, showComments=True, segmentOrClipper=True,
                 InOrOut=True, diffColors=False):
        self.points = points

        self.segmentOrClipper = segmentOrClipper

        self.colorLine = color
        self.colorPoints = color

        self.width = width

        self.lines = []
        self.updateLines()

        self.showComments = showComments

        self.pixels = []
        self.startPixel = None

        self.fillFlag = False
        self.WasGo = False
        self.cutArea = []

        self.InOrOut = InOrOut
        self.diffColors = diffColors

        self.resArea = []

    def getCoordPoints(self, field):
        res = []
        for p in self.points:
            # coord = p.coordShift(field)
            res.append((p.x, p.y))
        return res

    def changeStartPixel(self, newX, newY, color, showComments=False):
        self.startPixel = Pixel(x=newX, y=newY, color=color, showComments=showComments)

    def findFieldLines(self, field):
        for l in self.lines:
            l.findFieldLine(field)

    def updatePixels(self, field, cutPixels=[]):
        setCutPixels = set()
        for p in cutPixels:
            setCutPixels.add((p.x, p.y))

        self.pixels.clear()

        for l in self.lines:
            l.findFieldLine(field)


    def show(self, field):

        self.updateLines()

        for l in self.lines:
            l.needDash = len(self.cutArea) != 0
            l.show(field)

        if self.cutArea:
            res = []
            for p in self.cutArea:
                res.append((field.XShiftPC(p[0]), field.YShiftPC(p[1])))

            for i in range(len(res) - 1, -1, -1):
                self.resArea.append(field.create_line(res[i], res[i - 1], fill=Settings.COLOR_DEL, width=3))


    def updateWasGoFlag(self, newValue):
        self.WasGo = newValue

    def showWithDelay(self, field):
        for p in self.points:
            p.show(field)

        self.updateLines()
        for l in self.lines:
            l.show(field)

        if self.startPixel:
            self.startPixel.showLikePoint(field)

    def hide(self, field):
        for l in self.lines:
            l.hide(field)

        self.lines.clear()

        if self.resArea:
            for l in self.resArea:
                field.delete(l)
            self.resArea = []

    def addPoint(self, field, newPoint, color=None):
        if len(self.points) > 0:
            self.lines.append(CanvasSegment(self.points[-1], newPoint, color if color else self.colorPoints))

        self.points.append(newPoint)
        self.reShow(field)

    def reShowWithDelay(self, field, cutPixels=[], startPixel=Pixel(x=0, y=0, color=Settings.COLOR_NEW_POINT)):
        self.hide(field)
        self.pixels.clear()
        self.showWithDelay(field)

        for l in self.lines:
            l.findFieldLine(field)

        setCutPixels = set()
        for p in cutPixels:
            setCutPixels.add((p.x, p.y))

    def reShow(self, field):
        self.hide(field)
        self.show(field)

    def delPoint(self, field, delPoint):
        wasDel = False
        for i, point in enumerate(self.points):
            if Point.isPointsEqual(point, delPoint):
                point.hide(field)
                self.points.pop(i)
                wasDel = True

        if len(self.points) > 1 and self.points[0] != self.points[-1]:
            self.addPoint(field, Point_2d(self.points[0].x, self.points[0].y, self.points[0].color, showComments=self.points[0].showComments))

        self.reShow(field)
        return wasDel

    def updateLines(self):
        self.lines.clear()
        for i in range(len(self.points) - 1):
            if not self.segmentOrClipper:
                self.lines.append(CanvasSegment(self.points[i], self.points[i + 1], self.colorPoints, dash=(50, 1)))
            else:
                self.lines.append(CanvasSegment(self.points[i], self.points[i + 1], self.colorPoints, WasGo=self.WasGo,
                                                cutArea=self.cutArea, InOrOut=self.InOrOut, diffColors=self.diffColors))

    def isPointOn(self, field, X, Y):
        for p in self.points:
            if p.isClick(field, X, Y):
                return True
        return False

    def PointOnWithPoint(self, field, X, Y):
        for p in self.points:
            if p.isClick(field, X, Y):
                return p
        return None

    def updateShowFlag(self, newFlag):
        self.showComments = newFlag
        for p in self.points:
            p.ShowComments = self.showComments

        for pix in self.pixels:
            pix.ShowComments = self.showComments

    def changeColor(self, newColorPoint, newColorLine):
        self.colorLine = newColorLine
        self.colorPoints = newColorPoint

        for point in self.points:
            point.color = self.colorPoints

        for line in self.lines:
            line.color = self.colorPoints

    def rotatePol(self, pointCenter, alpha):
        for point in self.points:
            point.rotate(pointCenter, alpha)
        self.updateLines()

    def shiftPol(self, xShift, yShift):
        for point in self.points:
            point.shift(xShift, yShift)
        self.updateLines()

    def scalePol(self, x, y, kx, ky):
        for point in self.points:
            point.scale(x, y, kx, ky)
        self.updateLines()

    # Проверка, является ли полигон выпуклым
    def isConvexPolygon(self):
        # self.updateLines()
        for i, line in enumerate(self.lines):
            for j, segment in enumerate(self.lines):
                if j != (i - 1) % len(self.lines) and j != i and j != (i + 1) % len(self.lines) and line.isInter(segment):
                    return False
        return True
