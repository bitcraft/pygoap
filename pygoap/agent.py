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

from memory import MemoryManager
from motor import MotorManager

"""
programming impulses:
    when a precept is seen, add an action to a que, or pushback
    then use that instead of planning

agents are the ai fountation of NPC's

various NPC's are modeled using goap

actions need to be started and finished
could make a small scheduler...round robin, type
problem with mutually exclusive actions. (can't sit and run)
easy way:
    make a table of actions which cannot be run at once.

finding the intersection of plans...
    to plan out how to better prevent the actions of other agents

to make more realistic...
    npc should be able to make a plan about what another npc (or player) might do:
    ie: "i want to kill you"
        "you might run away"
        "i'll close the door, then you can't run away"

    this mean, that the objects can sense and percieve on behalf of another
    object.  look at you...you are bleeding.  attack.
    remembering the outcome of a plan...recursive planning...
    goals can be plans.
    that means that the inputs and outputs have to be the same
    when ever a goal is satisfied (or not), then the results can be
        stored in memory

    Locations are can be goals, too!

    predictive:
        as is, stores information about other objects.
        another goalmanager would have to be set up for each target

for performance:
    using flag-based "simple" action/effects (impliment this: think "bool")
    flags are managed by the actions that posted them
    consider using slots.

"""

__version__ = ".012"

DEBUG = True

# Basic imp of a blackboard.  uses a dict.
class Blackboard(object):
    def __init__(self):
        self.data = {}

    def tags(self):
        return self.data.keys()

    def post(self, key, value):
        self.data[key] = value

    def read(self, key):
        return self.data[key]

    def remove(self, key):
        try:
            del self.data[key]
        except KeyError:
            pass

class Agent(object):
    """
    An agent is tied to an object.
    the C4 architecture...kinda
    this is basically the most minimal living thing
    """

    def __init__(self):
        self.blackboard = Blackboard()

    def is_alive(self):
        return True

    def program(self, precept):
        pass

from pygoap import GoalManager
from planning import PlanManager, PathfindingError

class GoapAgent(Agent):
    # consider making an instance of ASTAR a class variable

    def __init__(self):
        super(GoapAgent, self).__init__()
        self.goal_manager = GoalManager(self.blackboard)
        self.plan_manager = PlanManager(self.blackboard)
        self.mem_manager = MemoryManager(self.blackboard)

        self.idle_timeout = 5
        self.idle_counter = 0
        self.actionq = []

    """
    this returning none stuff should go, just make it idle!
    """
    
    def program(self, precept):
        Agent.program(self, precept)

        # add what we see to our memory manager
        self.mem_manager.add_memory(precept)

        # handle precept triggers (callbacks)
        self.handle_triggers()

        # call the goap stuff
        action = self.tick()
        
        # our internal actions are just for planning,
        # so return an action our environment can use
        if action != None:
            return action.action_class(self, action)
        else:
            return None

    def handle_triggers(self):
        pass

    # this should be merged with the plan manager
    def reset(self):
        # clear our goal and plan...
        self.blackboard.remove("goal")
        self.blackboard.remove("plan")

        # un-invalidate goals
        for goal in self.goal_manager.invalid_goals:
            self.goal_manager.validate_goal(goal)

    # this should be merged with the plan manager
    def tick(self):
        if DEBUG:
            print "=== tick ============================================"
            print self.blackboard.data
            print "-----------------------------------------------------"

        if self.idle_counter:
            if self.idle_counter == self.idle_timeout:
                self.idle_counter = 0
                self.idle_timeout = 0
                for goal in self.goal_manager.all_goals:
                    goal.valid = True
            else:
                self.idle_counter += 1
                return

        # do we have a goal?
        try:
            goal = self.blackboard.read("goal")
        except KeyError:
            self.goal_manager.pick_goal()
            try:
                goal = self.blackboard.read("goal")
            except KeyError:
                return

        # test if our goal has been reached
        if goal.satisfied(self.blackboard):
            self.reset()
            return

        # yes, so do we have a plan?
        try:
            plan = self.blackboard.read("plan")
        except KeyError:
            try:
                self.plan_manager.make_plan()
                plan = self.blackboard.read("plan")
            except PathfindingError:
                self.goal_manager.invalidate_goal(goal)
                self.blackboard.remove("goal")
                return

        # if the plan isn't empty..
        if len(plan) > 0:
            # lets carry out the actions in our plan
            return plan.pop()
