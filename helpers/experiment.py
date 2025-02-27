from matplotlib import pyplot as plt
import time
from algorithms.twoDimensionalArraySweep import two_d_array_sweep

PLT_EXPERIMENT_NAME = "outputs/time_inter_plot.png"

def plot_results(batch_sizes, times, intersections):
    fig, ax1 = plt.subplots()

    color1 = 'tab:blue'
    ax1.set_xlabel('n')  # number of items
    ax1.set_ylabel('time (sec)', color=color1)
    ax1.plot(batch_sizes, times, marker='<', color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)

    # Create a second y-axis sharing the same x-axis
    ax2 = ax1.twinx()
    color2 = 'tab:red'
    ax2.set_ylabel('# of intersections', color=color2)
    ax2.plot(batch_sizes, intersections, linestyle='--', color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)

    plt.title('Figure 14: 2D; preprocessing time, varying n')
    plt.tight_layout()
    plt.savefig(PLT_EXPERIMENT_NAME, dpi=600, transparent=True)

def run_batch(dataset, batch_size, times, intersections, batch_sizes):
    dataset.set_portion(batch_size)
    start = time.perf_counter()
    _, inter = two_d_array_sweep(dataset)
    end = time.perf_counter()
    times.append(end - start)
    intersections.append(inter)
    batch_sizes.append(batch_size)



def run_experiment(dataset, batch=200):
    times = []
    intersections = []
    batch_sizes = []
    for batch_size in range(batch, len(dataset), batch):
        run_batch(dataset, batch_size, times, intersections, batch_sizes)

    if batch_size < len(dataset):
        run_batch(dataset, len(dataset), times, intersections, batch_sizes)

    plot_results(batch_sizes, times, intersections)