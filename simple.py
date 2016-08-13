# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# A very simple wxPython example.  Just a wx.Frame, wx.Panel,
# wx.StaticText, wx.Button, and a wx.BoxSizer, but it shows the basic
# structure of any wxPython application.
#----------------------------------------------------------------------


import wx
import socket


class MyFrame(wx.Frame):
    """
    This is MyFrame.  It just shows a few controls on a wxPanel,
    and has a simple menu.
    """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title,
                          pos=(150, 150), size=(350, 250))

        # Create the menubar
        menuBar = wx.MenuBar()

        # and a menu 
        menu = wx.Menu()

        # add an item to the menu, using \tKeyName automatically
        # creates an accelerator, the third param is some help text
        # that will show up in the statusbar
        str = '退出程序'
        menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", str)

        # bind the menu event to an event handler
        self.Bind(wx.EVT_MENU, self.OnTimeToClose, id=wx.ID_EXIT)

        # and put the menu on the menubar
        menuBar.Append(menu, "&Exit")
        self.SetMenuBar(menuBar)

        self.CreateStatusBar()
        

        # Now create the Panel to put the other controls on.
        panel = wx.Panel(self)

        # and a few controls
        text = wx.StaticText(panel, -1, "请输入号码")
        text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        text.SetSize(text.GetBestSize())
        txt = wx.TextCtrl(panel, 120, size=(140,-1),pos=(150, 10),style=wx.SIGILL)
        btn = wx.Button(panel, -1, "关闭")
        funbtn = wx.Button(panel, -1, "拨号")

        # bind the button events to handlers
        self.Bind(wx.EVT_BUTTON, self.OnTimeToClose, btn)
        self.Bind(wx.EVT_BUTTON, self.OnFunButton, funbtn)

        # Use a sizer to layout the controls, stacked vertically and with
        # a 10 pixel border around each
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text, 0, wx.ALL, 10)
        sizer.Add(btn, 0, wx.ALL, 10)
        sizer.Add(funbtn, 0, wx.ALL, 10)
        panel.SetSizer(sizer)
        panel.Layout()

        # And also use a sizer to manage the size of the panel such
        # that it fills the frame
        sizer = wx.BoxSizer()
        sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        

    def OnTimeToClose(self, evt):
        """Event handler for the button click."""
        print "See ya later!"
        self.Close()

    def OnFunButton(self, evt):
        """Event handler for the button click."""
        mycall = Call_phone()
        mycall()
        print "Having fun yet?"


class Call_phone(object):
    def __init__(self):
        self.TCP_IP = '192.168.1.189'
        self.TCP_PORT = 8180
        self.BUFFER_SIZE = 1024
        self.MESSAGE = "10010"

    def __call__(self, *args, **kwargs):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.TCP_IP, self.TCP_PORT))
        s.send(self.MESSAGE)
        s.close()


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, "Simple wxPython App")
        self.SetTopWindow(frame)

        print "Print statements go to this stdout window by default."

        frame.Show(True)
        return True



def ScreenCapture( captureStartPos, captureBmapSize, debug=False ):
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
        scrDcBmap = scrDC.GetAsBitmap()     # So easy !  Copy the entire Desktop bitmap.

        if debug :
            print 'DEBUG:  scrDcBmap.GetSize() ', scrDcBmap.GetSize()

    #end if

    return scrDcBmap.GetSubBitmap( wx.RectPS( captureStartPos, captureBmapSize ) )


app = MyApp(redirect=True)
app.MainLoop()

