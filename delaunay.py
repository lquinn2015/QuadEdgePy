from cell import Cell
from face import Face
from edge import QuadEdge
from vertex import Vertex
from debug import plotDebugTriangles
import numpy as np
from debug import embed_debug
import matplotlib.pyplot as plt

def deubg_print(s):
    #print(s)
    pass


def deubg_display(cell,name=None, disable=False):
    #plotDebugTriangles(cell, name=name)
    pass

class Delaunay:
    def triangulate(self, points):
        p1,p2,p3 = self.boundingTrianglePoints(points)
        bt = np.array([p1,p2,p3])

        points = np.insert(points, 2, np.arange(len(points))+3, axis=1)
        bt = np.insert(bt, 2, np.arange(3), axis=1)

        dt = Cell.makeTriangle(bt[0], bt[1], bt[2])
        root = DagNode(dt.faces[1])
        for i in range(len(points)):
            if i % 10000==0:
                print("Iter {}".format(i))
            #deubg_print("Inserting pt[{}]={}".format(i+3,points[i]))
            #deubg_display(dt,name="Before Inserting point: {}".format(i+3))
            #self.insert_point(dt, root, points[i])
            self.insertPointNonRecursive(dt, root, points[i])
            #deubg_display(dt,name="Point: {} finalized".format(i+3))
        """
        for f in dt.faces:
            pts = [v.id for v in f.getTrianglePoints()]
            if 0 in pts or 1 in pts or 2 in pts:
                f.alive = False

        dt.vertices = dt.vertices[3:]
        for v in dt.vertices:
            v.data = v.data-3
        """

        return dt
    

    def insert_point(self, dt, dag, p):
        rc, data = dag.findPoint(p)
        #deubg_print("point p:{}  is {} on {}".format(p, rc, data))
        if "inTriangle" in rc: # InscribedPointCase 
            orgTri = data
            dagNode = orgTri.data 

            e = orgTri.getEdge()
            otv = orgTri.getTrianglePoints()
            
            v = Vertex(p, dt)
            faces = [orgTri, Face(dt), Face(dt)]
            base = QuadEdge.makeEdgeFromVertex(e.org(),v) # make center
            QuadEdge.splice(base, e)
            start = base
            scaning = True
            i = 0
            while scaning:
                base = QuadEdge.connect(e, base.sym())
                dt.setOrbitLeft(e,faces[i])
                e = base.oprev()
                i += 1
                scaning = e.lnext() != start
            dt.setOrbitLeft(e,faces[i]) 
            #deubg_display(dt, name="Triangulate V{}".format(v.id))

            dagNode.expandDag(otv, faces)
            
            edges2legalize = [base.oprev(), base.dnext().oprev(), base.dprev().oprev()]
            p = base.dest()
            for e in edges2legalize:
                self.legalize(p, e, dt)

        elif "notFound" in rc:
            #deubg_print("We lost a point: {}?".format(p))
            for f in dt.faces[1:]:
                if f.alive:
                    v1,v2,v3 = f.getTrianglePoints()
                    #deubg_print("isPointInTriangle({},{},{}) = {} ".format(v1,v2,v3, Delaunay.isPointInTriangle([v1,v2,v3],p)))
            breakpoint()
            assert(0)
        else:  # on EdgeCase 
            #deubg_print("Handle EdgeCase")
            assert(0)
        return

    def insertPointNonRecursive(self, dt, dag, p):
        rc, data = dag.findPoint(p)
        #deubg_print("point p:{}  is {} on {}".format(p, rc, data))
        if "inTriangle" in rc: # InscribedPointCase 
            orgTri = data
            dagNode = orgTri.data 

            e = orgTri.getEdge()
            otv = orgTri.getTrianglePoints()
            
            v = Vertex(p, dt)
            faces = [orgTri, Face(dt), Face(dt)]
            base = QuadEdge.makeEdgeFromVertex(e.org(),v) # make center
            QuadEdge.splice(base, e)
            start = base
            scaning = True
            i = 0
            while scaning:
                base = QuadEdge.connect(e, base.sym())
                dt.setOrbitLeft(e,faces[i])
                e = base.oprev()
                i += 1
                scaning = e.lnext() != start
            dt.setOrbitLeft(e,faces[i]) 
            #deubg_display(dt, name="Triangulate V{}".format(v.id))

            dagNode.expandDag(otv, faces)

            while True:
                t = e.oprev()
                if t.dest().rightOf(e) and Delaunay.isPointInCircle([e.org(), t.dest(), e.dest()], p):
                    self.SwapAndDag(e)
                    e = e.oprev()
                elif e.onext() == start:
                    return 
                else:
                    e = e.onext().lprev()

        else:
            assert(0)


    
    @staticmethod
    def isIllegal(p, e, dt):
        i,j,k = e.org(), e.dest(), e.oprev().dest()
        if i.id in [0,1,2] and j.id in [0,1,2]: # on bounds
            return False
        print([i,j,k,p])

        kright, pright = k.rightOf(e), p.rightOf(e)
        if kright == pright:
            return False
        if Delaunay.isPointInCircle([i,k,j],p.pos):
            return True
        return False



    def legalize(self, p, e, dt):
       
        if Delaunay.isIllegal(p, e, dt):
            
            #deubg_print("{} illegl pre swap qe {}".format(e, e.quadedge))
            #deubg_display(dt,name="preswap e: V{} ---> V{}".format(e.org().id, e.dest().id))
            self.SwapAndDag(e)
              
            #deubg_print("{} legal post swap qe {}".format(e, e.quadedge))
            #deubg_display(dt, "post swap e: V{} ---> V{}".format(e.org().id, e.dest().id))
            edges2check = [e.onext(), e.oprev()] # we swap
            for e in edges2check:
                #deubg_print("Evaluating e: V{} ---> V{}".format(e.org().id, e.dest().id))
                self.legalize(p, e, dt)

    def SwapAndDag(self, e):
        f1_v, f2_v = e.left().getTrianglePoints(), e.right().getTrianglePoints()
        prev_f1_d, prev_f2_d = e.left().data, e.right().data
        
        QuadEdge.swap(e)

        prev_f1_d.expandDag(f1_v, [e.left(), e.right()])
        prev_f2_d.joinDag(f2_v, prev_f1_d)


    @staticmethod
    def isPointOnEdgeOfTriangle(triangle, p):
        v1,v2,v3 = triangle[0], triangle[1], triangle[1]
        a,b,c,p = v1.pos, v2.pos, v3.pos, p[:2]
        
        abp = np.pad(np.array([a,b,p]), ((0,0),(1,0)), constant_values=1)
        bcp = np.pad(np.array([b,c,p]), ((0,0),(1,0)), constant_values=1)
        cap = np.pad(np.array([c,a,p]), ((0,0),(1,0)), constant_values=1)

        d_abp = np.linalg.det(abp) 
        d_bcp = np.linalg.det(bcp) 
        d_cap = np.linalg.det(cap) 
         
        if d_abp == 0 and d_bcp > 0 and d_cap > 0: 
            return [v1, v2]
        if d_bcp == 0 and d_abp > 0 and d_cap > 0:
            return [v2, v3]
        if d_cap == 0 and d_abp > 0 and d_bcp > 0:
            return [v3, v1]
        return None
    
    @staticmethod
    def isPointInCircle(triangle, vp):
        v1,v2,v3 = triangle[0], triangle[1], triangle[2]
        c1,c2,c3,p0 = v1.pos, v2.pos, v3.pos, vp[:2]

        r1 = np.array([c1[0], c1[1], c1[0]**2 + c1[1]**2, 1])
        r2 = np.array([c2[0], c2[1], c2[0]**2 + c2[1]**2, 1])
        r3 = np.array([c3[0], c3[1], c3[0]**2 + c3[1]**2, 1])
        r4 = np.array([p0[0], p0[1], p0[0]**2 + p0[1]**2, 1])

        return np.linalg.det(np.array([r1,r2,r3,r4])) > 0

    @staticmethod
    def isPointInTriangle(triangle, p):
        v1,v2,v3 = triangle[0], triangle[1], triangle[2]
        a,b,c,p = v1.pos, v2.pos, v3.pos, p[:2]
        
        abp = np.pad(np.array([a,b,p]), ((0,0),(1,0)), constant_values=1)
        bcp = np.pad(np.array([b,c,p]), ((0,0),(1,0)), constant_values=1)
        cap = np.pad(np.array([c,a,p]), ((0,0),(1,0)), constant_values=1)
         
        c1 = np.linalg.det(abp) > 0 
        c2 = np.linalg.det(bcp) > 0 
        c3 = np.linalg.det(cap) > 0
        
        return c1 and c2 and c3
    
    def boundingTrianglePoints(self, points):
        
        bbox_mx = 999999
        bbox_Mx = -999999
        bbox_my = 999999
        bbox_My = -999999
        

        #O(N) really big bounds is probably much cheapher
        for p in points:
            x,y  = p[0], p[1]
            bbox_Mx = max(x, bbox_Mx)
            bbox_My = max(y, bbox_My)
            bbox_mx = min(x, bbox_mx)
            bbox_my = min(y, bbox_my)
       
        bbox_Mx += 5
        bbox_My += 5
        # select x1,x2,x3 
        x1 = np.array([bbox_mx - 5, bbox_My*2])
        x2 = np.array([bbox_mx- 5, bbox_my-5])
        # x1 to b slope
        m = (x1[1] - bbox_My) / (x1[0] - bbox_Mx)
        b0 = x1[1] - m * x1[0]
        x3 = np.array([ x2[0]*m + b0, x2[1]]) 
        
        return [x1,x2,x3]


