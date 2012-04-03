"""
lets make a drunk pirate.

scenerio:
    the pirate begins by idling
    soon....he spies a woman

he should attempt to get drunk and sleep with her...
...any way he knows how.
"""

__version__ = ".009"

from pygoap.agent import GoapAgent
from pygoap.environment import ObjectBase
from pygoap.tiledenvironment import TiledEnvironment
from pygoap.goals import *
import os, imp, sys

from pygame.locals import *


stdout = sys.stdout
global_actions = {}

def load_commands(agent, path):
    mod = imp.load_source("actions", os.path.join(path, "actions.py"))
    global_actions = dict([ (c.__name__, c()) for c in mod.exported_actions ])

    #for k, v in global_actions.items():
    #    print "testing action {}..."
    #    v.self_test()

    [ agent.add_action(a) for a in global_actions.values() ]


def is_female(precept):
    try:
        thing = precept.thing
    except AttributeError:
        return False
    else:
        if isinstance(thing, Human):
            return thing.gender == "Female"


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
    
    # make our little cove
    formosa = TiledEnvironment("formosa.tmx")

    time = 0
    interactive = 1

    run = True
    while run:
        stdout.write("=============== STEP {} ===============\n".format(time))

        formosa.run(1)

        if time == 1:
            pirate = Human("Male", "jack")
            load_commands(pirate, os.path.join("npc", "pirate"))
            #pirate.add_goal(SimpleGoal(is_idle=True))
            pirate.add_goal(SimpleGoal(is_drunk=True))
            formosa.add_thing(pirate)

        elif time == 3:
            rum = ObjectBase("rum")
            pirate.add_goal(HasItemGoal(pirate, rum))
            formosa.add_thing(rum)

        elif time == 5:
            formosa.move(rum, pirate.position)
            pass

        elif time == 6:
            wench = Human("Female", "wench")
            formosa.add_thing(wench)

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

        if time == 8: run = False


if __name__ == "__main__":
    import cProfile
    import pstats


    try:
        cProfile.run('run_once()', "pirate.prof")
    except KeyboardInterrupt:
        pass

    p = pstats.Stats("pirate.prof")
    p.strip_dirs()
    p.sort_stats('time').print_stats(10)
