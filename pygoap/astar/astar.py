# -*- coding: utf-8 -*-

"""
Copyright 2010, Leif Theden

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
what is LPA?

    the path is recalculated as the costs of nodes change. and has a lower
    requirement to reconfigure the path than a*.  should be used, though
    memory is an issue

what is d*

    the map is not known fully (or at all). updating the path has a lower cost
    than starting a new search everytime there is new information

###################

features:
    automatic building of node objects
    automatic caching
    customisable hooks
    finding paths via hook or method call
    pushback for better faster heap access

generally, using this module hides the complexities of pathfinding, and
is designed to be integrated into games.  more textbook like implimentations
exist, but the degisn of this is to be flexible, extendable, and sweet.

usage:

provide the constructor with a function that returns a list of tuples:
    reference to an obj
    cost of the obj
    a huerstic to speed up pathfinding
    [(ref, cost, h),...]

call findpath() for a list, or tick() to spread out the load.


notes:

i've considered it alot, but rewriting as a generator will not work since
its possible that the previous values we've given will not be used.

function call overhead kills here.  if you are worried about speed, some
functions could be hard coded to save some cycles.  of course, you will lose
some flexability when trying to subclass this.  decisions, decisions...

just send an object and a ref to a method that will return a list of
surrounding objects, this will take care of everything else.
the returned list can be 'popped' in the same order to travel the path

the function that return surrounding nodes needs to return the h
so the map needs to have this information

"""

__version__ = ".021"

from heapq import heappop, heappush
from collections import deque


# old versions of python wont have heappushpop
# provide somthing similiar from utilities
from heapq import heappushpop


DEBUG = False

class PathfindingError(Exception):
    pass

def trace_path(start):
    path = []
    node = start

    while node.parent != None:
        path.append(node.obj)
        node = node.parent

    path.append(node.obj)
    path.reverse()
    return Path(path, calcG(start))

def calcG(node):
    if node.parent != None:
        return node.cost + node.parent.g
    else:
        return node.cost

class Path(list):
    def __init__(self, path, cost):
        self[:] = list(path)
        self.cost = cost

    def __str__(self):
        return "{0}, c:{1}".format(super(Path,self).__str__(), self.cost)

class PathfindingNode(object):
    """
    Generic Node used by the pathfinder.

    Each node can have multiple costs associated with them.
    When comparing paths, the path with the total cost will be
    returned.

    "cost" = "G" in A* terms
    """

    __slots__ = ['obj','cost','closed','parent', 'g', 'h']

    def __init__(self, parent, obj=None, cost=1, h=0):
        self.parent = parent
        self.obj = obj
        self.cost = cost
        self.g = calcG(self)
        self.h = h
        self.closed = False

    def __repr__(self):
        try:
            return "<Node=obj: {0}, c:{1}, p:{2}>".format\
            (self.obj, self.cost, self.g)
        except AttributeError:
            return "<Node=obj: {0}, c:{1}, p:None>".format\
            (self.obj, self.cost)

class Astar(object):
    node_factory = PathfindingNode

    def __init__(self, start, finish, surr_func, reverse=True):
        self.start = start
        self.finish = finish
        self.surr_func = surr_func

        # the pushback here is used to speed up heap access
        self._pb = None
        self._node_cache = {}
        self._heap = []

        self.build_node(None, start, 0, 0)

    def _get_best_node(self):
        try:
            if self._pb == None:
                return heappop(self._heap)[1]
            else:
                node = heappushpop(self._heap, (self._pb.g + self._pb.h,self._pb))[1]
                self._pb = None
                return node
        except:
            raise PathfindingError

    def _add_node(self, node):
        if self._pb == None:
            self._pb = node
        else:
            heappush(self._heap, (self._pb.g + self._pb.h,self._pb))
            self._pb = node

    def build_node(self, parent, obj, cost, h):
        # override for special cases
        node = self.node_factory(parent, obj, cost, h)
        self._add_node(node)
        self._node_cache[obj] = node

        if DEBUG: print "A*:\tbuild {0}".format(node)

        return node

    def check_complete(self, node):
        # override for special cases
        return node.obj == self.finish

    def check_neighbor(self, neighbor):
        # override for special cases
        return not neighbor.closed

    def tick(self):
        keyNode = self._get_best_node()
        keyNode.closed = True

        # expose our current keynode for subclasses
        self.keyNode = keyNode

        if DEBUG:
            print "A*:\ttick {0}".format(keyNode)

        for obj, cost, h in self.surr_func(keyNode.obj, self.finish):
            try:
                neighbor = self._node_cache[obj]
            except KeyError:
                # neighbor is neither open nor closed
                neighbor = self.build_node(keyNode, obj, cost, h)
                continue

            if self.check_complete(neighbor):
                neighbor.parent = keyNode
                self.path = trace_path(self._node_cache[neighbor.obj])
                return self.path

            if self.check_neighbor(neighbor):
                # neighbor is open
                possG = keyNode.g + neighbor.cost

                if (possG < neighbor.g):
                    self._heap.remove((neighbor.g + neighbor.h, neighbor))
                    neighbor.parent = keyNode
                    neighbor.g = calcG(neighbor)
                    self._add_node(neighbor)
            else:
                # neighobor is closed
                continue

    def findpath(self):
        """
        findpath() will return a list of objs, not pathfinding nodes.
        """

        while (self.tick() == None): pass
        return self.path

if __name__ == "__main__":
    import mapdb
    import cProfile
    import pstats
    import sys

    mymap = mapdb.TestDB()

    nodeRef={}
    for node in mymap.get_nodes():
        nodeRef[node.id] = node

    start = nodeRef['Z']
    end = nodeRef['Q']

    """
    times:
    10000 reps

    8.978
    5.576
    4.34
    2.727
    2.687
    5.339 (runs correctly)
    """

    astar = Astar(start, end, mymap.get_surrounding3)
    path = astar.findpath()

    for node in path:
        print node

    def doit():
        for x in xrange(10000):
            astar = Astar(start, end, mymap.get_surrounding3)
            path = astar.findpath()

    cProfile.run('doit()', "astar.prof")

    p = pstats.Stats("astar.prof")
    p.strip_dirs()
    p.sort_stats('time').print_stats(10)
