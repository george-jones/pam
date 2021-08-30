from __future__ import division

import datetime
import math
import random

import Terrain
import MapGrapher
import Cod4Mapper
import datetime
import Gmap
import Geom
import Texture
import Shape

def windyPatch(tx, ty):
    p = Terrain.Patch(tx.u_size, tx.v_size)    
    for u in range(tx.u_size):
        for v in range(tx.v_size):
            windx = tx.points[u][v].z
            windy = ty.points[u][v].z
            w = math.sqrt(math.pow(windx, 2.0) + math.pow(windy, 2.0))
            p.setPoint(u, v, Geom.point3(tx.points[u][v].x, tx.points[u][v].y, w))            
    p.amplify(0, 1.0)
    return p

def overlayPatches(t, w, mult):
    rng = t.getRange()
    rngdiff = rng[1] - rng[0]
    tlo = Terrain.Patch(t.u_size, t.v_size)
    thi = Terrain.Patch(t.u_size, t.v_size)
    alo = None
    ahi = None
    plo = None
    phi = None
    for u in range(t.u_size):
        for v in range(t.v_size):
            p = t.points[u][v]
            a = 1.0 - w.points[u][v].z
            ahi = (p.z - rng[0]) / rngdiff
            alo = 1.0 - ahi
            ahi *= mult
            alo *= mult
            if ahi > 1.0:
                ahi = 1.0
            if alo > 1.0:
                alo = 1.0
            plo = Terrain.alphaPoint3(p.x, p.y, p.z, alo * a)
            phi = Terrain.alphaPoint3(p.x, p.y, p.z, ahi * a)
            tlo.points[u][v] = plo
            thi.points[u][v] = phi
    return (tlo, thi)

def skyBox(map, skysize, offset, skytxtName):  
    top = skysize.z + offset.z
    bot = -1*skysize.z + offset.z
    left = 0 + offset.x
    right = skysize.x + offset.x
    front = 0 + offset.y
    back = skysize.y + offset.y
    ww = 1

    skytxt = Texture.Basic(skytxtName, 1, 1)

    # left
    b = Shape.box(Geom.point3(left-ww/2,front,bot), Geom.point3(left-ww/2,back,bot), ww, top-bot)
    b.texture = skytxt
    map.shapes.append(b)

    # right
    b = Shape.box(Geom.point3(right+ww/2,front,bot), Geom.point3(right+ww/2,back,bot), ww, top-bot)
    b.texture = skytxt
    map.shapes.append(b)

    # front
    b = Shape.box(Geom.point3(left-ww,front-ww/2,bot), Geom.point3(right+ww,front-ww/2,bot), ww, top-bot)
    b.texture = skytxt
    map.shapes.append(b)

    # back
    b = Shape.box(Geom.point3(left-ww,back+ww/2,bot), Geom.point3(right+ww,back+ww/2,bot), ww, top-bot)    
    b.texture = skytxt
    map.shapes.append(b)

    # bottom
    b = Shape.box(Geom.point3(left-ww,(front+back)/2,bot-ww/2), Geom.point3(right+ww,(front+back)/2,bot-ww/2), (back-front), ww)
    b.texture = skytxt
    map.shapes.append(b)

    # top
    b = Shape.box(Geom.point3(left-ww,(front+back)/2,top-ww), Geom.point3(right+ww,(front+back)/2,top-ww), (back-front), ww)
    b.texture = skytxt
    map.shapes.append(b)

def waterAndFloor(map, skysize, offset, waterTxtName, floorTxtName, waterHeight):  
    ww = 1
    top = offset.z
    bot = -1*skysize.z + offset.z + ww
    left = 0 + offset.x
    right = skysize.x + offset.x
    front = 0 + offset.y
    back = skysize.y + offset.y

    waterCliptxt = Texture.Basic('clip_water', 1, 1)
    watertxt = Texture.Basic(waterTxtName, 1, 1)
    floortxt = Texture.Basic(floorTxtName, 1, 1)

    # clip_water
    # night_water_mud
    # water
    #b = Shape.box(Geom.point3(left-ww,(front+back)/2,top+waterHeight), Geom.point3(right+ww,(front+back)/2,top+waterHeight), (back-front), ww)
    #b.texture = waterCliptxt
    #map.shapes.append(b)

    #b = Shape.box(Geom.point3(left-ww,(front+back)/2,top+waterHeight), Geom.point3(right+ww,(front+back)/2,top+waterHeight), (back-front), ww)
    #b.texture = watertxt
    #map.shapes.append(b)

    b = Shape.box(Geom.point3(left-ww,(front+back)/2,top), Geom.point3(right+ww,(front+back)/2,top), (back-front), ww)
    b.texture = watertxt
    map.shapes.append(b)

    # floor
    b = Shape.box(Geom.point3(20+left-ww,(front+back)/2,bot+10), Geom.point3(-20+right+ww,(front+back)/2,bot+10), (-40+back-front), ww)
    b.texture = floortxt
    map.shapes.append(b)    

