from heapq import heappush, heappop

def heappushpop(heap, item):
    """Slow version of a fast function."""
    heappush(heap, item)
    return heappop(heap)
