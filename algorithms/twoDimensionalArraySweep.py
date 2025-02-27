import math
from DataStructures.MinHeap import MinHeap
from Datasets.Dataset import Dataset


class Node:
    __slots__ = ("ordering_exchange", "attribute1", "attribute2", "index")

    def __init__(self, ordering_exchange, attribute1, attribute2, index):
        self.ordering_exchange = ordering_exchange  # computed angle (in radians)
        self.attribute1 = attribute1  # left item (a [x, y] pair)
        self.attribute2 = attribute2  # right item (a [x, y] pair)
        self.index = index  # position in the current ordering

    def __lt__(self, other):
        return self.ordering_exchange < other.ordering_exchange

    def __repr__(self):
        return f'({self.attribute1}, {self.attribute2})'


def calc_ordering_exchange(attr_left, attr_right):
    """
    Compute the ordering exchange value for two items.
    Defined as atan((right.x - left.x) / (left.y - right.y)).
    If the denominator is zero, return π/2.
    """
    denom = attr_left[1] - attr_right[1]
    if denom == 0:
        return math.pi / 2
    return (attr_right[0] - attr_left[0]) / denom


def update_event(i, ordering, heap):
    """
    For index i, if the adjacent pair (ordering[i], ordering[i+1])
    can exchange order (i.e. left.y < right.y), compute the ordering
    exchange and push a new Node onto the heap.
    """
    n = len(ordering)
    if i < 0 or i >= n - 1:
        return

    y_left = ordering[i][1]
    y_right = ordering[i + 1][1]
    if y_left < y_right:
        oe = calc_ordering_exchange(ordering[i], ordering[i + 1])
        # avoid adding nodes that their angle exceeds the required range
        if oe > math.pi / 2:
            return
        heap.push(Node(oe, ordering[i], ordering[i + 1], i))


def swap_in_ordering(ordering, i):
    """
    Swap two adjacent items in the ordering.
    """
    ordering[i], ordering[i + 1] = ordering[i + 1], ordering[i]

def get_theta_and_update_the_event(heap, ordering):
    node = heap.pop()
    theta = node.ordering_exchange
    # Check if the event is still valid.
    if ordering[node.index] != node.attribute1 or ordering[node.index + 1] != node.attribute2:
        return None  # stale event; skip it.
    swap_in_ordering(ordering, node.index)
    # Update events for the affected adjacent pairs.
    update_event(node.index - 1, ordering, heap)
    update_event(node.index + 1, ordering, heap)
    return theta


def two_d_array_sweep(dataset: Dataset):
    """
    Implements the 2draysweep algorithm.

    Input:
      - dataset: an instance of Dataset that provides:
           • get_attributes(): returns a list of [x, y] pairs.
           • get_oracle(): returns a fairness oracle function that takes the ordering and returns True/False.

    Output:
      - A list of boundaries defining satisfactory regions.
        Each boundary is a tuple (theta, boundary_type), where boundary_type is 0 (start) or 1 (end).
    """
    ordering = dataset.get_attributes()  # list of [x, y] pairs
    oracle = dataset.get_oracle()
    n = len(ordering)

    # Build initial ordering Ω = ∇f((1,0))(D): sort descending by x-coordinate.
    ordering.sort(key=lambda item: item[0], reverse=True)

    heap = MinHeap()
    satisfactory_regions = []

    # Build initial heap: add events for each adjacent pair that can exchange order.
    for i in range(n - 1):
        if ordering[i][1] < ordering[i + 1][1]:
            heap.push(Node(calc_ordering_exchange(ordering[i], ordering[i + 1]), ordering[i], ordering[i + 1], i))

    theta = 0
    # First sweep loop: advance until the ordering is satisfactory.
    while heap.size() > 0:
        if oracle(ordering):
            satisfactory_regions.append((theta, 0))
            break
        theta = get_theta_and_update_the_event(heap, ordering)

    if heap.size() == 0 and not oracle(ordering):
        return satisfactory_regions, heap.intersections_count

    flag = oracle(ordering)
    # Second sweep loop: record transitions in fairness.
    while heap.size() > 0:
        theta = get_theta_and_update_the_event(heap, ordering)
        if theta is not None:
            new_sign = oracle(ordering)
            if flag and not new_sign:
                satisfactory_regions.append((theta, 1))  # end boundary of a satisfactory region.
            elif (not flag) and new_sign:
                satisfactory_regions.append((theta, 0))  # start boundary of a satisfactory region.
            flag = new_sign

    if flag:
        satisfactory_regions.append((math.pi / 2, 1))

    return satisfactory_regions, heap.intersections_count
