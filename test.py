"""
lets make a drunk pirate.

scenerio:
    the pirate begins by idling
    soon....he spies rum...

he should attempt to get drunk...
...any way he knows how.
"""

__version__ = ".013"

from pygoap.agent import GoapAgent
from pygoap.environment import ObjectBase
from pygoap.tiledenvironment import TiledEnvironment
from pygoap.goals import *
import os, imp, sys

from pygame.locals import *

import logging
logging.basicConfig(level=00)



stdout = sys.stdout
global_actions = {}


# somewhat hackish way to load actions (they are in the npcs/pirate folder)
def load_commands(agent, path):
    mod = imp.load_source("actions", os.path.join(path, "actions.py"))
    global_actions = dict([ (c.__name__, c()) for c in mod.exported_actions ])

    for k, v in global_actions.items():
        print "testing action {}...".format(v)

    [ agent.add_action(a) for a in global_actions.values() ]


# precept filter for the pirate to search for females
def is_female(precept):
    try:
        thing = precept.thing
    except AttributeError:
        return False
    else:
        if isinstance(thing, Human):
            return thing.gender == "Female"

# subclass the basic GoapAgent class to give them gender and names
class Human(GoapAgent):
    def __init__(self, gender, name="welp"):
        super(Human, self).__init__()
        self.gender = gender
        self.name = name

    def __repr__(self):
        return "<Human: %s>" % self.gender


def run_once():
    import pygame

    pygame.init()
    screen = pygame.display.set_mode((480, 480))
    pygame.display.set_caption('Pirate Island')

    screen_buf = pygame.Surface((240, 240))
    
    # make our little cove is a Tiled TMX map
    formosa = TiledEnvironment("formosa.tmx")

    time = 0
    interactive = 1

    run = True
    while run:
        stdout.write("=============== STEP {} ===============\n".format(time))

        formosa.run(1)


        # for the demo, we add items at different timesteps to debug and monitor
        # changes in the planner

        # add the pirate
        if time == 1:
            pirate = Human("Male", "jack")
            load_commands(pirate, os.path.join("npc", "pirate"))
            
            # give the pirate a goal that makes him want to get drunk
            pirate.add_goal(SimpleGoal(is_drunk=True))

            # this goal forces the agent to scan the environment if something
            # changes.  think of it as 'desire to be aware of the surroundings'
            pirate.add_goal(SimpleGoal(aware=True))

            formosa.add(pirate)
            
            # positions are a tuple: (container, (x, y))
            # this allows for objects to hold other objects
            formosa.set_position(pirate, (formosa, (0,0)))

        elif time == 3:

            # create rum and add it
            rum = ObjectBase("rum")
            formosa.add(rum)
            formosa.set_position(rum, (formosa, (2,5)))

        elif time == 6:

            # create a woman and add her
            wench = Human("Female", "wench")
            formosa.add(wench)

        if time >= 1:
            if pirate.condition('drunk'):
                print "YAY!  A drunk pirate is a happy pirate!"
                print "Test concluded"

        # clear the screen and paint the map
        screen_buf.fill((0,128,255))
        formosa.render(screen_buf)
        pygame.transform.scale2x(screen_buf, screen)
        pygame.display.flip()

        stdout.write("\nPRESS ANY KEY TO CONTINUE".format(time))
        stdout.flush()

        # wait for a keypress
        try:
            if interactive:
                event = pygame.event.wait()
            else:
                event = pygame.event.poll()
            while event:
                if event.type == QUIT:
                    run = False
                    break

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        run = False
                        break

                if not interactive: break

                if event.type == KEYUP: break

                if interactive:
                    event = pygame.event.wait()
                else:
                    event = pygame.event.poll()

        except KeyboardInterrupt:
            run = False

        stdout.write("\n\n");
        time += 1

        if time == 32: run = False


if __name__ == "__main__":
    import cProfile
    import pstats

    try:
        cProfile.run('run_once()', "pirate.prof")
    except KeyboardInterrupt:
        pass

    p = pstats.Stats("pirate.prof")
    p.strip_dirs()
    p.sort_stats('time').print_stats(20, "^((?!pygame).)*$")
    p.sort_stats('time').print_stats(20)
