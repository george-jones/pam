'''
Created on Oct 16, 2009

@author: gjones
'''

import Geom

# a natural texture map curves with the surface
# a uniform texture is the same, independent of the shape of the surface
map_type = { 'natural':0, 'uniform':1 };            

# used for brushes
class Basic():
    def __init__(self, txt, u_scale, v_scale):
        self.txt = txt;
        self.scale = Geom.point2(u_scale, v_scale)

# used for patches   
class Map():
    def __init__(self, txt, u_size, v_size, u_scale, v_scale, type):
        self.txt = txt
        self.size = Geom.point2(u_size, v_size)
        self.scale = Geom.point2(u_scale, v_scale)
        self.type = type;
    
def configToBasic(ob):
    return Basic(ob.txt, int(ob.x_scale), int(ob.y_scale))
    
def configToMap(ob, u_size, v_size, map_type):
    return Map(ob.txt, int(ob.x_scale), int(ob.y_scale), u_size, v_size, map_type)
    
caulk = Basic('caulk', 1, 1)
