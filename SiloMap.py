from __future__ import division

import datetime
import math
import random

import MapGrapher
import Cod4Mapper
import datetime
import Gmap
import Geom
import Texture
import Shape

siloTxt = [
    'ch_concretewall01',
    'ch_concretewall02',
    'ch_concretewall03',
    'ch_concretewall04',
    'ch_concretewall06',
    'ch_concretewall07',
    'ch_concretewall08',
    'ch_concretewall09',
    'ch_concretewall10',
    'ch_factory_corrugatedsiding1',
    'ch_factory_corrugatedsiding2',
    'ch_factory_corrugatedsiding3',
    'ch_factory_corrugatedsiding4',
    'me_blue_metal_wall',
    'ship_body_wall',
    'ship_outside_wall'
]

def deflate_nodes(nodes, path_width, tolerance):
    """

    Shrink graph, keeping radii constant

    """
    min_dist = None
    min_pt = nodes[0]['pt'].copy()
    max_pt = nodes[0]['pt'].copy()
    rmin = None
    # find shortest distance from a node to another node or to a path
    for n in nodes:
        p = n['pt']
        r = n['radius']
        if p.x < min_pt.x:
            min_pt.x = p.x
        if p.y < min_pt.y:
            min_pt.y = p.y
        if p.z < min_pt.z:
            min_pt.z = p.z
        if p.x > max_pt.x:
            max_pt.x = p.x
        if p.y > max_pt.y:
            max_pt.y = p.y
        if p.z > max_pt.z:
            max_pt.z = p.z            
        p = Geom.point2(p.x, p.y)
        for n2 in nodes:
            if n2 is not n:                
                d = p.dist(n2['pt']) - (r + n2['radius'])                
                if min_dist is None or d < min_dist:
                    min_dist = d
                    rmin = r + n2['radius']
                for n3 in n2['conn']:
                    if n3 is not n:
                        d = Geom.distancePointToSegment(p, n2['pt'], n3['pt']) - r
                        if min_dist is None or d < min_dist:
                            min_dist = d
                            rmin = r
    scale = (tolerance + rmin) / (min_dist + rmin)
    o = ((max_pt - min_pt) * (1 - scale, 1 - scale, 1)) / (2, 2, 1) + min_pt
    o.z = min_pt.z
    for n in nodes:
        p = n['pt']
        p = (p - min_pt) * (scale, scale, 1) + o
        n['pt'] = p

