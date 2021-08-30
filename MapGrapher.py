from __future__ import division

import random
import math
import Geom

def findNearestNode(p, nodes):
    minDist = None
    cn = None    
    for n in nodes:
        np = n['pt']
        if p.x != np.x and p.y != np.y:
            d = p.dist(np)
            if cn == None or d < minDist:
                minDist = d
                cn = n
    return cn

def trimOutlierPoints(pts, cp, tol):
    dtot = 0
    for p in pts:
        if p != cp:
            dtot += cp.dist(p)
    dave = dtot / (len(pts) - 1)
    dmax = (1 + tol) * dave
    return [ p for p in pts if cp.dist(p) <= dmax ]

def killTooClosePoints(pts, tol):
    for p in pts:
        for p2 in pts:
            if p != p2 and p in pts and p2 in pts:
                d = p.dist(p2)
                if d < tol:
                    pts.remove(p2)

def jigglePoints(pts, aved, power):    
    # using average distance as a kind of inflection point, apply a sort of backward
    # gravity.  points further away from eachother than d will be attracted to eachother.
    # points closer to eachother than d will repel eachother.

    # a place to store how much each point will move (in x,y directions) after all have been evaluated
    offsets = [ Geom.point3(0.0, 0.0, 0.0) for p in pts ]
    for i in range(0, len(pts)):
        p = pts[i]
        for p2 in pts:
            if p2 != p:
                d = p.dist(p2)
                s = 0.0
                # points that are right at the perfect distance don't effect eachother
                if d != aved:
                    v = Geom.point3(p2.x - p.x, p2.y - p.y, 0.0)
                    s = power * ((d - aved) / aved)
                    if (s < 0.0):                        
                        s *= 25
                    v *= (s, s, 1)
                    offsets[i] += v
    for i in range(0, len(pts)):
        p = pts[i]
        off = offsets[i]
        p += off

