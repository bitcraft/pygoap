"""
Memories are stored precepts.
A blackboard is a device to share information amongst actions.
This implementation uses sqlite3 as a backend for storing memories.

The MemManager class is not used.
"""



class MemoryManager(set):
    """
    a memory manager's purpose is to store and manage stored precepts.
    """

    def of_class(self, klass):
        for i in self:
            if isinstance(i, klass):
                yield i

class Blackboard(dict):
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
    shared, so that in the future, it will be easier to simulate agents with
    shared knowledge and subtle communication.
    """
    pass
