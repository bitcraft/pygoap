"""
Goals in the context of a pyGOAP agent give the planner some direction when
planning.  Goals are known to the agent and are constantly monitored and
evaluated.  The agent will attempt to choose the most relevant goal for it's
state (determined by the blackboard) and then the planner will determine a
plan for the agent to follw that will (possibly) satisfy the chosen goal.

See the modules effects.py and goals.py to see how these are used.

The Goal class has a lot of uses in the engine, see the pirate's actions for
an idea of what they are used for. Not all of the goals here are used/tested.

test() should return a float from 0-1 on how successful the action would be
if carried out with the given state of the bb.

touch() should modify a bb in some meaningful way as if the action was
finished successfully.
"""

from planning import GoalBase
from blackboard import Tag
import sys


DEBUG = 0

class SimpleGoal(GoalBase):
    """
    Goal that uses a dict to match precepts stored on a bb.
    """

    def test(self, bb):
        #f = [ k for (k, v) in self.kw.items() if v == False]

        for tag in bb.read():

            if tag == self.kw:
                return 1.0

        return 0.0

    def touch(self, bb):
        bb.post(Tag(**self.kw))

    def __repr__(self):
        return "<{}=\"{}\">".format(self.__class__.__name__, self.kw)


class EvalGoal(GoalBase):
    """
    uses what i think is a somewhat safe way of evaluating python statements.

    feel free to contact me if you have a better way
    """

    def test(self, bb):

        condition = self.args[0]

        # this only works for simple expressions
        cmpop = (">", "<", ">=", "<=", "==")

        i = 0
        index = 0
        expr = condition.split()
        while index == 0:
            try:
                index = expr.index(cmpop[i])
            except:
                i += 1
                if i > 5: break

        try:
            side0 = float(eval(" ".join(expr[:index]), bb))
            side1 = float(eval(" ".join(expr[index+1:]), bb))
        except NameError:
            return 0.0

        cmpop = cmpop[i]

        if (cmpop == ">") or (cmpop == ">="):
            if side0 == side1:
                return 1.0
            elif side0 > side1:
                v = side0 / side1
            elif side0 < side1:
                if side0 == 0:
                    return 0.0
                else:
                    v = 1 - ((side1 - side0) / side1)

        if v > 1: v = 1.0
        if v < 0: v = 0.0

        return v

    def touch(self, bb):
        def do_it(expr, d):

            try:
                exec expr in d
            except NameError as detail:
                # get name of missing variable
                name = detail[0].split()[1].strip('\'')
                d[name] = 0
                do_it(expr, d)

            return d

        d = {}
        d['__builtins__'] = None
        d = do_it(self.args[0], d)

        # the bb was modified
        bb.post(Tag(kw=d))

        return True


class AlwaysValidGoal(GoalBase):
    """
    Will always be valid.
    """

    def test(self, bb):
        return 1.0

    def touch(self, bb, tag):
        pass



class NeverValidGoal(GoalBase):
    """
    Will never be valid.
    """

    def test(self, bb):
        return 0.0

    def touch(self, bb, tag):
        pass



class PositionGoal(GoalBase):
    """
    This validator is for finding the position of objects.
    """

    def test(self, bb):
        """
        search memory for last known position of the target if target is not
        in agent's memory return 0.0.

        do pathfinding and determine if the target is accessable
            - if not return 0.0

        determine the distance required to travel to the target
        return 1.0 if the target is reachable
        """

        target = None
        target_position = None
        tags = bb.read("position")

        if DEBUG: print "[PositionGoal] testing {}".format(self.kw)

        for tag in tags:
            target = tag['obj']
            for k, v in self.kw.items():
                try:
                    value = getattr(target, k)
                except AttributeError:
                    continue

                if not v == value:
                    continue

                target_position = tag['position']
                break
            else:
                continue
            break

        if target_position:
            if DEBUG: print "[PositionGoal] {} {}".format(self.kw['owner'], target)
            return 1.0

            d = distance(position, target_position)
            if d > self.dist:
                return (float(self.dist / d)) * float(self.dist)
            elif d <= self.dist:
                return 1.0
            else:
                return 0.0


    def touch(self, bb):

        # this needs to be the same as what handle_precept() of an agent
        # would post if it had recv'd this from the environment
        tag = Tag(obj=self.kw['target'],
                position=self.kw['position'])

        bb.post(tag)

class HasItemGoal(GoalBase):
    """
    returns true if item is in inventory (according to bb)

    when creating instance, 'owner' must be passed as a keyword.
    its value can be any game object that is capable of holding an object

    NOTE: testing can be true to many different objects,
          but touching requires a specific object to function

    any other keyword will be evaluated against tags in the bb passed.
    """

    def __init__(self, owner, target=None, **kwargs):
        super(HasItemGoal, self).__init__(self)

        self.owner = owner
        self.target = None

        if target:
            self.target = target
        else:
            try:
                self.target = kwargs['target']
            except KeyError:
                pass

        if (self.target == None) and (kwargs == {}):
            raise Exception, "HasItemGoal needs more information"
            

    def test(self, bb):
        for tag in bb.read("position"):
            if (tag['position'][0] == self.owner) and \
            tag['obj'] == self.target:
                return 1.0
        
        return 0.0

    def touch(self, bb):
        # this has to be the same tag that the agent would add to its bb
        tag = Tag(obj=self.target, position=(self.owner, 0))

        if DEBUG: print "[HasItem] {} touch {}".format(self, tag)

        bb.post(Tag(obj=self.target, position=(self.owner, 0)))

