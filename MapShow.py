import wx
import MapGrapher

class MapShowPanel(wx.Panel):
    def __init__(self, parent, ID):
        wx.Panel.__init__(self, parent, ID)
        self.SetBackgroundColour(wx.Color(255, 255, 255))
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        self.graph = MapGrapher.Graph(7, 0.5, 0.075, 1.35)
        self.scale = 500

    def OnPaint(self, evt):        
        nodes = self.graph.getNodes()

        pdc = wx.PaintDC(self)        
        try:
            dc = wx.GCDC(pdc)
        except:
            dc = pdc            
        for n in nodes:
            pt = n['pt']
            dc.SetPen(wx.Pen(wx.Colour(0, 0, 255, 255)))

            color = wx.Colour(0, 0,0, pt.z * 255)

            dc.SetBrush(wx.Brush(color))

            dc.DrawCircle(25 + self.scale * pt.x, 25 + self.scale * pt.y, self.scale * n['radius'])
            for c in n['conn']:
                pt2 = c['pt']
                dc.DrawLine(25 + self.scale * pt.x, 25 + self.scale * pt.y, 25 + self.scale * pt2.x, 25 + self.scale * pt2.y)                

    def OnClick(self, evt):
        #self.graph.killIntersecting()
        #self.Refresh(True)
        self.graph.jiggle(0.0025)
        self.Refresh(True)
        wx.CallLater(100, self.OnClick, None)

class MapShowFrame(wx.Frame):
    def __init__(
        self, parent, ID, title, pos=(0,0),
        size=(1024,740), style=wx.DEFAULT_FRAME_STYLE):

        wx.Frame.__init__(self, parent, ID, title, pos, size, style)
        panel = MapShowPanel(self, wx.ID_ANY)        

# main
app = wx.PySimpleApp()
frame = MapShowFrame(None, wx.ID_ANY, "MapShow")
frame.Show(True)
app.MainLoop()