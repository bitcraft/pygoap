"""
This is an example module for programming actions for a pyGOAP agent.

The module must contain a list called "exported_actions".  This list should
contain any classes that you would like to add to the planner.

To make it convienent, I have chosen to add the class to the list after each
declaration, although you may choose another way.
"""

from pygoap.actions import *
from pygoap.goals import *


DEBUG = 0

def get_position(thing, bb):
    """
    get the position of the caller according to the blackboard
    """

    pos = None
    a = []

    tags = bb.read("position")
    tags.reverse()
    for tag in tags:
        if tag['obj'] == thing:
            pos = tag['position']
            a.append(tag)
            break

    if pos == None:
        raise Exception, "function cannot find position"

    return pos

exported_actions = []

class move(ActionBuilder):
    """
    you MUST have a mechanism that depletes a counter when moving, otherwise
    the planner will loop lessly moving the agent around to different places.
    """

    def get_actions(self, caller, bb):
        """
        return a list of action that this caller is able to move with
        """

        if not SimpleGoal(is_tired=True).test(bb):
            pos = caller.environment.can_move_from(caller, dist=30)
            return [ self.build_action(caller, p) for p in pos ]
        else:
            return []

    def build_action(self, caller, pos):
        a = move_action(caller)
        a.effects.append(PositionGoal(target=caller, position=pos))
        a.effects.append(SimpleGoal(is_tired=True))
        return a



class move_action(CallableAction):
    pass

exported_actions.append(move)


class look(CalledOnceAction):
    def start(self):
        self.caller.environment.look(self.caller)
        super(look, self).start()

#exported_actions.append(look)

class pickup(ActionBuilder):
    def get_actions(self, caller, bb):
        """
        return list of actions that will pickup an item at caller's position
        """

        caller_pos = get_position(caller, bb) 

        a = []
        for tag in bb.read("position"):
            if caller_pos == tag['position']:
                if not tag['obj'] == caller:
                    if DEBUG: print "[pickup] add {}".format(tag['obj'])
                    a.append(self.build_action(caller, tag['obj']))

        return a

    def build_action(self, caller, item):
        a = pickup_action(caller)
        a.effects.append(HasItemGoal(caller, item))
        return a

class pickup_action(CalledOnceAction):
    """
    take an object from the environment and place it into your inventory
    """
    pass

exported_actions.append(pickup)



class drink_rum(ActionBuilder):
    """
    drink rum that is in caller's inventory
    """

    def make_action(self, caller, tag, bb):
        a = drink_rum_action(caller)
        a.effects.append(SimpleGoal(is_drunk=True))
        a.effects.append(EvalGoal("charisma = charisma + 10"))

        return a

    def get_actions(self, caller, bb):
        """
        return list of actions that will drink rum from player's inv
        """

        a = []

        for tag in bb.read("position"):
            if tag['position'][0] == caller:
                if DEBUG: print "[drink rum] 1 {}".format(tag)
                if tag['obj'].name=="rum":
                    if DEBUG: print "[drink rum] 2 {}".format(tag)
                    a.append(self.make_action(caller, tag, bb))

        return a


class drink_rum_action(CallableAction):
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

exported_actions.append(drink_rum)



class idle(ActionBuilder):
    def get_actions(self, caller, bb):
        a = idle_action(caller)
        a.effects = [SimpleGoal(is_idle=True)]
        return [a]

class idle_action(CalledOnceAction):
    builder = idle

exported_actions.append(idle)


class buy_rum(CalledOnceAction):
    def setup(self):
        self.prereqs.append(NeverValidGoal())

#exported_actions.append(buy_rum)



class steal_rum(CalledOnceAction):
    def setup(self):
        self.effects.append(HasItemGoal(name="rum"))

#exported_actions.append(steal_rum)



class steal_money(CalledOnceAction):
    def setup(self):    
        self.effects.append(EvalGoal("money = money + 25"))

#exported_actions.append(steal_money)



class sell_loot(CalledOnceAction):
    def setup(self):
        self.prereqs.append(HasItemGoal(name="loot"))
        self.effects.append(EvalGoal("money = money + 100"))

#exported_actions.append(sell_loot)



class get_loot(CalledOnceAction):
    def setup(self):
        self.effects.append(HasItemGoal(name="loot"))

#exported_actions.append(get_loot)



class go_sailing(CalledOnceAction):
    pass

#exported_actions.append(go_sailing)



class beg_money(CalledOnceAction):
    def setup(self):
        self.effects.append(EvalGoal("money = money + 5"))

#exported_actions.append(beg_money)



class woo_lady(CalledOnceAction):
    def setup(self):
        self.prereqs = [
            EvalGoal("money >= 100"),
            EvalGoal("charisma >= 5"),
            PositionGoal(max_dist=3, name="wench")]

        self.effects = [
            EvalGoal("money = money - 100")]

#exported_actions.append(woo_lady)



class get_laid(CalledOnceAction):
    pass

#exported_actions.append(get_laid)



class do_dance(CalledOnceAction):
    def setup(self):
        self.effects.append(EvalGoal("money = money + 25"))

#exported_actions.append(do_dance)

