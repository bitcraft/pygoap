"""
Copyright 2010, 2011 Leif Theden

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
Memories are stored precepts.
A blackboard is a device to share information amongst actions.
This implementation uses sqlite3 as a backend for storing memories.

The MemManager class is not used.
"""

import sqlite3
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, sessionmaker

from collections import defaultdict

DEBUG = 0

Base = declarative_base()

class Tag(object):
    """
    simple object for storing data on a blackboard
    """

    def __init__(self, **kwargs):
        if 'kw' in kwargs.keys():
            del kwargs['kw']
            self.kw = kwargs
        else:
            self.kw = kwargs

    def __repr__(self):
        return "<Tag: {}>".format(self.kw)

class Memory(Base):
    __tablename__ = 'memory'

    id = Column(Integer, primary_key=True)
    owner = Column(String(255))
    value = Column(String(255))

    def __init__(self, owner, value):
        self.owner = owner
        self.value = value


# initialize our database
#engine = create_engine('sqlite://')
#Base.metadata.create_all(engine)


class MemoryManager(object):
    """
    a memory manager's purpose is to store precepts.

    memories here should be able to be recalled quickly.  like a blackboard,
    this class is designed to have many users (not thread safe now).
    """

    def __init__(self, owner=None):
        self.owner = owner

    def add(self, precept, confidence=1.0):
        """
        Precepts may have a confidence leve associated with them as a metric
        for sorting out precepts that may not be reliable.

        This mechanism primarly exists for users of a shared blackboard where
        they may post conflicting information.
        """

        Session = sessionmaker(bind=engine)
        session = Session()

        m = Memory(None, "")
         
        try:
            session.add(m)
            session.commit()
        except:
            if DEBUG: print "error:", m
            session.rollback()
            raise

    def search(self, tag, owner=None):
        alldata = session.query(Memory).all()
        for somedata in alldata:
            if DEBUG: print somedata


class Blackboard(object):
    """
    a blackboard is an abstract memory device.

    alternative, more robust solution would be a xml backend or database

    tags belong to a set of values that are known by the actions that an actor
    would find useful.  tag names are simple strings and have a value
    associated with them.  for simplicity, a blackboard could be used like a
    standard python dictionary.

    shared blackboards violate reality in that multiple agents share the same
    thoughts, to extend the metaphore.  but, the advantage of this is that in
    a real-time simulation, it gives the player the impression that the agents
    are able to collobroate in some meaningful way, without a significant
    impact in performace.

    that being said, i have chosen to restrict blackboards to a per-agent
    basis.  this library is meant for rpgs, where the action isn't real-time
    and would require a more realistic simulation of intelligence.

    however, i will still develop blackboards with the intention that they are
    shared, so that in the future, it will be easier to simulate the borg-mind.
    """

    def __init__(self):
        self.memory = []

    def __eq__(self, other):
        if isinstance(other, Blackboard):
            return self.memory == other.memory
        else:
            return False

    def post(self, tag):
        if not isinstance(tag, Tag):
            m="Only instances of tag objects can be stored on a blackboard"
            raise ValueError, m
       
        d = tag.kw.copy()
        self.memory.append(d)
        
    def read(self, *args, **kwargs):
        """
        return any data that match the keywords in the function call
        returns a list of dictionaries
        """

        if (args == ()) and (kwargs == {}):
            return self.memory

        tags = []
        r = []

        if DEBUG: print "[bb] args {}".format(args)
        if DEBUG: print "[bb] kwargs {}".format(kwargs)

        def check_args(tag):
            if args == ():
                return True
            else:
                keys = tag.keys()
                return all([ a in keys for a in args ])
                    
        def check_kwargs(tag):
            if kwargs == {}:
                return True
            else:
                raise ValueError, "Blackboards do not support search...yet"

        for tag in self.memory:
            if DEBUG: print "[bb] chk args {} {}".format(tag, check_args(tag))
            if DEBUG: print "[bb] chk kw {} {}".format(tag, check_kwargs(tag))
            if check_args(tag) and check_kwargs(tag):
                r.append(tag)

        #r.reverse()
        return r

    def update(self, other):
        self.memory.extend(other.memory)
