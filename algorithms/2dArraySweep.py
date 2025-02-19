import math
from DataStructures.MinHeap import MinHeap
from Datasets.Dataset import Dataset


class Node:
    def __init__(self, ordering_exchange, attribute1, attribute2, index):
        self.ordering_exchange = ordering_exchange
        self.attribute1 = attribute1
        self.attribute2 = attribute2
        self.index = index

    def __lt__(self, other):
        return self.ordering_exchange < other.ordering_exchange


def is_dominating(attribute1, attribute2):
    """
    attribute1 dominates attribute2 if there is no i in [1,d] s.t attribute2[i] > attribute1[i]
    and there is i in [1,d] s.t attribute1[i] > attribute2[i].

    * d is the size of the dataset (number of attributes)

    :param attribute1: first attribute
    :param attribute2: second attribute
    :return: True or False
    """
    result = not (attribute2[0] > attribute1[0] or attribute2[1] > attribute1[1])
    result = result and (attribute1[0] > attribute2[0] or attribute1[1] > attribute2[1])
    return result


def calc_ordering_exchange(attribute1, attribute2):
    return (attribute1[0] - attribute2[0]) / (attribute1[1] - attribute2[1])


def swap_attributes(attributes, node):
    index = node.index
    attributes[index], attributes[index + 1] = attributes[index + 1], attributes[index]
    node.attribute1, node.attribute2 = attributes[index], attributes[index+1]
    node.ordering_exchange = calc_ordering_exchange(attributes[index], attributes[index+1])


def twoDArraySweep(dataset: Dataset):
    attributes = dataset.get_attributes()
    heap = MinHeap()
    satisfactory_regions = []
    oracle = dataset.get_oracle()

    for i in range(len(attributes) - 1):
        attribute1, attribute2 = attributes[i], attributes[i + 1]
        if is_dominating(attribute1, attribute2):
            continue
        ordering_exchange = calc_ordering_exchange(attribute1, attribute2)
        node = Node(ordering_exchange, attribute1, attribute2, i)
        heap.push(node)

    theta = 0
    while heap.size() > 0:
        if oracle(attributes):
            satisfactory_regions.append((theta, 0))

        # swap the two attributes in 'attributes' and add the new intersection to the heap
        node = heap.pop()
        swap_attributes(attributes, node)
        heap.push(node)

    flag = True
    if heap.size() == 0:
        return theta

    while heap.size() > 0:
        node = heap.pop()
        swap_attributes(attributes, node)
        heap.push(node)

        sign = oracle(attributes)
        if flag and not sign:
            satisfactory_regions.append((theta, 1))
        elif not flag and sign:
            satisfactory_regions.append((theta, 0))
        flag = sign

    if flag:
        satisfactory_regions.append((math.pi / 2, 1))

    return satisfactory_regions
