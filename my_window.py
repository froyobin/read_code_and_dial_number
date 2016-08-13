#!/usr/bin/python
# -*- coding: utf-8 -*-

# review.py

import wx
import socket
import re
import pytesseract
import Image
import pyscreenshot as pyscreenst
class Example(wx.Frame):

    def __init__(self, parent, title):
        super(Example, self).__init__(parent, title=title,
            size=(300, 250))
        self.sb = self.CreateStatusBar()
        self.router = 1
        self.position = []
        self.connectstatus = False
        self.InitUI()
        self.Centre()
        self.Show()

    def InitUI(self):

        self.panel = wx.Panel(self)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        fgs = wx.FlexGridSizer(3, 2, 9, 25)

        title = wx.StaticText(self.panel, label="IP 地址")
        author = wx.StaticText(self.panel, label="输入电话号码")

        self.cb = wx.CheckBox(self.panel, -1, '屏幕读入')
        self.bitnumber = wx.StaticText(self.panel, label="")

        self.tc1 = wx.TextCtrl(self.panel)
        self.tc2 = wx.TextCtrl(self.panel)
        self.tc3 = wx.StaticText(self.panel, style=wx.TE_MULTILINE)
        self.dailbtn = wx.Button(self.panel, -1, "拨号")
        self.dailbtn.Disable()
        self.Connbtn = wx.Button(self.panel, -1, "连接")
        self.Samplebtn = wx.Button(self.panel, -1, "采样图像")
        self.Samplebtn.Disable()
        fgs.AddMany([(title), (self.tc1, 1, wx.EXPAND), (author),
            (self.tc2, 1, wx.EXPAND),(self.cb), (self.bitnumber, 1, wx.EXPAND),(self.Samplebtn,wx.EXPAND),(self.Connbtn), (self.dailbtn)])

        fgs.AddGrowableRow(2, 1)
        fgs.AddGrowableCol(1, 1)

        hbox.Add(fgs, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        self.panel.SetSizer(hbox)
        self.sb.SetStatusText('等待连接')
        self.Bind(wx.EVT_BUTTON, self.ondial, self.dailbtn)
        self.Bind(wx.EVT_BUTTON, self.onConnection, self.Connbtn)
        self.Bind(wx.EVT_BUTTON, self.onSample, self.Samplebtn)

        self.Bind(wx.EVT_CHECKBOX, self.oncheckbox, self.cb)

    def onSample(self, evt):

            dia = MyDialog(self, -1, '图像位置采样')
            dia.ShowModal()
            self.position = dia.get_position()
            sourcebmp = dia.get_bmp()
            sourcebmp.SaveFile("screenshot3.png", wx.BITMAP_TYPE_PNG)
            w = self.position[1].x - self.position[0].x
            h = self.position[1].y - self.position[0].y
            # print "################"
            # print self.position[0];
            # print self.position[1];
            # print len(self.position)
            # print w
            # print h
            # print "################"
            bitmap = ScreenCapture(self.position[0], (w, h), sourcebmp)
            bitmap = self.scale_bitmap(bitmap, w*2, h*2)
            bitmap.SaveFile("screenshot2.jpg", wx.BITMAP_TYPE_JPEG)
            number = pytesseract.image_to_string(Image.open("screenshot2.jpg"))
            self.bitnumber.SetLabel(number)
            dia.Destroy()


    def oncheckbox(self, evt):
        value = self.cb.GetValue()
        if value is True:
            self.router = 2
            self.tc2.Disable()
            self.Samplebtn.Enable()

        else:
            self.router = 1
            self.tc2.Enable()
            self.Samplebtn.Disable()

    def ondial(self, evt):
        """Event handler for the button click."""
        if self.router == 1:
            number = self.tc2.GetValue()
        else:
            number = self.bitnumber.GetLabel()
            print number
        ret = number.isdigit()
        if ret is True:
            dial_ret = self.myconnect.send_message(number)
            return
        else:
            dlg = wx.MessageDialog(parent=None, message="请确认电话填写合法?", caption="警告",
                                   style=wx.OK)

            if dlg.ShowModal() == wx.ID_OK:
                return

    def onConnection(self, evt):
        """Event handler for the button click."""

        if self.connectstatus == False:
            ipaddress = self.tc1.GetValue()
            if Network.valid_ip(ipaddress) == False:
                dlg = wx.MessageDialog(parent=None, message="请确认IP地址填写合法?", caption="警告",
                                       style=wx.OK)

                if dlg.ShowModal() == wx.ID_OK:
                    return
            self.myconnect = Network(ipaddress)
            self.sb.SetStatusText("正在连接....")
            ret = self.myconnect.connect()
            if ret is None:
                dlg = wx.MessageDialog(parent=None, message="连接失败", caption="警告",
                                       style=wx.OK)
                if dlg.ShowModal() == wx.ID_OK:
                    return

            self.Connbtn.SetLabel("断开")
            self.connectstatus = True
            self.sb.SetStatusText("连接成功！")
            self.dailbtn.Enable()

        else:
            self.Connbtn.SetLabel("连接")
            self.sb.SetStatusText("等待连接！")
            self.connectstatus = False
            self.myconnect.s.close()
            self.dailbtn.Disable()

    def scale_bitmap(self, bitmap, width, height):
        image = wx.ImageFromBitmap(bitmap)
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.BitmapFromImage(image)
        return result

class MyDialog(wx.Dialog):
    def __init__(self, parent, id, title):
        s = wx.ScreenDC()
        w, h = s.Size.Get()
        wx.Dialog.__init__(self, parent, id, title, size=(w,h))
        imgobj = pyscreenst.grab()
        # myWxImage = wx.EmptyImage(imgobj.size[0], imgobj.size[0])
        # self.bmp1 = wx.Image('whole_screen.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.bmp1 = self.Get_Screen_Bmp()
        self.bitmappanel = wx.StaticBitmap(self, -1, self.bmp1, (0, 0))
        self.bitmappanel.Bind(wx.EVT_LEFT_DOWN, self.selectpos)
        self.positon = []
        self.times = 0
        self.b = None

    def get_bmp(self):
        return self.bmp1

    def selectpos(self, evt):

        if self.times > 1:
            self.Close(True)
            return
        message = ['采集顶点成功', '采集尾点成功']
        dlg = wx.MessageDialog(parent=None, message=message[self.times], caption="消息",
                            style=wx.OK)

        self.times = self.times + 1
        if dlg.ShowModal() == wx.ID_OK:
            pos = evt.GetPosition()
            self.positon.append(pos)
            return

    def get_position(self):
        return self.positon



    def Get_Screen_Bmp(self):
        s = wx.ScreenDC()
        w, h = s.Size.Get()
        b = wx.EmptyBitmap(w, h)
        m = wx.MemoryDCFromDC(s)
        m.SelectObject(b)
        m.Blit(0, 0, w, h, s, 0, 0)
        m.SelectObject(wx.NullBitmap)
        return b

class Network(object):
    def __init__(self,ipaddress):
        self.TCP_PORT = 8180
        self.TCP_IP = ipaddress
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(10)

    def connect(self):
        try:
            self.s.connect((self.TCP_IP, self.TCP_PORT))
            return "OK"
        except Exception as e:
            return None

    def send_message(self,message):
        try:
            ret = self.s.send(message+'\n')
            return ret
        except Exception as e:
            return False


    @staticmethod
    def valid_ip(ip_str):
       pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
       if re.match(pattern, ip_str):
          return True
       else:
          return False



def ScreenCapture( captureStartPos, captureBmapSize, sourcebmp, debug=False):
    """
    General Desktop screen portion capture - partial or entire Desktop.

    My particular screen hardware configuration:
        wx.Display( 0 ) refers to the primary  Desktop display monitor screen.
        wx.Display( 1 ) refers to the extended Desktop display monitor screen (above the primary screen).

    Any particular Desktop screen size is :
        screenRect = wx.Display( n ).GetGeometry()

    Different wx.Display's in a single system may have different dimensions.
    """

    # A wx.ScreenDC provides access to the entire Desktop.
    # This includes any extended Desktop monitor screens that are enabled in the OS.
    scrDC = wx.ScreenDC()         # MSW HAS BUG:  DOES NOT INCLUDE ANY EXTENDED SCREENS.
    scrDcSize = scrDC.Size
    scrDcSizeX, scrDcSizeY = scrDcSize

    # Cross-platform adaptations :
    scrDcBmap     = scrDC.GetAsBitmap()
    scrDcBmapSize = scrDcBmap.GetSize()
    if debug :
        print 'DEBUG:  Size of scrDC.GetAsBitmap() ', scrDcBmapSize

    # Check if scrDC.GetAsBitmap() method has been implemented on this platform.
    if   not scrDcBmap.IsOk() :      # Not implemented :  Get the screen bitmap the long way.

        if debug :
            print 'DEBUG:  Using memDC.Blit() since scrDC.GetAsBitmap() is nonfunctional.'

        # Create a new empty (black) destination bitmap the size of the scrDC.
        scrDcBmap = wx.EmptyBitmap( *scrDcSize )    # Overwrire the invalid original assignment.
        scrDcBmapSizeX, scrDcBmapSizeY = scrDcSize

        # Create a DC tool that is associated with scrDcBmap.
        memDC = wx.MemoryDC( scrDcBmap )

        # Copy (blit, "Block Level Transfer") a portion of the screen bitmap
        #   into the returned capture bitmap.
        # The bitmap associated with memDC (scrDcBmap) is the blit destination.

        memDC.Blit( 0, 0,                           # Copy to this start coordinate.
                    scrDcBmapSizeX, scrDcBmapSizeY, # Copy an area this size.
                    scrDC,                          # Copy from this DC's bitmap.
                    0, 0,                    )      # Copy from this start coordinate.

        memDC.SelectObject( wx.NullBitmap )     # Finish using this wx.MemoryDC.
                                                # Release scrDcBmap for other uses.
    else :

        if debug :
            print 'DEBUG:  Using scrDC.GetAsBitmap()'

        # This platform has scrDC.GetAsBitmap() implemented.

        # scrDcBmap = scrDC.GetAsBitmap()     # So easy !  Copy the entire Desktop bitmap.
        scrDcBmap = sourcebmp
        if debug :
            print 'DEBUG:  scrDcBmap.GetSize() ', scrDcBmap.GetSize()

    #end if

    return scrDcBmap.GetSubBitmap( wx.RectPS( captureStartPos, captureBmapSize ) )


if __name__ == '__main__':

    app = wx.App()
    Example(None, title='智能拨号')
    app.MainLoop()
