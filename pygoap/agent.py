from environment import ObjectBase
from planning import plan
from actions import ActionContext
from memory import MemoryManager
from actionstates import *
from precepts import *
import logging

debug = logging.debug



NullAction = ActionContext(None)
NullAction.__enter__()
NullAction.__exit__()

# required to reduce memory usage
def time_filter(precept):
    return None if isinstance(precept, TimePrecept) else precept

class GoapAgent(ObjectBase):
    """
    AI Agent

    inventories will be implemented using precepts and a list.
    currently, only one action running concurrently is supported.
    """

    # this will set this class to listen for this type of precept
    # not implemented yet
    interested = []
    idle_timeout = 30

    def __init__(self, name=None):
        super(GoapAgent, self).__init__(name)
        self.memory = MemoryManager()
        self.planner = plan

        self.current_goal = None

        self.goals = []             # all goals this instance can use
        self.filters = []           # list of methods to use as a filter
        self.actions = []           # all actions this npc can perform
        self.plan = []              # list of actions to perform
                                    # '-1' will be the action currently used

        # this special filter will prevent time precepts from being stored
        self.filters.append(time_filter)

    def add_goal(self, goal):
        self.goals.append(goal)

    def remove_goal(self, goal):
        self.goals.remove(goal)

    def add_action(self, action):
        self.actions.append(action)

    def remove_action(self, action):
        self.actions.remove(action)

    def filter_precept(self, precept):
        """
        precepts can be put through filters to change them.
        this can be used to simulate errors in judgement by the agent.
        """
        for f in self.filters:
            precept = f(precept)
            if precept is None:
                break

        return precept

    def process(self, precept):
        """
        used by the environment to feed the agent precepts.
        agents can respond by sending back an action to take.
        """
        precept = self.filter_precept(precept)

        if precept:
            debug("[agent] %s recv'd precept %s", self, precept)
            self.memory.add(precept)

        if self.next_action is NullAction:
            self.replan()
            return self.next_action


    def replan(self):
        """
        force agent to re-evaluate goals and to formulate a plan
        """

        # get the relevancy of each goal according to the state of the agent
        s = ( (g.get_relevancy(self.memory), g) for g in self.goals )
        s = [ g for g in s if g[0] > 0.0 ]
        s.sort(reverse=True)

        debug("[agent] %s has goals %s", self, s)

        start_action = NullAction

        # starting for the most relevant goal, attempt to make a plan
        self.plan = []      
        for score, goal in s:
            tentative_plan = self.planner(self, self.actions,
                start_action, self.memory, goal)

            if tentative_plan:
                tentative_plan.pop()
                pretty = list(reversed(tentative_plan[:]))
                debug("[agent] %s has planned to %s", self, goal)
                debug("[agent] %s has plan %s", self, pretty)
                self.plan = tentative_plan
                self.current_goal = goal
                break


    # we only support one concurrent action (i'm lazy)
    def running_actions(self):
        return self.current_action

    @property
    def current_action(self):
        """
        get the current action of the current plan
        """

        try:
            return self.plan[-1]
        except IndexError:
            return NullAction

    @property
    def next_action(self):
        """
        if the current action is finished, return the next
        otherwise, return the current action
        """

        # this action is done
        if self.current_action.state == ACTIONSTATE_FINISHED:

            # there are more actions in the queue, so just return the next one
            if self.plan:
                return self.plan.pop()

            # no more actions, so the plan worked!
            else:

                # let the goal do its magic to the memory manager
                if self.current_goal:
                    self.current_goal.touch(self.memory)
                    self.current_goal = None
           
                return NullAction

        # this action failed somehow
        elif self.current_action.state == ACTIONSTATE_FAILED:
            raise Exception, "action failed, don't know what to do now!"

        # our action is still running, just run that
        elif self.current_action.state == ACTIONSTATE_RUNNING:
            return self.current_action
