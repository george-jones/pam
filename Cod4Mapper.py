from __future__ import division
import copy
import math

import Texture
import Shape
import Gmap
import Geom

# create map for Cod4
def write(m, cfg):
    mapFile = open("C:\\Program Files\\Activision\\Call of Duty 4 - Modern Warfare\\map_source\\" + m.name + ".map", "w")
    mapHeader(mapFile, False)
    for t in m.terrains:
        terrainWrite(mapFile, t)
    for s in m.shapes:
        shapeWrite(mapFile, s)
    mapFile.write("}\n")
    for o in m.objects:
        objectWrite(mapFile, o)    
    for o in getCod4Objects(m):
        objectWrite(mapFile, o)
    mapFile.close()
    
def getCod4Objects(m):
    ret = [ ]
    
    # need global intermission entity
    o = Gmap.Obj()
    o.pos = Geom.point3(m.bounds[0].x + 30, m.bounds[0].y + 30, m.bounds[1].z - 50)    
    o.prop['classname'] = 'mp_global_intermission'
    o.prop['angles'] = Geom.point3(0, 8, 45)
    ret.append(o)
        
    midpt = Geom.midPoint(m.bounds)
    midpt.z -= 50
    
    # throw a car in at the bottom of the map because that seems to fix the rainbow colored players problem
    o = Gmap.Obj()
    o.pos = Geom.point3(midpt.x, midpt.y, m.bounds[0].z + 20)    
    o.prop['classname'] = 'misc_prefab'
    o.prop['model'] = 'prefabs/mp_destructibles/vehicle_80s_sedan1_red_destructible.map'
    ret.append(o)        
    
    # find leftmost, rightmost, and most central spawn points.  These will have special uses in sabotage.
    leftSpawn = None
    rightSpawn = None
    midSpawn = None
    midDist = 0
    dist = 0
    for sp in m.spawnPoints:
        if leftSpawn is None or sp.x < leftSpawn.x:
            leftSpawn = sp
        if rightSpawn is None or sp.x > rightSpawn.x:
            rightSpawn = sp
        dist = midpt.dist(sp)
        if midSpawn is None or dist < minDist:
            minDist = dist
            midSpawn = sp
    
    # handle spawn points
    for sp in m.spawnPoints:
        o = Gmap.Obj()

        o.pos = sp + (0, 0, 10) # bump up a bit so player isn't stuck in the ground        
        o.prop['classname'] = 'mp_dm_spawn'
        ret.append(o)
        
        o = Gmap.Obj()
        o.pos = sp + (0, 0, 10)
        o.prop['classname'] = 'mp_tdm_spawn'
        ret.append(o)        
        
        o = Gmap.Obj()
        o.pos = sp + (0, 0, 10)
        o2 = None
        if sp is leftSpawn:
            o.prop['classname'] = 'misc_prefab'
            o.prop['model'] = 'prefabs/mp/sab_bomb_allies.map'
        elif sp is rightSpawn:
            o.prop['classname'] = 'misc_prefab'
            o.prop['model'] = 'prefabs/mp/sab_bomb_axis.map'
        elif sp is midSpawn:
            o.prop['classname'] = 'misc_prefab'
            o.prop['model'] = 'prefabs/mp/sab_bomb.map'        
        else:
            if sp.x <= midpt.x:
                o.prop['classname'] = 'mp_sab_spawn_allies_start'
                o2 = Gmap.Obj()
                o2.pos = o.pos
                o2.prop['classname'] = 'mp_sab_spawn_allies'
            else:
                o.prop['classname'] = 'mp_sab_spawn_axis_start'
                o2 = Gmap.Obj()
                o2.pos = o.pos
                o2.prop['classname'] = 'mp_sab_spawn_axis'
        ret.append(o)
        if o2 is not None:
            ret.append(o2)

        o = Gmap.Obj()
        o.pos = sp + (0, 0, 10)
        if sp.x <= midpt.x:
            o.prop['classname'] = 'mp_tdm_spawn_allies_start'
        else:
            o.prop['classname'] = 'mp_tdm_spawn_axis_start'
        ret.append(o)
        
    # minimap corner points (for airstrike height)        
    o = Gmap.Obj()
    o.pos = m.bounds[0].copy()    
    o.pos.z = m.terrainTop
    o.prop['classname'] = 'script_origin'
    o.prop['targetname'] = 'minimap_corner'
    ret.append(o)

    o = copy.deepcopy(o)
    o.pos = m.bounds[1].copy()
    o.pos.z = m.terrainTop
    ret.append(o)
        
    #
    # helicopter nodes
    #
    hh = m.bounds[1].z - 50
    
    # heli_start (3 corners)
    for i in range(0, 3):
        o = Gmap.Obj()
        if i == 0:
            o.pos = m.bounds[0].copy()
            o.pos.x += 50
            o.pos.y += 50
        elif i == 1:
            o.pos = m.bounds[0].copy()
            o.pos.x = m.bounds[1].x - 50
            o.pos.y += 50
        else:
            o.pos = Geom.point3(midpt.x, m.bounds[1].y - 50, hh)
            
        o.pos.z = hh
        o.prop['classname'] = 'script_origin'
        o.prop['targetname'] = 'heli_start'
        o.prop['target'] = "heli_enter_%d_1" % (i)
        ret.append(o)
                
        o = copy.deepcopy(o)
        o.pos = Geom.midPoint([o.pos, midpt])
        o.pos.z = hh
        o.prop['classname'] = 'script_origin'
        o.prop['targetname'] = "heli_enter_%d_1" % (i)
        o.prop['target'] = "heli_enter_%d_2" % (i)
        ret.append(o)

        o = copy.deepcopy(o)
        o.pos = Geom.midPoint([o.pos, midpt])
        o.pos.z = hh
        o.prop['classname'] = 'script_origin'
        o.prop['targetname'] = "heli_enter_%d_2" % (i)
        o.prop['target'] = "helimiddle"
        ret.append(o)
        
    # heli_leave
    o = Gmap.Obj()
    o.pos = m.bounds[0].copy()
    o.pos.x += 50
    o.pos.y += 50
    o.pos.z = hh - 30
    o.prop['classname'] = 'script_origin'
    o.prop['targetname'] = 'heli_leave'
    ret.append(o)
        
    o = copy.deepcopy(o)
    o.pos.x = m.bounds[1].x - 50
    ret.append(o)
    
    o = copy.deepcopy(o)
    o.pos.y = m.bounds[1].y - 50
    ret.append(o)

    o = copy.deepcopy(o)
    o.pos.x = m.bounds[0].x + 50
    ret.append(o)
    
    # middle and dest    
    o = Gmap.Obj()
    o.pos = midpt.copy()
    o.pos.z = hh - 60
    o.prop['classname'] = 'script_origin'
    o.prop['targetname'] = 'helimiddle'
    ret.append(o)    
    
    o = copy.deepcopy(o)
    o.pos.z += 30
    o.prop['classname'] = 'script_origin'
    o.prop['targetname'] = 'heli_dest'
    o.prop['target'] = 'helimiddle'
    ret.append(o)
            
    # loop
    loopSteps = 13
    loops = 7
    steps = loops * loopSteps
    mp2 = Geom.point2(midpt.x, midpt.y)
    hmp = Geom.point3(midpt.x, midpt.y, hh)
    rad = 0.6 * max(mp2.dist((leftSpawn.x, leftSpawn.y)), mp2.dist((rightSpawn.x, rightSpawn.y)))
    da = 2 * math.pi / loopSteps
    ang = 0
    r = rad
    z = hh
    dz = -30 / loopSteps
    dr = -1 * r / (2 * steps)
    for i in range(0, steps):
        pt = hmp + (r * math.cos(ang), r * math.sin(ang), 0)
        pt.z = z
        o = Gmap.Obj()
        o.pos = pt
        o.prop['classname'] = 'script_origin'
        if i == 0:
            o.prop['targetname'] = 'heli_loop_start'
            o.prop['target'] = 'heli_loop0'
            o.pos.z += 30
            ret.append(o)
            o = copy.deepcopy(o)
            o.pos.z -= 30                    
        o.prop['targetname'] = 'heli_loop%d' % (i)
        o.prop['target'] = 'heli_loop%d' % ((i+1) % steps)
        ret.append(o)
        ang += da
        z += dz
        r += dr
        
    # crash
    steps = 10
    o = Gmap.Obj()
    o.pos = midpt.copy()
    o.pos.z = hh
    o.prop['classname'] = 'script_origin'
    o.prop['targetname'] = 'heli_crash_start'
    o.prop['target'] = 'heli_crash0'
    ret.append(o)
    
    drop = 300
    o = Gmap.Obj()
    o.prop['classname'] = 'script_origin'
    o.pos = midpt.copy()
    o.pos.x += rad
    dx = (m.bounds[1].x - (midpt.x + rad)) / steps
    zc = (steps * steps) / (hh - drop - m.bounds[0].z)
    for i in range(0, steps):
        o = copy.deepcopy(o)
        o.prop['targetname'] = 'heli_crash%d' % (i)
        if i == steps-1:
            del o.prop['target']
        else:
            o.prop['target'] = 'heli_crash%d' % (i+1)
        o.pos.x += dx
        o.pos.z = (hh - drop) - i*i / zc
        ret.append(o)
    
    return ret

