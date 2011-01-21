# -*- coding: utf-8 -*-

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

__version__ = ".002"

from astar import Astar

class MotorManager(object):
	"""
	This is responsible for moving the agent around in the environment.

	not implemented
	"""
	def __init__(self, blackboard):
		self.blackboard = blackboard

	def update(self):
		try:
			self.blackboard.read("goto")
		except KeyError:
			pass

	def pathfind(self, location):
		pf = Astar(start, location, self.environment.get_surrounding)
		path = pf.findpath()
		if path:
			print "ok"
		else:
			print "fail"

	def move(self, location):
		raise NotImplementedError

class XYMotorManager(MotorManager):
	"""
	Has built in hueristics optimized for a 2d environment
	"""
	def pathfind(self, location):
		pass
