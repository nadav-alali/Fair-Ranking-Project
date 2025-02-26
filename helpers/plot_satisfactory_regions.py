import math
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

FILE_NAME = 'outputs/plot_satisfactory_regions.png'

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
    plt.savefig(FILE_NAME, dpi=600, transparent=True)
    return FILE_NAME