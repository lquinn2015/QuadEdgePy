import numpy as np

class Face:
    nextFaceId = 0
    def __init__(self, cell):
        self.id = Face.nextFaceId
        Face.nextFaceId += 1
        self.cell = cell
        self.edge = None
        cell.add_face(self)
        self.alive = True

    def addEdge(self, edge):
        self.edge = edge

    def getEdge(self):
        return self.edge
  

    def getTrianglePoints(self):
        """
        returns the faces points in ccw order will assert if face is not a triangle
        """
        v1 = self.edge.org() # ccw edge relative to the face
        v2 = self.edge.lnext().org()
        v3 = self.edge.lnext().lnext().org()
        return [v1 ,v2,v3]

    def __repr__(self):
        return "F(" + str(self.id) + ")"



