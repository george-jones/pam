from __future__ import division

import datetime
import math
import random
import copy

import MapGrapher
import Cod4Mapper
import datetime
import Gmap
import Geom
import Texture
import Shape
import Terrain

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

def wedge_terrain(pt, r, a0, a1, nr, nc):
    t = Terrain.Patch(nc+1, nr+1)
    t.textureMap = Texture.Map("ch_cliff01", t.u_size, t.v_size, 0.2, 0.2, Texture.map_type['uniform'])    
    da = (a1 - a0) / nc
    dr = r / nr
    for i in range(0, nc+1):        
        for j in range(0, nr+1):
            ang = a0 + i * da
            rad = j * dr            
            p = pt + Geom.point3(rad * math.cos(ang), rad * math.sin(ang), 0)
            t.points[i][j] = p
    t.invertNormals = True
    return t

def hemisphere_slice_terrain(pt, h, r, a0, a1, nr, nc, doorway, dwsegs):    
    doorway_height = 128
    dth = (math.pi / 2) / nr
    zmult = h / r
    if doorway == True:
        nr -= dwsegs
    t = Terrain.Patch(nc+1, nr+1)
    t.textureMap = Texture.Map("ch_cliff02", t.u_size, t.v_size, 0.2, 0.2, Texture.map_type['uniform'])
    da = (a1 - a0) / nc    
    for i in range(0, nc+1):        
        for j in range(0, int(nr+1)):
            ang = a0 + i * da
            th = j * dth
            x = r * math.sin(th) * math.cos(ang)
            y = r * math.sin(th) * math.sin(ang)
            z = r * math.cos(th) * zmult
            p = pt + Geom.point3(x, y, z)
            t.points[i][j] = p
    return t

