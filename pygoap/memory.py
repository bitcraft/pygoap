"""
Memories are stored precepts.
"""



class MemoryManager(set):
    """
    Store and manage precepts.
    
    shared blackboards violate reality in that multiple agents share the same
    thoughts, to extend the metaphore.  but, the advantage of this is that in
    a real-time simulation, it gives the player the impression that the agents
    are able to collobroate in some meaningful way, without a significant
    impact in performace.

    that being said, i have chosen to restrict blackboards to a per-agent
    basis.  this library is meant for rpgs, where the action isn't real-time
    and would require a more realistic simulation of intelligence.
    """

    def add(self, other):
        if len(self) > 20:
            self.pop()
        super(MemoryManager, self).add(other)

    def of_class(self, klass):
        for i in self:
            if isinstance(i, klass):
                yield i

