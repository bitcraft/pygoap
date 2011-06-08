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
working towards an event based framework.

i plan to use signals to communicate between subsystems.
the constant polling sugested by another author seems like too much

how are goals and actions not the same?
they both satisfy something, and have an effect, right?

IMPORTANT:
    goals are shared by all agents.  they should never change.

maybe impliment...

best guess:
    if no plan is available, just do anything...to mix things up a bit

"""


__version__ = "v.001"


DEBUG = True

def dlog(text):
    print "goal: %s" % text

class GoalManager(object):
    """
    This class organizes goals.

    The Goal Manager picks candidate goals from a pool of usable ones
    and sets it as the goal that should be satisfied.
    """

    def __init__(self, blackboard):
        # every goal this agent will consider using
        self.all_goals = []

        # every goal this agent currently wants to satisfy
        self.curr_goals = []

        # goals that cannot be satisfied
        self.invalid_goals = []

        self.blackboard = blackboard

    def add_goal(self, goal):
        self.all_goals.append(goal)

    def invalidate_goal(self, goal):
        """
        This is called when an error ocurrs during the planning of actions
        that will satisfy the goal.  Typically happens on broken action
        maps or when actions cannot be called due to lack of valid prereqs.
        """
        if DEBUG: print "invalidate goal:", goal
        self.invalid_goals.append(goal)

    def validate_goal(self, goal):
        """
        Called when a previously invalidated goal is valid again.
        Currently, this just means that the goal will be tested again.
        """
        try:
            self.invalid_goals.remove(goal)
        except ValueError:
            pass

    def check_invalids(self):
        pass

    def sort_goals(self):
        """
        Sorts the available goals in order of relevancy.

        This can be a big workload, as each action in the action map
        must be tested against the blackboard.
        """

        if len(self.all_goals) == 0:
            raise ValueError, "There are no goals set"

        # UPDATE THE GOALS
        self.curr_goals = [goal.update(self.blackboard)
            for goal in self.all_goals
            if goal not in self.invalid_goals]

        # SORT BY RELEVANCY
        s = [(goal.relevancy, goal) for goal in self.curr_goals]
        s.sort(reverse=True)

        # MAKE A LIST OF GOALS, SANS RELEVANCY
        self.curr_goals = [x[1] for x in s]

        if DEBUG:
            print self.curr_goals

    def pick_goal(self):
        """
        Post the best goal onto the blackboard.
        """

        try:
            self.sort_goals()
            self.blackboard.post("goal", self.curr_goals[0])
        except ValueError:
            pass

class GoalBase(object):
    """
    Goals:
        can be satisfied.
        can be valid
    """

    def __init__(self, s=None, r=None, v=True):
        self.satisfies = s
        self.relevancy = r

    def update(self, bb):
        """
        Return a float 0-1 on how "relevent" this goal is.
        Should be subclassed =)
        """
        raise NotImplementedError

    def satisfied(self, bb):
        """
        Test whether or not this goal has been satisfied
        """
        raise NotImplementedError

    def __repr__(self):
        return "<Goal=\"%s\">" % self.satisfies

class SimpleGoal(GoalBase):
    """
    Uses flags on a blackboard to test goals.
    """

    def update(self, bb):
        if self.satisfies in bb.tags():
            self.relevancy = 0
        else:
            self.relevancy = 1
        return self

    def satisfied(self, bb):
        try:
            bb.read(self.satisfies)
        except KeyError:
            return False
        else:
            return True

