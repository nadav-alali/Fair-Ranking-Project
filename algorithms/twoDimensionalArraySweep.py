import math
from DataStructures.MinHeap import MinHeap
from Datasets.Dataset import Dataset


class Node:
    def __init__(self, ordering_exchange, attribute1, attribute2, index):
        self.ordering_exchange = ordering_exchange  # ratio used to compute the angle (atan)
        self.attribute1 = attribute1  # left item (a [x, y] pair)
        self.attribute2 = attribute2  # right item (a [x, y] pair)
        self.index = index  # position in the current ordering

    def __lt__(self, other):
        return self.ordering_exchange < other.ordering_exchange


    def __hash__(self):
        return hash((self.ordering_exchange, tuple(self.attribute1[:-1]), tuple(self.attribute2[:-1])))


def calc_ordering_exchange(attr_left, attr_right):
    """
    Compute the ordering exchange value for two items.
    This value is defined as (right.x - left.x) / (left.y - right.y).
    It will be transformed to an angle using math.atan later.
    If the denominator is zero, we return infinity.
    """
    denom = attr_left[1] - attr_right[1]
    if denom == 0:
        return math.inf
    return (attr_right[0] - attr_left[0]) / denom


def update_event(i, ordering, heap):
    """
    Given an index i, if the adjacent pair (ordering[i], ordering[i+1])
    can potentially exchange order (i.e. left.y < right.y), compute the
    ordering exchange and push a new Node to the heap.
    """
    if i < 0 or i >= len(ordering) - 1:
        return
    if ordering[i][1] < ordering[i + 1][1]:
        ordering_exchange = calc_ordering_exchange(ordering[i], ordering[i + 1])
        node = Node(ordering_exchange, ordering[i], ordering[i + 1], i)
        heap.push(node)


def swap_in_ordering(ordering, i):
    """
    Swap two adjacent items in the ordering.
    """
    ordering[i], ordering[i + 1] = ordering[i + 1], ordering[i]


def two_d_array_sweep(dataset: Dataset):
    """
    Implements the 2draysweep algorithm.

    Input:
      - dataset: an instance of Dataset that provides:
           • get_attributes(): returns a list of [x, y] pairs
           • get_oracle(): returns a fairness oracle function that takes the ordering and returns True/False.

    Output:
      - A list of boundaries defining satisfactory regions.
        Each boundary is a tuple (theta, boundary_type), where boundary_type is 0 (start) or 1 (end).
    """
    ordering = dataset.get_attributes()  # list of [x, y] pairs
    oracle = dataset.get_oracle()
    n = len(ordering)

    # Build initial ordering Ω = ∇f((1,0))(D): sort descending by the first attribute (x)
    ordering.sort(key=lambda item: item[0], reverse=True)

    heap = MinHeap()
    satisfactory_regions = []

    # Build initial heap: for each adjacent pair that is not dominated (i.e. left.y < right.y), add an event.
    for i in range(n - 1):
        if ordering[i][1] >= ordering[i + 1][1]:
            continue  # skip pairs with a dominance relationship
        ordering_exchange = calc_ordering_exchange(ordering[i], ordering[i + 1])
        node = Node(ordering_exchange, ordering[i], ordering[i + 1], i)
        heap.push(node)

    theta = 0
    # First sweep loop: advance until the ordering becomes satisfactory.
    while heap.size() > 0:
        if oracle(ordering):
            satisfactory_regions.append((theta, 0))
            break
        node = heap.pop()
        # Compute current theta from the ordering exchange value.
        theta = node.ordering_exchange
        # Check if the event is still valid (i.e. the pair at position node.index has not changed).
        # if ordering[node.index] != node.attribute1 or ordering[node.index + 1] != node.attribute2:
        #     continue  # stale event; skip it
        # Swap the two items in the ordering.
        swap_in_ordering(ordering, node.index)
        # After the swap, update events for the adjacent pairs affected.
        update_event(node.index - 1, ordering, heap)
        update_event(node.index, ordering, heap)

    # If no events remain and the ordering is not satisfactory, return what we have.
    if heap.size() == 0 and not oracle(ordering):
        return satisfactory_regions

    flag = oracle(ordering)
    # Second sweep loop: record transitions in fairness.
    while heap.size() > 0:
        node = heap.pop()
        theta = node.ordering_exchange
        # if ordering[node.index] != node.attribute1 or ordering[node.index + 1] != node.attribute2:
        #     continue  # ignore stale event
        swap_in_ordering(ordering, node.index)
        update_event(node.index - 1, ordering, heap)
        update_event(node.index, ordering, heap)

        new_sign = oracle(ordering)
        if flag and not new_sign:
            satisfactory_regions.append((theta, 1))  # end boundary of a satisfactory region
        elif (not flag) and new_sign:
            satisfactory_regions.append((theta, 0))  # start boundary of a satisfactory region
        flag = new_sign

    if flag:
        satisfactory_regions.append((math.pi / 2, 1))

    return satisfactory_regions