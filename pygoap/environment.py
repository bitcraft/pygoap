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

__version__ = ".003"

from collections import deque

from precept import *
from agent import Agent

from action import \
	ACTIONSTATE_NOT_STARTED, \
	ACTIONSTATE_FINISHED, \
	ACTIONSTATE_RUNNING, \
	ACTIONSTATE_PAUSED

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
	inherit from this. Your Environment will typically need to implement:
		percept:           Define the percept that an agent sees.
		execute_action:    Define the effects of executing an action.
						Also update the agent.performance slot.
	The environment keeps a list of .objects and .agents (which is a subset
	of .objects). Each agent has a .performance slot, initialized to 0.
	"""
	
	object_classes = [] ## List of classes that can go into environment

	def __init__(self,):
		self.time = 0
		self.things = []
		self.agents = []

	"""Return the percept that the agent sees at this point. Override this."""
	def percept(self, agent):
		raise NotImplementedError

	"""Change the world to reflect this action. Override this."""
	def execute_action(self, agent, action):
		raise NotImplementedError

	"""Default location to place a new object with unspecified location."""
	def default_location(self, object):
		raise NotImplementedError

	"""If there is spontaneous change in the world, override this."""
	"""This is not worded correctly, exogenous == "outside the model."""
	def exogenous_change(self):
		pass

	"""By default, we're done when we can't find a live agent."""
	def is_done(self):
		for agent in self.agents:
			if agent.is_alive(): return False
		return True

	def step(self):
		"""Run the environment for one time step. If the
		actions and exogenous changes are independent, this method will
		do.  If there are interactions between them, you'll need to
		override this method."""
		self.time = self.time + 1

		if not self.is_done():
			actions = [agent.program(self.percept(agent))
				for agent in self.agents]

			for (agent, action) in zip(self.agents, actions):
				if isinstance(action, list):
					for a in action:
						if a != None:
							self.execute_action(agent, a)
				else:
					if action != None:
						self.execute_action(agent, action)
						self.exogenous_change()

	def run(self, steps=1000):
		"""Run the Environment for given number of time steps."""
		for step in range(steps):
				if self.is_done(): return
				self.step()

	def add_thing(self, thing, location=None):
		"""Add an object to the environment, setting its location. Also keep
		track of objects that are agents.  Shouldn't need to override this."""
		thing.location = location or self.default_location(thing)
		self.things.append(thing)
		if isinstance(thing, Agent):
				thing.performance = 0
				self.agents.append(thing)
		return self


class MappedEnvironment(Environment):
	"""
	Provides an envrionment that agents can move around in.  =)
	Pathfinding is built in (Astar).
	
	environments like this should keep a list of objects that exist
	in them, and be able to "fake" locations without an object (for
	memory considerations):: this is self.things
	
	"""
	
	def __init__(self):
		super(MappedEnvironment, self).__init__()
		self.pathfinder = None

	def get_surrounding(self, location):
		# return a list of locations around this one.
		# please override
		pass
		
	def calc_h(self, location1, location2):
		# a hint to the pathfinder
		pass

class XYEnvironment(MappedEnvironment):
	"""This class is for environments on a 2D plane, with locations
	labelled by (x, y) points, either discrete or continuous.  Agents
	perceive objects within a radius.  Each agent in the environment
	has a .location slot which should be a location such as (0, 1),
	and a .holding slot, which should be a list of objects that are
	held
	
	Provides a pathfinding interface.  =)
		- Shared amongst agents to reduce memory (LPA sometime?)
	"""

	def __init__(self, width=10, height=10):
		super(XYEnvironment, self).__init__()
		self.width = width
		self.height = height
		
		self.action_que = deque()

	def get_surrounding(self, location):
		"""Return all locations around this one."""
		x, y = location
		return ((x-1, y-1), (x-1, y), (x-1, y+1), (x, y-1), (x, y+1),
				(x+1, y-1), (x+1, y), (x+1, y+1))
				
	def calc_h(self, location1, location2):
		return distance(location1, location2)

	def objects_at(self, location):
		"""Return all objects exactly at a given location."""

		return [obj for obj in self.things if obj.location == location]

	def objects_near(self, location, radius):
		"""Return all objects within radius of location."""

		radius2 = radius * radius
		return [obj for obj in self.things
				if distance2(location, obj.location) <= radius2]

	def percept(self, agent):
		"""By default, agent perceives objects within radius r."""

		return [self.object_percept(obj, agent)
				for obj in self.objects_near(agent.location, 5)]

	def execute_action(self, action):
		action.start()
		self.action_que.appendleft(action)
		#print "execute", action

	def object_percept(self, obj, agent): #??? Should go to thing?
		"""Return the percept for this thing."""

		return Precept(self.time, PRECEPT_SIGHT, obj)

	def default_location(self, thing):
		return (random.choice(self.width), random.choice(self.height))

	def move_to(thing, destination):
		"""Move an thing to a new location."""
		pass

	def add_thing(self, thing, location=(1, 1)):
		Environment.add_thing(self, thing, location)
		thing.holding = []
		thing.held = None

	def turn_heading(self, heading, inc, \
					headings=[(1, 0), (0, 1), (-1, 0), (0, -1)]):
		"""Return the heading to the left (inc=+1) or right (inc=-1) in headings."""

		return headings[(headings.index(heading) + inc) % len(headings)]

	def step(self):
		"""Run the environment for one time step. If the
		actions and exogenous changes are independent, this method will
		do.  If there are interactions between them, you'll need to
		override this method."""
		
		self.time = self.time + 1

		self.step_action_que()

		if not self.is_done():
			# send precepts to all agents and store their action
			actions = [agent.program(self.percept(agent))
				for agent in self.agents]

			for (agent, action) in zip(self.agents, actions):
				if isinstance(action, list):
					for a in action:
						if a != None:
							self.execute_action(a)
							self.step_action_que()
							self.exogenous_change()
				else:
					if action != None:
						self.execute_action(action)
						self.step_action_que()
						self.exogenous_change()
	
			self.step_action_que()
	
	
	# xxx: agents should take take of their action que, not environment
	def step_action_que(self):
		# update our actions in progress
		[a.update() for a in self.action_que]
		
		# get all the actions that are finished!
		finished = [a for a in self.action_que if \
			a.state == ACTIONSTATE_FINISHED]
		
		for action in finished:
			action.touch()
			self.action_que.remove(action)
