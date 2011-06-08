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
this is a rewrite of my old goap library in an attempt to make
it less of a mess of classes and try to consolidate everything
into one class and to make it more event-based

the current plan is to have a subprocess monitoring the
environment and doing all the pygoap stuff in a seperate
process.

how to handle ai?  multiprocessing to get around the GIL in CPython.
why not threads?  because we are CPU restricted, not IO.

memory managers and blackboards should be related.
this will allow for expectations, since a memory can be simulated in the future

memory:
should be a heap
memory added will be wrapped with a counter
everytime a memory is fetched, the counter will be added
eventually, memories not being used will be removed
and the counters will be reset

memories should be a tree
if a memory is being added that is similiar to an existing memory,
then the existing memory will be updated, rather than replaced.

to keep memory usage down, goals and effects are only instanced once.
so, do not do anything crazy, like attempting to change a goal at runtime,
since it will effect avery agent that relies on it.

to handle idle actions:
    an idle action should have a very low cost associated with it
    the planner will then always choose this when there is nothing better to do


"""

from heapq import heappop, heappush
from collections import deque

import random
import sys
import traceback
import copy

# old versions of python wont have heappushpop
# provide somthing similiar from utilities
from heapq import heappushpop

ACTIONSTATE_NOT_STARTED = 0
ACTIONSTATE_FINISHED    = 1
ACTIONSTATE_RUNNING     = 2
ACTIONSTATE_PAUSED      = 3
ACTIONSTATE_BAILED      = 4
ACTIONSTATE_FAILED      = 5


DEBUG = False

def dlog(text):
    print text

class Precept(object):
    def __init__(self, *arg, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return "<Precept: %s>" % self.__dict__

def distance((ax, ay), (bx, by)):
    "The distance between two (x, y) points."
    return math.hypot((ax - bx), (ay - by))

def distance2((ax, ay), (bx, by)):
    "The square of the distance between two (x, y) points."
    return (ax - bx)**2 + (ay - by)**2

def clip(vector, lowest, highest):
    """Return vector, except if any element is less than the corresponding
    value of lowest or more than the corresponding value of highest, clip to
    those values.
    >>> clip((-1, 10), (0, 0), (9, 9))
    (0, 9)
    """
    return type(vector)(map(min, map(max, vector, lowest), highest))

class Environment(object):
    """Abstract class representing an Environment.  'Real' Environment classes
    inherit from this.
    The environment keeps a list of .objects and .agents (which is a subset
    of .objects). Each agent has a .performance slot, initialized to 0.
    """

    def __init__(self, things=[], agents=[], time=0):
        self.time   = time
        self.things = things
        self.agents = agents

        # TODO, if agents are passed, we need to init them, possibly
        # by sending the relivant precepts, (time, location, etc)

        self.action_que = []

    def default_location(self, object):
        """
        Default location to place a new object with unspecified location.
        """
        raise NotImplementedError

    def run(self, steps=1000):
        """
        Run the Environment for given number of time steps.
        """
        [ self.update(1) for step in xrange(steps) ]

    def add_thing(self, thing, location=None):
        """
        Add an object to the environment, setting its location. Also keep
        track of objects that are agents.  Shouldn't need to override this.
        """
        thing.location = location or self.default_location(thing)
        self.things.append(thing)

        # add the agent
        if isinstance(thing, GoapAgent):
                thing.performance = 0
                thing.environment = self
                self.agents.append(thing)

        # should update vision for all interested agents (correctly, that is)
        [ self.look(a) for a in self.agents if a != thing ]

    def update(self, time_passed):
        """
        * Update our time
        * Update actions that may be running
        * Update all of our agents
        * Add actions to the que
        """

        #for a in self.agents:
        #    print "agent:", a.blackboard.__dict__

        new_actions = []

        # update time
        self.time += time_passed

        self.action_que = [ a for a in self.action_que if a != None ]

        # update all the actions that may be running
        precepts = [ a.update(time_passed) for a in self.action_que ]
        precepts = [ p for p in precepts if p != None ]

        """
        # let agents know that they have finished an action
        new_actions.extend([ action.caller.handle_precept(
        Precept(sense="self", time=self.time, action=action))
        for action in self.action_que
        if action.state == ACTIONSTATE_FINISHED ])
        """


        # add the new actions
        self.action_que.extend(new_actions)
        self.action_que = [ a for a in self.action_que if a != None ]

        # remove actions that are completed
        self.action_que = [ a for a in self.action_que
            if a.state != ACTIONSTATE_FINISHED ]

        # send precepts of each action to the agents
        for p in precepts:
            actions = [ a.handle_precept(p) for a in self.agents ]
            self.action_que.extend([ a for a in actions if a != None ])
        
        # let all the agents know that time has passed
        t = Precept(sense="time", time=self.time) 
        self.action_que.extend([ a.handle_precept(t) for a in self.agents ])

        # this is a band-aid until there is a fixed way to
        # manage actions returned from agents
        self.action_que = [ a for a in self.action_que if a != None ]

        # start any actions that are not started
        [ action.start() for action in self.action_que if action.state == ACTIONSTATE_NOT_STARTED ]

class Pathfinding2D(object):
    def get_surrounding(self, location):
        """
        Return all locations around this one.
        """

        x, y = location
        return ((x-1, y-1), (x-1, y), (x-1, y+1), (x, y-1), (x, y+1),
                (x+1, y-1), (x+1, y), (x+1, y+1))
                
    def calc_h(self, location1, location2):
        return distance(location1, location2)

class XYEnvironment(Environment, Pathfinding2D):
    """
    This class is for environments on a 2D plane, with locations
    labelled by (x, y) points, either discrete or continuous.  Agents
    perceive objects within a radius.  Each agent in the environment
    has a .location slot which should be a location such as (0, 1),
    and a .holding slot, which should be a list of objects that are
    held
    """

    def __init__(self, width=10, height=10):
        super(XYEnvironment, self).__init__()
        self.width = width
        self.height = height

    def look(self, caller, direction=None, distance=None):
        """
        Simulate vision.

        In normal circumstances, all kinds of things would happen here,
        like ray traces.  For now, assume all objects can see every
        other object
        """
        a = [ caller.handle_precept(
            Precept(sense="sight", thing=t, location=t.location)) 
            for t in self.things if t != caller ] 

        for action in a:
            if isinstance(action, list):
                self.action_que.extend(action)
            else:
                self.action_que.append(action)

    def objects_at(self, location):
        """
        Return all objects exactly at a given location.
        """
        return [ obj for obj in self.things if obj.location == location ]

    def objects_near(self, location, radius):
        """
        Return all objects within radius of location.
        """
        radius2 = radius * radius
        return [ obj for obj in self.things  
                if distance2(location, obj.location) <= radius2 ]

    def default_location(self, thing):
        return (random.randint(0, self.width), random.randint(0, self.height))

def get_exception():
    cla, exc, trbk = sys.exc_info()
    return traceback.format_exception(cla, exc, trbk)

class PyEval(object):
    """
    A safer way to evaluate strings.

    probably should do some preprocessing to make sure its really safe
    NOTE: might modify the dict bassed to it. (not really tested)
    """

    def make_dict(self, bb=None):
        safe_dict = {}

        # clear out builtins
        safe_dict["__builtins__"] = None

        if bb != None:
            # copy the dictionaries
            for tag in bb.tags():
                safe_dict[tag] = bb.read(tag)

        return safe_dict

    # mostly for prereq's
    def do_eval(self, expr, bb):
        d = self.make_dict(bb)

        #print "EVAL:", expr
        try:
            result = eval(expr, d)
            return result
        except NameError:
            # we are missing a value we need to evaluate the expression
            return 0

    # mostly for effect's
    def do_exec(self, expr, bb):
        d = self.make_dict(bb)

        #print "EXEC:", expr

        try:
            # a little less secure
            exec expr in d

        #except NameError as detail:
            # missing a value needed for the statement
            # we make a default value here, but really we should ask the agent
            # if it knows that to do with this name, maybe it knows....
    
            # get name of missing variable
        #    name = detail[0].split()[1].strip('\'')
        #    d[name] = 0
        #    exec self.expr in d

        except NameError:
            detail = get_exception()
            name = detail[3].split('\'')[1]
            d[name] = 0
            exec expr in d

        # the bb was modified
        for key, value in d.items():
            if key[:2] != "__":
                bb.post(key, value)

        return True

    def measured_eval(self, expr_list, bb, goal_expr):
        """
        do a normal exec, but compare the results
        of the expr and return a fractional value
        that represents how effective the expr is
        """
       
        # prepare our working dict 
        d0 = self.make_dict(bb)

        # build our test dict by evaluating each expression
        for expr in exec_list:
            # exec the expression we are testing
            finished = False
            while finished == False:
                finished = True
                try:
                    exec exec_expr in d0
                except NameError as detail:
                    finished = False
                    name = detail[0].split()[1].strip('\'')
                    d0[name] = 0

        return self.cmp_dict(self, d0, goal_expr)

    def cmp_bb(self, d, goal_expr):

        # this only works for simple expressions
        cmpop = (">", "<", ">=", "<=", "==")

        i = 0
        index = 0
        expr = goal_expr.split()
        while index == 0:
            try:
                index = expr.index(cmpop[i])
            except:
                i += 1
                if i > 5: break

        try:
            side0 = float(eval(" ".join(expr[:index]), d))
            side1 = float(eval(" ".join(expr[index+1:]), d))
        except NameError:
            return float(0)

        cmpop = cmpop[i]

        if (cmpop == ">") or (cmpop == ">="):
            if side0 == side1:
                v = 1.0
            elif side0 > side1:
                v = side0 / side1
            elif side0 < side1:
                if side0 == 0:
                    v = 0
                else:
                    v = 1 - ((side1 - side0) / side1)

        if v > 1: v = 1.0
        if v < 0: v = 0.0

        return v 

    def cmp_bb2(self, d, goal_expr):

        # this only works for simple expressions
        cmpop = (">", "<", ">=", "<=", "==")

        i = 0
        index = 0
        expr = goal_expr.split()
        while index == 0:
            try:
                index = expr.index(cmpop[i])
            except:
                i += 1
                if i > 5: break

        try:
            side0 = float(eval(" ".join(expr[:index]), d))
            side1 = float(eval(" ".join(expr[index+1:]), d))
        except NameError:
            return float(0)

        cmpop = cmpop[i]

        #side0, side1 = sorted((side0, side1))i

        if (cmpop == ">") or (cmpop == ">="):
            if side0 == 0: return side1
            v = 1 - ((side1 - side0) / side1)
        elif (cmpop == "<") or (cmpop == "<="):
            if side1 == 0: return side0
            v = (side0 - side1) / side0

        return v 


    def __str__(self):
            return "<PyEval: %s>" % self.expr
            return v0 >= v1

def calcG(node):
    cost = node.cost
    while node.parent != None:
        node = node.parent
        cost += node.cost 
    return cost

class PlanningNode(object):
    """
    each node has a copy of a bb (self.bb_delta) in order to simulate a plan.
    """

    def __init__(self, parent, obj, cost, h, bb=None, touch=True):
        self.parent = parent
        self.obj = obj
        self.cost = cost
        self.g = calcG(self)
        self.h = h

        if parent != None:
            self.bb_delta = copy.deepcopy(parent.bb_delta)
        elif bb != None:
            self.bb_delta = copy.deepcopy(bb)

        if touch: self.obj.touch(self.bb_delta)

    def __repr__(self):
        try:
            return "<Node: %s, c:%s, p:%s // %s>" % \
            (self.obj, self.cost, self.parent.obj, self.bb_delta.tags())
        except AttributeError:
            return "<Node: %s, c:%s, p:None // %s>" % \
            (self.obj, self.cost, self.bb_delta.tags())


class BasicActionPrereq(object):
    """
    Basic - just look for the presence of a tag on the bb.
    """

    def __init__(self, prereq):
        self.prereq = prereq

    def valid(self, bb):
        """
        Given the bb, can we run this action?
        """

        if (self.prereq == None) or (self.prereq == ""):
            return 1.0
        elif self.prereq in bb.tags():
            return 1.0
        else:
            return 0.0

    def __repr__(self):
        return "<BasicActionPrereq=\"%s\">" % self.prereq

class ExtendedActionPrereq(object):
    """
    These classes can use strings that evaluate variables on the blackboard.
    """

    def __init__(self, prereq):
        self.prereq = prereq

    def valid(self, bb):
        #e = PyEval()
        #return e.do_eval(self.prereq, bb)

        e = PyEval()
        d = copy.deepcopy(bb.tagDB)
        return e.cmp_bb(d, self.prereq)

    def __repr__(self):
        return "<ExtendedActionPrereq=\"%s\">" % self.prereq

class BasicActionEffect(object):
    """
    Basic - Simply post a tag with True as the value.
    """

    def __init__(self, effect):
        self.effect = effect

    def touch(self, bb):
        bb.post(self.effect, True)

    def __repr__(self):
        return "<BasicActionEffect=\"%s\">" % self.effect

class ExtendedActionEffect(object):
    """
    Extended - Use PyEval.
    """

    def __init__(self, effect):
        self.effect = effect

    def touch(self, bb):
        e = PyEval()
        bb = e.do_exec(self.effect, bb)

    def __repr__(self):
        return "<ExtendedActionEffect=\"%s\">" % self.effect


class GoalBase(object):
    """
    Goals:
        can be satisfied.
        can be valid
    """

    def __init__(self, s=None, r=None, value=1):
        self.satisfies = s
        self.relevancy = r
        self.value = value

    def get_relevancy(self, bb):
        """
        Return a float 0-1 on how "relevent" this goal is.
        Should be subclassed =)
        """
        raise NotImplementedError

    def satisfied(self, bb):
        """
        Test whether or not this goal has been satisfied
        """
        raise NotImplementedError

    def __repr__(self):
        return "<Goal=\"%s\">" % self.satisfies

class AlwaysSatisfiedGoal(GoalBase):
    """
    goal will never be satisfied.

    use for an idle condition
    """

    def get_relevancy(self, bb):
        return self.value

    def satisfied(self, bb):
        return 1.0

class SimpleGoal(GoalBase):
    """
    Uses flags on a blackboard to test goals.
    """

    def get_relevancy(self, bb):
        if self.satisfies in bb.tags():
            return 0.0
        else:
            return self.value

    def satisfied(self, bb):
        try:
            bb.read(self.satisfies)
        except KeyError:
            return 0.0
        else:
            return 1.0

class EvalGoal(GoalBase):
    """
    This goal will use PyEval objects to return
    a fractional value on how satisfied it is.

    These will enable the planner to execute
    a plan, even if it is not the best one.
    """

    def __init__(self, expr):
        self.expr = expr
        self.satisfies = "non"
        self.relevancy = 0
        self.value = 1

    def get_relevancy(self, bb):
        return .5

    def satisfied(self, bb):
        e = PyEval()
        d = copy.deepcopy(bb.tagDB)
        return e.cmp_bb(d, self.expr)

class SimpleActionNode(object):
    """
    action:
        has a prereuisite
        has a effect
        has a reference to a class to "do" the action

    this is like a singleton class, to cut down on memory usage

    TODO:
        use XML to store the action's data.
        names matched as locals inside the bb passed
    """

    def __init__(self, name, p=None, e=None):
        self.name = name
        self.prereqs = []
        self.effects = []

        # costs.
        self.time_cost = 0
        self.move_cost = 0

        self.start_func = None

        try:
            self.effects.extend(e)
        except:
            self.effects.append(e)

        try:
            self.prereqs.extend(p)
        except:
            self.prereqs.append(p)

    def set_action_class(self, klass):
        self.action_class = klass

    def valid(self, bb):
        """
        return a float from 0-1 that describes how valid this action is.

        validity of an action is a measurement of how effective the action
        will be if it is completed successfully.

        if any of the prereqs are not partially valid ( >0 ) then will
        return 0

        this value will be used in planning.

        for many actions a simple 0 or 1 will work.  for actions which
        modify numerical values, it may be useful to return a fractional
        value.
        """

        total = [ i.valid(bb) for i in self.prereqs ]
        if 0 in total: return 0
        return float(sum(total)) / len(self.prereqs)

    # this is run when the action is succesful
    # do something on the blackboard (varies by subclass)
    def touch(self, bb):
        [ i.touch(bb) for i in self.effects ]

    def __repr__(self):
        return "<Action=\"%s\">" % self.name

class CallableAction(object):
    """
    callable action class.

    subclass this class to implement the code side of actions.
    for the most part, "start" and "update" will be the most
    important methods to use
    """

    def __init__(self, caller, validator):
        self.caller    = caller
        self.validator = validator
        self.state     = ACTIONSTATE_NOT_STARTED

    def touch(self):
        """
        mark the parent's blackboard to reflect changes
        of a successful execution
        """
        self.validator.touch(self.caller.blackboard)
        
    def valid(self, do=False):
        """
        make sure the action is able to be started
        """
        return self.validator.valid(self.caller.blackboard)

    def start(self):
        """
        start running the action
        """
        self.state = ACTIONSTATE_RUNNING
        print self.caller, "is starting to", self.__class__.__name__

    def update(self, time):
        """
        actions which occur over time should implement
        this method.

        if the action does not need more that one cycle, then
        you should use the calledonce class
        """

    def fail(self, reason=None):
        """
        maybe what we planned to do didn't work for whatever reason
        """
        self.state = ACTIONSTATE_FAILED

    def bail(self):
        """
        stop the action without the ability to complete or continue
        """
        self.state = ACTIONSTATE_BAILED

    def finish(self):
        """
        the planned action was completed and the result
        is correct
        """
        if self.state == ACTIONSTATE_RUNNING:
            self.state = ACTIONSTATE_FINISHED
            self.touch()
            print self.caller, "is finshed", self.__class__.__name__

    def ok_finish(self):
        """
        determine if the action can finish now
        if cannot finish now, then the action
        will bail if it is forced to finish.
        """

        return self.state == ACTIONSTATE_FINISHED

class CalledOnceAction(CallableAction):
    """
    Is finished imediatly when started.
    """
    def start(self):
        # valid might return a value less than 1
        # this means that some of the prereqs are not
        # completely satisfied.
        # since we want everything to be completely
        # satisfied, we require valid == 1.
        if self.valid() == 1:
            CallableAction.start(self)
            CallableAction.finish(self)
        else:
            self.fail()

    def update(self, time):
        pass

class PausableAction(CallableAction):
    def pause(self):
        self.state = ACTIONSTATE_PAUSED

class Blackboard(object):
    """
    Memory device meant to be shared among Agents
    used for planning.
    data should not contain references to other objects
    references will cause the planning phase to use inconsistant data
    only store copies of objects

    blackboards that will be shared amongst agents will have to
    store the creating agent in the memories metadata

    class attribute access may be emulated and use a blackboard
    as the dict, instead of (self.__dict__)

    this will allow game object programming in a way that does not
    have to deal with details of the AI subsystem

    planning may introduce it's own variables onto the blackboard
    they will always have a "_goap_" prefix
    """

    def __init__(self):
        self.memory = []
        self.tagDB =  {}

    def tags(self):
        return self.tagDB.keys()

    def add(self, precept, tags=[]):
        self.memory.append(precept)
        for tag in tags:
            self.tagDB[tag] = precept

    def post(self, tag, value):
        self.tagDB[tag] = value

    def read(self, tag):
        return self.tagDB[tag]

    def search(self):
        return self.memory[:]

def time_filter(precept):
    if precept.sense == "time":
        return None
    else:
        return precept

def get_children(node, actions, duplicate_parent=False):

    # do some stuff to determine the children of this node
    if duplicate_parent:
        skip = []
    else:
        skip = [node.obj]

    node0 = node
    while node0.parent != None:
        node0 = node0.parent
        skip.append(node0.obj)

    children = []
    for a in [ i for i in actions if i not in skip]:
        score = a.valid((node.bb_delta))
        if score > 0: children.append((score, PlanningNode(node, a, 1, 1)))

    children.sort()

    return children

class GoapAgent(object):
    """
    AI thingy

    every agent should have at least one goal (otherwise, why use it?)
    """

    # this will set this class to listen for this type of precept
    interested = []

    def __init__(self):
        self.idle_timeout = 30
        self.blackboard   = Blackboard()

        self.current_action = None  # what action is being carried out now.
                                    # This must be a real action.
                                    # reccommened to use a idle action if nothin else

        self.goals = []             # all goals this instance will use
        self.invalid_goals = []     # goals that cannot be satisfied now
        self.filters = []           # filter precepts.  see the method of same name.
        self.actions = []           # all actions this npc can perform
        self.plan = []
        self.current_goal = None

        # handle time precepts intelligently
        self.filters.append(time_filter)

    def add_goal(self, goal):
        self.goals.append(goal)

    def remove_goal(self, goal):
        self.goals.remove(goal)

    def invalidate_goal(self, goal):
        self.invalid_goals.append(goal)

    def add_action(self, action):
        self.actions.append(action)

    def remove_action(self, action):
        self.actions.remove(action)

    def filter_precept(self, precept):
        """
        precepts can be put through filters to change them.
        this can be used to simulate errors in judgement by the agent.
        """

        for f in self.filters: precept = f(precept)
        return precept

    def handle_precept(self, precept):
        """
        do something with the precept
        the goals will be re-evaulated based on our new precept, if any

        also managed the plan, so this should be called occasionally
            # use time precepts

        """

        # give our filters a chance to change the precept
        precept = self.filter_precept(precept)

        # our filters may have caused us to ignore the precept
        if precept != None:
            self.blackboard.add(precept)
            self.invalid_goals = []

        return self.replan()

    def replan(self):
        if self.current_action == None: return None

        # use this oppurtunity to manage our plan
        if (self.plan == []) and (self.current_action.ok_finish()):
            self.plan = self.get_plan()

        if self.plan != []:

            if self.current_action.state == ACTIONSTATE_FINISHED:
                action = self.plan.pop()
                self.current_action = action.action_class(self, action)
                return self.current_action

            elif self.current_action.state == ACTIONSTATE_FAILED:
                self.plan = self.get_plan()

            elif self.current_action.state == ACTIONSTATE_RUNNING:
                if self.current_action.__class__ == self.plan[-1].action_class:
                    self.plan.pop()
                else:
                    if self.current_action.ok_finish():
                        self.current_action.finish()



    def get_plan(self):
        """
        pick a goal and plan if able to

        consolidated to remove function calls....
        """

        # UPDATE THE GOALS
        s = [(goal.get_relevancy(self.blackboard), goal)
            for goal in self.goals
            if goal not in self.invalid_goals]

        # SORT BY RELEVANCY
        s.sort(reverse=True)
        goals = [ i[1] for i in s ]
      
        for goal in goals:
            ok, plan = self.search_actions(self.actions, self.current_action.validator, self.blackboard, goal)
            if ok == False:
                print self, "cannot", goal
                self.invalidate_goal(goal)
            else:
                print self, "wants to", goal
                if len(plan) > 1: plan = plan[:-1]
                return plan

        return []

    def search_actions(self, actions, start_action, start_blackboard, goal):
        """
        actions must be a list of actions that can be used to satisfy the goal.
        start must be an action, blackboard represents current state
        goal must be a goal

        differs slightly from normal astar in that:
            there are no connections between nodes
            the state of the "map" changes as the nodes are traversed
            there is no closed list (behaves like a tree search)

        because of the state being changed as the algorithm progresses,
        state has be be saved with each node.  also, there will be several
        copies of the nodes, since they will have different state.

        sometime, i will implement different factors that will adjust the data
        given to reflect different situations with the agent.

        for example, it would be nice sometimes to search for a action set that
        is very short and the time required is also short.  this would be good
        for escapes.

        in other situations, if time is not a consideration, then maybe the best
        action set would be different.

        the tree thats built here will always have the same shape for each
        action map.  we just need to priotize it.
        """

        pushback = None     # the pushback is used to limit node access in the heap
        success = False

        keyNode = PlanningNode(None, start_action, 0, 0, start_blackboard, False)

        heap = [(0, keyNode)]

        # the root can return a copy of itself, the others cannot
        return_parent = 1

        while len(heap) != 0:

            # get the best node.  if we have a pushback, then push it and pop the best
            if pushback == None:
                keyNode = heappop(heap)[1]
            else:
                keyNode = heappushpop(heap, (pushback.g + pushback.h, pushback))[1]
                pushback = None

            # if our goal is satisfied, then stop
            #if (goal.satisfied(keyNode.bb_delta)) and (return_parent == 0):
            if goal.satisfied(keyNode.bb_delta):
                success = True
                break

            # go through each child and determine the best one
            for score, child in get_children(keyNode, actions, return_parent):
                if child in heap:
                    possG = keyNode.g + child.cost
                    if (possG < child.g):
                        child.parent = keyNode
                        child.g = calcG(child)
                        # TODO: update the h score
                else:
                    # add node to our heap, using pushpack if needed
                    if pushback == None:
                        heappush(heap, (child.g + child.h, child))
                    else:
                        heappush(heap, (pushback.g + pushback.h, pushback))
                    pushpack = child

            return_parent = 0

        if success:
            #if keyNode.parent == None: return True, []
            path0 = [keyNode.obj]
            path1 = [keyNode]
            while keyNode.parent != None:
                keyNode = keyNode.parent
                path0.append(keyNode.obj)
                path1.append(keyNode)

            # determine if we have suboptimal goals
            for a in path1:
                if a.parent != None:
                    prereqs = [ (p.valid(a.parent.bb_delta), p) for p in a.obj.prereqs ] 
                    failed = [ p[1] for p in prereqs if p[0] < 1.0 ]
                    if len(failed) > 0:
                        new_goal = EvalGoal(failed[0].prereq)
                        new_plan = self.search_actions(actions, start_action, start_blackboard, new_goal)
                        return new_plan

            return True, path0
        else:
            return False, []


