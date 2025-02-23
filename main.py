import random

from Datasets.COMPAS.COMPAS import COMPAS
from Datasets.Toy.Toy import Toy
from algorithms.twoDimensionalArraySweep import two_d_array_sweep

import math
import matplotlib.pyplot as plt
import numpy as np

import math
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import numpy as np


def plot_satisfactory_regions(boundaries, max_radius=4):
    """
    boundaries: list of (angle, boundary_type)
      angle in radians, boundary_type in {0, 1} (0=start, 1=end)
    max_radius: how far the wedges/lines extend from origin
    """
    # 1) Sort boundaries by angle
    boundaries_sorted = sorted(boundaries, key=lambda x: x[0])

    # 2) Identify the angular intervals that are "satisfactory."
    in_region = False
    start_angle = None
    regions = []

    for angle, btype in boundaries_sorted:
        if btype == 0 and not in_region:
            start_angle = angle
            in_region = True
        elif btype == 1 and in_region:
            end_angle = angle
            in_region = False
            regions.append((start_angle, end_angle))

    # 3) Plot using matplotlib
    fig, ax = plt.subplots()

    # (a) Draw each "satisfactory" wedge in green
    for (start, end) in regions:
        wedge = Wedge(
            (0, 0),
            max_radius,
            math.degrees(start),
            math.degrees(end),
            color='green',
            alpha=0.3
        )
        ax.add_patch(wedge)

    # (b) Draw boundary lines (the “events”)
    #     We'll color them blue if boundary_type=0, green if boundary_type=1
    for angle, btype in boundaries_sorted:
        x = max_radius * math.cos(angle)
        y = max_radius * math.sin(angle)
        color = 'blue' if btype == 0 else 'green'
        ax.plot([0, x], [0, y], color=color, linewidth=2)

    ax.set_xlim([0, max_radius])
    ax.set_ylim([0, max_radius])
    ax.set_aspect('equal', 'box')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    plt.title('Satisfactory Regions (2D)')
    plt.show()




compas_dataset = Toy()
sorted_satisfactory_regions = two_d_array_sweep(compas_dataset)
print(sorted_satisfactory_regions)
plot_satisfactory_regions(sorted_satisfactory_regions)

# compas_dataset = COMPAS(constraints={'race': {'African-American': (0, 0.6)}})
#
# for portion in range(200, len(compas_dataset.dataset), 200):
#     compas_dataset.set_portion(portion)
#     sorted_satisfactory_regions = two_d_array_sweep(compas_dataset)
#     print(sorted_satisfactory_regions)
#     plot_satisfactory_regions(sorted_satisfactory_regions)