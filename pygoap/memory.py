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

__version__ = ".003"

DEBUG = False

class Memory(object):
    """
    Memory objects are "value-added" precepts.

    This to add here could be a timestamp, previous action, location, mood, etc.
    """

    def __init__(self):
        pass


# many we could use a database or something that tracks memory for all agents,
# rather than each doing its own memory

class MemoryManagerBase(object):
    def __init__(self, blackboard):
        self.blackboard = blackboard

    def update(self, time_passed):
        """
        This is supposed to remove old memories, sort them, whathaveyou.
        """
        pass 

    def make_memory(self, precept):
        # memory objects go here 
        return precept

    def add_memory(self, precept):
        raise NotImplementedError

    def search(self, sense):
        raise NotImplementedError

class MemoryManager(MemoryManagerBase):
    def __init__(self, blackboard):
        super(MemoryManager, self).__init__(blackboard)
        self.data = []

    def add_memory(self, precept):
        # saving time precepts would be a waste of memory
        if hasattr(precept, "time"):
            return
        self.data.append(self.make_memory(precept))

    def search(self, sense=None):
        # return a copy, not the list
        if sense == None:
            return list(self.data[:])

        return [p for p in self.data if hasattr(p, sense)]

class SharedMemoryManager(MemoryManagerBase):
    pass
    
