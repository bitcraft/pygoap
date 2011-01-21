# some Tk stuff, not implemented

"""
Copyright 2010, Leif Theden

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
"""

from Tkinter import *

class Token(object):
	"""
	base of something drawable on a Tk canvas
	"""
	pass

class EnvironmentDisplay(Canvas):
	"""
	displays a 2d environment
	"""
	def __init__(self, master, *arg, **kwarg):
		Canvas.__init__(self, master, *arg, **kwarg)
		self.agents = {}
		self.environment = None

	def add_agent(self, agent):
		ctags = ('agent')
		x, y = agent.location
		self.create_rectangle(x*20,y*20,x+20,y+20, tags=ctags)

	def set_environment(self, env):
		self.environment = env
		self.update_map()

	def update_agents(self):
		pass
		
	def create_map(self):
		for thing in self.environment.things:
			self.add_agent(thing)

	def update_map(self):
		self.create_map()

class EnvrionmentFrame(Frame):
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.pack()
		self.create_widgets()
		
	def create_widgets(self):
		c = EnvironmentDisplay(self, width=200, height=200)
		c.pack({'side': 'top'})
		self.environment_display = c

		qb = Button(self)
		qb['text'] = "Quit"
		qb['command'] = self.quit
		qb.pack({'side':'bottom'})
		self.quit_button = qb
		
		ub = Button(self)
		ub['text'] = "Update"
		ub['command'] = self.environment_display.update_map
		ub.pack({'side':'bottom'})
		self.update_button = ub