class DagNode:
    nodeId = 0
    def __init__(self, t):
        self.isLeaf = 1
        self.id = DagNode.nodeId 
        DagNode.nodeId += 1
        self.vertices = t.getTrianglePoints()
        self.triangleRef = t
        self.nodes = []
        t.data = self

    def findPoint(self, p):
        v1,v2,v3 = self.vertices
        inTri = Delaunay.isPointInTriangle(self.vertices, p)
        onEdge = Delaunay.isPointOnEdgeOfTriangle(self.vertices, p)
        #deubg_print("Searching for {} in {}-{}-{}: [{}, {}]".format(p, v1.id, v2.id, v3.id, inTri, onEdge))
        if not inTri and onEdge == None:
            return ("notFound", None)
        elif self.isLeaf == 1:
            if inTri:
                return ("inTriangle", self.triangleRef)
            else:
                return ("onEdge", onEdge)
        else:
            for node in self.nodes:
                rc,data = node.findPoint(p)
                if "notFound" not in rc:
                    return (rc, data)
        
        return ("notFound", None)


    def expandDag(self, triV, newTri):
        assert(self.isLeaf == 1)
        ids = [v.id for v in triV]
        #deubg_print("expand DagNode[{}] contains {},  TriV {}-{}-{}".format(self.id, self.vertices,ids[0],ids[1],ids[2]))

        self.isLeaf = 0
        self.vertices = triV
        for i,t in enumerate(newTri):
            d = DagNode(t)
            t.data = d
            ids = [v.id for v in t.getTrianglePoints()]
            
            #if i == len(newTri)-1:
            #    #deubg_print("\to--->DagNode[{}] contains {}: {}".format(d.id, ids, t.getTrianglePoints()))
            #else:
            #    #deubg_print("\to--->DagNode[{}] contains {}: {}, ".format(d.id, ids, t.getTrianglePoints()))
            self.nodes.append(d)

    def joinDag(self, triV, dagNode):
        assert(self.isLeaf == 1)
        assert(dagNode.isLeaf == 0)

        ids = [v.id for v in triV]
        #deubg_print("join DagNode[{}] contains {},  TriV {}-{}-{}".format(self.id, self.vertices,ids[0],ids[1],ids[2]))
        self.isLeaf = 0
        self.vertices = triV
        self.nodes = dagNode.nodes
        

    def __repr__(self):
        if self.isLeaf == 1:
            v1,v2,v3 = self.vertices
            return "DagNodeLeaf({})[ Triangle{}: \n\t{}\n\t{}\n\t{}\n]".format(self.id,self.triangleRef,v1,v2,v3)
        else:
            ids = [d.id for d in self.nodes]
            return "DagNodeInternal({})[{}]--\n".format(self.id, ids) + repr(self.vertices)  
