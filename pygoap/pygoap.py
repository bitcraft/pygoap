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

from collections import defaultdict
from types import DictType

"""
event based, more and more

what should be shared amonst all instances of GoalManager:
    Possible actions. why have a bunch of copies?

prereq and effects are statements that test the value of a known variable

i plan to use signals to communicate between subsystems.
the constant polling sugested by another author seems like too much

how are goals and actions not the same?
they both satisfy something, and have an effect, right?

the astar is unique in that:
    the finish is then prereq are None, or can be satisfied
    the start is our goal

maybe impliment...

impluses:
    a shorter version of astar, forward-searching with a short limit
    this would get the actor moving, instead of planning

best guess:
    if no plan is available, just do anything...to mix things up a bit

"""

__version__ = "goap v.016"

DEBUG = False

def dlog(text):
    print "goap: %s" % text

# goals are shared by all agents.  they should never change them
# goal managers can keep track of goals using lists or variables, but
# never change any instance variables, as there should only be one
# instance of any particular goal, which is shared by all agents

class GoalManager(object):
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
        self.invalid_goals.append(goal)

    def validate_goal(self, goal):
        try:
            self.invalid_goals.remove(goal)
        except ValueError:
            pass

    def check_invalids(self):
        pass

    def sort_goals(self):
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
        try:
            self.sort_goals()
            self.blackboard.post("goal", self.curr_goals[0])
        except ValueError:
            pass

class ActionPrereqBase(object):
    def __init__(self, p):
        self.prereq = p

    def valid(self, bb):
        raise NotImplementedError

    def __repr__(self):
        return "<ActionPrereq=\"%s\">" % self.prereq

class BasicActionPrereq(ActionPrereqBase):
    """Basic - just look for the presence of a tag."""
    def valid(self, bb):
        """Given the bb, can we run this action?
        """
        if self.prereq == None or self.prereq == "":
            return True
        else:
            return self.prereq in bb.tags()

    def __repr__(self):
        return "<BasicActionPrereq=\"%s\">" % self.prereq

class ExtendedActionPrereq(ActionPrereqBase):
    def __init__(self, prereq):
        super(ExtendedActionPrereq, self).__init__(prereq)
        self._validator = PyEval(prereq)

    def valid(self, bb):
        r = self._validator.do_eval(bb)
        #if DEBUG:
            #dlog("validator - {0} {1} {2}".format(self, self._validator, r))
            # breaks object security by accessing bb's data
            #dlog("bb: {0}".format(bb.data))
        return r

    def __repr__(self):
        return "<ExtendedActionPrereq=\"%s\">" % self.prereq

class ActionEffectBase(object):
    # valid checks to make sure is valid
    # touching will tell a blackboard that it has happened

    def __init__(self, effect):
        self.effect = effect

    def touch(self, bb):
        raise NotImplementedError

    def __repr__(self):
        return "<ActionEffect=\"%s\">" % self.effect

class BasicActionEffect(ActionEffectBase):
    """Basic - Simply post a tag with True as the value."""
    def touch(self, bb):
        bb.post(self.effect, True)

    def __repr__(self):
        return "<BasicActionEffect=\"%s\">" % self.effect

class ExtendedActionEffect(ActionEffectBase):
    """Extended - Use PyEval."""
    def __init__(self, effect):
        super(ExtendedActionEffect, self).__init__(effect)
        self._touchator = PyEval(effect)

    def touch(self, bb):
        bb = self._touchator.do_exec(bb)

    def __repr__(self):
        return "<ExtendedActionEffect=\"%s\">" % self.effect

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
        """Return a float 0-1 on how "relevent" this goal is.
        Should be subclassed =)"""
        raise NotImplementedError

    def satisfied(self, bb):
        raise NotImplementedError

    def __repr__(self):
        return "<Goal=\"%s\">" % self.satisfies

class SimpleGoal(GoalBase):
    """Uses flags on a blackboard to test."""

    def update(self, bb):
        if self.satisfies not in bb.tags():
            self.relevancy = 1
        else:
            self.relevancy = 0
        return self

    def satisfied(self, bb):
        try:
            bb.read(self.satisfies)
            return True
        except KeyError:
            return False

# used when we are running python2.5...  osx
def get_exception():
    import sys
    import traceback
    cla, exc, trbk = sys.exc_info()
    return traceback.format_exception(cla, exc, trbk)


class PyEval(object):
    """
    A safer way to evaluate strings.

    probably should do some preprocessing to make sure its really safe

    warning, might modify the dict bassed to it.
    """

    def __init__(self, expr):
        self.expr = expr

    def make_dict(self, bb):
        safe_dict = {}

        # clear out builtins
        safe_dict["__builtins__"] = None

        # copy the dictionaries
        for tag in bb.tags():
            safe_dict[tag] = bb.read(tag)

        return safe_dict

    # mostly for prereq's
    def do_eval(self, bb):
        d = self.make_dict(bb)

        try:
            # this always works if we are evaluating variables
            return eval(self.expr, d)
        except NameError:
            # we are missing a value we need to evaluate the expression
            return False

    # mostly for effect's
    def do_exec(self, bb):
        d = self.make_dict(bb)

        try:
            # a little less secure
            exec self.expr in d

        #except NameError as detail:
            # missing a value needed for the statement
            # we make a default value here, but really we should ask the agent
            # if it knows that to do with this name, maybe it knows....
    
            # get name of missing variable
        #    name = detail[0].split()[1].strip('\'')
        #    d[name] = 0
        #    exec self.expr in d

        except NameError:
            detail = get_exception()
            name = detail[3].split('\'')[1]
            d[name] = 0
            exec self.expr in d

        # the bb was modified
        for key, value in d.items():
            bb.post(key, value)
        return True

    def __str__(self):
            return "<PyEval: %s>" % self.expr
            return v0 >= v1
