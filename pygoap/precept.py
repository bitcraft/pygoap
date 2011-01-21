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

__version__ = ".001"

PRECEPT_ALL   = 0
PRECEPT_SIGHT = 1
PRECEPT_SOUND = 2
PRECEPT_FEEL  = 3

class Precept(object):
	__slots__ = ['time', 'thing', 'sense']

	def __init__(self, time, sense, thing):
		self.sense = sense
		self.thing = thing
		self.time = time
