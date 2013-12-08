'''
Written by Jesse Merritt
February 20, 2012

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

Generates G-Code to re-surface a CNC table or mill pockets.  

The GUI requires WX.

The program depends on the following modules:
wx:  	Manages the GUI
------------------------------------------------------------------------------------------------------

'''

import wx
import sys
import os
import time
import tempfile

#Dimensions
x = 0	# Location of X Axis
y = 0	# Location of Y Axis
z = 0	# Location of Z Axis

units = 'Imperial'
unitsList = 'Imperial', 'Metric'
directionList = ['Auto', 'X', 'Y']

header = ';\tGenerated by pyPocketer, a simple pocketing program written in python\n;\tWritten by Jesse Merritt\n;\thttps://github.com/jes1510/pyPocketer\n;\n'	  
tempf = tempfile.NamedTemporaryFile(delete=False)	
  
class MainWindow(wx.Frame):
	
	def __init__(self, parent, title="pyPocketer") :	
		global preferredDirection
		global directionList
		self.parent = parent	   
		mainFrame = wx.Frame.__init__(self,self.parent, title=title, size=(800,400))		 

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
		self.sizer11 = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer12 = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer13 = wx.BoxSizer(wx.HORIZONTAL)
		self.rootSizer = wx.BoxSizer(wx.VERTICAL)						
		self.statusBar = self.CreateStatusBar()							  # statusbar in the bottom of the window								  

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
		menuBar.Append(filemenu,"&File")					# Adding the "filemenu" to the MenuBar	   
		menuBar.Append(helpmenu, "Help")
		self.SetMenuBar(menuBar)							# Adding the MenuBar to the Frame content.		

			
		#	Labels and important stuff for the GUI
		self.unitsLabel = wx.StaticText(mainPanel, 1, "Units:")
		self.unitsBox = wx.ComboBox(mainPanel, -1, choices=unitsList)

		self.xLabel = wx.StaticText(mainPanel, 1, "X Dimension:")
		self.xBox = wx.TextCtrl(self)

		self.yLabel = wx.StaticText(mainPanel, 1, "Y Dimension:")
		self.yBox = wx.TextCtrl(self) 
		
		self.xOffsetLabel = wx.StaticText(mainPanel, 1, "X Offset:")
		self.xOffsetBox = wx.TextCtrl(self) 
		
		self.yOffsetLabel = wx.StaticText(mainPanel, 1, "Y Offset:")
		self.yOffsetBox = wx.TextCtrl(self) 

		self.diameterLabel = wx.StaticText(mainPanel, 1, "Tool Diameter")
		self.diameterBox = wx.TextCtrl(self)		

		self.overlapLabel = wx.StaticText(mainPanel, 1, "Overlap %")
		self.overlapBox = wx.TextCtrl(self)

		self.liftLabel = wx.StaticText(mainPanel, 1, "Z Liftoff Height:")
		self.liftBox = wx.TextCtrl(self)

		self.finalDepthLabel = wx.StaticText(mainPanel, 1, "Final Depth:")
		self.finalDepthBox = wx.TextCtrl(self)

		self.stepDepthLabel = wx.StaticText(mainPanel, 1, "Max Step Depth:")
		self.stepDepthBox = wx.TextCtrl(self)

		self.speedLabel = wx.StaticText(mainPanel, 1, "Feed Rate:")
		self.speedBox = wx.TextCtrl(self)

		self.directionLabel = wx.StaticText(mainPanel, 1, "Preferred Direction:")
		self.directionBox = wx.ComboBox(mainPanel, -1, choices=directionList)

		self.ofLabel = wx.StaticText(mainPanel, 1, "Output filename:")
		self.ofBox = wx.TextCtrl(self)	
		
		self.objectLabel = wx.StaticText(mainPanel, 1, "Object Label:")
		self.objectBox = wx.TextCtrl(self)	

		self.usetoolOffsetBox = wx.CheckBox(mainPanel, 1, 'Use Tool Offset')
		self.enablePocketing = wx.CheckBox(mainPanel, 1, 'Enable Pocketing')
		self.drillCorners = wx.CheckBox(mainPanel, 1, 'Drill Corners')
		self.includeM2 = wx.CheckBox(mainPanel, 1, "Include M2")

		self.writeFileButton = wx.Button(mainPanel, -1, 'Write to file')
		self.copyClipboardButton = wx.Button(mainPanel, -1, 'Copy to Clipboard')

		#  Sizers.  Everything is on rootSizer; these are grouped in pairs for clarity	   
		self.sizer1.Add(self.unitsLabel, 1, wx.EXPAND)
		self.sizer1.Add(self.unitsBox, 1, wx.EXPAND)

		self.sizer2.Add(self.xLabel, 1, wx.EXPAND)
		self.sizer2.Add(self.xBox, 1, wx.EXPAND)  

		self.sizer2.Add(self.yLabel, 1, wx.EXPAND)
		self.sizer2.Add(self.yBox, 1, wx.EXPAND)
		
		self.sizer3.Add(self.xOffsetLabel, 1, wx.EXPAND)
		self.sizer3.Add(self.xOffsetBox, 1, wx.EXPAND)
		self.sizer3.Add(self.yOffsetLabel, 1, wx.EXPAND)
		self.sizer3.Add(self.yOffsetBox, 1, wx.EXPAND)

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

		self.sizer9.Add(self.speedLabel, 1, wx.EXPAND)
		self.sizer9.Add(self.speedBox, 1, wx.EXPAND)		

		self.sizer10.Add(self.directionLabel, 1, wx.EXPAND)
		self.sizer10.Add(self.directionBox, 1, wx.EXPAND) 

		self.sizer11.Add(self.usetoolOffsetBox, 1, wx.EXPAND)
		self.sizer11.Add(self.enablePocketing, 1, wx.EXPAND)
		self.sizer11.Add(self.drillCorners, 1, wx.EXPAND)
		self.sizer11.Add(self.includeM2, 1, wx.EXPAND)
		

		self.sizer12.Add(self.ofLabel, 1, wx.EXPAND)
		self.sizer12.Add(self.ofBox, 1, wx.EXPAND) 
		
		self.sizer12.Add(self.objectLabel, 1, wx.EXPAND)
		self.sizer12.Add(self.objectBox, 1, wx.EXPAND) 
		
		
		self.sizer13.Add(self.writeFileButton, 1, wx.EXPAND)  
		self.sizer13.Add(self.copyClipboardButton, 1, wx.EXPAND)

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
		self.rootSizer.Add(self.sizer11, 1, wx.EXPAND)
		self.rootSizer.Add(self.sizer12, 1, wx.EXPAND) 
		self.rootSizer.Add(self.sizer13, 1, wx.EXPAND) 

		#	Bind events to buttons
		self.Bind(wx.EVT_CLOSE, self.OnExit)
		self.Bind(wx.EVT_MENU, self.onAbout, menuAbout)
		self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
		#	   self.Bind(wx.EVT_MENU, self.OnSave, menuSave)
		self.Bind(wx.EVT_BUTTON, self.writeFile, self.writeFileButton)
		self.Bind(wx.EVT_COMBOBOX, self.selectUnits, self.unitsBox)
		self.Bind(wx.EVT_COMBOBOX, self.selectDirection, self.directionBox)
		self.Bind(wx.EVT_BUTTON, self.onClipboard, self.copyClipboardButton)

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
		self.finalDepthBox.SetValue('-0.125')
		self.stepDepthBox.SetValue('0.125')
		self.ofBox.SetValue('pocket.ngc')	
		self.unitsBox.SetValue('Imperial')
		self.directionBox.SetValue('Auto')
		self.speedBox.SetValue('12')	
		self.xOffsetBox.SetValue('0')
		self.yOffsetBox.SetValue('0')
		self.objectBox.SetValue('Object 1')
		self.includeM2.SetValue(True)

		self.Layout()
		self.Show(True)		
	
	def selectUnits(self, e):
		global unitsList	
		global units		
		units = unitsList[e.GetSelection()]

		
	def selectDirection(self, e) :
		global directionList
		global preferredDirection
		preferredDirection = directionList[e.GetSelection()]	 

	def onAbout(self, e) :	 #	File written 
		dlg = wx.MessageDialog(self, "A Simple G-Code generator for milling pockets.\nhttps://github.com/jes1510/pyPocketer\nSee the README for help", 'About:' , wx.OK | wx.ICON_EXCLAMATION)  
		dlg.ShowModal()   
   
	def showClipboardWritten(self) :
		dlg = wx.MessageDialog(self, "The G-Code has been generated and copied to the clipboard", 'Success!' , wx.OK | wx.ICON_EXCLAMATION)  
		dlg.ShowModal()		
		
	def showFileWritten(self) :	 #	File written 
		dlg = wx.MessageDialog(self, "The G-Code has been generated and written to file", 'Success!' , wx.OK | wx.ICON_EXCLAMATION)  
		dlg.ShowModal()		 
		
	def showValueError(self) :	#	Value Error.  Called if a string is in a box that should be a number
		dlg = wx.MessageDialog(self, "There is a value wrong!", 'Error!', wx.OK | wx.ICON_ERROR)  
		dlg.ShowModal()
 
	def OnExit(self,e):		 # stuff to do when the program is ending	
		tempf.close()
		self.Destroy()			  # wipe out window and dump to the OS
		
	def onClipboard(self, e) :
		# based on code from http://python.dzone.com/articles/wxpython-how-use-clipboard
		tempf.seek(0)	
		self.buildGCode() 
		tempf.seek(0)			
		self.dataObj = wx.TextDataObject()
		data = ''.join(tempf.readlines())		
		self.dataObj.SetText(data)			
		if wx.TheClipboard.Open():
			wx.TheClipboard.SetData(self.dataObj)
			wx.TheClipboard.Close()
			self.showClipboardWritten()
		else:
			wx.MessageBox("Unable to open the clipboard", "Error")		
		
		
	def writeFile(self, e) :
		tempf.seek(0)	
		self.buildGCode() 
		tempf.seek(0)	
		filename = self.ofBox.GetValue()
		of = open(filename, 'a')
	
		for i in tempf.readlines() :
			of.write(i)			
		
		of.write('\n\n\n')
		of.close()
		self.showFileWritten()	 
			
	def buildGCode(self) :
		global header   
		global x
		global y
		global z	

		try :
			
			feedRate = str(float(self.speedBox.GetValue()))
			diameter = float(self.diameterBox.GetValue())
			xMax = float(self.xBox.GetValue())
			yMax = float(self.yBox.GetValue())
			toolDiameter = float(self.diameterBox.GetValue())
			zMax = float(self.liftBox.GetValue())
			maxDepth = float(self.finalDepthBox.GetValue())
			stepValue = float(self.stepDepthBox.GetValue())	
			overlap = float(self.overlapBox.GetValue())/100		
			xOffset = float(self.xOffsetBox.GetValue())
			yOffset = float(self.yOffsetBox.GetValue())
			jogFeedRate = feedRate
			
			
			preferredDirection = directionList[max(self.directionBox.GetSelection(), 0)]
			
		
					
		except :
			self.showValueError()
	
		if self.usetoolOffsetBox.GetValue() :
			toolOffset = .5 * toolDiameter
		else :
			toolOffset = 0

		pocketing =  self.enablePocketing.GetValue()
		if preferredDirection == 'Auto' :
			if xMax > yMax :
				preferredDirection = 'X'
	
			else :
				preferredDirection = 'Y'  

		tempf.write(header)			
		tempf.write(';	Units: ' + units + '\n')
		tempf.write(';	Tool Diameter: ' + str(toolDiameter) + '\n')
		tempf.write(';	Feedrate: ' + str(feedRate) + '\n')
		tempf.write(';	Overlap %: ' + str(overlap * 100) + '\n')
		tempf.write(';	X = ' + str(xMax) + '\n')
		tempf.write(';	Y = ' + str(yMax) + '\n')
		tempf.write(';	Depth Step: ' + str(stepValue) + '\n')
		tempf.write(';	Milling Depth: ' + str(maxDepth) + '\n')
		tempf.write(';	Preferred Direction = ' + preferredDirection + '\n')
		if toolOffset :
			tempf.write(';	Tool toolOffset WAS calculated\n')
		else :
			tempf.write(';	Tool toolOffset was NOT calculated\n')
			tempf.write(';\n')	  
			
		
		tempf.write(';\t' + self.objectBox.GetValue() + '\n')
		tempf.write(';---------------------------------------\n;\n')

		if units == 'Imperial' :
			tempf.write('G20\n')
		else :
			f.write('G21\n')	  
	  
		tempf.write('f' + feedRate + '\n')	  
		tempf.write('G0 f'+ str(jogFeedRate) + '  z' + str(zMax) + '\n') 

		z = 0 - stepValue

		if overlap == 0 :
			overlap = 1		   
	  
		while z > (maxDepth - stepValue)  : 	
			if preferredDirection == 'Y' :	
				#if toolOffset :
				tempf.write('G0 f'+ str(jogFeedRate) + '  y' + str((toolOffset*2) + yOffset) + ' x' + str((toolOffset*2) + xOffset) + '\n') # toolOffset for tool
				tempf.write('G1 f'+ str(feedRate) + ' ' + '+ str(feedRate) + ' 'z' + str(z) + '\n')

				# Start a profile operation first
				tempf.write('G1 f'+ str(feedRate) + ' ' + 'y' + str((yMax - toolOffset) + yOffset) + '\n') 
				tempf.write('G1 f'+ str(feedRate) + ' ' + 'x' + str((xMax - toolOffset) + xOffset) + '\n')
				tempf.write('G1 f'+ str(feedRate) + ' ' + 'y' + str(toolOffset + yOffset) + '\n') 
				tempf.write('G1 f'+ str(feedRate) + ' ' + 'x' + str(toolOffset + xOffset) + '\n')

				if pocketing:		
					xSteps = self.drange(float(diameter) * overlap,xMax, float(diameter) * overlap) 
					idx = 0
					for i in range(0,len(xSteps)):	
						
						tempf.write('G1 f'+ str(feedRate) + ' ' + 'y' + str((yMax - toolOffset) + yOffset) + '\n') 

						try :
							tempf.write('G1 f'+ str(feedRate) + ' ' + 'x' + str((xSteps[idx]) + xOffset) + '\n')
							tempf.write('G1 f'+ str(feedRate) + ' ' + 'y' + str(toolOffset + yOffset) + '\n')	
							idx = idx + 1
							tempf.write('G1 f'+ str(feedRate) + ' ' + 'x' + str(x(Steps[idx]) + xOffset) + '\n' )
					  
		
						except :		
							tempf.write('G1 f'+ str(feedRate) + ' ' + 'x' + str((xMax - toolOffset) + xOffset) + '\n')
							tempf.write('G1 f'+ str(feedRate) + ' ' + 'y' + str(toolOffset + yOffset) + '\n')
							break 
						idx = idx + 1
	   
  
			if preferredDirection == 'X' : 
				#if toolOffset :
				tempf.write('G1 f'+ str(feedRate) + ' ' + 'x' + str(toolOffset + xOffset) + ' y' + str(toolOffset + yOffset) + '\n')
					
				tempf.write('G1 f'+ str(feedRate) + ' ' + 'z' + str(z) + '\n')
				tempf.write('G1 f'+ str(feedRate) + ' ' + 'x' + str((xMax - toolOffset) + xOffset) + '\n') 
				tempf.write('G1 f'+ str(feedRate) + ' ' + 'y' + str((yMax - toolOffset) + yOffset) + '\n')
				tempf.write('G1 f'+ str(feedRate) + ' ' + 'x' + str(toolOffset + xOffset) + '\n') 
				tempf.write('G1 f'+ str(feedRate) + ' ' + 'y' + str(toolOffset + yOffset) + '\n')
				
				
				if pocketing :	  
					ySteps = self.drange(float(diameter) * overlap,yMax, float(diameter) * overlap) 
					idx = 0
					for i in range(0,len(ySteps)):	
						
						tempf.write('G1 f'+ str(feedRate) + ' ' + 'x' + str((xMax - toolOffset) + xOffset) + '\n') 

						try :
							tempf.write('G1 f'+ str(feedRate) + ' ' + 'y' + str(ySteps[idx] + yOffset) + '\n')
							tempf.write('G1 f'+ str(feedRate) + ' ' + 'x' + str(toolOffset + xOffset) + '\n')	
							idx = idx + 1
							tempf.write('G1 f'+ str(feedRate) + ' ' + 'y' + str(ySteps[idx] + yOffset) + '\n' )

						except :		
							tempf.write('G1 f'+ str(feedRate) + ' ' + 'y' + str(yMax + yOffset) + '\n')
							tempf.write('G1 f'+ str(feedRate) + ' ' + 'x' + str(toolOffset + xOffset) + '\n')
							break
						
						idx += 1
		  
			z -= abs(stepValue)	# Decrement the Z axis and do it all again if needed
	
		if self.drillCorners.GetValue() :
			tempf.write(';\tStart of corner drills\n')			
			tempf.write('G81 x' + str(xOffset) + ' y' + str(yOffset) + ' R' + str(zMax) + ' Z'+ str(maxDepth) +'\n') 
			tempf.write('G81 x' + str(xOffset) + ' y' + str(yMax + yOffset) + ' R' + str(zMax) + ' Z'+ str(maxDepth) +'\n')
			tempf.write('G81 x' + str(xMax + xOffset) + ' y' + str(yMax + yOffset) + ' R' + str(zMax) + ' Z'+ str(maxDepth) +'\n')
			tempf.write('G81 x' + str(xMax + xOffset) + ' y' + str(yOffset) + ' R' + str(zMax) + ' Z'+ str(maxDepth) +'\n')	


	  
		tempf.write('G0 f'+ str(jogFeedRate) + '  z' + str(zMax) + '\n')
		tempf.write('G0 f'+ str(jogFeedRate) + '  x0 y0\n')
		
		if self.includeM2.GetValue() == True :
			tempf.write('M02\n')
			tempf.write(';	End of code\n')	
		
		else :
			tempf.write(';	End of Section\n')
			tempf.write(';---------------------------------------\n;\n')
			 
  
	  
	def drange (self, start, stop, step) :	# range() doesn't work with floats so we do this instead
		r = start
		l = []
		while r < stop :
			l.append(r)
			r += step
		return l   

	

app = wx.App(False)		 
frame = MainWindow(None)	

app.MainLoop()
