import matplotlib.pyplot as plt
import matplotlib.tri
import matplotlib.tri as mtri
from cell import Cell
import numpy as np
import IPython

def embed_debug():
    IPython.embed()

def plotDebugTriangles(cell,name=None):
    
    fig,ax = plt.subplots()
    ax.set_title(name)
    ax.set_aspect('equal')
    points = np.array([np.append(v.pos,v.data) for v in cell.vertices])
    triangles = exportTriangleIds(cell)
    triang = mtri.Triangulation(points[:,0], points[:,1], triangles=triangles)
    plt.triplot(triang, marker="o")
    #for i in range(len(points)):
    #    plt.annotate(points[i,2],(points[i,0], points[i,1])) 
    plt.show(block=False)
    

def plotCTT(points, dt, radius=20):
    
    # Create a plot with matplotlib.pyplot
    fig, ax = plt.subplots()
    ax.margins(0.1)
    ax.set_aspect('equal')
    plt.axis([-1, radius+1, -1, radius+1])

    # Plot our Delaunay triangulation (plot in blue)
    cx, cy = zip(*points)
    dt_tris = dt.exportTriangles()
    ax.triplot(matplotlib.tri.Triangulation(cx, cy, dt_tris), 'o-')

def exportTriangleIds(cell):
    triangles = []

    for f in cell.faces[1:]:
        if f.alive:
            v1,v2,v3 = f.getTrianglePoints()
            triangles.append([int(v1.data), int(v2.data), int(v3.data)])


    return triangles

