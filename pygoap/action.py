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

ACTIONSTATE_NOT_STARTED = 0
ACTIONSTATE_FINISHED    = 1
ACTIONSTATE_RUNNING     = 2
ACTIONSTATE_PAUSED      = 3

"""
this class was orginally one, but to cut on memory usage, I have
split the action class into two parts based on usage:

* planning
* doing stuff in an environment

there is still a tight coupling between the two, but this will save
memory in this way:
when the game is processing a lot of actions, according to the
environments que, each will have to be instanced, but, this isn't good,
since the planning portion can have high memory requirements

this way, there only needs to be one instance of the planning action node.

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

__version__ = ".004"

class ActionNodeBase(object):
    """
    action:
        has a prereuisite
        has a effect
        has a reference to a class to "do" the action

        once completed, then clean the blackboard

    this is like a singleton class, to cut down on memory usage

    TODO:
        use XML to store the action's data.
        names matched as locals inside the bb passed
    """

    def __init__(self, name, p=None, e=None):
        self.name = name
        self.prereqs = []
        self.effects = []

        # costs.
        self.time_cost = 0
        self.move_cost = 0

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

    # this should not be cached.
    def valid(self, bb):
        """Given the bb, can we run this action?"""
        raise NotImplementedError

    # this is run when the action is succesful
    # do something on the blackboard (varies by subclass)
    def touch(self, bb):
        raise NotImplementedError

    def __repr__(self):
        return "<Action=\"%s\">" % self.name

class SimpleActionNode(ActionNodeBase):
    def valid(self, bb):
        for p in self.prereqs:
            if p.valid(bb) == False:
                return False

        return True

    def touch(self, bb):
        [e.touch(bb) for e in self.effects]

class CallableAction(object):
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
        if self.state == ACTIONSTATE_NOT_STARTED:
            self.start()
        elif self.state == ACTIONSTATE_RUNNING:
            self.proceed(time_passed)

    def finish(self):
        self.state = ACTIONSTATE_FINISHED

class CalledOnceAction(CallableAction):
    """
    Is finished imediatly when started.
    """
    def start(self):
        self.finish()

class PausableAction(CallableAction):
    def pause(self):
        self.state = ACTIONSTATE_PAUSED

    def update(self, time_passed):
        if self.state != ACTIONSTATE_PAUSED:
            CallableAction.update(self, time)
