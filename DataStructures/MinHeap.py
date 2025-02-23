import heapq


class MinHeap:
    def __init__(self):
        self.heap = []
        self.seen_nodes = set()

    def push(self, val):
        """Push a value onto the heap."""
        if val not in self.seen_nodes:
            heapq.heappush(self.heap, val)
            # self.seen_nodes.add(val)

    def pop(self):
        """Pop and return the smallest value from the heap."""
        if self.heap:
            return heapq.heappop(self.heap)
        raise IndexError("pop from an empty heap")

    def peek(self):
        """Return the smallest value without popping it."""
        if self.heap:
            return self.heap[0]
        raise IndexError("peek from an empty heap")

    def is_empty(self):
        """Check if the heap is empty."""
        return len(self.heap) == 0

    def size(self):
        """Return the size of the heap."""
        return len(self.heap)

    def heapify(self, iterable):
        """Convert an iterable into a heap."""
        self.heap = list(iterable)
        heapq.heapify(self.heap)

    def get_heap(self):
        """Return the internal heap list."""
        return self.heap