class Graph:
    # create graph object
    # numPoints - number of points to start with.  some may get pruned off.
    # dtol - % tolerance for distance to center at which to prune before making connections.
    # ctol - distance at which points are considered too close together.  keep in mind 0-1 scale.
    # dist_tol - % of average size under which extra nonconflicting connections are created
    def __init__(self, numPoints, dtol, ctol, dist_tol):
        self.__points = None
        self.__nodes = [ ]
        self.__dtol = dtol
        self.__ctol = ctol
        self.__dist_tol = dist_tol
        self.__runTries = 0
        self.originalJiggleDist = None
        ret = False
        while ret == False:
            ret = self.__run(numPoints)

    def __run(self, numPoints):

        self.__runTries += 1
        if self.__runTries == 10000:
            raise Exception('Failed too many times to create a sensible graph')

        # randomly generate N points
        self.__points = [ Geom.point3(random.random(), random.random(), 0.0) for i in range(0, numPoints) ]    

        # stretch out the points so they take up the entire unit square
        try:
            Geom.scalePoints(self.__points, (1.0, 1.0))
        except ZeroDivisionError:            
            return False

        for i in range(0, 20):
            self.jiggle(0.0025)

        killTooClosePoints(self.__points, self.__ctol)        

        # pick the center-most point
        cp = Geom.findCentralPoint(self.__points)    

        # get rid of extreme points
        self.__points = trimOutlierPoints(self.__points, cp, self.__dtol)

        try:
            Geom.scalePoints(self.__points, (1.0, 1.0))
        except ZeroDivisionError:            
            return False        

        # pick the center-most point
        cp = Geom.findCentralPoint(self.__points)

        self.__connectAll(cp)
        self.__extraConnect()                    
        self.__setNodeRadii()
        self.__killIntersecting()
        self.__randomZ()

        return True

    def __setNodeRadii(self):
        deflate_min = 1.17 # 55% contraction minimum -> tan(90 * 0.55) = 1.17
        deflate_max = 1.96 # 70% contraction maximum -> tan(90 * 0.7) = 1.96
        deflater = deflate_min + random.random() * (deflate_max - deflate_min)
        for n in self.__nodes:
            nn = findNearestNode(n['pt'], self.__nodes)
            if nn is not None:
                # multipler between 0.3 -> 1.0.  arctangent approaches pi/2 as its argument grows.
                mult = math.atan(len(n['conn']) / deflater) / (math.pi / 2)                
                d = n['pt'].dist(nn['pt'])
                n['radius'] = (d / 2) * mult
            else:
                n['radius'] = 0

    def __killIntersecting(self):
        # for every node, check to see if there are any lines connecting other nodes
        # that pass through this one's radius
        for n in self.__nodes:
            for n2 in self.__nodes:
                if n2 is n:
                    continue # skip n
                for n3 in n2['conn']:
                    if n3 is n:
                        continue # skip n
                    d = Geom.distancePointToSegment(n['pt'], n2['pt'], n3['pt'])
                    if d < n['radius']:
                        # whack the connection
                        self.__disconnectNodes(n2, n3)


    def killIntersecting(self):
        self.__killIntersecting()

    def jiggle(self, power):
        # get average distance to midpoint
        if self.originalJiggleDist is None:
            mp = Geom.midPoint(self.__points)
            aved = 0.0
            for p in self.__points:
                aved += p.dist(mp)
            aved /= len(self.__points)
            self.originalJiggleDist = aved
        else:
            aved = self.originalJiggleDist

        jigglePoints(self.__points, self.originalJiggleDist, power)
        killTooClosePoints(self.__points, self.__ctol)

    def __connectNodes(self, n1, n2):
        for n in n1['conn']:
            if n is n2:
                return
        for n in n2['conn']:
            if n is n1:
                return            
        n1['conn'].append(n2)  
        n2['conn'].append(n1)

    def __disconnectNodes(self, n1, n2):
        if n2 in n1['conn']:
            n1['conn'].remove(n2)
        if n1 in n2['conn']:
            n2['conn'].remove(n1)

    def __connectPoint(self, n, p2):        
        n2 = { 'pt': p2, 'conn': [ ] }
        self.__nodes.append(n2)
        self.__connectNodes(n, n2)

    def __connectAll(self, cp):
        cn = { 'pt': cp, 'conn': [ ] }
        self.__nodes.append(cn)

        # gather all points that except the central point        
        ungraphed = [ p for p in self.__points if p != cp ]

        # while not every point is on the graph
        while len(ungraphed) > 0:
            # find the point nearest the center that is not on the graph
            p = Geom.findNearest(cp, ungraphed)
            # find its nearest neighbor node that is on the graph
            n = findNearestNode(p, self.__nodes)
            self.__connectPoint(n, p)
            ungraphed.remove(p)

    def __nodeConnected(self, n1, n2):
        inConn = False
        pt2 = n2['pt']
        for n in n1['conn']:
            pt = n['pt']
            if pt.compare(pt2):
                return True
        return False

    def __extraConnect(self):
        # find interesting loop-forming connections that don't cause problems
        # for nodes connected to at least 3 others

        # find close-together unconnected nodes that don't cross any existing
        # lines that are shorter lines than a certain tolerance.
        # first, calculate the average connection length.
        ave_len = 0.0
        num_conn = 0
        for n in self.__nodes:
            for c in n['conn']:
                dist = n['pt'].dist(c['pt'])
                ave_len += dist
                num_conn += 1
        if num_conn > 0:
            ave_len /= num_conn
        tol = ave_len * self.__dist_tol
        # make a list of all unconnected nodes that are closer together than
        # the minimum tolerance
        u = [ ]
        lines = [ ]

        for n in self.__nodes:
            for n2 in self.__nodes:
                if n['pt'].compare(n2['pt']) == False:
                    if self.__nodeConnected(n2, n):
                        # add to list of lines for later comparison.
                        # see that the inverse of this line isn't already listed
                        # because the complimentary connection was already found
                        found = False
                        for ln in lines:
                            if ln[1].compare(n['pt']) and ln[0].compare(n2['pt']):
                                found = True
                                break
                        if found == False:
                            lines.append((n['pt'], n2['pt']))
                    else:
                        d = n['pt'].dist(n2['pt'])
                        if n['pt'].dist(n2['pt']) < tol:
                            u.append((n, n2))        
        # trim any connection lines that intersect any other existing lines
        u2 = []
        for c in u:
            intersected = False
            for ln in lines:
                i = Geom.linesIntersect(ln[0], ln[1], c[0]['pt'], c[1]['pt'], True)
                if i is not None:
                    if i.compare(ln[0]) == False and i.compare(ln[1]) == False and i.compare(c[0]['pt']) == False and i.compare(c[1]['pt']) == False:
                        intersected = True
            if intersected == False:
                u2.append(c)
                lines.append((c[0]['pt'], c[1]['pt']))  
        for c in u2:
            self.__connectNodes(c[0], c[1])

    def __randomZ(self):
        for n in self.__nodes:
            n['pt'].z = random.random()

    def numPoints(self):
        return len(self.__points)

    def numNodes(self):
        return len(self.__nodes)

    def getNodes(self):
        return self.__nodes        