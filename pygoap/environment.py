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

from precepts import *
from actionstates import *
from itertools import chain
import logging

debug = logging.debug



class ObjectBase(object):
    """
    class for objects that agents can interact with
    """

    def __init__(self, name='noname'):
        self.name = name

    def get_actions(self, other):
        """
        generate a list of actions that could be used with this object
        """
        return []        

    def __repr__(self):
        return "<Object: {}>".format(self.name)


class Environment(object):
    """Abstract class representing an Environment.  'Real' Environment classes
    inherit from this.
    """

    def __init__(self, entities=[], agents=[], time=0):
        self.time = time
        self._agents = []
        self._entities = []
        self._positions = {}

        [ self.add(i) for i in entities ]
        [ self.add(i) for i in agents ]

        self.action_que = []

    @property
    def agents(self):
        return iter(self._agents)

    @property
    def entities(self):
        return chain(self._entities, self._agents)

    def get_position(self, entity):
        raise NotImplementedError


    # this is a placeholder hack.  proper handling will go through
    # model_precept()
    def look(self, caller):
        for i in chain(self._entities, self._agents):
            caller.process(LocationPrecept(i, self._positions[i]))


    def run(self, steps=1000):
        """
        Run the Environment for given number of time steps.
        """

        [ self.update(1) for step in xrange(steps) ]

    def add(self, entity, position=None):
        """
        Add an entity to the environment
        """

        from agent import GoapAgent

        debug("[env] adding %s", entity)


        # hackish way to force agents to re-evaulate their environment
        for a in self._agents:
            to_remove = []

            for p in a.memory.of_class(DatumPrecept):
                if p.name == 'aware':
                    to_remove.append(p)

            [ a.memory.remove(p) for p in to_remove]

        # add the agent
        if isinstance(entity, GoapAgent):
            self._agents.append(entity)
            entity.environment = self
            self._positions[entity] = (None, (0, 0))

            # clever hack to let the planner know who the memory belongs to
            entity.process(DatumPrecept('self', entity))
        else:
            self._entities.append(entity)

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

        # let all the agents know that time has passed and bypass the modeler
        p = TimePrecept(self.time) 
        [ a.process(p) for a in self.agents ]

        # get all the running actions for the agents
        self.action_que = [ a.running_actions() for a in self.agents ]

        # start any actions that are not started
        [ action.__enter__() for action in self.action_que 
            if action.state == ACTIONSTATE_NOT_STARTED ]

        # update all the actions that may be running
        precepts = [ a.update(time_passed) for a in self.action_que ]
        precepts = [ p for p in precepts if not p == None ]


    def broadcast_precepts(self, precepts, agents=None):
        """
        for efficiency, please use this for sending a list of precepts
        """
        if agents == None:
            agents = self.agents

        model = self.model_precept

        for p in precepts:
            [ a.process(model(p, a)) for a in agents ]

    def model_precept(self, precept, other):
        """
        override this to model the way that precept objects move in the
        simulation.  by default, all precept objects will be distributed
        indiscriminately to all agents.
        """
        return precept

