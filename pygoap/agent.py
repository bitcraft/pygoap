from environment import ObjectBase
from planning import plan, InstancedAction
from blackboard import Blackboard, MemoryManager, Tag
from actionstates import *


NullAction = InstancedAction()


# required to reduce memory usage
def time_filter(precept):
    if precept.sense == "time":
        return None
    else:
        return precept


class GoapAgent(ObjectBase):
    """
    AI Agent

    inventories will be implemented using precepts and a list.
    currently, only one action running concurrently is supported.
    """

    # this will set this class to listen for this type of precept
    # not implemented yet
    interested = []

    def __init__(self):
        self.idle_timeout = 30
        self.bb           = Blackboard()
        #self.mem_manager  = MemoryManager(self)
        self.planner      = plan

        self.current_goal   = None

        self.goals = []             # all goals this instance can use
        self.filters = []           # list of methods to use as a filter
        self.actions = []           # all actions this npc can perform
        self.plan = []              # list of actions to perform
                                    # '-1' will be the action currently used

        # this special filter will prevent time precepts from being stored
        self.filters.append(time_filter)

    def add(self, other, origin):
        # we simulate the agent's knowledge of its inventory with precepts
        p = Precept(sense="inventory")

        # do the actual add
        super(GoapAgent, self).add(other, origin)
        
    def remove(self, obj):
        # we simulate the agent's knowledge of its inventory with precepts
        p = Precept(sense="inventory")

        # do the actual remove
        super(GoapAgent, self).remove(other, origin)
        
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
            if precept == None:
                break

        return precept

    def handle_precept(self, pct):
        """
        used by the environment to feed the agent precepts.
        agents can respond by sending back an action to take.
        """

        # give our filters a chance to change the precept
        pct = self.filter_precept(pct)

        # our filters may have caused us to ignore the precept
        if pct == None: return None
       
        print "[agent] {} recv'd pct {}".format(self, pct)

        # this line has been added for debugging purposes
        self.plan = []
 
        if pct.sense == "position":
            self.bb.post(Tag(position=pct.position, obj=pct.thing))

        return self.next_action()

    def replan(self):
        """
        force agent to re-evaluate goals and to formulate a plan
        """

        # get the relevancy of each goal according to the state of the agent
        s = [ (g.get_relevancy(self.bb), g) for g in self.goals ]
        s = [ g for g in s if g[0] > 0 ]
        s.sort(reverse=True)

        print "[agent] goals {}".format(s)

        # starting for the most relevant goal, attempt to make a plan      
        for score, goal in s:
            ok, plan = self.planner(
                self,
                self.actions,
                self.current_action(),
                self.bb,
                goal)

            if ok:
                print "[agent] {} has planned to {}".format(self, goal)
                pretty = list(reversed(plan[:]))
                print "[agent] {} has plan {}".format(self, pretty)
                return plan
            else:
                print "[agent] {} cannot {}".format(self, goal)

        return []

    def current_action(self):
        try:
            return self.plan[-1]
        except IndexError:
            return NullAction

    def running_actions(self):
        return self.current_action()

    def next_action(self):
        """
        get the next action of the current plan
        """

        if self.plan == []:
            self.plan = self.replan()

        current_action = self.current_action()

        # this action is done, so return the next one
        if current_action.state == ACTIONSTATE_FINISHED:
            return self.plan.pop()

        # this action failed somehow
        elif current_action.state == ACTIONSTATE_FAILED:
            raise Exception, "action failed, don't know what to do now!"

        # our action is still running, just run that
        elif current_action.state == ACTIONSTATE_RUNNING:
            return current_action


