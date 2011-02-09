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

"""
NOTE: how do we create a "class" of objects?  ie: there may be many
    bottles of rum, but how do we make distinctions between them?
    (do we?)  should we ru-use the python syntax?  (probably)

    the ThingMeta allows for objects that do not need to model physics.
    with them, they are special classes that satisfy some condition only
    by themselves.  ie, that are unique because that it what they are...
    as opposed to what they do.  (i realize that you could say that there
    really are no things that are intrinsically unique, but that everything
    has meaning because of what it does, but by using this idea, it makes
    object creation much easier (you dont have to model them all).
"""

class ThingMeta(cls, bases, dict):
    """
    Solution to "many bottles of rum problem"
    """
    pass


class Thing(object):
    """
    This is something that the environment can tell agents about.
    What does it look like?
    How big is it?
    How much does it weigh?



    """
    pass

class Liquid(object):
    """
    Class for liquid/liquid like objects
    
    Measured in ml
    """
    def __init__(self, amount):
        # really, if this changes, we should make different
        # liquid objects that represent that amount lost
        # CONSERVATION OF MATTER
        self.amount = amount

class Rum(Liquid):
    pass 

class Container(thing):
    """
    A Container is an object that is meant to hold other things
    """

    def __init__(self):
        # measumement in ml
        self.capacity = 100

        # measurement in cm
        self.mouth_size = 2

        # what is inside?
        self.contains = None

    def pour(self, where):
        pass

    def add(self, other):
        pass


class Bottle(Container):
    """
    A bottle is a container with a mouth.
    Fluids and things must be able to fit into the mouth.
    """

    def __init__(self):
        super(Bottle, self)__init__(self):
        # measureed in cm
        self.mouth_size = 2

    def add(self, other):
        # get total volume of the other object
        # if total volume is less that my capacity
        # get shortest dimension of the other object
        # if sortest dimension is smaller than mouth_size
        super(Bottle, self).add(other)
