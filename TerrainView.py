import random
import math

import wx

import Terrain
import Geom

def make_terrain():
    t = Terrain.Patch(40, 40)
    t.randomize(0, 1.0)
    for i in range(0, 5):
        t.smooth()
    t.amplify(0, 1.0)
    return t
    
def make_terrain2():
    sz = 40 # 40
    s = int(random.randrange(5, 50)) # 30 is a good value
    p = 0.25 + 1.25 * random.random() # 0.65 is a good value
    pre_smooth = random.choice((True, False))
    post_smooth = random.choice((True, False))
    invert = random.choice((True, False))
    
    twx = Terrain.Patch(sz, sz)
    twx.randomize(0.0, 1.0)
    for i in range(0, s):
        twx.smooth()
    twx.amplify(-1.0, 1.0)
    twx.power(p)
    
    twy = Terrain.Patch(sz, sz)
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
    t.amplify(0, 1.0)
    t.invert()
    return (t, twx, twy)

class TerrainViewPanel(wx.Panel):
    def __init__(self, parent, ID):
        wx.Panel.__init__(self, parent, ID)
        self.SetBackgroundColour(wx.Color(255, 255, 255))
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.ta = make_terrain2()
        self.boxsize = 5 #18
       
    def OnPaint(self, evt):
        sq2 = math.sqrt(2.0)
        bs = self.boxsize
        draw_vec = False
        pdc = wx.PaintDC(self)        
        try:
            dc = wx.GCDC(pdc)
        except:
            dc = pdc
        t = self.ta[0]
        txp = self.ta[1].points
        typ = self.ta[2].points
        for u in range(t.u_size):
            for v in range(t.v_size):
                val = t.points[u][v].z
                #val = (val+1.0) / 2.0
                c = min(int(val * 256), 255)
                dx = txp[u][v].z
                dy = typ[u][v].z
                d = math.sqrt(dx*dx + dy*dy)
                red = int(c * d / sq2)
                blue = 255 - red
                color = wx.Colour(red, c, blue)
                dc.SetPen(wx.Pen(color))
                dc.SetBrush(wx.Brush(color))   
                dc.DrawRectangle(u*bs, v*bs, bs, bs)
                if draw_vec:
                    p1 = Geom.point2((u+0.5)*bs, (v+0.5)*bs)
                    dx = txp[u][v].z / 2.0
                    dy = typ[u][v].z / 2.0
                    p2 = Geom.point2(p1.x + bs * dx, p1.y + bs * dy)
                    color = wx.Colour(255, 255, 0)
                    dc.SetPen(wx.Pen(color))
                    dc.SetBrush(wx.Brush(color))
                    dc.DrawLine(p1.x, p1.y, p2.x, p2.y)
                    dc.DrawCircle(p1.x, p1.y, 2)
        

class TerrainViewFrame(wx.Frame):
    def __init__(
        self, parent, ID, title, pos=(0,0),
        size=(1024,740), style=wx.DEFAULT_FRAME_STYLE):

        wx.Frame.__init__(self, parent, ID, title, pos, size, style)
        panel = TerrainViewPanel(self, wx.ID_ANY)        
        
# main
app = wx.PySimpleApp()
frame = TerrainViewFrame(None, wx.ID_ANY, "TerrainView")
frame.Show(True)
app.MainLoop()
