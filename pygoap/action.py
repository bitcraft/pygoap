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
This class was orginally one, but to cut on memory usage, I have
split the action class into two parts based on usage:

Nodes:       For Planning
ActionClass: For the environment

Nodes should only be instanced once, and will be used by the planner.

ActionClasses will be instanced everytime the agent wants to perform
an action in the environment.  This is the class you want to change if
you want the agent to actually do something that it is planning on doing.

TODO/NOTES:

for scheduling, we need to enable actions to run concurently.
for example, we might want to move somewhere when we do something else,
or whatever.  same goes for motor class.

for scheduling, we need to specify whether or not the action can be called
concurrently, and an automatic way to do so is by using a time-line, and
a space-line.  since our agent operates in time and space, the changes
to those should affect the decision made.

for example, it would make sence more for the agent to do something quick
that is in its que over something longer time is an issue.

each action therefore should add time and distance as a cost.  those costs
can be weighted by the planner when making decisions.

"""

__version__ = ".007"

ACTIONSTATE_NOT_STARTED = 0
ACTIONSTATE_FINISHED    = 1
ACTIONSTATE_RUNNING     = 2
ACTIONSTATE_PAUSED      = 3


from utilities import PyEval


def dlog(text):
    print "action: %s" % text


class ActionNodeBase(object):
    """
    Action Node:
        has a prereuisite
        has a effect
        has a reference to a class to "do" the action

        once completed, then clean the blackboard

    This class is for planning use only!

    TODO:
        use XML to store the action's data.
        names matched as locals inside the bb passed
    """

    def __init__(self, name, p=None, e=None):
        self.name = name
        self.prereqs = []
        self.effects = []

        self.start_func = None

        try:
            self.effects.extend(e)
        except:
            self.effects.append(e)

        try:
            self.prereqs.extend(p)
        except:
            self.prereqs.append(p)

    def set_action_class(self, klass):
        self.action_class = klass

    def valid(self, bb):
        """
        Given the bb, can we run this action?

        This should not be cached.
        """
        raise NotImplementedError

    def touch(self, bb):
        """
        This is run when the action is succesful
       
        Should do something to the blackboard to make sure planner
        knows we've completed successfully. 
        """
        raise NotImplementedError

    def __repr__(self):
        return "<Action=\"%s\">" % self.name

class SimpleActionNode(ActionNodeBase):
    """
    This Node class deligates valid and touch to "validator" and
    "prereq" classes.
    """

    def valid(self, bb):
        for p in self.prereqs:
            if p.valid(bb) == False:
                return False

        return True

    def touch(self, bb):
        [e.touch(bb) for e in self.effects]

class CallableAction(object):
    """
    The Action class is used for actions that require the action to run
    over time.  They will be updated as often as the agent is updated.

    You should override, start, proceed, and finish.
    """

    def __init__(self, caller, validator):
        self.caller = caller
        self.validator = validator
        self.state = ACTIONSTATE_NOT_STARTED

    def touch(self):
        self.validator.touch(self.caller.blackboard)
        
    def valid(self):
        return self.validator.valid(self.caller.blackboard)

    def start(self):
        self.state = ACTIONSTATE_RUNNING
        print "starting:", self.__class__.__name__, self.caller

    def proceed(self):
        pass

    def update(self, time_passed):
        if self.state == ACTIONSTATE_RUNNING:
            self.proceed(time_passed)
        elif self.state == ACTIONSTATE_NOT_STARTED:
            self.start()

    def finish(self):
        self.touch()
        self.state = ACTIONSTATE_FINISHED

class CalledOnceAction(CallableAction):
    """
    Action is finished immediately when started.
    """
    def start(self):
        self.finish()

class PausableAction(CallableAction):
    def pause(self):
        self.state = ACTIONSTATE_PAUSED

    def update(self, time_passed):
        if self.state != ACTIONSTATE_PAUSED:
            CallableAction.update(self, time)

class ActionPrereqBase(object):
    def __init__(self, p):
        self.prereq = p

    def valid(self, bb):
        raise NotImplementedError

    def __repr__(self):
        return "<ActionPrereq=\"%s\">" % self.prereq

class BasicActionPrereq(ActionPrereqBase):
    """
    Basic - just look for the presence of a tag on the bb.
    """

    def valid(self, bb):
        """
        Given the bb, can we run this action?
        """

        if (self.prereq == None) or (self.prereq == ""):
            return True
        else:
            return self.prereq in bb.tags()

    def __repr__(self):
        return "<BasicActionPrereq=\"%s\">" % self.prereq

class ExtendedActionPrereq(ActionPrereqBase):
    """
    These classes can use strings that evaluate variables on the blackboard.
    """

    def __init__(self, prereq):
        super(ExtendedActionPrereq, self).__init__(prereq)
        self._validator = PyEval(prereq)

    def valid(self, bb):
        return self._validator.do_eval(bb)

    def __repr__(self):
        return "<ExtendedActionPrereq=\"%s\">" % self.prereq

class LocationActionPrereq(ActionPrereqBase):
    """
    Location Based

    For this to be valid, the location on the bb must be the same.
    """

    def __init__(self, location):
        self.location = location

    def valid(self, bb):
        """
        Do a pathfinding test to see if this action is valid or not
        Obviously, care needs to be taken that this isn't called too much
        """
        pass

    def __repr__(self):
        return "<MovementActionPrereq=\"%s\">" % self.location

class ActionEffectBase(object):
    """
    This object knows what should happen after an action succesfully happens
    """

    def __init__(self, effect):
        self.effect = effect

    # called when action is successful
    def touch(self, bb):
        raise NotImplementedError

    def __repr__(self):
        return "<ActionEffect=\"%s\">" % self.effect

class BasicActionEffect(ActionEffectBase):
    """
    Basic - Simply post a tag with True as the value.
    """

    def touch(self, bb):
        bb.post(self.effect, True)

    def __repr__(self):
        return "<BasicActionEffect=\"%s\">" % self.effect

class ExtendedActionEffect(ActionEffectBase):
    """
    Extended - Use PyEval.
    """

    def __init__(self, effect):
        super(ExtendedActionEffect, self).__init__(effect)
        self._touchator = PyEval(effect)

    def touch(self, bb):
        bb = self._touchator.do_exec(bb)

    def __repr__(self):
        return "<ExtendedActionEffect=\"%s\">" % self.effect



