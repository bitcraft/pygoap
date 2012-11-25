"""
These are the building blocks for creating pyGOAP agents that are able to
interact with their environment in a meaningful way.

When actions are updated, they can return a precept for the environment to
process.  The action can emit a sound, sight, or anything else for other
objects to consume.

These classes will be known to an agent, and chosen by the planner as a means
to satisfy the current goal.  They will be instanced and the agent will
execute the action in some way, one after another.

Actions need to be split into ActionInstances and ActionBuilders.

An ActionInstance's job is to work in a planner and to carry out actions.
A ActionBuilder's job is to query the caller and return a list of suitable
actions for the memory.
"""

from actionstates import *
import sys



test_fail_msg = "some goal is returning None on a test, this is a bug."

class ActionBuilder(object):
    """
    ActionBuilders examine a blackboard and return a list of actions that can
    be successfully completed at the time.

    The actions that are returned will be assumed to be valid and will not be
    tested.  Please make sure that the actions are valid.
    """

    def __call__(self, caller, memory):
        return self.get_actions(caller, memory)

    def get_actions(self, caller, memory):
        """
        Return a list of actions
        """
        raise NotImplementedError

    def __repr__(self):
        return "<ActionBuilder: {}>".format(self.__class__.__name__)


class ActionContext(object):
    """
    Context where actions take place.
    """

    def __init__(self, caller, **kwargs):
        self.caller  = caller
        self.state   = ACTIONSTATE_NOT_STARTED
        self.prereqs = []
        self.effects = []
        self.costs   = {}
        self.__dict__.update(kwargs)

    def __enter__(self):
        """
        Please do not override this method.  Use enter instead.
        """
        self.state = ACTIONSTATE_RUNNING
        self.enter()
        return self

    def __exit__(self, *exc):
        """
        Please do not override this method.  Use exit instead.
        """
        if self.state is ACTIONSTATE_RUNNING:
            self.state = ACTIONSTATE_FINISHED
        if self.state is not ACTIONSTATE_ABORTED:
            self.exit()
        return False

    def enter(self):
        """
        This method will be called after this context becomes active
        """
        pass

    def exit(self):
        """
        This method will be called after this context become inactive
        """
        pass

    def update(self, time):
        """
        This method will be called periodically by the environment.
        """
        pass

    def fail(self):
        """
        Call this method if the context is not able to complete
        """
        self.state = ACTIONSTATE_FAILED

    def abort(self):
        """
        Call this method to stop this context without cleaning it up
        """
        self.state = ACTIONSTATE_ABORTED

    def test(self, memory=None):
        """
        Determine whether or not this context is able to start (begin())

        return a float from 0-1 that describes how valid this action is.

        validity of an action is a measurement of how effective the action will
        be if it is completed successfully.

        if any of the prereqs are not partially valid ( >0 ) then will return 0

        for many actions a simple 0 or 1 will work.  for actions which
        modify numerical values, it may be useful to return a fractional value.
        """

        if memory is None: raise Exception

        if not self.prereqs: return 1.0
        values = ( i.test(memory) for i in self.prereqs )

        try:
            return float(sum(values)) / len(self.prereqs)
        except TypeError:
            print zip(values, self.prereqs)
            print test_fail_msg
            sys.exit(1)

    def touch(self, memory=None):
        """
        Call after the planning phase is complete.
        """
        if memory is None:
            memory = self.caller.memory
        [ i.touch(memory) for i in self.effects ]

    def __repr__(self):
        return '<Action: {}>'.format(self.__class__.__name__)


class CalledOnceContext(ActionContext):
    """
    Is finished immediately when started.
    """

    def __enter__(self):
        if self.test() == 1.0:
            super(CalledOnceContext, self).enter()
            super(CalledOnceContext, self).exit()
        else:
            self.fail()