def mapHeader(mapFile, do_sun):
    str = 'iwmap 4\n' + \
        '// entity 0\n' + \
        '{\n' + \
        '"_color" "0.95 0.95 1.000000"\n' + \
        '"diffusefraction" ".55"\n' + \
        '"northyaw" "90"\n' + \
        '"classname" "worldspawn"\n'
    
    if do_sun:
        str += '"sundirection" "-35 195 0"\n' + \
            '"suncolor" "0.99 0.98 0.86"\n' + \
            '"sunlight" "1.5"\n' + \
            '"ambient" ".05"\n' + \
            '"sundiffusecolor" "0.94 0.94 1.000000"\n'
    else:
        str += '"sunIsPrimaryLight" "0"\n' + \
            '"ambient" ".40"\n' # .05 too dark, .55 too light
    
    mapFile.write(str)
    
def point3_write(file, p):
    file.write(" ( %.2f %.2f %.2f )" % (p.x, p.y, p.z))
    
def plane_write(file, plane, txt):    
    point3_write(file, plane.p0)
    point3_write(file, plane.p1)
    point3_write(file, plane.p2)   
    file.write(" %s %d %d 0 0 0 0 lightmap_gray 16384 16384 0 0 0 0\n" % (txt.txt, txt.scale.x, txt.scale.y))

