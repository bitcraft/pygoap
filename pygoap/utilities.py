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


__version__ = "v.001"

import sys
import traceback




DEBUG = True

def dlog(text):
    print "goap: %s" % text

# used when we are running python2.5...  osx
def get_exception():
    cla, exc, trbk = sys.exc_info()
    return traceback.format_exception(cla, exc, trbk)

class PyEval(object):
    """
    A safer way to evaluate strings.

    probably should do some preprocessing to make sure its really safe
    NOTE: might modify the dict bassed to it. (not really tested)
    """

    def __init__(self, expr):
        self.expr = expr

    def make_dict(self, bb):
        safe_dict = {}

        # clear out builtins
        safe_dict["__builtins__"] = None

        # copy the dictionaries
        for tag in bb.tags():
            safe_dict[tag] = bb.read(tag)

        return safe_dict

    # mostly for prereq's
    def do_eval(self, bb):
        d = self.make_dict(bb)

        try:
            # this always works if we are evaluating variables
            return eval(self.expr, d)
        except NameError:
            # we are missing a value we need to evaluate the expression
            return False

    # mostly for effect's
    def do_exec(self, bb):
        d = self.make_dict(bb)

        try:
            # a little less secure
            exec self.expr in d

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
            exec self.expr in d

        # the bb was modified
        for key, value in d.items():
            bb.post(key, value)
        return True

    def __str__(self):
            return "<PyEval: %s>" % self.expr
            return v0 >= v1

