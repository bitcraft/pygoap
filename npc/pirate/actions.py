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
        self.parent.environment.look(self.parent)


class MoveAction(ActionContext):
    def enter(self):
        self.path = self.parent.environment.pathfind(self.startpoint,
                    self.endpoint)

        # remove the first node, which is the starting node
        self.path.pop()

    def update(self, time):
        if self.path:
            pos = self.path.pop()
            self.parent.environment.set_position(self.parent,
                    (self.parent.environment, pos))

        if not self.path:
            self.finish()

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
    def enter(self):
        print "drinking!"
        self.drunkness = 1
        
    def update(self, time):
        self.drunkness += 1
        if self.drunkness >= 3:
            self.parent.set_condition('drunk', True)
            self.finish()

exported_actions = []


###  ACTION BUILDERS
###

class move_to_entity(ActionBuilder):
    """
    return a list of action that this caller is able to move with
    """

    def get_actions(self, caller, memory):
        here = get_position(caller, memory) 
        visited = []

        for pct in memory.of_class(PositionPrecept):
            if pct.entity is caller or pct.position in visited:
                continue

            visited.append(pct.position)

            action = MoveAction(caller)
            action.setStartpoint(here)
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
            #print "looking for rum", pct
            if pct.position[0] == 'self' and pct.entity.name == "rum":
                action = DrinkRumAction(caller)
                action.effects.append(SimpleGoal(is_drunk=True))
                #action.effects.append(EvalGoal("charisma = charisma + 10"))
                yield action


exported_actions.append(drink_rum)


class look(ActionBuilder):
    def get_actions(self, caller, memory):
        action = LookAction(caller)
        action.effects.append(SimpleGoal(aware=True))
        yield action
        

exported_actions.append(look)
