"""
Since a pyGOAP agent relies on cues from the environment when planning, having
a stable and efficient virtual environment is paramount.  

When coding your game or simulation, you can think of the environment as the
conduit that connects your actors on screen to their simulated thoughts.  This
environment simply provides enough basic information to the agents to work.  It
is up to you to make it useful.

objects should be able to produce actions that would be useful, rather than the
virtual actors knowing eacatly how to use and what to do with other objects.
This concept comes from 'The Sims', where each agent doesn't need to know how
to use every object, but can instead query the object for actions to do with it.
"""

from actionstates import *
from itertools import chain, repeat, product, izip



class ObjectBase(object):
    """
    class for objects that agents can interact with
    """

    def __init__(self, name):
        self.name = name
        self.inventory = []

    def handle_precept(self, precept):
        pass

    def add(self, other, origin):
        """
        add something to this object's inventory
        the object must have an origin.
        the original position of the object will lose this object:
            dont remove it manually!
        """

        origin.inventory.remove(other)
        self.inventory.append(other)

    def remove(self, obj):
        """
        remove something from this object's inventory
        """

        self.inventory.remove(other)

    def get_actions(self, other):
        """
        generate a list of actions that could be used with this object
        """
        return []        

    def __repr__(self):
        return "<Object: {}>".format(self.name)


class Precept(object):
    """
    This is the building block class for how an agent interacts with the
    simulated environment.
    """

    def __init__(self, *arg, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return "<Precept: %s>" % self.__dict__


class Environment(object):
    """Abstract class representing an Environment.  'Real' Environment classes
    inherit from this.
    """

    def __init__(self, things=[], agents=[], time=0):
        self.time   = time
        self.agents = []
        self.things = []

        [ self.add_thing(i) for i in things ]
        [ self.add_thing(i) for i in agents ]

        self.action_que = []

    def default_position(self, object):
        """
        Default position to place a new object with unspecified position.
        """

        raise NotImplementedError

    def run(self, steps=1000):
        """
        Run the Environment for given number of time steps.
        """

        [ self.update(1) for step in xrange(steps) ]

    def add_thing(self, thing, position=None):
        """
        Add an object to the environment, setting its position. Also keep
        track of objects that are agents.  Shouldn't need to override this.
        """

        from agent import GoapAgent

        thing.position = position or self.default_position(thing)
        self.things.append(thing)

        print "[env] adding {}".format(thing)

        # add the agent
        if isinstance(thing, GoapAgent):
            self.agents.append(thing)
            thing.performance = 0
            thing.environment = self

        # for simplicity, agents always know where they are
        i = Precept(sense="position", thing=thing, position=thing.position)
        thing.handle_precept(i)

        # should update vision for all interested agents (correctly, that is)
        [ self.look(a) for a in self.agents if a != thing ]

    def update(self, time_passed):
        """
        * Update our time
        * Let agents know time has passed
        * Update actions that may be running
        * Add new actions to the que

        this could be rewritten.
        """

        # update time in the simulation
        self.time += time_passed

        # let all the agents know that time has passed
        # bypass the modeler for simplicity
        p = Precept(sense="time", time=self.time) 
        [ a.handle_precept(p) for a in self.agents ]

        # update all the actions that may be running
        precepts = [ a.update(time_passed) for a in self.action_que ]
        precepts = [ p for p in precepts if not p == None ]

        # get all the running actions for the agents
        self.action_que = chain([ a.running_actions() for a in self.agents ])
       
        # start any actions that are not started
        [ action.start() for action in self.action_que 
            if action.state == ACTIONSTATE_NOT_STARTED ]

    def broadcast_precepts(self, precepts, agents=None):
        """
        for efficiency, please use this for sending a list of precepts
        """
        
        if agents == None:
            agents = self.agents

        model = self.model_precept

        for p in precepts:
            [ a.handle_precept(model(p, a)) for a in agents ]

    def model_precept(self, precept, other):
        """
        override this to model the way that precept objects move in the
        simulation.  by default, all precept objects will be distributed
        indiscriminately to all agents.

        while this behavior may be desirable for some types of precepts,
        it doesn't make sense in many.

        the two big things to model here would be vision and sound.
        """

        return precept

