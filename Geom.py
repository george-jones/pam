from __future__ import division
import math
import unittest
from test import test_support

class point2():
    # todo, consider using __slots__
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "(%s, %s)" % (self.x, self.y)

    def __otherTuple(self, other):
        try:
            t = (other.x, other.y)	
        except AttributeError:
            # already a tuple or sequence?
            t = other
            if len(t) < 2:
                raise Exception("Must be passed point or iterable with at least 2 values")
        return t

    def __add__(self, other):
        t = self.__otherTuple(other)
        return point2(self.x + t[0], self.y + t[1])	    

    def __sub__(self, other):
        t = self.__otherTuple(other)
        return point2(self.x - t[0], self.y - t[1])

    def __mul__(self, other):
        t = self.__otherTuple(other)
        return point2(self.x * t[0], self.y * t[1])

    def __div__(self, other):
        t = self.__otherTuple(other)
        return point2(self.x / t[0], self.y / t[1])

    def __truediv__(self, v):
        return self.__div__(v)	

    def __iadd__(self, other):
        t = self.__otherTuple(other)
        self.x += t[0]
        self.y += t[1]
        return self

    def __imul__(self, other):
        t = self.__otherTuple(other)
        self.x *= t[0]
        self.y *= t[1]
        return self

    def __idiv__(self, other):
        t = self.__otherTuple(other)
        self.x /= t[0]
        self.y /= t[1]
        return self

    def __itruediv__(self, v):
        return self.__idiv__(v)

    def __neg__(self):
        return point2(-1 * self.x, -1 * self.y)

    def copy(self):
        return point2(self.x, self.y)

    def dot(self, other):
        t = self.__otherTuple(other)
        return self.x * t[0] + self.y * t[1]

    def magnitude(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def unitize(self):
        mag = self.magnitude()
        if mag > 0:
            self.x /= mag
            self.y /= mag

    def angleBetween(self, other):
        mag_1 = self.magnitude()
        try:
            mag_2 = other.magnitude()
            v2 = other
        except AttributeError:
            v2 = point2(other[0], other[1])
            mag_2 = v2.magnitude()
        dot = self.dot(v2)
        c = dot / (mag_1 * mag_2)
        return math.acos(c)

    def dist(self, other):
        t = self.__otherTuple(other)
        return math.sqrt(math.pow(self.x - t[0], 2.0) + math.pow(self.y - t[1], 2.0))

    def compare(self, pt):
        return self.x == pt.x and self.y == pt.y

class point3():
    # todo, consider using __slots__
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return "(%s, %s, %s)" % (self.x, self.y, self.z)

    def __otherTuple(self, other):
        try:
            t = (other.x, other.y, other.z)
        except AttributeError:
            # already a tuple or sequence?
            t = other
            if len(t) < 3:
                raise Exception("Must be passed point or iterable with at least 3 values")
        return t

    def __add__(self, other):
        t = self.__otherTuple(other)
        return point3(self.x + t[0], self.y + t[1], self.z + t[2])	    

    def __sub__(self, other):
        t = self.__otherTuple(other)
        return point3(self.x - t[0], self.y - t[1], self.z - t[2])

    def __mul__(self, other):
        t = self.__otherTuple(other)
        return point3(self.x * t[0], self.y * t[1], self.z * t[2])

    def __div__(self, other):
        t = self.__otherTuple(other)
        return point3(self.x / t[0], self.y / t[1], self.z / t[2])

    def __truediv__(self, other):
        return self.__div__(other)

    def __iadd__(self, other):
        t = self.__otherTuple(other)
        self.x += t[0]
        self.y += t[1]
        self.z += t[2]
        return self

    def __imul__(self, other):
        t = self.__otherTuple(other)
        self.x *= t[0]
        self.y *= t[1]
        self.z *= t[2]
        return self

    def __idiv__(self, other):
        t = self.__otherTuple(other)
        self.x /= t[0]
        self.y /= t[1]
        self.z /= t[2]
        return self

    def __itruediv__(self, other):
        return self.__idiv__(other)

    def __neg__(self):
        return point3(-1 * self.x, -1 * self.y, -1 * self.z)

    def copy(self):
        return point3(self.x, self.y, self.z)    

    def dot(self, other):
        t = self.__otherTuple(other)
        return self.x * t[0] + self.y * t[1]  + self.z * t[2]

    def cross(self, other):
        t = self.__otherTuple(other)
        return point3(self.y * t[2] - self.z * t[1],
                      self.z * t[0] - self.x * t[2],
                      self.x * t[1] - self.y * t[0])

    def magnitude(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def unitize(self):
        mag = self.magnitude()
        if mag > 0:
            self.x /= mag
            self.y /= mag
            self.z /= mag    

    def angleBetween(self, other):	
        mag_1 = self.magnitude()
        try:
            mag_2 = other.magnitude()
            v2 = other
        except AttributeError:
            v2 = point3(other[0], other[1], other[2])
            mag_2 = v2.magnitude()
        dot = self.dot(v2)
        c = dot / (mag_1 * mag_2)
        return math.acos(c)

    def dist(self, other):
        t = self.__otherTuple(other)
        return math.sqrt(math.pow(self.x - t[0], 2.0) + math.pow(self.y - t[1], 2.0) + math.pow(self.z - t[2], 2.0))

    def compare(self, pt):
        return self.x == pt.x and self.y == pt.y and self.z == pt.z

def midPoint(pts):
    lp = len(pts)
    if lp == 0:
        raise Exception("Must pass at least 1 point in array")

    if isinstance(pts[0], point2):
        tp = point2(0, 0)
        d = (lp, lp)
    else:
        tp = point3(0, 0, 0)
        d = (lp, lp, lp)

    for i in range(0, lp):
        tp += pts[i]

    return tp / d

def findNearest(mp, pts):
    minDist = None
    cp = None    
    for p in pts:        
        if p != mp:
            d = p.dist(mp)
            if cp == None or d < minDist:
                minDist = d
                cp = p
    return cp

def findCentralPoint(pts):
    minDist = None
    cp = None
    mp = midPoint(pts)
    return findNearest(mp, pts)

def scalePoints(pts, s):
    if isinstance(s, point3):
        s3 = True
    elif isinstance(s, point2):	
        s3 = False
    elif len(s) == 3:
        s3 = True
        s = point3(s[0], s[1], s[2])
    elif len(s) == 2:
        s3 = False
        s = point2(s[0], s[1])
    else:
        raise Exception("scalePoints must be passed a point2, point3, or iterable with 2 or 3 values")	

    if s3:
        minp = point3(None, None, None)
        maxp = point3(None, None, None)
    else:
        minp = point2(None, None)
        maxp = point2(None, None)

    # figure out current max and min
    for p in pts:
        if maxp.x is None or p.x > maxp.x:
            maxp.x = p.x
        if maxp.y is None or p.y > maxp.y:
            maxp.y = p.y
        if s3:
            if isinstance(p, point3) and (maxp.z is None or p.z > maxp.z):
                maxp.z = p.z

        if minp.x is None or p.x < minp.x:
            minp.x = p.x
        if minp.y is None or p.y < minp.y:
            minp.y = p.y                
        if s3:
            if isinstance(p, point3) and (minp.z is None or p.z < minp.z):
                minp.z = p.z

    xmult = s.x / (maxp.x - minp.x) # can throw ZeroDivisionError
    ymult = s.y / (maxp.y - minp.y)        
    if s3 and maxp.z is not None and minp.z is not None:
        zmult = s.z / (maxp.z - minp.z)

    for i in range(0, len(pts)):
        p = pts[i]
        if isinstance(pts[i], point3):
            if s3:
                pts[i] -= minp
                pts[i] *= (xmult, ymult, zmult)
            else:
                pts[i] -= (minp.x, minp.y, 0)
                pts[i] *= (xmult, ymult, 1)			    
        else:	    
            pts[i] -= (minp.x, minp.y)
            pts[i] *= (xmult, ymult)

# returns:
#  -1: not in bounding box
#   0: in bounding box
#   1: in triangle
def inTriangle(P, tri_pts):

    # using barycentric coordinate method, taken from
    # http://www.blackpawn.com/texts/pointinpoly/default.html

    if len(tri_pts) != 3:
        raise Exception("Passed wrong number of points (" + tri_pts.length + ")")    

    A = tri_pts[0]
    B = tri_pts[1]
    C = tri_pts[2]

    min_x = A.x
    max_x = A.x
    min_y = A.y
    max_y = A.y

    min_x = min((min_x, B.x))
    min_x = min((min_x, C.x))
    max_x = max((max_x, B.x))
    max_x = max((max_x, C.x))

    min_y = min((min_y, B.y))
    min_y = min((min_y, C.y))
    max_y = max((max_y, B.y))
    max_y = max((max_y, C.y))

    # if not in bounding box, just bail out now
    if P.x < min_x or P.x > max_x or P.y < min_y or P.y > max_y:
        return -1

    # Compute vectors
    v0 = C - A
    v1 = B - A
    v2 = P - A

    # Compute dot products
    dot00 = v0.dot(v0)
    dot01 = v0.dot(v1)
    dot02 = v0.dot(v2)
    dot11 = v1.dot(v1)
    dot12 = v1.dot(v2)

    # Compute barycentric coordinates
    invDenom = 1 / (dot00 * dot11 - dot01 * dot01)
    u = (dot11 * dot02 - dot01 * dot12) * invDenom
    v = (dot00 * dot12 - dot01 * dot02) * invDenom

    # Check if point is in triangle
    if (u >= 0) and (v >= 0) and (u + v <= 1):
        return 1
    else:
        return 0

def linesIntersect(a1, a2, b1, b2, betweenSegments):
    d = (b2.y - b1.y) * (a2.x - a1.x) - (b2.x - b1.x) * (a2.y - a1.y)
    if (d == 0.0):
        return None
    n1 = (b2.x - b1.x) * (a1.y - b1.y) - (b2.y - b1.y) * (a1.x - b1.x)
    n2 = (a2.x - a1.x) * (a1.y - b1.y) - (a2.y - a1.y) * (a1.x - b1.x)
    if n1 == n2 and n1 == 0:
        return None
    ua = n1 / d
    ub = n2 / d
    if (betweenSegments == True and
        (ua < 0.0 or ua > 1.0 or ub < 0.0 or ub > 1.0)):
        return None
    x = a1.x + ua * (a2.x - a1.x)
    y = a1.y + ua * (a2.y - a1.y)
    return point2(x, y)

# common logic for point-to-line and point-to-segment functions
def __distP2LHelper(c, a, b):
    r_numerator = (c.x-a.x)*(b.x-a.x) + (c.y-a.y)*(b.y-a.y)
    r_denominator = (b.x-a.x)*(b.x-a.x) + (b.y-a.y)*(b.y-a.y)
    r = r_numerator / r_denominator
    px = a.x + r*(b.x-a.x)
    py = a.y + r*(b.y-a.y)
    s =  ((a.y-c.y)*(b.x-a.x)-(a.x-c.x)*(b.y-a.y)) / r_denominator
    distanceLine = math.fabs(s) * math.sqrt(r_denominator)
    return (distanceLine, r)

def distancePointToLine(c, a, b):
    return __distP2LHelper(c, a, b)[0] # only care about distance (first member of tuple)

# 2D distance from a point c to a finite line segment a->b
# see http://www.codeguru.com/forum/printthread.php?t=194400
def distancePointToSegment(c, a, b):
    (distanceLine, r) = __distP2LHelper(c, a, b)
    if (r >= 0) and (r <= 1):
        distanceSegment = distanceLine        
    else:
        dist1 = (c.x-a.x)*(c.x-a.x) + (c.y-a.y)*(c.y-a.y)
        dist2 = (c.x-b.x)*(c.x-b.x) + (c.y-b.y)*(c.y-b.y)
        if dist1 < dist2:
            distanceSegment = math.sqrt(dist1)                
        else:
            distanceSegment = math.sqrt(dist2)

    return distanceSegment            

class plane():
    def __init__(self, p0, p1, p2):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2        

#
# Unit tests
#

class MyTestCasePoint2(unittest.TestCase):
    def testInit(self):
        p = point2(1, 2)
        self.assertEqual(p.x, 1)
        self.assertEqual(p.y, 2)

    def testAdd(self):
        p = point2(1, 2)
        p2 = p + (1, 1)
        self.assertEqual(p2.x, 2)
        self.assertEqual(p2.y, 3)	
        p2 = p + point2(1, 1)
        self.assertEqual(p2.x, 2)
        self.assertEqual(p2.y, 3)

    def testIAdd(self):
        p = point2(1, 2)
        p += (1, 1)
        self.assertEqual(p.x, 2)
        self.assertEqual(p.y, 3)
        p = point2(1, 2)
        p += point2(1, 1)
        self.assertEqual(p.x, 2)
        self.assertEqual(p.y, 3)	

    def testMult(self):
        p = point2(1, 2)
        p2 = p * (3, 3)
        self.assertEqual(p2.x, 3)
        self.assertEqual(p2.y, 6)
        p = point2(1, 2)
        p2 = p * point2(3, 3)
        self.assertEqual(p2.x, 3)
        self.assertEqual(p2.y, 6)

    def testIMult(self):
        p = point2(1, 2)
        p *= (3, 3)
        self.assertEqual(p.x, 3)
        self.assertEqual(p.y, 6)
        p = point2(1, 2)
        p *= point2(3, 3)
        self.assertEqual(p.x, 3)
        self.assertEqual(p.y, 6)

    def testDiv(self):
        p = point2(2, 8)
        p2 = p / (2, 4)
        self.assertEqual(p2.x, 1)
        self.assertEqual(p2.y, 2)
        p = point2(2, 8)
        p2 = p / point2(2, 4)
        self.assertEqual(p2.x, 1)
        self.assertEqual(p2.y, 2)

    def testIDiv(self):
        p = point2(2, 8)
        p /= (2, 4)
        self.assertEqual(p.x, 1)
        self.assertEqual(p.y, 2)
        p = point2(2, 8)
        p /= point2(2, 4)
        self.assertEqual(p.x, 1)
        self.assertEqual(p.y, 2)

    def testNeg(self):
        p = -point2(1, 2)
        self.assertEqual(p.x, -1)
        self.assertEqual(p.y, -2)

    def testDot(self):
        p = point2(1, 2)
        p2 = point2(3, 2)
        self.assertEqual(p.dot(p2), 7)
        p = point2(1, 2)	
        self.assertEqual(p.dot((3, 2)), 7)	

    def testMag(self):
        p = point2(3, 4)
        self.assertEqual(p.magnitude(), 5)

    def testDist(self):
        p = point2(3, 4)
        p2 = point2(-3, -4)
        self.assertEqual(p.dist(p2), 10)
        p = point2(3, 4)	
        self.assertEqual(p.dist((-3, -4)), 10)

    def testAngle(self):
        p = point2(1, 1)
        p2 = point2(-1, 1)
        self.assertEqual(p.angleBetween(p2), math.pi / 2)

class MyTestCasePoint3(unittest.TestCase):
    def testInit(self):
        p = point3(1, 2,3)
        self.assertEqual(p.x, 1)
        self.assertEqual(p.y, 2)
        self.assertEqual(p.z, 3)

    def testAdd(self):
        p = point3(1, 2, 3)
        p2 = p + (1, 1, 1)
        self.assertEqual(p2.x, 2)
        self.assertEqual(p2.y, 3)
        self.assertEqual(p2.z, 4)
        p2 = p + point3(1, 1, 1)
        self.assertEqual(p2.x, 2)
        self.assertEqual(p2.y, 3)
        self.assertEqual(p2.z, 4)

    def testIAdd(self):
        p = point3(1, 2, 3)
        p += (1, 1, 1)
        self.assertEqual(p.x, 2)
        self.assertEqual(p.y, 3)
        self.assertEqual(p.z, 4)
        p = point3(1, 2, 3)
        p += point3(1, 1, 1)
        self.assertEqual(p.x, 2)
        self.assertEqual(p.y, 3)
        self.assertEqual(p.z, 4)

    def testMult(self):
        p = point3(1, 2, 3)
        p2 = p * (3, 3, 3)
        self.assertEqual(p2.x, 3)
        self.assertEqual(p2.y, 6)
        self.assertEqual(p2.z, 9)
        p = point3(1, 2, 3)
        p2 = p * point3(3, 3, 3)
        self.assertEqual(p2.x, 3)
        self.assertEqual(p2.y, 6)
        self.assertEqual(p2.z, 9)

    def testIMult(self):
        p = point3(1, 2, 3)
        p *= (3, 3, 3)
        self.assertEqual(p.x, 3)
        self.assertEqual(p.y, 6)
        self.assertEqual(p.z, 9)
        p = point3(1, 2, 3)
        p *= point3(3, 3, 3)
        self.assertEqual(p.x, 3)
        self.assertEqual(p.y, 6)
        self.assertEqual(p.z, 9)

    def testDiv(self):
        p = point3(2, 8, 16)
        p2 = p / (2, 4, 2)
        self.assertEqual(p2.x, 1)
        self.assertEqual(p2.y, 2)
        self.assertEqual(p2.z, 8)
        p = point3(2, 8, 16)
        p2 = p / point3(2, 4, 2)
        self.assertEqual(p2.x, 1)
        self.assertEqual(p2.y, 2)
        self.assertEqual(p2.z, 8)

    def testIDiv(self):
        p = point3(2, 8, 16)
        p /= (2, 4, 2)
        self.assertEqual(p.x, 1)
        self.assertEqual(p.y, 2)
        self.assertEqual(p.z, 8)
        p = point3(2, 8, 16)
        p /= point3(2, 4, 2)
        self.assertEqual(p.x, 1)
        self.assertEqual(p.y, 2)
        self.assertEqual(p.z, 8)

    def testNeg(self):
        p = -point3(1, 2, 3)
        self.assertEqual(p.x, -1)
        self.assertEqual(p.y, -2)
        self.assertEqual(p.z, -3)

    def testDot(self):
        p = point3(1, 2, 3)
        p2 = point3(3, 2, 1)
        self.assertEqual(p.dot(p2), 10)
        p = point3(1, 2, 3)
        self.assertEqual(p.dot((3, 2, 1)), 10)

    def testMag(self):
        p = point3(2, 4, 4)
        self.assertEqual(p.magnitude(), 6)

    def testDist(self):
        p = point3(2, 4, 4)
        p2 = point3(-2, -4, -4)
        self.assertEqual(p.dist(p2), 12)
        p = point3(2, 4, 4)
        self.assertEqual(p.dist((-2, -4, -4)), 12)

    def testAngle(self):
        p = point3(0, 1, 1)
        p2 = point3(0, 1, -1)
        self.assertEqual(p.angleBetween(p2), math.pi / 2)

    def testCross(self):
        p = point3(1, 0, 0)
        p2 = point3(0, 1, 0)
        c = p.cross(p2)
        self.assertEqual(c.x, 0)
        self.assertEqual(c.y, 0)
        self.assertEqual(c.z, 1)

class MyTestCaseAssorted(unittest.TestCase):
    def testMidpoint(self):
        pt = midPoint([ point2(0, 0), point2(6, 6)])
        self.assertEqual(pt.x, 3)
        self.assertEqual(pt.y, 3)
        pt = midPoint([ point3(0, 0, 0), point3(4, 4, 4)])
        self.assertEqual(pt.x, 2)
        self.assertEqual(pt.y, 2)
        self.assertEqual(pt.z, 2)

    def testNearestPoint(self):	
        pt = findNearest(point2(1, 1), [ point2(0, 0), point2(10, 10) ])
        self.assertEqual(pt.x, 0)	

        pt = findNearest(point3(1, 1, 1), [ point3(0, 0, 500), point3(10, 10, 10) ])
        self.assertEqual(pt.x, 10)

    def testCentral(self):
        pt = findCentralPoint([ point3(0, 0, 0), point3(0.75, 0.75, 0.75), point3(1, 1, 1) ])
        self.assertEqual(pt.x, 0.75)

    def testScalePts(self):
        # scaling point3's by a point3
        pts = [ point3(2, 2, 2), point3(8, 12, -7), point3(-2, -4, 5) ]
        scalePoints(pts, point3(1, 1, 1))	
        self.assertEqual(pts[1].x, 1.0)
        self.assertEqual(pts[0].y, 0.375)
        self.assertEqual(pts[2].z, 1.0)

        # scaling point3's by a point2
        pts = [ point3(2, 2, 2), point3(8, 12, -7), point3(-2, -4, 5) ]
        scalePoints(pts, point2(1, 1))	
        self.assertEqual(pts[1].x, 1.0)
        self.assertEqual(pts[0].y, 0.375)
        self.assertEqual(pts[2].z, 5) # should be unchanged

        # scaling point2's by a point3
        pts = [ point2(2, 2), point2(8, 12), point2(-2, -4) ]
        scalePoints(pts, point3(1, 1, 1))
        self.assertEqual(pts[1].x, 1.0)
        self.assertEqual(pts[0].y, 0.375)

        # scaling point2's by a point2
        pts = [ point2(2, 2), point2(8, 12), point2(-2, -4) ]
        scalePoints(pts, point2(1, 1))
        self.assertEqual(pts[1].x, 1.0)
        self.assertEqual(pts[0].y, 0.375)

    def testInTri(self):
        tri = [ point2(0, 0), point2(1, 0), point2(1, 1) ]
        self.assertEqual(inTriangle(point2(1.1, 0.5), tri), -1)
        self.assertEqual(inTriangle(point2(0.5, 0.75), tri), 0)
        self.assertEqual(inTriangle(point2(0.25, 0.25), tri), 1)

    def testIntersect(self):
        p1 = point2(0, 0)
        p2 = point2(10, 0)
        p3 = point2(5, 5)
        p4 = point2(5, -5)
        i = linesIntersect(p1, p2, p3, p4, True)
        self.assertEqual(i.x, 5)
        self.assertEqual(i.y, 0)
        p1 = point2(0, 0)
        p2 = point2(1, 1)
        p3 = point2(3, 1)
        p4 = point2(4, 0)
        i = linesIntersect(p1, p2, p3, p4, True)
        self.assertEqual(i, None)
        i = linesIntersect(p1, p2, p3, p4, False)
        self.assertEqual(i.x, 2)
        self.assertEqual(i.y, 2)

    def testDistToLine(self):
        p = point2(2, 2)
        a = point2(3, 3)
        b = point2(3, 5)
        self.assertEqual(1, distancePointToLine(p, a, b))

    def testDistToSeg(self):
        p = point2(2, 4)
        a = point2(3, 3)
        b = point2(3, 5)
        self.assertEqual(1, distancePointToSegment(p, a, b))

        p = point2(3, 0)
        a = point2(3, 3)
        b = point2(3, 5)
        self.assertEqual(3, distancePointToSegment(p, a, b))            

if __name__ == '__main__':
    test_support.run_unittest(MyTestCasePoint2, MyTestCasePoint3, MyTestCaseAssorted)