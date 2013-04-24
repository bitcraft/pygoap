"""
Memories are stored precepts.
"""



class MemoryManager(set):
    """
    Store and manage precepts.
    
    Shared blackboards violate reality in that multiple agents share the same
    thoughts, to extend the metaphor.  But, the advantage of this is that in
    a real-time simulation, it gives the player the impression that the agents
    are able to collaborate in some meaningful way, without a significant
    impact in performance.

    That being said, i have chosen to restrict blackboards to a per-agent
    basis.  This library is meant for RPGs, where the action isn't real-time
    and would require a more realistic simulation of intelligence.
    """

    def of_class(self, klass):
        for i in self:
            if isinstance(i, klass):
                yield i

