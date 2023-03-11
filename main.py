from cell import Cell
from edge import Edge
from face import Face
from vertex import Vertex
import numpy as np
from pyDelaunay2D.delaunay2D import Delaunay2D
from delaunay import Delaunay
from debug import plotDebugTriangles, exportTriangleIds, plotCTT
import itertools
import matplotlib.pyplot as plt


def test1():

    c= Cell.makeTriangle((0,0),(1,0),(0,1))
    return c


def testSwap():
    cell = Cell.make((0,0))
    v1 = cell.vertices[0]
    e1 = v1.getEdge()
    left = e1.left()
    right = e1.right()

    v2 = cell.makeVertexEdge(v1,(1,0),left,right).dest()
    v3 = cell.makeVertexEdge(v2,(1,1),left,right).dest()
    v4 = cell.makeVertexEdge(v3,(0,1),left,right).dest()

    insideEdge = cell.makeFaceEdge(right, v1, v3)
    print(cell) 
    cell.swap(insideEdge)
    print(cell)

def testAlg():
    cell =Cell.makeTetrahedron((0,0),(1,0),(0,1),(0.5,0.5))
    bottom_triangle = cell.faces[1] 

    v1 = Vertex(np.array([.3,.25]), cell) # yes
    v2 = Vertex(np.array([.55,.55]), cell) # no
    c1 = Delaunay.isPointInTriangle(bottom_triangle, v1)
    c2 = Delaunay.isPointInTriangle(bottom_triangle, v2)
    
    v3 = Vertex(np.array([.25,.25]), cell) 
    c1 = Delaunay.isPointOnEdgeOfTriangle(bottom_triangle, v3) # yes 
    c2 = Delaunay.isPointOnEdgeOfTriangle(bottom_triangle, v2) # no
    assert(c1 != None)
    assert(c2 == None)

    t1,t2,t3 = bottom_triangle.getTrianglePoints()
    c1 = Delaunay.isPointInCircle(t1,t2,t3, v3) # yes
    c2 = Delaunay.isPointInCircle(t1,t2,t3, v2) # no
    assert(c1 == True)
    assert(c2 != True)
    return cell

def bad_swap_early():
    points = np.array([ [6.142e+00,5.630e+00], [1.327e+01,1.177e+01], [1.229e+00,1.524e+01], [5.819e+00,1.047e+01], [1.237e+01,6.706e+00], [1.070e+00,4.413e+00], [9.660e+00,1.097e+01], [1.013e+01,8.013e-01], [1.174e+00,1.292e+01], [1.136e+01,1.689e+01], [1.830e+01,1.824e+01], [1.545e+01,3.086e+00], [9.088e+00,5.509e+00], [1.003e+01,1.216e+01], [1.594e+01,1.783e+01], [1.612e+01,2.697e+00], [2.235e+00,1.245e+00], [7.109e+00,3.317e+00], [5.670e+00,1.991e+01], [1.491e+00,9.771e+00], [1.419e+00,3.166e+00], [1.043e+01,8.170e-01], [2.005e+00,1.541e+01], [4.246e+00,1.717e+01], [1.107e+01,1.106e+01], [1.083e+01,3.114e+00], [5.542e+00,1.068e+01], [1.477e+00,4.467e+00], [1.278e+01,7.295e+00], [1.138e-01,1.164e+01], [1.072e+01,2.084e+00], [1.682e+01,1.899e+00], [1.609e+01,1.662e+01], [9.644e+00,5.974e+00], [7.121e+00,1.637e+01], [1.327e+01,1.052e+01], [5.878e+00,7.818e+00], [1.024e+00,3.608e+00], [7.036e+00,6.976e+00], [1.051e+01,1.504e+01], [6.166e+00,1.253e+01], [5.648e+00,1.821e+01], [1.134e+01,4.431e+00], [1.074e+01,1.588e+01], [1.060e+01,9.051e+00], [1.358e-03,6.266e+00], [1.369e+01,5.602e+00], [1.319e+01,5.424e+00], [1.367e+01,1.367e+01], [1.392e+01,9.101e+00]])

    print("Point set: " + str(points))
    dt = Delaunay()
    cell = dt.triangulate(points)
    plotDebugTriangles(cell)
    import matplotlib.pyplot as plt
    plt.show()

def comp_test():
    points = np.random.random((200,2)) * 20
    dt = Delaunay2D() # not fast
    for p in points:
        dt.addPoint(p)
    triangles = dt.exportTriangles()
    print("Comparsion test TV:")
    print("Point set: " + str(points))
    print("TV_Triangles: " + str(triangles))
    plotCTT(points, dt)
    dt = Delaunay()
    cell = dt.triangulate(points)
    plotDebugTriangles(cell)
    dv_tri = exportTriangleIds(cell)
    print("DUT_TV_Triangles: " + str(dv_tri))

    plt.show()

np.set_printoptions(precision=3)
#triangle = test1()
#tetra = testAlg()
#testSwap()
#bad_swap_early()
comp_test()
