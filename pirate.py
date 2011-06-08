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

__version__ = ".004"

import csv, sys, os, imp

try:
  import psyco
except ImportError:
  pass

from pygoap import *


"""
lets make a drunk pirate.

scenerio:
    the pirate begins by idling
    after 5 seconds of the simulation, he sees a girl

he should attempt to get drunk and sleep with her...
...any way he knows how.
"""

global_actions = {}

def load_commands(agent, path):
    def is_expression(string):
        if "=" in string:
            return True
        else:
            return False

    def parse_line(p, e):
        prereqs = []
        effects = []

        if p == "":
            prereqs = None
        else:
            for x in p.split(","):
                x = x.strip()
                if is_expression(x):
                    p2 = ExtendedActionPrereq(x)
                else:
                    p2 = BasicActionPrereq(x)

                prereqs.append(p2)

        for x in e.split(","):
            x = x.strip()
            if is_expression(x):
                e2 = ExtendedActionEffect(x)
            else:
                e2 = BasicActionEffect(x)

            effects.append(e2)

        return prereqs, effects

    # more hackery
    mod = imp.load_source("actions", os.path.join(path, "actions.py"))

    csvfile = open(os.path.join(path, "actions.csv"))
    sample = csvfile.read(1024)
    dialect = csv.Sniffer().sniff(sample)
    has_header = csv.Sniffer().has_header(sample)
    csvfile.seek(0)

    r = csv.reader(csvfile, delimiter=';')

    for n, p, e in r:
        prereqs, effects = parse_line(p, e)
        action = SimpleActionNode(n, prereqs, effects)
        action.set_action_class(mod.__dict__[n])
        agent.add_action(action)

        global_actions[n] = action

def is_female(precept):
    try:
        thing = precept.thing
    except AttributeError:
        pass
    else:
        if isinstance(thing, Human):
            return thing.gender == "Female"

class Human(GoapAgent):
    def __init__(self, gender):
        super(Human, self).__init__()
        self.gender = gender

    def handle_precept(self, precept):
        if is_female(precept):
            self.blackboard.post("sees_lady", True)
            
        return super(Human, self).handle_precept(precept)

    def __repr__(self):
        return "<Human: %s>" % self.gender

def run_once():
    pirate = Human("Male")

    # lets load some pirate commands
    load_commands(pirate, os.path.join("npc", "pirate"))

    pirate.current_action = global_actions["idle"].action_class(pirate, global_actions["idle"])
    pirate.current_action.start()

    # the idle goal will always be run when it has nothing better to do
    pirate.add_goal(SimpleGoal("idle", value=.1))

    # he has high aspirations in life
    # NOTE: he needs to be drunk to get laid (see action map: actions.csv)
    pirate.add_goal(SimpleGoal("is_drunk"))
    pirate.add_goal(SimpleGoal("is_laid"))
    #pirate.add_goal(EvalGoal("money >= 50"))

    # make our little cove
    formosa = XYEnvironment()

    # add the pirate
    formosa.add_thing(pirate)

    # simulate the pirate idling
    formosa.run(15)

    # add a female
    print "=== wench appears"
    wench = Human("Female")
    formosa.add_thing(wench)

    # simulate with the pirate and female
    formosa.run(15)

if __name__ == "__main__":
    import cProfile
    import pstats

    cProfile.run('run_once()', "pirate.prof")

    p = pstats.Stats("pirate.prof")
    p.strip_dirs()
    p.sort_stats('time').print_stats(10)
