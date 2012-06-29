from heapq import heappush, heappop, heappushpop, heapify
from collections import defaultdict

class Astar(object):
    pass


class Node(object):
    __slots__ = ['parent', 'x', 'y', 'g', 'h', 'f', 'is_closed']

    def __init__(self, pos=(0,0)):
        self.x, self.y = pos
        self.parent = None
        self.g = 0
        self.h = 0
        self.is_closed = 0

    def __eq__(self, other):
        try:
            return (self.x == other.x) and (self.y == other.y)
        except AttributeError:
            return False

    def __repr__(self):
        return "<Node: x={} y={}>".format(self.x, self.y)

def getSurrounding(node):
    return ((node.x-1, node.y-1), (node.x, node.y-1), (node.x+1, node.y-1), \
            (node.x-1, node.y),   (node.x+1, node.y), \
            (node.x-1, node.y+1), (node.x, node.y+1), (node.x+1, node.y+1))

def dist(start, finish):
    return abs(finish.x - start.x) + abs(finish.y - start.y)

def calcG(node):
    score=0
    score += node.g
    while not node.parent == None:
        node = node.parent
        score += node.g
    return score


def calcH(node, finish):
    # somehow factor in the cost of other nodes
    return abs(finish.x - node.x) + abs(finish.y - node.y)


def search(start, finish, factory):
    """perform basic a* search on a 2d map.
   
    Args:
        start:      tuple that defines the starting position
        finish:     tuple that defined the finish
        factory:    function that will return a Node object from a position

    Factory can return None, which means the area is not passable.
 
    """

    finishNode = factory(finish)
    startNode = factory(start)
    startNode.h = calcH(startNode, finishNode)

    # used to locate nodes in the heap and modify their f scores
    heapIndex = {}
    entry = [startNode.g + startNode.h, startNode]
    heapIndex[startNode] = entry

    openlist = [entry]

    nodeHash = {}
    nodeHash[start] = startNode

    while openlist:
        try:
            f, keyNode = heappop(openlist)
            while keyNode == None:
                f, keyNode = heappop(openlist)
        except IndexError:
            break
        else:
            del heapIndex[keyNode]

        if keyNode == finishNode:
            path = [(keyNode.x, keyNode.y)]
            while not keyNode.parent == None:
                keyNode = keyNode.parent
                path.append((keyNode.x, keyNode.y))
            return path

        keyNode.is_closed = 1

        for neighbor in getSurrounding(keyNode):
            try:
                node = nodeHash[neighbor]
            except KeyError:
                node = factory(neighbor)
                if node:
                    nodeHash[neighbor] = node
                    score = keyNode.g + dist(keyNode, node)
                    node.parent = keyNode
                    node.g = score
                    node.h = calcH(node, finishNode)
                    entry = [node.g + node.h, node]
                    heapIndex[node] = entry
                    heappush(openlist, entry)
            else:
                if not node.is_closed:
                    score = keyNode.g + dist(keyNode, node)
                    if score < node.g:
                        node.parent = keyNode
                        node.g = score
                        entry = heapIndex.pop(node)
                        entry[1] = None
                        newentry = [node.g + node.h, node]
                        heapIndex[node] = newentry
                        heappush(openlist, newentry)

    return []


def search_test(tests=1000):
    area = [[0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0]]

    def factory((x, y)):
        if x < 0 or y < 0:
            return None

        try:
            if area[y][x] == 0:
                node = Node((x, y))
                return node
            else:
                return None
        except IndexError:
            return None

    return search((0,0), (5,9), factory)


if __name__ == "__main__":
    print  search_test()