def hexahedron_write(file, hh):
    pts = hh.points

    file.write('{\n')
    
    # top
    p = Shape.Plane(pts[7], pts[4], pts[5])
    plane_write(file, p, hh.faceTextures['top'] or hh.texture)
    
    # right
    p = Shape.Plane(pts[3], pts[7], pts[6])
    plane_write(file, p, hh.faceTextures['right'] or hh.texture)
    
    # back
    p = Shape.Plane(pts[6], pts[5], pts[1])
    plane_write(file, p, hh.faceTextures['back'] or hh.texture)
    
    # left
    p = Shape.Plane(pts[5], pts[4], pts[0])
    plane_write(file, p, hh.faceTextures['left'] or hh.texture)
    
    # front
    p = Shape.Plane(pts[4], pts[7], pts[3])
    plane_write(file, p, hh.faceTextures['front'] or hh.texture)

    # bottom
    p = Shape.Plane(pts[0], pts[3], pts[2])
    plane_write(file, p, hh.faceTextures['bottom'] or hh.texture)
            
    file.write('}\n')

def shapeWrite(mapFile, s):
    if isinstance(s, Shape.Hexahedron):
        hexahedron_write(mapFile, s)
    
def terrainWrite(mapFile, tp):
    m = 16
    tm = tp.textureMap;
    
    if tp.u_size > m or tp.v_size > m: # because large patches don't compile well and tend to crash Radiant
        tpa = tp.split(m, m)
        for t in tpa:
            t.textureMap = tm
            terrainWrite(mapFile, t)
        return
        
    def texture_values(p, u, v, p_first):
        ret = { 'u':0, 'v':0, 'd1':0, 'd2':0 }
        if tm.type == Texture.map_type['uniform']:
            ret['u'] = p.x / tm.scale.x
            ret['v'] = p.y / tm.scale.y
            ret['d1'] = ret['u'] / 64
            ret['d2'] = ret['v'] / 64
        elif tm.type == Texture.map_type['natural']:        
            ret['u'] = tm.scale.x * tm.size.x * (u / (len(tp.points)-1))
            dist = p_first.dist(p)
            ret['v'] = dist * tm.scale.y
            ret['d1'] = ret['u'] / 64
            ret['d2'] = ret['v'] / 64
        return ret
    
    def output_point(p, u, v, p_first):
        z = p.z
        o = texture_values(p, u, v, p_first)
        mapFile.write("      v %.2f %.2f %.2f " % (p.x, p.y, p.z))
        if hasattr(p, 'a'):
            a = p.a
            if a < 1.0:
                mapFile.write(" c 255 255 255 %d" % int(255 * a))
        mapFile.write('t %.2f %.2f %.2f %.2f\n' % (o['u'], o['v'], o['d1'], o['d2']))
        
    mapFile.write(' {\n')
    mapFile.write('  mesh\n')
    mapFile.write('  {\n')
    mapFile.write('   ' + tm.txt + '\n')
    mapFile.write('   lightmap_gray\n')
    
    # I have no clue what the 16 and 8 are.
    mapFile.write('   %d %d 16 8\n' % (tp.u_size, tp.v_size))
    for u in range(0, tp.u_size):
        p_first = tp.points[u][0]
        mapFile.write('   (\n')
        rng = None
        if tp.invertNormals == True:
            rng = range(int(tp.v_size-1), -1, -1)
        else:
            rng = range(0, int(tp.v_size))
        for v in rng:
            output_point(tp.points[u][v], u, v, p_first)
        mapFile.write('   )\n')
    mapFile.write('  }\n')
    mapFile.write(' }\n')

