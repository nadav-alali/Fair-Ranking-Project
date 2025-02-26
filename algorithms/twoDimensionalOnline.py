import math


def two_d_online(sorted_satisfactory_regions: list, w1: float, w2: float):
    r = math.sqrt(w1 ** 2 + w2 ** 2)
    theta = math.pi / 2 if w1 == 0 else math.atan2(w2, w1)
    low, high = 0, len(sorted_satisfactory_regions) - 1
    while high - low > 1:
        mid = (low + high) // 2
        if sorted_satisfactory_regions[mid][0] < theta:
            low = mid
        else:
            high = mid

    if sorted_satisfactory_regions[low][1] == 0 and sorted_satisfactory_regions[low][0] <= theta < sorted_satisfactory_regions[high][0]:
        return w1, w2

    if (theta - sorted_satisfactory_regions[low][0]) < (sorted_satisfactory_regions[high][0] - theta):
        return r * math.cos(sorted_satisfactory_regions[low][0]), r * math.sin(sorted_satisfactory_regions[low][0])

    return r * math.cos(sorted_satisfactory_regions[high][0]), r * math.sin(sorted_satisfactory_regions[high][0])
