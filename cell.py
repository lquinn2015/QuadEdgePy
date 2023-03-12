from edge import QuadEdge
from edge import Edge
from vertex import Vertex
from face import Face

class CellVertexIterator:
    def __init__(self, cell):
        self.cell = cell
        self.count = len(self.cell.vertices)

    def __iter__(self):
        return self

    def __next__(self):
        if self.count < 1:
            raise StopIteration
        self.count = self.count -1
        return self.cell.vertices[self.count]

class CellFaceIterator:
    def __init__(self, cell):
        self.cell = cell
        self.count = len(self.cell.faces)

    def __iter__(self):
        return self
		
    def __next__(self):
        if (count < 1):
            raise StopIteration
        self.count = self.count - 1
        return self.cell.faces[self.count]

class Cell:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.quadedges = [] 

    def add_face(self, face):
        self.faces.append(face)
    def add_vertex(self, vertex):
        self.vertices.append(vertex)
    def add_quadedge(self, qe):
        self.quadedges.append(qe)

    
    def makeVertexEdge(self, vertex, vnewPos, left, right):
        """
                 \  |  /          we get 1 of these edges from v1
                  \ | /             we need to iterate over all edges i.e onext    
           left     v1    right     until we find e1 s.t e1.left == left and
                   /  \             e2.right 
                  /    \

        """
        edge = vertex.getEdge()
        edge1 = self.getOrbitLeft(edge, right)
        edge2 = self.getOrbitLeft(edge, left)
        
        if edge1 == None:
            print("PANIC Cell::makeVertexEdge unable to find right face")
            breakpoint()
        if edge2 == None:
            print("PANIC Cell::makeVertexEdge unable to find left face")
            breakpoint()
        vnew = Vertex(vnewPos, self)
        
        enew = QuadEdge.make(self).rot()

        QuadEdge.splice(edge2, enew )
        QuadEdge.splice(edge1, enew.sym())

        enew.setOrg(edge1.org())
        enew.setLeft(edge2.left())
        enew.setRight(edge1.left())

        self.setOrbitOrg(enew.sym(), vnew)
        return enew

    def makeFaceEdge(self, face, org, dest):

        # locate edge leaving each of the vertices in the face's orbit
        edge = face.getEdge()
        edge1 = self.getOrbitOrg(edge, org)
        edge2 = self.getOrbitOrg(edge, dest)

        if edge1 == None:
            print("PANIC cell cannot locate origin vertex: (" + repr(org) + ") on face " + repr(face))
            breakpoint()
        if edge2 == None:
            print("PANIC cell cannot locate origin vertex: (" + repr(dest) + ") on face " + repr(face))
            breakpoint()

        fnew = Face(self)
        enew = QuadEdge.make(self)

        QuadEdge.splice(edge2, enew.sym())
        QuadEdge.splice(edge1, enew)
        enew.setOrg(edge1.org())
        enew.setDest(edge2.org())
        enew.setLeft(edge2.left())

        self.setOrbitLeft(enew.sym(), fnew)
        return enew


    def getOrbitLeft(self, edge, left):
        scan = edge
        scanning = True
        while scanning:
            if scan.left() == left:
                return scan
            scan = scan.onext()
            scanning = scan != edge
        return None
    
    def setOrbitLeft(self, edge, left):

        scan = edge
        scanning = True
        while scanning:
            scan.setLeft(left)
            scan = scan.lnext()
            scanning = scan != edge
        left.addEdge(scan)

    def getOrbitOrg(self, edge, org):
        scan = edge
        scanning = True
        while scanning:
            if scan.org() == org:
                return scan
            scan = scan.lnext()
            scanning = scan != edge 
        return None 

    def setOrbitOrg(self, edge, org):
        scan = edge
        scanning = True
        while scanning:
            scan.setOrg(org)
            scan = scan.onext()
            scanning = scan != edge
   
    def __repr__(self):
        return repr(self.vertices) + "\n" + repr(self.faces) + "\n" + repr(self.quadedges)

    @staticmethod
    def deleteEdge(e):
        cell = e.quadedge.cell
        QuadEdge.splice(e, e.oprev())
        QuadEdge.splice(e.sym(), e.sym().oprev())
        cell.edges.remove(e)


    @staticmethod
    def make(pos):
        cell = Cell()
        vertex = Vertex(pos, cell)
        left = Face(cell)
        right = Face(cell)
        e = QuadEdge.make(cell).invrot()
        e.setOrg(vertex)
        e.setDest(vertex)
        e.setLeft(left)
        e.setRight(right)
        return cell

    @staticmethod
    def makeTriangle(pos1, pos2, pos3):
        cell = Cell.make(pos1)
        v1 = cell.vertices[0]
        e1 = v1.getEdge()
        left = e1.left()
        right = e1.right()
        v2 = cell.makeVertexEdge(v1,pos2,left,right).dest()
        v3 = cell.makeVertexEdge(v2,pos3,left,right).dest()

        return cell


    def insertSite(self, vdata, orgTri):
        """
        Inserts a vertex and connects it to all corners parent
        must check if we inserted on an edge. 
        """
        e = orgTri.getEdge()
        v = Vertex(vdata, self)
        base = QuadEdge.makeEdgeFromVertex(e.org(), v)
        QuadEdge.splice(base, e)
        
        startEdge = base
        scanning = True
        while scanning:
            base = QuadEdge.connect(e, base.sym())
            e = base.oprev()
            scanning = e.lnext() != startEdge

        return startEdge

    def getEdgeBetween(self, v1,v2):
        edge = v1.getEdge()
        scan = edge
        scannig = True
        while scannig:
            if scan.dest() == v2:
                return scan
            scan = scan.onext()
            scannig = scan != edge

        print("There exists no edge between " + repr(v1) + "," + repr(v2))
        assert(0)

    @staticmethod
    def makeTetrahedron(p1, p2, p3, p4):
        cell = Cell.make(p1)
        v1 = cell.vertices[0]
        e1 = v1.getEdge()
        left = e1.left()
        right = e1.right()

        v2 = cell.makeVertexEdge(v1,p2,left,right).dest() #  setOrbitOrg #
        v3 = cell.makeVertexEdge(v2,p3,left,right).dest()
        v4 = cell.makeVertexEdge(v3,p4,left,right).dest()
        
        front = cell.makeFaceEdge(left, v2, v4).right()
        back = cell.makeFaceEdge(right, v1, v3).right()
        return cell


