"""
Copyright 2010, 2011  Leif Theden


This file is part of lib2d.

lib2d is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

lib2d is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with lib2d.  If not, see <http://www.gnu.org/licenses/>.
"""

import pygame
from pygame.locals import *


class Context(object):
    """
    Contexts are used anywhere a handler uses a stack to manage information.
    Currently are used in:
        Context Driver for the game
        FSA for controller handling

    The main purpose of the 4 different methods defined here is to manage
    memory usage.  Please follow the format to make sure your game uses memory
    effeciently.

    init:
        should be the the minimum amout of data needed, such as filenames and
        names of other resources to be loaded when context is endered

    enter:
        called when context is the running context
        load any sounds, images, data files here that are needed

    exit:
        unload any data not directly needed, such as images and sounds and all
        other data loaded in enter()

    terminate:
        unload any other data that you loaded in init()

    """

    def __enter__(self):
        self.enter()

    def __exit__(self):
        self.exit()


    def init(self, *args, **kwargs):
        """
        Called before context is placed in a stack
        This will only be called once over the lifetime of a context
        """

        pass


    def enter(self):
        """
        Called after focus is given to the context
        This may be called several times over the lifetime of the context
        """

        pass


    def exit(self):
        """
        Called after focus is lost
        This may be called several times over the lifetime of the context
        """

        pass


    def terminate(self):
        """
        Called after the context is removed from a stack
        This will only be called once
        """

        pass


class ContextDriver(object):
    """
    ContextDriver will manage a list of different contexts.

    Contexts are stored in a simple FILO queue.

    The current_context attribute will be the context at the top of the stack.

    When a context is added to the ContextDriver, it will have the 'driver'
    attribute set to the Driver.  Contexts are welcome to remove themselves or
    other contexts.
    """


    def __init__(self):
        self._stack = []


    def remove(self, context, exit=True, terminate=True):
        """
        remove the context from the stack
        """

        old_context = self.current_context
        self._stack.remove(context)
        if exit:
            context.__exit__()

        if context is old_context:
            new_context = self.current_context
            if new_context:
                new_context.__enter__()

        if terminate:
            context.terminate()


    def queue(self, new_context, *args, **kwargs):
        """
        queue a context just before the current context
        when the current context finishes, the context passed will be run
        """

        new_context.driver = self
        new_context.init(*args, **kwargs)
        self._stack.insert(-1, new_context)


    def append(self, new_context, *args, **kwargs):
        """
        start a new context and hold the current context.

        idea: the old context could be pickled and stored to disk.
        """

        old_context = self.current_context

        new_context.driver = self
        new_context.init(*args, **kwargs)
        self._stack.append(new_context)

        if old_context:
            old_context.__exit__()

        new_context.__enter__()


    @property
    def current_context(self):
        try:
            return self._stack[-1]
        except IndexError:
            return None