def silo(m, n, siloHeight, pathWidth):
    tooSmall = False
    r = n['radius']

    # amount that path extends, as a proportion of the silo's
    # radius, to either side of the center of the path.  a proportion
    # of the radius is the same as an angle expressed in radians.
    pathAngle = pathWidth / r

    # collect opening angles    
    o = [ ]
    for cn in n['conn']:
        a = math.atan2(cn['pt'].y - n['pt'].y, cn['pt'].x - n['pt'].x)
        oa = a - pathAngle/2
        if oa < 0:
            oa += 2 * math.pi
        o.append(oa)
    o.sort()

    # see if any of the angles is too close to another
    for i in range(0, len(o)):
        a = o[i];
        a2 = 0        
        if i == len(o)-1:
            a2 = 2 * math.pi + o[0]
        else:
            a2 = o[i+1]
        if a2 - a <= pathAngle:
            tooSmall = True
            raise Exception, "Bad map generated.  Do over."


    txt = Texture.Basic(random.choice(siloTxt), 256, 256)
    txtCaulk = Texture.Basic('caulk', 64, 64)
    txtFloor1 = Texture.Basic('ch_factory_floorgrate', 64, 64)
    txtFloor2 = Texture.Basic('icbm_greymetal', 256, 256)

    centerBump = 0

    # spawn points
    sprad = r - 100
    if sprad > 0:
        for i in range(0, 4):
            a = i * math.pi / 2 
            pt = n['pt'] + (sprad * math.cos(a), sprad * math.sin(a), siloHeight/2 + centerBump - 5)
            m.spawnPoints.append(pt)

    cc = 8
    for a in o:
        p1 = n['pt'] + (r * math.cos(a), r * math.sin(a), 0)        
        p1_inner = n['pt'] + Geom.point3(cc * math.cos(a), cc * math.sin(a), 0)        
        p2 = n['pt'] + (r * math.cos(a+pathAngle), r * math.sin(a+pathAngle), 0)
        p2_inner = n['pt'] + (cc * math.cos(a+pathAngle), cc * math.sin(a+pathAngle), 0)
        s = Shape.box(p1, p2, 8, siloHeight/2)
        s.texture = txt
        m.shapes.append(s)
        t1 = (0, 0, siloHeight/2)
        t2 = (0, 0, 4)
        hh = Shape.Hexahedron()            
        hh.points[0] = p1 + t1
        hh.points[1] = p1_inner + t1
        hh.points[2] = p2_inner + t1
        hh.points[3] = p2 + t1
        hh.points[4] = hh.points[0] + t2
        hh.points[5] = hh.points[1] + t2 + (0, 0, centerBump)
        hh.points[6] = hh.points[2] + t2 + (0, 0, centerBump)
        hh.points[7] = hh.points[3] + t2
        hh.texture = txtFloor2
        m.shapes.append(hh)        

    segments = [ ]
    maxAngle = math.pi / 8 # would yield 16 segments around
    for i in range(0, len(o)):
        a1 = o[i] + pathAngle
        a2 = o[(i+1) % len(o)]
        if a2 < a1:
            a2 += 2 * math.pi
        da = a2-a1
        while da > maxAngle:
            da /= 2
        a = a1
        cc = 8
        while a < a2:
            p1 = n['pt'] + (r * math.cos(a), r * math.sin(a), 0)
            p0_inner = n['pt'] + ((r-5) * math.cos(a), (r-5) * math.sin(a), 0)
            p1_inner = n['pt'] + Geom.point3(cc * math.cos(a), cc * math.sin(a), 0)
            a += da
            if a > a2:
                a = a2
            p2 = n['pt'] + (r * math.cos(a), r * math.sin(a), 0)            
            p3_inner = n['pt'] + ((r-5) * math.cos(a), (r-5) * math.sin(a), 0)            
            p2_inner = n['pt'] + Geom.point3(cc * math.cos(a), cc * math.sin(a), 0)
            # TODO - make it perfect
            s = Shape.box(p1, p2, 8, siloHeight)
            s.texture = txt
            m.shapes.append(s)

            # make wedge connecting to center
            t1 = (0, 0, siloHeight/2 - 4)
            t2 = (0, 0, 4)
            hh = Shape.Hexahedron()            
            hh.points[0] = p0_inner + t1
            hh.points[1] = p1_inner + t1
            hh.points[2] = p2_inner + t1
            hh.points[3] = p3_inner + t1
            hh.points[4] = hh.points[0] + t2
            hh.points[5] = hh.points[1] + t2
            hh.points[6] = hh.points[2] + t2
            hh.points[7] = hh.points[3] + t2
            hh.texture = txtCaulk
            hh.faceTextures['top'] = txtFloor1
            m.shapes.append(hh)                        

