"""
These are the building blocks for creating pyGOAP agents that are able to
interact with their environment in a meaningful way.

When actions are updated, they can return a precept for the environment to
process.  The action can emit a sound, sight, or anything else for other
objects to consume.

These classes will be known to an agent, and chosen by the planner as a means
to satisfy the current goal.  They will be instanced and the the agent will
execute the action in some way, one after another.

Actions need to be split into ActionInstances and ActionBuilders.

An ActionInstance's job is to work in a planner and to carry out actions.
A ActionBuilder's job is to query the caller and return a list of suitable
actions for the bb.
"""

from planning import *
from actionstates import *
import sys


test_fail_msg = "some goal is returning None on a test, this is a bug."

class ActionBuilder(object):
    """
    ActionBuilders examine a blackboard and return a list of actions
    that can be successfully completed at the the time.
    """

    def get_actions(self, caller, bb):
        raise NotImplementedError

    def __init__(self, **kwargs):
        self.prereqs = []
        self.effects = []
        self.costs   = {}

        self.__dict__.update(kwargs)

        self.setup()

    def setup(self):
        """
        add the prereqs, effects, and costs here
        override this
        """
        pass

    def __repr__(self):
        return "<ActionBuilder: {}>".format(self.__class__.__name__)


class CallableAction(InstancedAction):
    """
    callable action class.

    subclass this class to implement the code side of actions.
    for the most part, "start" and "update" will be the most
    important methods to overload.
    """

    def __init__(self, caller, **kwargs):
        self.caller     = caller
        self.state      = ACTIONSTATE_NOT_STARTED

        self.prereqs = []
        self.effects = []
        self.costs   = {}

        self.__dict__.update(kwargs)

    def test(self, bb=None):
        """
        make sure the action is able to be started
        return a float from 0-1 that describes how valid this action is.

        validity of an action is a measurement of how effective the action
        will be if it is completed successfully.

        if any of the prereqs are not partially valid ( >0 ) then will
        return 0

        this value will be used in planning.

        for many actions a simple 0 or 1 will work.  for actions which
        modify numerical values, it may be useful to return a fractional
        value.
        """

        # NOTE: may be better written with itertools

        if bb == None: raise Exception

        if len(self.prereqs) == 0: return 1.0
        total = [ i.test(bb) for i in self.prereqs ]
        print "[goal] {} test {}".format(self, total)
        #if 0 in total: return 0
        try:
            return float(sum(total)) / len(self.prereqs)
        except TypeError:
            print zip(total, self.prereqs)
            print test_fail_msg
            sys.exit(1)


    def touch(self, bb=None):
        """
        call when the planning phase is complete
        """
        if bb == None: bb = self.caller.bb
        [ i.touch(bb) for i in self.effects ]


    def start(self):
        """
        start running the action
        """
        self.state = ACTIONSTATE_RUNNING


    def update(self, time):
        """
        actions which occur over time should implement
        this method.

        if the action does not need more that one cycle, then
        you should use the calledonceaction class
        """
        pass


    def fail(self, reason=None):
        """
        maybe what we planned to do didn't work for whatever reason
        """
        self.state = ACTIONSTATE_FAILED


    def abort(self):
        """
        stop the action without the ability to complete or continue
        """
        self.state = ACTIONSTATE_BAILED


    def finish(self):
        """
        the planned action was completed and the result is correct
        """
        if self.state == ACTIONSTATE_RUNNING:
            self.state = ACTIONSTATE_FINISHED


    def ok_finish(self):
        """
        determine if the action can finish now
        if cannot finish now, then the action
        should bail if it is forced to finish.
        """
        return self.state == ACTIONSTATE_FINISHED


    def pause(self):
        """
        stop the action from updating.  should be able to continue.
        """
        self.state = ACTIONSTATE_PAUSED


class CalledOnceAction(CallableAction):
    """
    Is finished immediately when started.
    """

    def start(self):
        # valid might return a value less than 1
        # this means that some of the prereqs are not
        # completely satisfied.
        # since we want everything to be completely
        # satisfied, we require valid == 1.
        if self.test() == 1.0:
            CallableAction.start(self)
            CallableAction.finish(self)
        else:
            self.fail()

    def update(self, time):
        pass


