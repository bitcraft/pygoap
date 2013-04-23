from pygoap.actions import *
from pygoap.goals import *

from pygoap.agent import GoapAgent
from pygoap.environment import Environment


class PrintActionContext(CalledOnceContext):
    def enter(self):
        print "hello world"

class PrintAction(ActionBuilder):
    def get_actions(self, caller, memory):
        action = PrintActionContext(caller)
        action.effects.append(SimpleGoal(introduced_self=True))
        yield action



agent = GoapAgent()
agent.add_action(PrintAction())

friendly_goal = SimpleGoal(introduced_self=True)
agent.add_goal(friendly_goal)

env = Environment()
env.add(agent)

env.update(1)