def cave_room(m, n, pathWidth, doorsegs, nr, nc):
    tooSmall = False
    r = n['radius']
    cave_height = 256

    # amount that path extends, as a proportion of the silo's
    # radius, to either side of the center of the path.  a proportion
    # of the radius is the same as an angle expressed in radians.
    pathAngle = pathWidth / r

    # collect opening angles

    # sort function for (angle, node) tuples
    def angsort(ang1, ang2):
        return cmp(ang1[0], ang2[0])
    
    o = [ ]    
    for cn in n['conn']:
        a = math.atan2(cn['pt'].y - n['pt'].y, cn['pt'].x - n['pt'].x)
        oa = a - pathAngle/2
        if oa < 0:
            oa += 2 * math.pi
        o.append((oa, cn))
    o.sort(angsort)

    # see if any of the angles is too close to another
    for i in range(0, len(o)):
        a = o[i][0];
        a2 = 0        
        if i == len(o)-1:
            a2 = 2 * math.pi + o[0][0]
        else:
            a2 = o[i+1][0]
        if a2 - a <= pathAngle:
            tooSmall = True
            raise Exception, "Bad map generated.  Do over."

    patches = [ ]    
    for a in o:
        pat = (wedge_terrain(n['pt'], r, a[0], a[0] + pathAngle, nr, nc), 
               hemisphere_slice_terrain(n['pt'], cave_height, r, a[0], a[0] + pathAngle, nr, nc, True, doorsegs),
               a)
        patches.append(pat)        
        
    segments = [ ]
    maxAngle = math.pi / 8 # would yield 16 segments around
    for i in range(0, len(o)):
        a1 = o[i][0] + pathAngle
        a2 = o[(i+1) % len(o)][0]
        if a2 < a1:
            a2 += 2 * math.pi
        da = a2-a1
        while da > maxAngle:
            da /= 2
        a = a1
        while a < a2:
            a_initial = a
            a += da
            if a > a2:
                a = a2
            a_final = a
            pat = (wedge_terrain(n['pt'], r, a_initial, a_final, nr, nc),
                   hemisphere_slice_terrain(n['pt'], cave_height, r, a_initial, a_final, nr, nc, False, doorsegs),
                   (a_initial, None))
            patches.append(pat)
            
    bump = Terrain.Patch(32, 32)
    bump.setRectangularXY(n['pt'].x - r - 100, n['pt'].y - r - 100, n['pt'].x + r + 100, n['pt'].y + r + 100)
    bump.randomize(0.0, 1.0)
    for i in range(0, 5):
        bump.smooth()
    bump.amplify(0, 1)
    bump.power(6)
    bump.amplify(0, 100)
    # flatten somewhat everything past a certain radius.  Then smooth again so it blends in.
    flat_rad = 0.8 * r
    pt = Geom.point2(n['pt'].x, n['pt'].y)
    flatten = 0.25
    for i in range(0, bump.u_size):
        for j in range(0, bump.v_size):
            br = pt.dist(bump.points[i][j])
            if br >= flat_rad:
                bump.points[i][j].z *= flatten
    for i in range(0, 3):
        bump.smooth()
    bump.amplify(0, 100)
    
    zbump = Terrain.Patch(32, 32)
    zbump.setRectangularXY(n['pt'].x - r - 100, n['pt'].y - r - 100, n['pt'].x + r + 100, n['pt'].y + r + 100)
    zbump.randomize(0.0, 1.0)
    for i in range(0, 5):
        zbump.smooth()
    zbump.power(8)
    zbump.amplify(0, r/2)
    zbump.circularTaper(0, 9*r/10, r)    

    # spawn points
    sprad = r / 2
    if sprad > 0:
        for i in range(0, 4):
            a = i * math.pi / 2 
            pt = n['pt'] + (sprad * math.cos(a), sprad * math.sin(a), -5)
            pt.z = n['pt'].z + bump.heightAt(pt)
            m.spawnPoints.append(pt)            
        
    floor2alpha = Terrain.Patch(bump.u_size, bump.v_size)
    floor2alpha.setRectangularXY(n['pt'].x - r - 100, n['pt'].y - r - 100, n['pt'].x + r + 100, n['pt'].y + r + 100)
    floor3alpha = Terrain.Patch(bump.u_size, bump.v_size)
    floor3alpha.setRectangularXY(n['pt'].x - r - 100, n['pt'].y - r - 100, n['pt'].x + r + 100, n['pt'].y + r + 100)
    flooralphas = [ floor2alpha, floor3alpha ]
    for fa in flooralphas:
        fa.randomize(0, 0.65)
        for i in range(0, 5):
            fa.smooth()
        fa.amplify(0, 0.65)
            
    for pat in patches:
        floor = pat[0]
        dome = pat[1]
        floor2 = copy.deepcopy(floor)        
        # "ch_asphaltcracks01_dec"
        floor2.textureMap = Texture.Map("ch_cliff02_decal", floor2alpha.u_size, floor2alpha.v_size, 0.1, 0.1, Texture.map_type['uniform'])
        floor3 = copy.deepcopy(floor)
        floor3.textureMap = Texture.Map("kh_mud03_decal", floor3alpha.u_size, floor3alpha.v_size, 0.15, 0.15, Texture.map_type['uniform'])
        for i in range(0, floor.u_size):
            for j in range(0, floor.v_size):
                p = floor.points[i][j]
                p.z += bump.heightAt(p)
                p2 = floor2.points[i][j]
                p2.a = floor2alpha.heightAt(p2)
                p2.z = p.z
                p3 = floor3.points[i][j]
                p3.a = floor3alpha.heightAt(p3)
                p3.z = p.z
                
        m.terrains.append(floor)
        m.terrains.append(floor2)
        m.terrains.append(floor3)

        lim = int(dome.v_size-1)
        is_door = False
        if dome.v_size < nr:
            lim += 1
            is_door = True            
            
        for i in range(0, dome.u_size):
            for j in range(0, lim):
                p = dome.points[i][j]
                p.z += zbump.heightAt(p)
            if is_door == False:
                # move bottom to be welded with floor
                j = dome.v_size-1
                dome.points[i][j].z = floor.points[i][j].z
                
        dome2 = copy.deepcopy(dome)         
        dome3 = copy.deepcopy(dome)        
        dome2.textureMap = Texture.Map("kh_mud03_decal", dome2.u_size, dome2.v_size, 256, 16, Texture.map_type['natural'])
        # ch_asphaltcracks01_dec
        dome3.textureMap = Texture.Map("ch_cliff02_decal", dome3.u_size, dome3.v_size, 0.1, 0.1, Texture.map_type['uniform'])

        for i in range(0, int(dome2.u_size)):
            for j in range(0, int(dome2.v_size)):
                p = dome2.points[i][j]
                h = (p.z - n['pt'].z) / cave_height
                h += random.random() * 0.4 - 0.2
                if h > 1.0:
                    h = 1.0
                elif h < 0.0:
                    h = 0.0
                pa = Terrain.alphaPoint3(p.x, p.y, p.z, 1.0 - h)
                dome2.points[i][j] = pa
                h = (p.z - n['pt'].z) / cave_height
                h = random.random() * 0.65
                pa = Terrain.alphaPoint3(p.x, p.y, p.z, h)
                dome3.points[i][j] = pa
        m.terrains.append(dome)
        m.terrains.append(dome2)
        m.terrains.append(dome3)
    
    # central light
    spotname = 'auto' + str(len(m.objects))
    lightheight = patches[0][1].points[0][0].z - 15
    light = Gmap.Obj()
    light.pos = Geom.point3(n['pt'].x, n['pt'].y, lightheight)
    light.prop['def'] = 'light_point_linear'
    light.prop['radius'] = r * 0.95
    light.prop['_color'] = '1 1 1'
    light.prop['intensity'] = '1'
    light.prop['classname'] = 'light'
    light.prop['spawnflags'] = '1' # PRIMARY_OMNI
    light.prop['target'] = spotname
    m.objects.append(light)
    
    # spot point
    spot = Gmap.Obj()
    spot.pos = light.pos.copy()
    spot.pos.z -= lightheight
    spot.prop['targetname'] = spotname
    spot.prop['classname'] = 'info_null'
    m.objects.append(spot)
    
    # lamp object
    lamp = Gmap.Obj()
    lamp.pos = light.pos + (0, 0, 15)
    lamp.prop['classname'] = 'misc_prefab'
    lamp.prop['model'] = 'prefabs/misc_models/icbm_cagelamp_on.map'
    m.objects.append(lamp)        
        
    def psort(p1, p2):
        return angsort(p1[2], p2[2])
    patches.sort(psort)
    
    exits = [ ]
    for i, p in enumerate(patches):        
        p = patches[i]
        if p[2][1] is not None:
            i_prev = i-1
            if i_prev < 0:
                i_prev = len(patches)-1
            i_next = i+1
            if i_next >= len(patches):
                i_next = 0
            p_prev = patches[i_prev]
            p_next = patches[i_next]            
            floor = p[0]
            dome = p[1]
            d_prev = p_prev[1]
            d_next = p_next[1]
            pts = [ ]
            for u in range(0, dome.u_size):
                pts.append(dome.points[u][dome.v_size-1])
            for v in range(d_next.v_size-doorsegs, d_next.v_size-1):
                pts.append(d_next.points[0][v])
            for u in range(floor.u_size-1, -1, -1):
                pts.append(floor.points[u][floor.v_size-1])
            for v in range(d_prev.v_size-2, d_prev.v_size-doorsegs-1, -1):
                pts.append(d_prev.points[d_prev.u_size-1][v])
            e = { 'node': p[2][1], 'points': pts }
            exits.append(e)        
    return exits

