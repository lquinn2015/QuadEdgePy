import numpy as np

class Vertex:
    nextVid = 0
    def __init__(self,vdata,cell):
        self.id = Vertex.nextVid
        Vertex.nextVid += 1
        self.pos = np.array([vdata[0], vdata[1]])
        self.data = vdata[2:]
        self.cell = cell
        self.edge = None
        self.cell.add_vertex(self)

    def addEdge(self, outgoing_edge):
        self.edge = outgoing_edge

    def getEdge(self):
        return self.edge

    def rightOf(self, e):
        return Vertex.orient_test(e.dest().pos, e.org().pos, self.pos) > 0
    
    def leftOf(self, e):
        return Vertex.orient_test(e.org().pos, e.dest().pos, self.pos) > 0

    def getEdgeBetween(self, o):
        """ O(1) if planar
        """
        start = self.getEdge()
        scan = start
        scanning = True
        while scanning:
            if scan.dest() == o:
                return scan
            scan = scan.onext()
            scanning = scan != start
        return None

    @staticmethod
    def orient_test(p,q,r):
        return np.linalg.det(np.array([ [1, p[0], p[1]], [1, q[0], q[1]], [1, r[0],r[1]] ]))

    def __repr__(self):
        eid = self.edge.id if self.edge != None else "E(-)"
        return "V(" + str(self.data) + ": " + str(self.pos) + ", edge: " + str(eid) +")"
