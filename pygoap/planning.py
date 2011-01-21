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

import copy

from mapdb import MemoryDB
from astar import Astar, PathfindingNode, PathfindingError
from agent import Blackboard

DEBUG = False

# since this gets attached to mobiles, don't inherit from mud objects?
# a shared resource should be the planning map
# this could be a singleton for all objects in the game
# it is up to the agent classes to define a list of actions they can do
# THIS COULD BE A HEAP, BUT NEEDS TO BE RESORTED CONSTANTLY
# GOALS COULD INFOR THE MANAGER THAT THEY HAVE CHANGED, THEN COULD PUSH/POP
# A HEAP

__version__ = ".002"

class PlanningNode(PathfindingNode):
	"""
	each node should contain a delta of the blackboard.  ugh!
	"""
	def __init__(self, *arg, **kwarg):
		super(PlanningNode, self).__init__(*arg, **kwarg)
		self.bb_delta = Blackboard()

	def __repr__(self):
		try:
			return "<Node=obj: %s, c:%s, p:%s // %s>" % \
			(self.obj, self.cost, self.parent.obj, self.bb_delta.data)
		except AttributeError:
			return "<Node=obj: %s, c:%s, p:None // %s>" % \
			(self.obj, self.cost, self.bb_delta.data)

class Planner(Astar):
	"""
	weakness, the planner cannot repeat actions.
	use astar to generate a plan to reach a goal.
	notable differences:
		uses a "blackboard" to check for finished state

	startnode gets a bb.  each neighbor or child will apply its "effect" on the
	blackboard (don't run the action), then a delta is created and applied to
	that child.

	deltas are not implimented, but should be sometime
	implimenting them would require a trace from each node to reconstruct it,
	and i don't want to code that right now.  they are labled as deltas, but
	are just copies

	the "keynode" will update the planner with its blackboard.  this is used to
	find actions which are valid and able to be used.

	if actions are used twice in a plan, then a copy needs to be made.
	this would make it possible to repeat actions in order to reach a goal.
	if a node is closed, but still valid, then give a copy of the action
	a copy is needed to preserve the orginal order
	"""

	def __init__(self, bb, *arg, **kwarg):
		self.blackboard = bb
		super(Planner, self).__init__(*arg, **kwarg)
		self.node_factory = PlanningNode

	def _get_best_node(self):
		# get our node
		node = super(Planner, self)._get_best_node()
		self.blackboard = node.bb_delta
		return node

	def check_complete(self, node):
		return self.finish.satisfied(node.bb_delta)

	def check_neighbor(self, neighbor):
		# do normal checks, and reject neighbors who are no longer valid
		if super(Planner, self).check_neighbor(neighbor):
			return neighbor.obj.valid(self.keyNode.bb_delta)
		else:
			return False
			#if neighbor != None:
				#if neighbor.closed and neighbor.obj.valid(self.keyNode.bb_delta):
					#print "copy??", neighbor
					#neighbor = None
					#return True

	def build_node(self, obj, parent, cost, h):
		# get the node we are adding
		# should return None if unable to

		if parent != None:
			if obj.valid(parent.bb_delta):
				node = super(Planner, self).build_node(obj, parent, cost, h)
			else:
				return None
		else:
			node = super(Planner, self).build_node(obj, parent, cost, h)

		# if our parent is None, then this is the start node
		# apply our blackboard
		if parent == None:
			node.bb_delta = copy.deepcopy(self.blackboard)
		else:
			# get the parents blackboard
			t = copy.deepcopy(parent.bb_delta)

			# apply the action as if it was completed ok
			node.obj.touch(t)

			# copy the new bb
			node.bb_delta = t

		if DEBUG:
			dlog("planner - node: %s" % node)

		return node

class PlanningMap(MemoryDB):
	"""
	a map of actions.  and a goal.
	"""

	def get_surrounding3(self, action):
		"""
		return a list of anything we can do
		if action==None, then return a list of all available nodes.
		"""

		surr = list(self.get_nodes())

		if action != None:
			surr.remove(action)

		return surr

class PlanManager(object):
	"""This actually "plans", attached to agents."""

	def __init__(self, blackboard):
		self.action_map = PlanningMap()
		self.blackboard = blackboard
		self.plan = None

	def tick(self):
		pass

	# an alias more or less
	def add_action(self, action):
		self.action_map.add_node(action)

	def get_surrounding(self, action):
		surr = self.action_map.get_surrounding3(action)

		# don't ask how i figured out this magic
		l = len(surr)
		surr = zip(*(surr,[1]*l, [1]*l))

		return surr

	def make_plan(self):
		# get the current goal from the blackboard
		try:
			goal = self.blackboard.read("goal")
		except KeyError:
			raise KeyError, "Cannot make_plan, no goal set"

		# get our idling action.  obviously there are better ways to do this
		actions = self.action_map.get_nodes()
		idle = [a for a in actions if a.name == "idle"][0]

		planner = Planner(self.blackboard, idle, goal, self.get_surrounding)

		# this is cpu intensive!
		try:
			self.plan = planner.findpath()
		except PathfindingError:
			raise

		# astar will return a list with idle included...we dont want it!
		self.plan = self.plan[1:]
		self.plan.reverse()

		if DEBUG:
			dlog("planner - plan: %s" % self.plan)
			dlog("bb: %s" % self.blackboard.data)

		# post to blackboard
		self.blackboard.post("plan", self.plan)