def getSpawnPoints(map, t, n, ctr, r, minDist):    
    while len(map.spawnPoints) < n:
        skip = False
        pt2 = Geom.point2(random.randrange(ctr.x - r, ctr.x + r), random.randrange(ctr.x - r, ctr.x + r))
        if pt2.dist(ctr) <= r:
            pt3 = Geom.point3(pt2.x, pt2.y, t.heightAt(pt2))
            # make sure it isn't too close to an existing spawn point
            for esp in map.spawnPoints:
                if esp.dist(pt3) < minDist:
                    skip = True
                    break
            if skip == False:
                map.spawnPoints.append(pt3)

bigstuff = [
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_dead_pine_lg.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_dead_pine_med.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_dead_pine_sm.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_dead_pine_xl.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_red_pine_lg.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_red_pine_log_lg.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_red_pine_log_med.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_red_pine_med.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_red_pine_sm.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_red_pine_stump_lg.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_red_pine_stump_lg_nomantle.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_red_pine_stump_sm.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_red_pine_stump_xl.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_red_pine_xl.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_red_pine_xxl.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_tree_grey_oak_lg_a.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_tree_grey_oak_med_a.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_tree_grey_oak_sm_a.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_tree_grey_oak_sm_ts.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_tree_grey_oak_xl_a.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_tree_pine_lg.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_tree_pine_sm.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_tree_pine_xl.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_tree_river_birch_lg_a.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/foliage_tree_river_birch_lg_b.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/ch_crate24x24.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/ch_crate24x36.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/ch_crate32x48.map" },    
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/ch_crate48x64.map" },
    { 'classname': 'misc_prefab', 'model': "prefabs/misc_models/ch_crate64x64.map" }
]

smallstuff = [
    { 'classname': 'misc_model', 'model': 'foliage_litegrass_squareclump' },
    { 'classname': 'misc_model', 'model': 'foliage_grass_short_squareclumpshort' },
    { 'classname': 'misc_model', 'model': 'foliage_grass_flowerplants_squareclump' },
    { 'classname': 'misc_model', 'model': 'foliage_grass_triangularclump' },
    { 'classname': 'misc_model', 'model': 'foliage_grass_triangularclumpshort' },
    { 'classname': 'misc_model', 'model': 'foliage_grass_tuft_shortwide' },
    { 'classname': 'misc_model', 'model': 'foliage_drygrass_triangularclump' },
    { 'classname': 'misc_model', 'model': 'foliage_shrub_group01' },
    { 'classname': 'misc_model', 'model': 'foliage_shrub_brownmid' },
    { 'classname': 'misc_model', 'model': 'foliage_shrub_browntall' },
    { 'classname': 'misc_model', 'model': 'foliage_bush_big' },
    { 'classname': 'misc_model', 'model': 'wetwork_fallen_oakbranch_02' },
    { 'classname': 'misc_model', 'model': 'wetwork_creekrock_01' },
    { 'classname': 'misc_model', 'model': 'wetwork_creekrock_02' }
]

def randomObjects(m, t, tp, psize, tsize, waterHeight):
    stuffList = [
        { 'list': smallstuff, 'num': 400, 'minScale': 0.75, 'maxScale': 2.5, 'power': 2, 'spawnOn': True },
        { 'list': bigstuff, 'num': 150, 'minScale': 0.5, 'maxScale': 1.3, 'power': 3, 'spawnOn': False }
    ]
    spawnTol = 50

    for stuff in stuffList:
        numObj = stuff['num']
        npl = 10000 # possible locations
        d = 2 * numObj / npl
        pwr = stuff['power'] # sharpness of division between unlikely and likely to place locations
        pl = [ ]

        mapCenter = Geom.point2(tsize / 2, tsize / 2)    

        while len(pl) < npl:
            x = random.random() * tsize
            y = random.random() * tsize
            r = mapCenter.dist((x, y))
            if r < psize / 2:                
                pt = Geom.point3(x, y, 0)
                pt2 = Geom.point2(x, y)
                pt.z = tp.heightAt(pt) # probability terrain's height
                if stuff['spawnOn'] == True:
                    pl.append(pt)
                else:
                    collide = False
                    for sp in m.spawnPoints:
                        # 2D distance check
                        if pt2.dist(sp) <= spawnTol:
                            collide = True
                            break
                    if collide == False:
                        pl.append(pt)

        for i in range(0, len(pl)):
            pt = pl[i]
            p = 0
            if pt.z <= 0.5:
                p = d * math.pow(pt.z * 2, pwr) / 2
            else:
                p = d * (1.0 - math.pow((1.0 - pt.z)*2, pwr)/2)
            if random.random() <= p:        
                s = random.choice(stuff['list'])
                obj = Gmap.Obj()
                for k in s.keys():
                    obj.prop[k] = s[k]
                obj.pos = Geom.point3(pt.x, pt.y, 0)
                obj.pos.z = t.heightAt(obj.pos) # true terrain's height
                if obj.pos.z >= waterHeight:
                    obj.prop['angles'] = Geom.point3(0, 0, random.randrange(0, 360))
                    obj.prop['modelscale'] = random.random() * (stuff['maxScale'] - stuff['minScale']) + stuff['minScale']
                    m.objects.append(obj)