def main(mod):
    m = Gmap.Map()
    today = datetime.date.today()    
    theday = today + datetime.timedelta(days=0)
    m.name = theday.strftime("mp_%Y%m%d")
    
    # playable size
    psize = 3500    

    # terrain size (x and y)
    tsize = 3800

    # terrain height
    m.terrainTop = 500

    pathWidth = 128
    pathThickness = 20
    railHeight = 128
    
    # approximate length of each segment of connecting tunnels
    tsl = 64
    
    # how many vertical segments doorways occupy
    doorsegs = 2

    # sky
    skysize = Geom.point3(tsize+1500, tsize+1500, m.terrainTop+300)
    skyoffset = Geom.point3(-750, -750, 0)    
    Gmap.skyBox(m, skysize, skyoffset, 'sky_ac130')

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

    radmult = min((scale.x, scale.y))
    for n in nodes:
        n['pt'] -= ptMin
        n['pt'] *= scale
        n['radius'] *= radmult

    deflate_nodes(nodes, pathWidth, pathWidth)

    # find maximum slope, for determining appropriate z scaling
    maxSlope = 0
    allowedSlope = 0.65
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
    
    paths = [ ]
    nr = 7
    nc = 4    
    for n in nodes:
        exits = cave_room(m, n, pathWidth, doorsegs, nr, nc)
        for e in exits:            
            p = None
            found = False
            # look for opposite connection first
            for psearch in paths:
                if psearch['n2'] is n and psearch['n1'] is e['node']:                    
                    p = psearch
                    break
            if p is None:
                p = { 'n1': n, 'n2': e['node'], 'pts1': e['points'], 'pts2': None }
                paths.append(p)
            else:
                p['pts2'] = e['points']
            
    for p in paths:
        a = p['pts1']
        b = p['pts2']
        k = len(a)+1
        caps = [ ]
        caps.append([ ])
        caps.append([ ])
        for i0 in range(0, k):
            i = i0
            if i >= len(a):
                i -= len(a)
            if i <= nc:
                j = nc - i
            else:
                j = nc + 1 + (len(a) - i - 1)
                if j >= len(b):
                    j -= len(b)
            pa = a[i]            
            pb = b[j]
            caps[0].append(pa)
            caps[1].append(pb)
        dist = caps[0][0].dist(caps[1][0])
        segs = int(math.ceil(dist / tsl))
        slices = segs + 1        
        s = [ ]
        for i in range(0, slices):
            if i == 0:
                s.append(caps[0])
            elif i == slices-1:
                s.append(caps[1])
            else:
                # interpolate
                sl = [ ]
                for j in range(0, len(caps[0])):
                    ma = slices-i-1
                    mb = i
                    mt = ma + mb
                    pa = caps[0][j] * (ma, ma, ma)
                    pb = caps[1][j] * (mb, mb, mb)
                    pt = (pa + pb) / (mt, mt, mt)
                    sl.append(pt)
                s.append(sl)
        # create terrain from slices
        t = Terrain.Patch(len(s[0]), slices)
        t.textureMap = Texture.Map("ch_cliff02", t.u_size, t.v_size, 256, 4, Texture.map_type['natural'])
        for i in range(0, len(s)): # len(s)
            sl = s[i]
            for j in range(0, len(sl)):
                t.points[j][i] = sl[j]
                
        # create a terrain that mirrors the final tunnel in u,v size (almost).  randomize.  loop: force v endpoints to 0, smooth, amplify.
        rt = Terrain.Patch(t.u_size-1, t.v_size)
        rt.randomize(0, 1)

        def zerocaps():
            for i in range(0, t.u_size-1): # not final endpoint (same as start)
                for j in (0, t.v_size-1): # not range - just the end points
                    rt.points[i][j] = Geom.point3(i, j, 0)
        zerocaps()        
        for x in range(0, 2):
            rt.smooth()
            zerocaps()
        rt.amplify(0, 1)
        
        # move through each cross section (constant v-value), find midpoint
        midpoints = [ ]
        for j in range(0, t.v_size):
            midpoints.append(Geom.midPoint([ t.points[i][j] for i in range(0, t.u_size-1) ]))

        # push points out, by increasing radius by amount specified at that point by mirrored terrain.
        tmult = 32
        m.terrains.append(t)
        for j in range(1, t.v_size-1):
            mp = midpoints[j]
            for i in range(0, t.u_size):
                if i == t.u_size - 1:
                    t.points[i][j] = t.points[0][j].copy()
                else:
                    pt = t.points[i][j]
                    v = pt - mp
                    v.unitize()
                    v *= (tmult, tmult, tmult)
                    rtz = rt.points[i][j].z
                    v *= (rtz, rtz, rtz)
                    t.points[i][j] = pt + v
                
        # decal textures
        # "ch_asphaltcracks01_dec"
        txt = [ "ch_cliff02_decal", "kh_mud03_decal" ]
        for k in range(0, len(txt)):
            rt.randomize(0, 0.65)
            for i in range(0, 5):
                rt.smooth()
            rt.amplify(0, 0.65)
            dt = Terrain.Patch(t.u_size, t.v_size)
            dt.textureMap = Texture.Map(txt[k], dt.u_size, dt.v_size, 256, 4, Texture.map_type['natural']) # 
            for i in range(0, t.u_size):
                for j in range(0, t.v_size):
                    pt = t.points[i][j].copy()
                    if i == t.u_size-1:
                        pt.a = rt.points[0][j].z
                    else:                    
                        pt.a = rt.points[i][j].z
                    dt.points[i][j] = pt
            m.terrains.append(dt)

    # pass on to module
    mod.write(m, None)

if __name__ == '__main__':
    main(Cod4Mapper)