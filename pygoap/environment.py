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

"""
modified from AIMA-python, Peter Norvig
"""

__version__ = ".009"

import random
from collections import deque
from agent import Agent
from action import ACTIONSTATE_FINISHED
from precept import Precept


def distance((ax, ay), (bx, by)):
    "The distance between two (x, y) points."
    return math.hypot((ax - bx), (ay - by))

def distance2((ax, ay), (bx, by)):
    "The square of the distance between two (x, y) points."
    return (ax - bx)**2 + (ay - by)**2

def clip(vector, lowest, highest):
    """Return vector, except if any element is less than the corresponding
    value of lowest or more than the corresponding value of highest, clip to
    those values.
    >>> clip((-1, 10), (0, 0), (9, 9))
    (0, 9)
    """
    return type(vector)(map(min, map(max, vector, lowest), highest))

class Environment(object):
    """Abstract class representing an Environment.  'Real' Environment classes
    inherit from this.
    The environment keeps a list of .objects and .agents (which is a subset
    of .objects). Each agent has a .performance slot, initialized to 0.
    """

    def __init__(self, things=[], agents=[], time=0):
        self.time   = time
        self.things = things
        self.agents = agents

        # TODO, if agents are passed, we need to init them, possibly
        # by sending the relivant precepts, (time, location, etc)

        self.action_que = []

    def default_location(self, object):
        """
        Default location to place a new object with unspecified location.
        """
        raise NotImplementedError

    def run(self, steps=1000):
        """
        Run the Environment for given number of time steps.
        """
        [ self.update(1) for step in xrange(steps) ]

    def add_thing(self, thing, location=None):
        """
        Add an object to the environment, setting its location. Also keep
        track of objects that are agents.  Shouldn't need to override this.
        """
        thing.location = location or self.default_location(thing)
        self.things.append(thing)

        # add the agent
        if isinstance(thing, Agent):
                thing.performance = 0
                thing.environment = self
                self.agents.append(thing)

    def update(self, time_passed):
        """
        * Update our time
        * Update actions that may be running
        * Update all of our agents
        * Add actions to the que
        """

        # update time
        self.time += time_passed

        # this is a band-aid until there is a fixed way to
        # manage actions returned from agents
        self.action_que = [ a for a in self.action_que if a != None ]

        print self.action_que

        # update all the actions that may be running
        precepts = [ a.update(time_passed) for a in self.action_que ]
        precepts = [ p for p in precepts if p != None ]

        # remove actions that are completed
        self.action_que = [ a for a in self.action_que \
            if a.state != ACTIONSTATE_FINISHED ]

        # send precepts of each action to the agents
        for p in precepts:
            actions = [ a.program(p) for a in self.agents ]
            self.action_que.extend([ a for a in actions if a != None ])
        
        # let all the agents know that time has passed
        t = Precept(sense="time", time=self.time) 
        self.action_que.extend([ a.program(t) for a in self.agents ])

class Pathfinding2D(object):
    def get_surrounding(self, location):
        """
        Return all locations around this one.
        """

        x, y = location
        return ((x-1, y-1), (x-1, y), (x-1, y+1), (x, y-1), (x, y+1),
                (x+1, y-1), (x+1, y), (x+1, y+1))
                
    def calc_h(self, location1, location2):
        return distance(location1, location2)

class XYEnvironment(Environment, Pathfinding2D):
    """
    This class is for environments on a 2D plane, with locations
    labelled by (x, y) points, either discrete or continuous.  Agents
    perceive objects within a radius.  Each agent in the environment
    has a .location slot which should be a location such as (0, 1),
    and a .holding slot, which should be a list of objects that are
    held
    """

    def __init__(self, width=10, height=10):
        super(XYEnvironment, self).__init__()
        self.width = width
        self.height = height

    def look(self, caller, direction=None, distance=None):
        """
        Simulate vision.

        In normal circumstances, all kinds of things would happen here,
        like ray traces.  For now, assume all objects can see every
        other object
        """
        a = [ caller.program(
            Precept(sense="sight", thing=t, location=t.location)) 
            for t in self.things ] 

        print "Look", a

        self.action_que.extend(a)

    def objects_at(self, location):
        """
        Return all objects exactly at a given location.
        """
        return [ obj for obj in self.things if obj.location == location ]

    def objects_near(self, location, radius):
        """
        Return all objects within radius of location.
        """
        radius2 = radius * radius
        return [ obj for obj in self.things  
                if distance2(location, obj.location) <= radius2 ]

    def default_location(self, thing):
        return (random.randint(0, self.width), random.randint(0, self.height))

