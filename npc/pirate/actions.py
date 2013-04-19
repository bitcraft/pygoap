"""
This is an example module for programming actions for a pyGOAP agent.

The module must contain a list called "exported_actions".  This list should
contain any classes that you would like to add to the planner.

To make it convienent, I have chosen to add the class to the list after each
declaration, although you may choose another way.
"""

from pygoap.actions import *
from pygoap.goals import *


def get_position(entity, memory):
    """
    Return the position of [entity] according to memory.
    """
    for pct in memory.of_class(PositionPrecept):
        if pct.entity is entity:
            return pct.position


class LookAction(CalledOnceContext):
    def enter(self):
        print "LOOKING"
        self.parent.environment.look(self.parent)


class MoveAction(ActionContext):
    def update(self, time):
        print self, "moving?"

    def setStartpoint(self, pos):
        self.startpoint = pos
 
    def setEndpoint(self, pos):
        self.endpoint = pos


class PickupAction(CalledOnceContext):
    """
    take an object from the environment and place it into your inventory
    """
    pass


class DrinkRumAction(ActionContext):
    def start(self):
        self.caller.drunkness = 1
        super(drink_rum, self).start()
        
    def update(self, time):
        if self.valid():
            self.caller.drunkness += 1
            if self.caller.drunkness == 5:
                self.finish()
        else:
            self.fail()

    def finish(self):
        super(drink_rum, self).finish()



exported_actions = []

class move_to_entity(ActionBuilder):
    """
    return a list of action that this caller is able to move with

    you MUST have a mechanism that depletes a counter when moving, otherwise
    the planner will loop lessly moving the agent around to different places.
    """

    def get_actions(self, caller, memory):
        visited = []

        for pct in memory.of_class(PositionPrecept):
            if pct.entity is caller or pct.position in visited:
                continue

            visited.append(pct.position)

            action = MoveAction(caller)
            action.setEndpoint(pct.position[1])
            action.effects.append(PositionGoal(caller, pct.position))
            yield action

exported_actions.append(move_to_entity)


class pickup(ActionBuilder):
    def get_actions(self, caller, memory):
        """
        return list of actions that will pickup an item at caller's position
        """
        here = get_position(caller, memory) 

        for pct in memory.of_class(PositionPrecept):
            if here == pct.position and pct.entity is not caller:
                action = PickupAction(caller)
                action.effects.append(HasItemGoal(pct.entity))
                yield action 

exported_actions.append(pickup)


class drink_rum(ActionBuilder):
    """
    drink rum that is in caller's inventory
    """

    def get_actions(self, caller, memory):
        for pct in memory.of_class(PositionPrecept):
            if pct.position[0] == 'self' and pct.entity.name == "rum":
                action = DrinkRumAction(caller)
                action.effects.append(SimpleGoal(is_drunk=True))
                action.effects.append(EvalGoal("charisma = charisma + 10"))
                yield action


exported_actions.append(drink_rum)



class look(ActionBuilder):
    def get_actions(self, caller, memory):
        action = LookAction(caller)
        action.effects.append(SimpleGoal(aware=True))
        yield action
        

exported_actions.append(look)
