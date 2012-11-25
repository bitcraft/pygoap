from blackboard import MemoryManager
from actionstates import *
from actions import *

from heapq import heappop, heappush, heappushpop
from itertools import permutations
import logging
import sys

debug = logging.debug



def get_children(caller, parent, builders, dupe_parent=False):
    """
    return every other action on this branch that has not already been used
    """
    def keep_node(node):
        keep = True
        node0 = node.parent
        while not node0.parent == None:
            if node0.parent == node:
                keep = False
                break
            node0 = node0.parent

        return keep

    def get_actions2(builders, caller, parent):
        for builder in builders:
            for action in builder(caller, parent.memory):
                yield PlanningNode(parent, action)

    def get_actions(builders, caller, parent):
        for builder in builders:
            for action in builder(caller, parent.memory):
                node = PlanningNode(parent, action)
                if keep_node(node): 
                    yield node

    #print list(permutations(get_actions2(builders, caller, parent)))

    return get_actions(builders, caller, parent) 


def calcG(node):
    cost = node.cost
    while not node.parent == None:
        node = node.parent
        cost += node.cost 
    return cost


class PlanningNode(object):
    """
    """

    def __init__(self, parent, action, memory=None):
        self.parent = parent
        self.action = action
        self.memory = MemoryManager()
        self.delta = MemoryManager()
        #self.cost = action.calc_cost()
        self.cost = 1
        self.g = calcG(self)
        self.h = 1

        if parent:
            self.memory.update(parent.memory)

        elif memory:
            self.memory.update(memory)

        action.touch(self.memory)
        action.touch(self.delta)

    def __eq__(self, other):
        if isinstance(other, PlanningNode):
            return self.delta == other.delta
        else:
            return False

    def __repr__(self):
        if self.parent:
            return "<PlanNode: '%s', cost: %s, p: %s>" % \
            (self.action.__class__.__name__,
                self.cost,
                self.parent.action.__class__.__name__)

        else:
            return "<PlanNode: '%s', cost: %s, p: None>" % \
            (self.action.__class__.__name__,
                self.cost)


def plan(caller, actions, start_action, start_memory, goal):
    """
    Return a list of actions that could be called to satisfy the goal.
    """

    # the pushback is used to limit node access in the heap
    pushback = None 
    keyNode = PlanningNode(None, start_action, start_memory)
    openlist = [(0, keyNode)]

    # the root can return a copy of itself, the others cannot
    # this allows the planner to produce plans that duplicate actions
    # this feature is currently on a hiatus
    return_parent = 0

    debug("[plan] solve %s starting from %s", goal, start_action)
    debug("[plan] memory supplied is %s", start_memory)

    success = False
    while openlist or pushback:

        # get the best node.
        if pushback is None:
            keyNode = heappop(openlist)[1]
        else:
            keyNode = heappushpop(openlist,
                (pushback.g + pushback.h, pushback))[1]
            pushback = None

        #debug("[plan] testing %s against %s", keyNode.action, keyNode.memory)

        # if our goal is satisfied, then stop
        #if (goal.satisfied(keyNode.memory)) and (return_parent == 0):
        if goal.test(keyNode.memory):
            success = True
            debug("[plan] successful %s", keyNode.action)
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
        while not keyNode.parent is None:
            keyNode = keyNode.parent
            path0.append(keyNode.action)

        return path0

    else:
        return []


