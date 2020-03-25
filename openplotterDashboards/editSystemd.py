#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2020 by Sailoog <https://github.com/openplotter>
#                     e-sailing <https://github.com/e-sailing/openplotter-avnav>
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.

import wx, os, webbrowser, subprocess, sys, time
import wx.richtext as rt

from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform
from openplotterSignalkInstaller import editSettings

class ProcessSetting(wx.Dialog): 

	def __init__(self, process):
		self.conf = conf.Conf()
		self.process = process
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(os.path.abspath(__file__))
		currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-dashboards',currentLanguage)
		
		wx.Dialog.__init__(self, None, title=_('Process management for') + ' ' + process, size=(450,320))
		pnl = wx.Panel(self)
		pnl.SetBackgroundColour(wx.Colour(230,230,230,255))
		icon = wx.Icon(self.currentdir+"/data/openplotter-dashboards.png", wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)		
		
		self.lblList = [_('Enable'),_('Disable')]

		self.systemdbox = wx.RadioBox(pnl, label = 'Autostart', choices = self.lblList, majorDimension = 1, style = wx.RA_SPECIFY_ROWS)
		self.systemdbox.Bind(wx.EVT_RADIOBOX,self.onSystemdBox)

		sbox0 = wx.BoxSizer(wx.VERTICAL)
		sbox0.Add(self.systemdbox, 0, wx.ALL, 5)
		#sbox0.Add(self.skbox, 0, wx.ALL, 5)

		sbox = wx.StaticBox(pnl, -1, _('Status'))

		self.aStatusList = [_('active'),_('inactive')]
		self.aStatusbox = wx.RadioBox(pnl, label = _('ActiveState'), choices = self.aStatusList, majorDimension = 1, style = wx.RA_SPECIFY_ROWS)
		self.aStatusbox.Enable(False)

		self.bStatusList = [_('running'),_('dead')] 
		self.bStatusbox = wx.RadioBox(pnl, label = _('Substate'), choices = self.bStatusList, majorDimension = 1, style = wx.RA_SPECIFY_ROWS)
		self.bStatusbox.Enable(False)

		sbox1 = wx.StaticBoxSizer(sbox, wx.VERTICAL)
		sbox1.Add(self.aStatusbox, 0, wx.ALL, 5)
		sbox1.Add(self.bStatusbox, 0, wx.ALL, 5)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(sbox0, 1, wx.ALL, 5)
		hbox.AddStretchSpacer(1)
		hbox.Add(sbox1, 1, wx.ALL, 5)

		self.start = wx.Button(pnl, label=_('Start'))
		self.start.Bind(wx.EVT_BUTTON, self.onStart)
		self.stop = wx.Button(pnl, label=_('Stop'))
		self.stop.Bind(wx.EVT_BUTTON, self.onStop)
		self.restart = wx.Button(pnl, label=_('Restart'))
		self.restart.Bind(wx.EVT_BUTTON, self.onRestart)
		
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(hbox, 0, wx.ALL, 0)
		vbox.AddStretchSpacer(1)
		vbox.Add(self.start, 0, wx.LEFT | wx.BOTTOM, 5)
		vbox.Add(self.stop, 0, wx.ALL, 5)
		vbox.Add(self.restart, 0, wx.ALL, 5)
		pnl.SetSizer(vbox)

		self.statusUpdate()
		self.Centre() 
		self.Show(True)

	def statusUpdate(self): 
		command = 'systemctl show ' + self.process + ' --no-page'
		output = subprocess.check_output(command.split(),universal_newlines=True)
		if 'UnitFileState=enabled' in output:	self.systemdbox.SetSelection(0)
		else: 									self.systemdbox.SetSelection(1)
		if 'ActiveState=active' in output:		self.aStatusbox.SetSelection(0)
		else: 									self.aStatusbox.SetSelection(1)
		if 'SubState=running' in output:		self.bStatusbox.SetSelection(0)
		else: 									self.bStatusbox.SetSelection(1)
		
	def onSystemdBox(self,e):
		if self.lblList[0] == self.systemdbox.GetStringSelection():
			subprocess.call(['systemctl', 'enable', self.process])
		else:
			subprocess.call(['systemctl', 'stop', self.process])
			subprocess.call(['systemctl', 'disable', self.process])
								
	def onStart(self,e):
		subprocess.call(['systemctl', 'start', self.process])
		self.statusUpdate()

	def onStop(self,e):
		subprocess.call(['systemctl', 'stop', self.process])
		self.statusUpdate()

	def onRestart(self,e):
		subprocess.call(['systemctl', 'restart', self.process])
		self.statusUpdate()
		
	def ShowStatusBar(self, w_msg, colour):
		self.GetStatusBar().SetForegroundColour(colour)
		self.SetStatusText(w_msg)

	def ShowStatusBarRED(self, w_msg):
		self.ShowStatusBar(w_msg, (130,0,0))

	def ShowStatusBarGREEN(self, w_msg):
		self.ShowStatusBar(w_msg, (0,130,0))

	def ShowStatusBarBLACK(self, w_msg):
		self.ShowStatusBar(w_msg, wx.BLACK) 

	def ShowStatusBarYELLOW(self, w_msg):
		self.ShowStatusBar(w_msg,(255,140,0))
		

def main():
	app = wx.App()
	if len(sys.argv)>1:
		dlg = ProcessSetting(sys.argv[1])
		time.sleep(1)
		result = dlg.ShowModal()

if __name__ == '__main__':
	main()
