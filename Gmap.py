import Texture
import Shape
import Geom

class Map():
    def __init__(self):
        self.name = None
        self.terrains = [ ] # patches of ground, etc
        self.shapes = [ ] # geometric shapes, probably boxes mostly
        self.poi = [ ] # points of interest
        self.objects = [ ] # predefined objects that make the map more interesting
        self.bounds = None
        self.spawnPoints = [ ]
        self.terrainTop = 0

class Obj():
    def __init__(self):
        self.name = None
        self.pos = None # point3 - position
        self.size = None # point3 - final size
        self.scale = None # point3 - multiple of original size to reach final size        
        self.prop = { } # flexible properties

# make a skybox
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