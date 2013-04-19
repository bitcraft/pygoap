from memory import MemoryManager
from actionstates import *
from actions import *

from heapq import heappop, heappush, heappushpop
from itertools import permutations, chain
import logging
import sys

debug = logging.debug



def get_children(parent0, parent, builders):
    def get_used_class(node):
        while node.parent is not None:
            yield node.builder
            node = node.parent

    used_class = set(get_used_class(parent))

    for builder in builders:
        if builder in used_class:
            continue

        for action in builder(parent0, parent.memory):
            node = PlanningNode(parent, builder, action)
            yield node


def calcG(node):
    cost = node.cost
    while not node.parent == None:
        node = node.parent
        cost += node.cost 
    return cost


class PlanningNode(object):
    """
    """

    def __init__(self, parent, builder, action, memory=None):
        self.parent = parent
        self.builder = builder
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


def plan(parent, builders, start_action, start_memory, goal):
    """
    Return a list of builders that could be called to satisfy the goal.
    Cannot duplicate builders in the plan
    """

    # the pushback is used to limit node access in the heap
    pushback = None 
    keyNode = PlanningNode(None, None, start_action, start_memory)
    openlist = [(0, keyNode)]
    closedlist = []

    debug("[plan] solve %s starting from %s", goal, start_action)
    debug("[plan] memory supplied is %s", start_memory)

    success = False
    while openlist or pushback:

        # get the best node and remove it from the openlist
        if pushback is None:
            keyNode = heappop(openlist)[1]
        else:
            keyNode = heappushpop(openlist,
                (pushback.g + pushback.h, pushback))[1]
            pushback = None
    
        # if our goal is satisfied, then stop
        if goal.test(keyNode.memory):
            success = True
            debug("[plan] successful %s", keyNode.action)
            break

        for child in get_children(parent, keyNode, builders):
            if child in openlist:
                possG = keyNode.g + child.cost
                if (possG < child.g):
                    child.parent = keyNode
                    child.g = calcG(child)
                    # TODO: update the h score
            else:
                # add node to our openlist, using pushpack if needed
                if pushback is None:
                    heappush(openlist, (child.g + child.h, child))
                else:
                    heappush(openlist, (pushback.g + pushback.h, pushback))
                pushback = child

    if success:
        path = [keyNode.action]
        while keyNode.parent is not None:
            path.append(keyNode.action)
            keyNode = keyNode.parent

        return path

    else:
        return []


