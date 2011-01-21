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

import csv, sys, os, imp

try:
  import psyco
except ImportError:
  pass

from pygoap.action import SimpleActionNode
from pygoap.pygoap import BasicActionPrereq, ExtendedActionPrereq, SimpleGoal
from pygoap.pygoap import BasicActionEffect, ExtendedActionEffect
from pygoap.agent import GoapAgent
from pygoap.environment import XYEnvironment, PRECEPT_ALL

"""
two threads:
	one for core logic
	one for updating the display

lets make a drunk pirate.

scenerio:
	the pirate begins by idling
	after 5 seconds of the simulation, he sees a girl

he should attempt to get drunk and sleep with her...
...any way he knows how.
"""

global_actions = {}

def load_commands(agent, path):
	def is_expression(string):
		if "=" in string:
			return True
		else:
			return False

	def parse_line(p, e):
		prereqs = []
		effects = []

		if p == "":
			prereqs = None
		else:
			for x in p.split(","):
				x = x.strip()
				if is_expression(x):
					p2 = ExtendedActionPrereq(x)
				else:
					p2 = BasicActionPrereq(x)

				prereqs.append(p2)

		for x in e.split(","):
			x = x.strip()
			if is_expression(x):
				e2 = ExtendedActionEffect(x)
			else:
				e2 = BasicActionEffect(x)

			effects.append(e2)

		return prereqs, effects

	# more hackery
	mod = imp.load_source("actions", os.path.join(path, "actions.py"))

	csvfile = open(os.path.join(path, "actions.csv"))
	sample = csvfile.read(1024)
	dialect = csv.Sniffer().sniff(sample)
	has_header = csv.Sniffer().has_header(sample)
	csvfile.seek(0)

	r = csv.reader(csvfile, delimiter=';')

	for n, p, e in r:
		prereqs, effects = parse_line(p, e)
		action = SimpleActionNode(n, prereqs, effects)
		action.set_action_class(mod.__dict__[n])
		agent.plan_manager.add_action(action)

def find_females(precepts):
	humans = [p.thing for p in precepts if isinstance(p.thing, Human)]
	females = [h for h in humans if h.gender == "Female"]

	# remove duplicates
	females = list(set(females))
	return females

class Human(GoapAgent):
	def __init__(self, gender):
		super(Human, self).__init__()
		self.gender = gender

	def program(self, precept):
		action = super(Human, self).program(precept)
		females = find_females(self.mem_manager.search(PRECEPT_ALL))
		if females:
			self.blackboard.post("target", females[0])

		return action

class Rum(object):
	pass

pirate = Human("Male")

# lets load some pirate commands
load_commands(pirate, os.path.join("npc", "pirate"))

# he has high aspirations in life
pirate.goal_manager.add_goal(SimpleGoal("is_drunk"))
pirate.goal_manager.add_goal(SimpleGoal("is_laid"))

#pirate.blackboard.post("is_evil", True)
#pirate.blackboard.post("is_weak", True)

# make our little cove
formosa = XYEnvironment()

# add the pirate
formosa.add_thing(pirate)
formosa.add_thing(Rum())

wench = Human("Female")

formosa.run(10)
print "=== wench"
formosa.add_thing(wench)
formosa.run(10)		

