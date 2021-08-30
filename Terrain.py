from __future__ import division
import random
import copy
import math

import Geom
import Util

class Patch():
    def __init__(self, u_size, v_size):
        if u_size < 2 or v_size < 2:
            raise Exception('Terrain Patches must be 2x2 or larger')
        self.u_size = u_size
        self.v_size = v_size
        self.points = [ ]
        self.rectangular = False
        self.rectTriFind = None
        self.invertNormals = False

        for u in range(0, self.u_size):
            self.points.append([ ])
            for v in range(0, int(self.v_size)):
                self.points[u].append(Geom.point3(0, 0, 0))

    def setPoint(self, u, v, p3):
        self.points[u][v] = copy.copy(p3)

    def __rectTriFind(self, pt):
        ret = None

        if Util.inRange(pt.x, self.__rectMinX, self.__rectMaxX) == False or Util.inRange(pt.y, self.__rectMinY, self.__rectMaxY) == False:
            return ret

        u = int(math.floor((pt.x - self.__rectMinX) * self.__rectScaleX))
        v = int(math.floor((pt.y - self.__rectMinY) * self.__rectScaleY))
        c1 = Geom.point2(self.points[u][v].x, self.points[u][v].y)
        c2 = Geom.point2(self.points[u+1][v+1].x, self.points[u+1][v+1].y)
        # get 2D distances
        d1 = c1.dist(pt)
        d2 = c2.dist(pt)

        if d1 < d2:
            ret = [ self.points[u][v], self.points[u][v+1], self.points[u+1][v] ]
        else:
            ret = [ self.points[u][v+1], self.points[u+1][v+1], self.points[u+1][v] ]

        return ret

    def setRectangular(self):    
        self.rectangular = True

        min_x = self.points[0][0].x
        min_y = self.points[0][0].y
        max_x = self.points[self.u_size-1][self.v_size-1].x
        max_y = self.points[self.u_size-1][self.v_size-1].y
        scale_x = (self.u_size-1) / (max_x - min_x)
        scale_y = (self.v_size-1) / (max_y - min_y)

        self.__rectMinX = min_x
        self.__rectMinY = min_y
        self.__rectMaxX = max_x
        self.__rectMaxY = max_y
        self.__rectScaleX = scale_x
        self.__rectScaleY = scale_y        

        # basically saying it's ok to call this now
        self.rectTriFind = self.__rectTriFind

    def setRectangularXY(self, x0, y0, x1, y1):
        y_coords = []
        for v in range(0, self.v_size):
            y_coords.append(y0 + (y1-y0) * (v / (self.v_size-1)))
        for u in range(0, self.u_size):
            ptsu = self.points[u];
            x = x0 + (x1-x0) * (u / (self.u_size-1))
            for v in range(0, self.v_size):
                pt = ptsu[v]
                pt.x = x
                pt.y = y_coords[v]                
        self.setRectangular()

    def randomize(self, low, high):
        amplitude = high - low
        for u in range(0, self.u_size):
            ptsu = self.points[u]
            for v in range(0, self.v_size):
                ptsu[v].z = amplitude * random.random() + low

    def smoothWeights(self, weights):
        for u in range(0, int(self.u_size)):
            u_plus = (u+1) % self.u_size
            if u > 0:
                u_minus = u-1
            else:
                u_minus = self.u_size - 1
            for v in range(0, self.v_size):
                v_plus = (v+1) % self.v_size
                if v > 0:
                    v_minus = v-1
                else:
                    v_minus = self.v_size - 1

                vals = (
                    weights[u][v]['cm'],
                    weights[u_plus][v]['cr'],
                    weights[u_minus][v]['cl'],
                    weights[u][v_plus]['bm'],
                    weights[u][v_minus]['tm'],
                    weights[u_plus][v_plus]['br'],
                    weights[u_plus][v_minus]['tr'],
                    weights[u_minus][v_plus]['bl'],
                    weights[u_minus][v_minus]['tl']
                )
                z = 0
                for k in vals:
                    z += k

                self.points[u][v].z = z


    # a crazy kind of smoothing that puts more weight on different neighbors
    # based on the velocities at that certain point, specified using two
    # separate terrains, one for x and one for y.
    def smoothWindy(self, twx, twy):
        weights = [ [ 0.0 for v in range(0, self.v_size) ] for u in range(0, self.u_size) ]
        if self.u_size != twx.u_size or self.v_size != twx.v_size \
           or self.u_size != twy.u_size or self.v_size != twy.v_size:
            raise Exception("Incompatible terrain sizes")
        # weights at each point depend on the wind
        for u in range(0, self.u_size):
            for v in range(0, self.v_size):
                w = { }
                wnd = Geom.point2(twx.points[u][v].z, twy.points[u][v].z)
                # consider a rectangle extending from the pixel, in the u and v
                # direction, just past the bounds of the pixel, and then pushed
                # further by the wind
                p1 = Geom.point2(-0.75, -0.75)
                p2 = Geom.point2(0.75, 0.75)
                d1x = 0.0
                d2x = 0.0
                d1y = 0.0
                d2y = 0.0
                if wnd.x < 0:
                    d1x = wnd.x * 0.75
                else:
                    d2x = wnd.x * 0.75
                if wnd.y < 0:
                    d1y = wnd.y * 0.75
                else:
                    d2y = wnd.y * 0.75
                p1 += (d1x, d1y)
                p2 += (d2x, d2y)
                a = (p2.x - p1.x) * (p2.y - p1.y)
                w['tl'] = (-0.5 - p1.x) * (-0.5 - p1.y) / a
                w['tm'] = (-0.5 - p1.y) / a
                w['tr'] = (p2.x - 0.5) * (-0.5 - p1.y) / a
                w['cl'] = (-0.5 - p1.x) / a
                w['cm'] = 1.0 / a
                w['cr'] = (p2.x - 0.5) / a
                w['bl'] = (-0.5 - p1.x) * (p2.y - 0.5) / a
                w['bm'] = (p2.y - 0.5) / a
                w['br'] = (p2.x - 0.5) * (p2.y - 0.5) / a
                weights[u][v] = w
        self.smoothWeights(weights)

    def smooth(self):
        w = { 'tl':0.025, 'tm':0.1, 'tr':0.025, 'cl':0.1, 'cm':0.5, 'cr':0.1, 'bl':0.025, 'bm':0.1, 'br':0.025 }
        weights = [ [ ] for u in range(0, self.u_size) ]
        # precompute all weighted point values
        for u in range(0, self.u_size):
            for v in range(0, self.v_size):
                o = { }
                z = self.points[u][v].z
                for k in w.keys():
                    o[k] = w[k] * z;          
                weights[u].append(o)
        self.smoothWeights(weights)

    def power(self, p):
        for u in range(0, self.u_size):
            ptsu = self.points[u]
            for v in range(0, self.v_size):
                pt = ptsu[v]
                sgn = 1.0
                val = pow(abs(pt.z), p)
                if pt.z < 0.0:
                    val *= -1.0
                pt.z = val

    def getRange(self):
        zmin = None
        zmax = None
        # determine current range
        for u in range(0, self.u_size):
            ptsu = self.points[u]
            for v in range(0, self.v_size):
                pt = ptsu[v]
                ptz = pt.z
                if zmin is None or ptz < zmin:
                    zmin = ptz    
                if zmax is None or ptz > zmax:
                    zmax = ptz
        return (zmin, zmax)

    def amplify(self, low, high):
        zmin = None
        zmax = None
        ptsu = None
        u = 0
        v = 0
        ci = 0
        mult = 0.0
        offset = 0.0
        pt = None
        ptz = 0        

        (zmin, zmax) = self.getRange()

        # perfectly flat.  can't be amplified.
        if zmax-zmin == 0.0:
            return False

        mult = (high - low) / (zmax - zmin)
        offset = low - zmin

        for u in range(0, self.u_size):
            ptsu = self.points[u]
            for v in range(0, self.v_size):
                pt = ptsu[v]
                pt.z = (pt.z - zmin) * mult + low

        return True

    def onTerrain (self, point):
        if self.rectTriFind:
            return self.rectTriFind(point)      

        tris = [ ]

        for u in range(0, self.u_size-1):
            for v in range(0, self.v_size-1):
                for t in range(0, 2):
                    tri = None
                    intri = None

                    if t == 0:
                        # bottom-left
                        tri = [ self.points[u][v], self.points[u+1][v], self.points[u][v+1] ]
                    else: 
                        # top-right  
                        tri = [ self.points[u+1][v], self.points[u+1][v+1], self.points[u][v+1] ]            

                    intri = Geom.inTriangle(point, tri)
                    if intri == 1:
                        return tri

    def heightAt (self, point):
        tri = self.onTerrain(point);
        if tri is None:
            raise Exception('Point ' + str(point) + ' not on terrain')
        vec1 = tri[1] - tri[0]
        vec2 = tri[2] - tri[0]
        norm = vec2.cross(vec1)
        # not on the plane after all
        if norm.z == 0.0:
            return 0.0
        a = tri[1]
        z = a.z - ((point.x-a.x)*norm.x + (point.y-a.y)*norm.y) / norm.z
        return z

    def split(self, max_u, max_v):
        if self.u_size > max_u:
            us_1 = int(math.ceil(self.u_size / 2))
            us_2 = 1 + self.u_size - us_1
            tp1 = Patch(us_1, self.v_size)
            tp2 = Patch(us_2, self.v_size)
            for u in range(0, us_1):
                tp1.points[u] = self.points[u]
            for u in range(0, us_2):
                tp2.points[u] = self.points[u+us_1-1]
            return (tp1, tp2)        
        elif self.v_size > max_v:
            vs_1 = int(math.ceil(self.v_size / 2))
            vs_2 = 1 + self.v_size - vs_1
            tp1 = Patch(self.u_size, vs_1)
            tp2 = Patch(self.u_size, vs_2)
            for u in range(0, self.u_size):
                for v in range(0, self.v_size):
                    do_1 = False
                    do_2 = False
                    if v < vs_1:
                        do_1 = True
                    if v >= vs_1 - 1:
                        do_2 = True
                    if do_1 is True:
                        tp1.points[u][v] = self.points[u][v]
                    if do_2 is True:
                        tp2.points[u][1+v-vs_1] = self.points[u][v] 
            return (tp1, tp2)
        else:
            return self
        #us_1 = int(math.ceil(self.u_size / 2))
        #us_2 = 1 + self.u_size - us_1
        #tp1 = Patch(us_1, self.v_size)
        #tp2 = Patch(us_2, self.v_size)
        #for u in range(0, us_1):
        #    tp1.points[u] = self.points[u]
        #for u in range(0, us_2):
        #    tp2.points[u] = self.points[u+us_1-1]
        #return (tp1, tp2)

    def invert(self):
        rng = self.getRange()
        for u in range(0, self.u_size):
            ptsu = self.points[u]
            for v in range(0, self.v_size):
                pt = ptsu[v]
                pt.z = rng[0] + rng[1] - pt.z

    def circularTaper(self, lower, r1, r2):
        rng = self.getRange()
        cx = 0
        cy = 0
        lowz = rng[0] - lower
        if self.u_size % 2 == 1:
            cx = self.points[self.u_size // 2][0].x
        else:
            cx = (self.points[self.u_size // 2][0].x + self.points[self.u_size // 2 - 1][0].x) / 2
        if self.v_size % 2 == 1:
            cy = self.points[0][self.v_size // 2].y
        else:
            cy = (self.points[0][self.v_size // 2].y + self.points[0][self.v_size // 2 - 1].y) / 2                
        c = Geom.point2(cx, cy)
        for u in range(0, self.u_size):
            ptsu = self.points[u]
            for v in range(0, self.v_size):                
                pt = ptsu[v]
                rad = c.dist(pt)
                if rad >= r1:
                    if rad >= r2:
                        pt.z = lowz
                    else:
                        prop = (r2 - rad) / (r2 - r1)
                        pt.z = lowz + prop * pt.z - rng[0]

    def radiusSmooth(self, n, r1, r2, midpt):        
        ts = Patch(self.u_size, self.v_size)
        ts.points = copy.deepcopy(self.points)
        dr = r2 - r1
        for i in range(0, n):
            ts.smooth()        
        for u in range(0, self.u_size):        
            for v in range(0, self.v_size):
                pt = self.points[u][v]
                spt = ts.points[u][v]
                d = midpt.dist((pt.x, pt.y))
                if d >= r1 and d <= r2:
                    p1 = (r2 - d) / dr
                    p2 = 1.0 - p1
                    pt.z = p1 * pt.z + p2 * spt.z

class alphaPoint3(Geom.point3):
    def __init__(self, x, y, z, a):
        Geom.point3.__init__(self, x, y, z)
        self.a = a                        