def radialFence(m, terrain, tsize, r, fenceTxtName, caulkTxtName, numSegs, fenceHeight):
    c = Geom.point3(tsize/2, tsize/2, 0)    
    a = math.pi * 2 / numSegs
    pts = [ c + (r * math.cos(i * a), r * math.sin(i * a), 0) for i in range(0, numSegs) ]

    ftxt = Texture.Basic(fenceTxtName, 256, 256)
    ctxt = Texture.Basic(caulkTxtName, 256, 256)

    for pt in pts:
        pt.z = terrain.heightAt(pt) - fenceHeight

    for i in range(0, len(pts)):
        i2 = (i + 1) % len(pts)
        pt = pts[i]
        pt2 = pts[i2]
        b = Shape.box(pt, pt2, 8, fenceHeight * 2)        
        # fence textured faces
        b.faceTextures['top'] = ftxt
        b.faceTextures['left'] = ftxt
        b.faceTextures['right'] = ftxt
        # caulk textured faces
        b.faceTextures['bottom'] = ctxt
        b.faceTextures['back'] = ctxt
        b.faceTextures['front'] = ctxt
        m.shapes.append(b)

def main(mod):    
    m = Gmap.Map()
    today = datetime.date.today()    
    theday = today + datetime.timedelta(days=2)
    m.name = theday.strftime("mp_%Y%m%d")

    # playable size
    psize = 3500    

    # terrain size (x and y)
    tsize = 3800

    # terrain height
    tmin = 0
    tmax = 600    
    m.terrainTop = tmax

    # water level
    waterHeight = 75

    # sky
    skysize = Geom.point3(tsize+1500, tsize+1500, tmax+650)
    skyoffset = Geom.point3(-750, -750, 0)    
    skyBox(m, skysize, skyoffset, 'sky_sp_airplane')

    m.bounds = (Geom.point3(skyoffset.x, skyoffset.y, -1 * skysize.z + skyoffset.z),
                Geom.point3(skyoffset.x + skysize.x, skyoffset.y + skysize.y, skyoffset.z + skysize.z))

    waterAndFloor(m, skysize, skyoffset, 'ac_treesheet_dist', 'ch_grass_01', waterHeight)

    # make a terrain
    sz = 40
    s = int(random.randrange(5, 50)) # 30 is a good value
    p = 0.25 + 1.25 * random.random() # 0.65 is a good value    

    print "s: %d, p: %f\n" % (s, p)

    pre_smooth = True
    post_smooth = True

    twx = Terrain.Patch(sz, sz)
    twx.setRectangularXY(0, 0, tsize-1, tsize-1)
    twx.randomize(0.0, 1.0)
    for i in range(0, s):
        twx.smooth()
    twx.amplify(-1.0, 1.0)
    twx.power(p)

    twy = Terrain.Patch(sz, sz)
    twy.setRectangularXY(0, 0, tsize-1, tsize-1)
    twy.randomize(0.0, 1.0)
    for i in range(0, s):
        twy.smooth()
    twy.amplify(-1.0, 1.0)
    twy.power(p)

    t = Terrain.Patch(sz, sz)
    t.randomize(0, 1.0)
    if pre_smooth:
        t.smooth()
    t.smoothWindy(twx, twy)
    if post_smooth:
        t.smooth()
    t.amplify(tmin, tmax)
    t.setRectangularXY(0, 0, tsize-1, tsize-1)

    # turn into a circular island
    t.circularTaper(100, psize/2, tsize/2)
    t.radiusSmooth(40, psize/4, (psize + tsize)/4, Geom.point2(tsize/2, tsize/2))

    # set terrain texture  ch_grass_01
    t.textureMap = Texture.Map("ch_grass_01", 6000, 6000, 1, 1, Texture.map_type['uniform'])

    # create a patch that represents the overall "windiness" at each point
    wp = windyPatch(twx, twy)
    wp.setRectangularXY(0, 0, tsize-1, tsize-1)

    # sky_mp_citystreets
    # sky_pripyat
    # sky_sp_airplane
    # create overlay patches  "ch_ground_dirt3_footprint"
    overlays = overlayPatches(t, wp, 1.25)
    overlays[0].textureMap = Texture.Map("kh_mud03_decal", 5400, 5400, 1, 1, Texture.map_type['uniform'])
    overlays[1].textureMap = Texture.Map("ch_cliff02_decal", 5000, 5000, 1, 1, Texture.map_type['uniform'])

    getSpawnPoints(m, t, 30, Geom.point2(tsize / 2, tsize / 2), (psize / 2) * 0.9, 200)

    randomObjects(m, t, wp, psize, tsize, waterHeight)

    radialFence(m, t, tsize, psize * 0.48, 'ch_concretewall08', 'caulk', 32, 128)

    # make a graph
    #g = MapGrapher.Graph(8, 0.5, 0.075, 1.35)    

    m.terrains.append(t)
    for op in overlays:
        m.terrains.append(op)

    # pass on to module
    mod.write(m, None)

if __name__ == '__main__':
    main(Cod4Mapper)