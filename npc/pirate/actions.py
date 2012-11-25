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
    for precept in memory.of_class(PositionPrecept):
        if precept.entity is entity:
            return precept.position


class MoveAction(ActionContext):
    def update(self, time):
        super(MoveAction, self).update(time)
        if self.caller.position[1] == self.endpoint:
            self.finish()
        else:
            env = self.caller.environment
            path = env.pathfind(self.caller.position[1], self.endpoint)
            path.pop() # this will always the the starting position
            env.move(self.caller, (env, path.pop()))

    def setStartpoint(self, pos):
        self.startpoint = pos
 
    def setEndpoint(self, pos):
        self.endpoint = pos


class PickupAction(CalledOnceContext):
    """
    take an object from the environment and place it into your inventory
    """
    pass


class DrinkRunAction(ActionContext):
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

        for precept in memory.of_class(PositionPrecept):
            if precept.entity is caller or precept.position in visited:
                continue

            visited.append(precept.position)

            action = MoveAction(caller)
            action.setEndpoint(precept.position[1])
            action.effects.append(PositionGoal(caller, precept.position))
            yield action

exported_actions.append(move_to_entity)


class pickup(ActionBuilder):
    def get_actions(self, caller, memory):
        """
        return list of actions that will pickup an item at caller's position
        """
        here = get_position(caller, memory) 

        for precept in memory.of_class(PositionPrecept):
            if here == precept.position and precept.entity is not caller:
                action = PickupAction(caller)
                action.effects.append(HasItemGoal(precept.entity))
                yield action 

exported_actions.append(pickup)



class drink_rum(ActionBuilder):
    """
    drink rum that is in caller's inventory
    """

    def make_action(self, caller, tag, memory):
        a = drink_rum_action(caller)
        a.effects.append(SimpleGoal(is_drunk=True))
        a.effects.append(EvalGoal("charisma = charisma + 10"))

        return a

    def get_actions(self, caller, memory):
        """
        return list of actions that will drink rum from player's inv
        """

        a = []
        for precept in memory.of_class(PositionPrecept):
            if precept.position[0] == caller:
                if DEBUG: print "[drink rum] 1 {}".format(tag)
                if tag['obj'].name=="rum":
                    if DEBUG: print "[drink rum] 2 {}".format(tag)
                    a.append(self.make_action(caller, tag, memory))

        return a

exported_actions.append(drink_rum)

