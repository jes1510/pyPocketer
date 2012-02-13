'''
Written by Jesse Merritt
February 12, 2012

   This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Generates G-Code to re-surface a CNC table,  

The GUI requires WX.

The program depends on the following modules:
wx:  	Manages the GUI
wx.lib.newevent:  Event manager

Change Log:
------------------------------------------------------------------------------------------------------


'''
import serial 
import wx
import sys
import os
import time

version = "0.1"

#Dimensions
x = 0	# Location of X Axis
y = 0	# Location of Y Axis
z = 0	# Location of Z Axis

units = 'Imperial'
unitsList = 'Imperial', 'Metric'
  
class MainWindow(wx.Frame):
    def __init__(self, parent, title="pyPocketer") :    
        self.parent = parent       
        mainFrame = wx.Frame.__init__(self,self.parent, title=title, size=(800,600))         
        
        mainPanel = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)
        
        #   Build sizers and statusbar
        self.sizer1 = wx.BoxSizer(wx.HORIZONTAL) 
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL) 
        self.sizer3 = wx.BoxSizer(wx.HORIZONTAL) 
        self.sizer4 = wx.BoxSizer(wx.HORIZONTAL) 
        self.sizer5 = wx.BoxSizer(wx.HORIZONTAL) 
        self.sizer6 = wx.BoxSizer(wx.HORIZONTAL) 
        self.sizer7 = wx.BoxSizer(wx.HORIZONTAL)   
        self.sizer8 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer9 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer10 = wx.BoxSizer(wx.HORIZONTAL)
        self.rootSizer = wx.BoxSizer(wx.VERTICAL)                        
        self.statusBar = self.CreateStatusBar()                              # statusbar in the bottom of the window                                  

        # Setting up the menus
        filemenu= wx.Menu()
        setupmenu = wx.Menu()
        helpmenu = wx.Menu()       

        menuSave = filemenu.Append(wx.ID_SAVE, "Save", "Save the current data")     
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")     
        menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About"," Information about this program")  

        # Menubar
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File")                    # Adding the "filemenu" to the MenuBar       
        menuBar.Append(helpmenu, "Help")
        self.SetMenuBar(menuBar)                            # Adding the MenuBar to the Frame content.        
        
        #	Input boxes for distance and speed\        
  

					
        self.unitsLabel = wx.StaticText(mainPanel, 1, "Units:")
        self.unitsBox = wx.ComboBox(mainPanel, -1, choices=unitsList)
        
        self.xLabel = wx.StaticText(mainPanel, 1, "X Dimension:")
        self.xBox = wx.TextCtrl(self)
        
        self.yLabel = wx.StaticText(mainPanel, 1, "Y Dimension:")
        self.yBox = wx.TextCtrl(self)   
        
        
        self.diameterLabel = wx.StaticText(mainPanel, 1, "Tool Diameter")
        self.diameterBox = wx.TextCtrl(self) 
        
        self.overlapLabel = wx.StaticText(mainPanel, 1, "Percent Overlap")
        self.overlapBox = wx.TextCtrl(self)
        
        self.liftLabel = wx.StaticText(mainPanel, 1, "Z Liftoff Height:")
        self.liftBox = wx.TextCtrl(self)
        
        self.finalDepthLabel = wx.StaticText(mainPanel, 1, "Final Depth:")
        self.finalDepthBox = wx.TextCtrl(self)
        
        self.stepDepthLabel = wx.StaticText(mainPanel, 1, "Step Depth:")
        self.stepDepthBox = wx.TextCtrl(self)
        
        self.ofLabel = wx.StaticText(mainPanel, 1, "Output filename:")
        self.ofBox = wx.TextCtrl(self)    
      
        self.writeFileButton = wx.Button(mainPanel, -1, 'Write to file')
        
        #  Sizers.  Everything is on rootSizer         
        self.sizer1.Add(self.unitsLabel, 1, wx.EXPAND)
        self.sizer1.Add(self.unitsBox, 1, wx.EXPAND)
        
        self.sizer2.Add(self.xLabel, 1, wx.EXPAND)
        self.sizer2.Add(self.xBox, 1, wx.EXPAND)  
        
        self.sizer3.Add(self.yLabel, 1, wx.EXPAND)
        self.sizer3.Add(self.yBox, 1, wx.EXPAND)
        
        self.sizer4.Add(self.diameterLabel, 1, wx.EXPAND)
        self.sizer4.Add(self.diameterBox, 1, wx.EXPAND) 
        
        self.sizer5.Add(self.overlapLabel, 1, wx.EXPAND)
        self.sizer5.Add(self.overlapBox, 1, wx.EXPAND)
        
        self.sizer6.Add(self.liftLabel, 1, wx.EXPAND)
        self.sizer6.Add(self.liftBox, 1, wx.EXPAND)
        
        self.sizer7.Add(self.finalDepthLabel, 1, wx.EXPAND)
        self.sizer7.Add(self.finalDepthBox, 1, wx.EXPAND)
        
        self.sizer8.Add(self.stepDepthLabel, 1, wx.EXPAND)
        self.sizer8.Add(self.stepDepthBox, 1, wx.EXPAND)                 
        self.sizer9.Add(self.ofLabel, 1, wx.EXPAND)
        self.sizer9.Add(self.ofBox, 1, wx.EXPAND)  
        self.sizer10.Add(self.writeFileButton, 1, wx.EXPAND)  
        
        self.rootSizer.Add(self.sizer1, 1, wx.EXPAND)
        self.rootSizer.Add(self.sizer2, 1, wx.EXPAND)
        self.rootSizer.Add(self.sizer3, 1, wx.EXPAND)
        self.rootSizer.Add(self.sizer4, 1, wx.EXPAND)
        self.rootSizer.Add(self.sizer5, 1, wx.EXPAND)
        self.rootSizer.Add(self.sizer6, 1, wx.EXPAND)
        self.rootSizer.Add(self.sizer7, 1, wx.EXPAND)
        self.rootSizer.Add(self.sizer8, 1, wx.EXPAND)
        self.rootSizer.Add(self.sizer9, 1, wx.EXPAND)
        self.rootSizer.Add(self.sizer10, 1, wx.EXPAND)
        

	#	Bind events to buttons
        self.Bind(wx.EVT_CLOSE, self.OnExit)
