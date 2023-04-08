# based losely on https://www.cs.cmu.edu/afs/andrew/scs/cs/15-463/2001/pub/src/a2/quadedge.html
# dual ids %2 = 0  primal %2 == 1

import uuid


class Edge:
    def __init__(self):

        self.index = None # index in the quadedge
        self.quadedge = None # quad edge we belong too
        self.id = None

        self.next = None 
        self.vertex = None 
        self.face = None 

    def sym(self):
       i = self.index
       return self.quadedge[i+2] if i < 2 else self.quadedge[i-2]
    def rot(self):
       i = self.index
       return self.quadedge[i+1] if i < 3 else self.quadedge[i-3]
    def invrot(self):
       i = self.index
       return self.quadedge[i-1] if i > 0 else self.quadedge[i+3]
   

    def onext(self):
        return self.next 
    def oprev(self):
        return self.rot().onext().rot() 
    
    def dnext(self):
        return self.sym().onext().sym()
    def dprev(self):
        return self.invrot().onext().invrot()

    def lnext(self):
        return self.invrot().onext().rot()
    def lprev(self):
        return self.onext().sym()

    def rnext(self):
        return self.rot().onext().invrot()
    def rprev(self):
        return self.sym().onext()

    def org(self):
        return self.vertex
    def dest(self):
        return self.sym().vertex

    def left(self):
        return self.rot().face
    def right(self):
        return self.invrot().face

    def setOrg(self, org):
        self.vertex = org
        org.addEdge(self)

    def setDest(self, v):
        self.sym().vertex = v 
        v.addEdge(self.sym())

    def setLeft(self, left):
        self.rot().face = left
        left.addEdge(self)

    def setRight(self, right):
        self.invrot().face = right
        right.addEdge(self.sym())

    def crawl(self, invarient):
        chain = repr(self)
        scan = invarient(self)
        scanning = True
        while scanning:
            chain += " -> " + repr(scan)
            scan = invarient(scan)
            scanning = scan != self
        chain += " -> " + repr(scan)
        return chain


    def __repr__(self):
        eid = self.id if self.id != None else "-"
        nid = self.next.id if self.next != None and self.next.id != None else "-"
        if self.org() == None:
            return "{} -> E({}) -> {}".format(self.face, eid, self.sym().face)
        return "V({}) -> E({}) -> V({})".format(self.org().data, eid, self.dest().data)
        return "E("+ str(eid) + ")[next: " + str(nid) + "]"

class QuadEdge:
    nextId = 0
    def __init__(self,cell):
        self.cell = cell
        self.cell.add_quadedge(self)
        self.id = QuadEdge.nextId >> 2

        self.edges = [Edge() for i in range(4)]
        ids = [QuadEdge.nextId+i for i in range(4)]
        nid = [0,3,2,1]
        QuadEdge.nextId += 4
        for i in range(4):
            e = self.edges[i]
            e.index = i
            e.id = ids[i]
            e.next = self.edges[nid[i]]
            e.quadedge = self

    @staticmethod
    def make(cell):
        return QuadEdge(cell).edges[0]

    @staticmethod
    def swap(e):
        """
            .             .
        bl/  \b          /|\
         /    \         / | \
        s------d  ===> .  |  . 
        \     /         \ | /
        a\   /alnext     \|/
           .              .

        """
        a = e.oprev()
        b = e.sym().oprev()
        f1,f2 = e.left(), e.right()

        QuadEdge.splice(e,a)
        QuadEdge.splice(e.sym(),b)
        QuadEdge.splice(e, a.lnext())
        QuadEdge.splice(e.sym(), b.lnext())
        e.setOrg(a.dest())
        e.setDest(b.dest())
        e.quadedge.cell.setOrbitLeft(e,f1)
        e.quadedge.cell.setOrbitLeft(e.sym(), f2)

    @staticmethod
    def makeEdgeFromVertex(src, dst):
        base = QuadEdge.make(src.cell)
        base.setOrg(src)
        base.setDest(dst)
        return base

    @staticmethod
    def killEdge(e):
        l,r = e.left(), e.right()
        r.alive = False
        l.alive = False

        a,b = e.oprev(), e.sym().oprev()
        QuadEdge.splice(e,a)
        QuadEdge.splice(e.sym(),b)
        a.org().addEdge(a)
        b.org().addEdge(b)
        a.quadedge.cell.setOrbitLeft(a, l)

    @staticmethod
    def connect(a,b):
        e = QuadEdge.makeEdgeFromVertex(a.dest(), b.org())
        QuadEdge.splice(e, a.lnext())
        QuadEdge.splice(e.sym(), b)
        return e

    @staticmethod
    def splice(a, b):
        """
            O = splice(a,b)splice(a,b) i.e splice is its own inverse
            splice either
                A: splits a face loop and merges two vertex loops
                B: splits a vertex loop and merges two face loops
        """
        alpha = a.onext().rot()
        beta  = b.onext().rot()

        t1 = b.onext()
        t2 = a.onext()
        t3 = beta.onext()
        t4 = alpha.onext()

        a.next = t1
        b.next = t2
        alpha.next = t3 
        beta.next = t4

    def __repr__(self):
        es = "qe: " + str(self.id) + "\n\t"
        for i,e in enumerate(self.edges): 
            if e.org() != None:
                es += repr(e.org()) + "---E("+repr(e.id)+")--->" + repr(e.dest()) + "\n\t"
            else:
                es += repr(e.face) + "---E(" +repr(e.id)+")--->" + repr(e.sym().face) + "\n\t"
        return str(es) + "\n"

    def __getitem__(self, index):
        return self.edges[index]
