from __future__ import division
import Geom

class Hexahedron():
    def __init__(self):
        self.points = [ Geom.point3(0, 0, 0) for i in range(0, 8) ]
        self.texture = None
        self.faceTextures = { 'top': None, 'bottom': None, 'right': None, 'left': None, 'front': None, 'back': None }

class Plane():
    def __init__(self, p0, p1, p2):        
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2

# Box - can be used for a large variety of things.  The points (a, b) form a line across the
# bottom middle of the box.  The box has a thickness w and a height h.
def box(a, b, w, h):
    # calculate all eight points
    #
    #       5-------6  ^
    #      /|      /|  h
    #     / |     / |  |
    #    /  1---B/--2  V
    #   4-------7  /
    #   | /   / | /
    #   |/   /  |/
    #   0---A---3
    #
    #   <---w--->

    hh = Hexahedron()

    # diff is the vector running from a to b    
    diff = b - a
    diff.z = 0 # ignore change in z direction    
    diff.unitize()    
    diff *= (w/2, w/2, 1)    

    # diff is perpendicular to the line 0-3, so we see x's and y's transposed
    hh.points[0] = Geom.point3(a.x - diff.y, a.y + diff.x, a.z)
    hh.points[1] = Geom.point3(b.x - diff.y, b.y + diff.x, b.z)
    hh.points[2] = Geom.point3(b.x + diff.y, b.y - diff.x, b.z)
    hh.points[3] = Geom.point3(a.x + diff.y, a.y - diff.x, a.z)
    hh.points[4] = hh.points[0] + (0, 0, h)
    hh.points[5] = hh.points[1] + (0, 0, h)
    hh.points[6] = hh.points[2] + (0, 0, h)
    hh.points[7] = hh.points[3] + (0, 0, h)

    return hh