#       self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
#       self.Bind(wx.EVT_MENU, self.setupPort, menuPorts)
#       self.Bind(wx.EVT_MENU, self.OnSave, menuSave)
        self.Bind(wx.EVT_BUTTON, self.writeFile, self.writeFileButton)
        self.Bind(wx.EVT_COMBOBOX, self.selectUnits)


        # set the sizers
        self.SetSizer(self.rootSizer)
        self.SetAutoLayout(1)
        self.rootSizer.Fit(self)     
        
        #	Set preset values
	self.xBox.SetValue('14.0')
	self.yBox.SetValue('11.5')	
	self.diameterBox.SetValue('.75')
	self.overlapBox.SetValue('50')	
	self.liftBox.SetValue('1.0')
	self.finalDepthBox.SetValue('.125')
	self.stepDepthBox.SetValue('.125')
	self.ofBox.SetValue('table.ngc')	
        self.unitsBox.SetValue('Imperial')
        
        self.Layout()
	self.Show(True)		
	
    def selectUnits(self, e):
	global unitsList	
	global units	
	
        units = unitsList[e.GetSelection()]
        print units
        
        
	
    def showComError(self) :     #	Can't open COM port
        dlg = wx.MessageDialog(self, "Could not open COM port!", 'Error!', wx.OK | wx.ICON_ERROR)  
        dlg.ShowModal()
        self.OnExit(self)	#	Dump out
        
    def showComWriteError(self) :     #	Can't open COM port
        dlg = wx.MessageDialog(self, "Error writing to Com port!", 'Error!', wx.OK | wx.ICON_ERROR)  
        dlg.ShowModal()
        
    def showComTimeoutError(self) :     #	Can't open COM port
        dlg = wx.MessageDialog(self, "Controller did not respond!", 'Error!', wx.OK | wx.ICON_ERROR)  
        dlg.ShowModal() 
        
    def showValueError(self) :	#	General error.  Not really implemented
        dlg = wx.MessageDialog(self, "I need a number!", 'Error!', wx.OK | wx.ICON_ERROR)  
        dlg.ShowModal()
 
    def OnExit(self,e):         # stuff to do when the program is ending     
        global ser
        try :
	  self.ser.close()  	# Needs to be in a try in case it wasn't opened
	except :
	  pass
	
        self.Destroy()              # wipe out window and dump to the OS
        
    def readDistance(self) :
      try :
	d = abs(round(float(self.distanceBox.GetValue()), 6))
      	return d
      	
      except :	
	self.showValueError()      


    def writeFile(self, e) :
      print "Button!"
   
    

    

app = wx.App(False)         # wx instance
frame = MainWindow(None)    # main window frame

app.MainLoop()