def main(mod):
    m = Gmap.Map()
    today = datetime.date.today()    
    theday = today + datetime.timedelta(days=3)
    m.name = theday.strftime("mp_%Y%m%d")
    #m.name = 'mp_mysilo'

    # playable size
    psize = 3500    

    # terrain size (x and y)
    tsize = 3800

    # terrain height
    m.terrainTop = 1000

    pathWidth = 128
    pathThickness = 20
    railHeight = 128

    # sky
    skysize = Geom.point3(tsize+1500, tsize+1500, m.terrainTop+650)
    skyoffset = Geom.point3(-750, -750, 0)    
    Gmap.skyBox(m, skysize, skyoffset, 'sky_sp_airplane')

    m.bounds = (Geom.point3(skyoffset.x, skyoffset.y, -1 * skysize.z + skyoffset.z),
                Geom.point3(skyoffset.x + skysize.x, skyoffset.y + skysize.y, skyoffset.z + skysize.z))

    # make a graph
    g = MapGrapher.Graph(7, 0.5, 0.075, 1.35)
    nodes = g.getNodes()

    # scale graph    
    ptMin = None
    ptMax = None
    for n in nodes:
        pt = n['pt']
        r = n['radius']
        if ptMin is None:
            ptMin = pt.copy()
            ptMin.x -= r
            ptMin.y -= r
        else:
            if pt.x - r < ptMin.x:
                ptMin.x = pt.x - r
            if pt.y - r < ptMin.y:
                ptMin.y = pt.y - r
            if pt.z - r < ptMin.z:
                ptMin.z = pt.z - r
        if ptMax is None:
            ptMax = pt.copy()
            ptMax.x += r
            ptMax.y += r
            ptMax.z += r
        else:
            if pt.x + r > ptMax.x:
                ptMax.x = pt.x + r
            if pt.y + r > ptMax.y:
                ptMax.y = pt.y + r
            if pt.z + r > ptMax.z:
                ptMax.z = pt.z + r

    md = max((ptMax.x - ptMin.x, ptMax.y - ptMin.y))
    scale = Geom.point3(psize/md, psize/md, psize/md)

    siloHeight = 500

    txt2 = Texture.Basic('icbm_greymetal', 256, 256)
    txtrail = Texture.Basic('com_glass_clear', 256, 256)
    radmult = min((scale.x, scale.y))
    for n in nodes:
        n['pt'] -= ptMin
        n['pt'] *= scale
        n['radius'] *= radmult

    deflate_nodes(nodes, pathWidth, pathWidth)        

    # find maximum slope, for determining appropriate z scaling
    maxSlope = 0
    allowedSlope = 0.75
    twopts = None
    for n in nodes:
        p = Geom.point2(n['pt'].x, n['pt'].y)
        for n2 in n['conn']:
            p2 = n2['pt']
            d = p.dist(p2) - (n['radius'] + n2['radius']) # 2D distance
            zdiff = abs(n['pt'].z - p2.z)
            if d > 0:
                s = zdiff / d
                if s > maxSlope:
                    maxSlope = s
                    twopts = (n['pt'], n2['pt'])
    zMult = allowedSlope / maxSlope
    for n in nodes:
        n['pt'].z *= zMult        

    pathsMade = [ ]

    for n in nodes:

        silo(m, n, siloHeight, pathWidth)
        r1 = n['radius']

        for n2 in n['conn']:
            found = False
            for t in pathsMade:
                if t[0] is n2 and t[1] is n:
                    found = True
            if found == False:
                pathsMade.append((n, n2))                

                # contract to outside of silo                
                v = n['pt'] - n2['pt']
                v.unitize()
                dist = n['pt'].dist(n2['pt'])
                p1 = n2['pt'] + v * (dist - r1, dist - r1, dist - r1)
                p1.z = n['pt'].z + siloHeight/2 - pathThickness

                r2 = n2['radius']
                v = n2['pt'] - n['pt']
                v.unitize()
                p2 = n['pt'] + v * (dist - r2, dist - r2, dist - r2)
                p2.z = n2['pt'].z + siloHeight/2 - pathThickness

                s = Shape.box(p1, p2, pathWidth, pathThickness)
                s.texture = txt2
                m.shapes.append(s)

                # add rails
                # rotate unit vector 90 degrees
                v = Geom.point3(-1 * v.y, v.x, 0)
                v *= (pathWidth / 2 + 2, pathWidth / 2 + 2, 0)
                rp1 = p1 + v
                rp2 = p2 + v
                s = Shape.box(rp1, rp2, 4, pathThickness + railHeight)
                s.texture = txtrail
                m.shapes.append(s)

                rp1 = p1 - v
                rp2 = p2 - v
                s = Shape.box(rp1, rp2, 4, pathThickness + railHeight)
                s.texture = txtrail
                m.shapes.append(s)

    # pass on to module
    mod.write(m, None)

if __name__ == '__main__':
    main(Cod4Mapper)