def objectWrite(file, o):
    entStr = '{\n' + \
      '"origin" "%.2f %.2f %.2f"\n' % (o.pos.x, o.pos.y, o.pos.z)
    handled = [ ]
    
    if 'model' in o.prop:
        entStr += '"model" "' + o.prop['model'] + '"\n'
        handled.append('model')
    
    if 'classname' in o.prop:
        entStr += '"classname" "' + o.prop['classname'] + '"\n'    
        handled.append('classname')
    
    if 'angles' in o.prop:
        entStr += '"angles" "' + str(o.prop['angles'].y) + ' ' + str(o.prop['angles'].z) + ' ' + str(o.prop['angles'].x) + '"\n'
        handled.append('angles')
    
    if 'modelscale' in o.prop:
        entStr += '"modelscale" "%.2f"\n' % (o.prop['modelscale'])
        handled.append('modelscale')
        
    if 'targetname' in o.prop:
        entStr += '"targetname" "' + o.prop['targetname'] + '"\n'
        handled.append('targetname')
        
    if 'target' in o.prop:
        entStr += '"target" "' + o.prop['target'] + '"\n' 
        handled.append('target')
    
    for a in o.prop.items():
        if a[0] not in handled:
            entStr += '"' + a[0] + '" "' + str(a[1]) + '"\n'
        
    entStr += '}\n'
    file.write(entStr)