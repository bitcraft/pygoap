from blackboard import Blackboard
from heapq import heappop, heappush, heappushpop
import sys



DEBUG = 0

def get_children(caller, parent, actions, dupe_parent=False):
    """
    return every other action on this branch that has not already been used
    """

    def keep_node(node):
        # verify node is ok by making sure it is not duplicated in it's branch

        keep = True

        node0 = node.parent
        while not node0.parent == None:
            if node0.parent == node:
                keep = False
                break
            node0 = node0.parent

        return keep

    children = []

    if DEBUG: print "[plan] actions: {}".format([a for a in actions])

    for a in actions:
        if DEBUG: print "[plan] checking {}".format(a)
        for child in a.get_actions(caller, parent.bb):
            node = PlanningNode(parent, child)

            if keep_node(node): 
                #if DEBUG: print "[plan] got child {}".format(child)
                children.append(node)
                
    return children


def calcG(node):
    cost = node.cost
    while not node.parent == None:
        node = node.parent
        cost += node.cost 
    return cost


class PlanningNode(object):
    """
    each node has a copy of a bb (self.bb) in order to simulate a plan.
    """

    def __init__(self, parent, action, bb=None):
        self.parent = parent
        self.action = action
        self.bb = Blackboard()
        self.delta = Blackboard()
        #self.cost = action.calc_cost()
        self.cost = 1
        self.g = calcG(self)
        self.h = 1

        if not parent == None:
            self.bb.update(parent.bb)

        elif not bb == None:
            self.bb.update(bb)

        action.touch(self.delta)
        self.bb.update(self.delta)

    def __eq__(self, other):
        if isinstance(other, PlanningNode):
            #if DEBUG: print "[cmp] {} {}".format(self.delta.memory, other.delta.memory)
            return self.delta == other.delta
        else:
            return False

    def __repr__(self):
        try:
            return "<PlanNode: '%s', cost: %s, p: %s>" % \
            (self.action.__name__,
                self.cost,
                self.parent.action.__class__.__name__)

        except AttributeError:
            return "<PlanNode: '%s', cost: %s, p: None>" % \
            (self.action.__class__.__name__,
                self.cost)

class GoalBase(object):
    """
    Goals:
        can be satisfied.
        can be valid

    Goals, ActionPrereqs and ActionEffects are now that same class.  They share
    so much functionality and are so logically similar that they have been made
    into one class.

    The only difference is how they are used.  If a goal is used by the planner
    then that will be the final point of the plan.  if it is used in
    conjunction with an action, then it will function as a prereq.
    """

    def __init__(self, *args, **kwargs):
        try:
            self.condition = args[0]
        except IndexError:
            self.condition = None

        self.value = 1.0
        self.args = args
        self.kw = kwargs

        self.satisfied = self.test

    def touch(self, bb):
        if DEBUG: print "[debug] goal {} has no touch method".format(self)

    def test(self, bb):
        if DEBUG: print "[debug] goal {} has no test method".format(self)

    def get_relevancy(self, bb):
        """
        will return the "relevancy" value for this goal/prereq.

        as a general rule, the return value here should never equal
        what is returned from test()
        """

        if not self.test(bb): return self.value
        return 0.0       


    def self_test(self):
        """
        make sure the goal is sane
        """

        bb = Blackboard()
        self.touch(bb)
        assert self.test(bb) == True


    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)


class InstancedAction(object):
    """
    This action is suitable as a generic 'idling' action.
    """

    builder = None

    def __init__(self):
        self.state = None

    def touch(self, bb):
        if DEBUG: print "[debug] action {} has no touch method".format(self)

    def test(self, bb):
        if DEBUG: print "[debug] action {} has no test method".format(self)

    def __repr__(self):
        return self.__class__.__name__


def plan(caller, actions, start_action, start_blackboard, goal):
    """
    differs slightly from normal astar in that:
        there are no connections between nodes
        the state of the "map" changes as the nodes are traversed
        there is no closed list (behaves like a tree search)
        hueristics are not available

    this is not implied to be correct or effecient
    """

    # the pushback is used to limit node access in the heap
    pushback = None 
    success = False

    keyNode = PlanningNode(None, start_action, start_blackboard)

    openlist = [(0, keyNode)]

    # the root can return a copy of itself, the others cannot
    # this allows the planner to produce plans that duplicate actions
    # this feature is currently on a hiatus
    return_parent = 0

    if DEBUG: print "[plan] solve {} planning {}".format(goal, start_action)

    while openlist or pushback:

        # get the best node.
        if pushback == None:
            keyNode = heappop(openlist)[1]
        else:
            keyNode = heappushpop(
                openlist, (pushback.g + pushback.h, pushback))[1]

            pushback = None

        if DEBUG: print "[plan] testing action {}".format(keyNode.action)
        if DEBUG: print "[plan] against bb {}".format(keyNode.bb.read())

        # if our goal is satisfied, then stop
        #if (goal.satisfied(keyNode.bb)) and (return_parent == 0):
        if goal.test(keyNode.bb):
            success = True
            if DEBUG: print "[plan] successful {}".format(keyNode.action)
            break

        for child in get_children(caller, keyNode, actions, return_parent):
            if child in openlist:
                possG = keyNode.g + child.cost
                if (possG < child.g):
                    child.parent = keyNode
                    child.g = calcG(child)
                    # TODO: update the h score
            else:
                # add node to our openlist, using pushpack if needed
                if pushback == None:
                    heappush(openlist, (child.g + child.h, child))
                else:
                    heappush(openlist, (pushback.g + pushback.h, pushback))
                pushpack = child

        return_parent = 0

    if success:
        path0 = [keyNode.action]
        path1 = [keyNode]
        while not keyNode.parent == None:
            keyNode = keyNode.parent
            path0.append(keyNode.action)
            path1.append(keyNode)

        return True, path0

    else:
        return False, []


