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

from precept import PRECEPT_ALL

__version__ = ".001"

DEBUG = False

class Memory(object):
	def __init__(self):
		pass

# many we could use a database or something that tracks memory for all agents,
# rather than each doing its own memory

# dict...maybe hold timestamps...then will rack lastseen, etc

class MemoryManagerBase(object):
	def __init__(self, blackboard):
		self.blackboard = blackboard

	def add_memory(self, precept):
		raise NotImplementedError

	def search(self, sense):
		raise NotImplementedError

class MemoryManager(MemoryManagerBase):
	def __init__(self, blackboard):
		super(MemoryManager, self).__init__(blackboard)
		self.data = []

	def add_memory(self, precept):
		self.data.append(precept)

	def search(self, sense):
		# return a copy, not the list
		if sense == PRECEPT_ALL:
			return list(self.data[:])

		return [p for p in self.data if p.sense == sense]

class SharedMemoryManager(MemoryManagerBase):
	pass
	
