"""Used for plotting adaptation graphs and for running Welche's t-tests.
"""
import sys
import os
sys.path.append(os.path.abspath("."))

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
from scipy import stats

X_WIDTH_GAP=8

def plot_adaption_graph():
    """Plots adaptation graph and runs t-tests.
    """

    def set_box_color(bp, color):
        """Sets colours of box + whisker plot things"""
        plt.setp(bp['boxes'], color=color)
        plt.setp(bp['whiskers'], color=color)
        plt.setp(bp['caps'], color=color)
        # plt.setp(bp['medians'], color='black')

    sim_data_20k = []
    sim_data_40k = []
    sim_data_ref_20k = []
    sim_data_ref_40k = []
    sim_data_neat = []
    sim_data_ref_tripod = []

    # read in data
    for scenario in range(5):
        data_20k = list(np.loadtxt(os.path.join(os.path.dirname(__file__), "..", "..",          "experiments", "output", "CPG", "20k", f"perfs_{scenario}.dat")).flatten()/5)
        data_40k = list(np.loadtxt(os.path.join(os.path.dirname(__file__), "..", "..",          "experiments", "output", "CPG", "40k", f"perfs_{scenario}.dat")).flatten()/5)
        data_ref_20k = list(np.loadtxt(os.path.join(os.path.dirname(__file__), "..", "..",      "experiments", "output", "REF", "20k", f"perfs_{scenario}.dat")).flatten()/5)
        data_ref_40k = list(np.loadtxt(os.path.join(os.path.dirname(__file__), "..", "..",      "experiments", "output", "REF", "40k", f"perfs_{scenario}.dat")).flatten()/5)
        data_neat = list(np.loadtxt(os.path.join(os.path.dirname(__file__), "..", "..",         "experiments", "output", "CPG", "neat-no-adpatation", f"NEAT-CPG-{scenario}.dat")).flatten()/5)
        data_ref_tripod = list(np.loadtxt(os.path.join(os.path.dirname(__file__), "..", "..",   "experiments", "output", "REF", "tripod-no-adapatation", f"tripod_{scenario}.dat")).flatten()/5)
        # add to array
        sim_data_20k.append(data_20k)
        sim_data_40k.append(data_40k)
        sim_data_ref_20k.append(data_ref_20k)
        sim_data_ref_40k.append(data_ref_40k)
        sim_data_neat.append(data_neat)
        sim_data_ref_tripod.append(data_ref_tripod)

    # performance stats. Not required for graph. Should have a reference perhaps
    print("performance stats - % drops")
    sim_data_20k_summary        = [np.average(subarray) for subarray in sim_data_20k]
    sim_data_40k_summary        = [np.average(subarray) for subarray in sim_data_40k]
    sim_data_neat_summary       = [np.average(subarray) for subarray in sim_data_neat]
    sim_data_ref_20k_summary    = [np.average(subarray) for subarray in sim_data_ref_20k]
    sim_data_ref_40k_summary    = [np.average(subarray) for subarray in sim_data_ref_40k]
    sim_data_ref_tripod_summmary = [np.average(subarray) for subarray in sim_data_ref_tripod]
    
    print(f'SX:\t\tNEAT\t20k\t40k\t\t20kR\t40kr\tref')
    for scenario in range(0, 5):
        perf_drop_20k_summary           = 1 - (sim_data_20k_summary[scenario] / sim_data_20k_summary[0])
        perf_drop_40k_summary           = 1 - (sim_data_40k_summary[scenario] / sim_data_40k_summary[0])
        perf_drop_neat_summary          = 1 - (sim_data_neat_summary[scenario] / sim_data_neat_summary[0])
        perf_drop_ref_20k_summary       = 1 - (sim_data_ref_20k_summary[scenario] / sim_data_ref_20k_summary[0])
        perf_drop_ref_40k_summary       = 1 - (sim_data_ref_40k_summary[scenario] / sim_data_ref_40k_summary[0])
        perf_drop_ref_tripod_summmary   = 1 - (sim_data_ref_tripod_summmary[scenario] / sim_data_ref_tripod_summmary[0])
        print(f'S{scenario}:\t\t{perf_drop_20k_summary:.3f}\t{perf_drop_40k_summary:.3f}\t{perf_drop_neat_summary:.3f}\t\t{perf_drop_ref_20k_summary:.3f}\t{perf_drop_ref_40k_summary:.3f}\t{perf_drop_ref_tripod_summmary:.3f}')

    #################### BEGIN T-TESTS ####################
    print("Performance stats - p values")
    print(f'SX:\t\t CPG Adapt v. Ref adapt \t CPG Adapt v. CPG No adapt \t Ref adapt v. Ref no adapt')
    for scenario in range(1, 5):
        t_statistic, p_value            = stats.ttest_ind(sim_data_20k[scenario] + sim_data_40k[scenario]       , sim_data_ref_20k[scenario]+sim_data_ref_40k[scenario] , equal_var=False)
        t_statistic_neat, p_value_neat  = stats.ttest_ind(sim_data_20k[scenario]       , sim_data_neat[scenario]                                         , equal_var=False)
        t_statistic, p_value_ref        = stats.ttest_ind(sim_data_ref_20k[scenario]+sim_data_ref_40k[scenario] , sim_data_ref_tripod[scenario]                                  , equal_var=False)
        # t_statistic, p_value = stats.ttest_ind(sim_data_ref_20k[scenario] + sim_data_ref_40k[scenario], sim_data_ref_20k[scenario]+sim_data_ref_40k[scenario], equal_var=False)
        print(f'S{scenario}:\t\t {p_value:.3f} \t\t\t\t {p_value_neat:.3f} \t\t\t\t {p_value_ref:.8f}')

    # map size stats. Also not really needed for graphs
    print('\n\nmap size statistics - p values')
    print(f'SX:\t\t CPG 20k vs 40k \t Ref 20k vs 40k')
    for scenario in range(5):
        t_statistic, p_value = stats.ttest_ind(sim_data_20k[scenario], sim_data_40k[scenario])
        t_statistic, p_value_ref = stats.ttest_ind(sim_data_ref_20k[scenario], sim_data_ref_40k[scenario])
        print(f'S{scenario}:\t\t {p_value:.3f} \t\t\t {p_value_ref:.3f}')
    #################### END T-TESTS ####################

    ticks = ['None (S0)', 'S1', 'S2', 'S3', 'S4']
    box_width = 0.4
    color_20k = 'blue'
    color_40k = 'indigo'
    color_ref_20k = 'salmon'
    color_ref_40k = 'red'

    fig, ax = plt.subplots()
    # fig.set_size_inches(w=3.3, h=2.0)
    fig.set_size_inches(w=12, h=8.0)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True)
    ax.set_title('Adapted Fitness')
    ax.set_xlabel('Failure scenario')
    ax.set_ylabel('Fitness ($m/s$)')  #$ms^{-1}$

    # PROPS for decorating plot objects
    flierprops = dict(marker='o', markersize=5, linestyle='none', markeredgecolor='darkgray')
    # meanline = dict(linestyle='-', color='white')
    # meanpoint = dict(marker='D', markeredgecolor='black', markerfacecolor='red')
    medianprops = dict(linestyle='-', color='silver')
    medianprops_ref = dict(linestyle='-', color='black')
    positions = np.array(range(len(sim_data_40k))) * X_WIDTH_GAP      ## Maybe change to 4

    # Plot actual Data
    bp20k = plt.boxplot(sim_data_20k, positions=positions - 0.75,       widths=box_width, showfliers=False,showmeans=False,flierprops=flierprops, zorder=-1, medianprops=medianprops, patch_artist=True, )
    bp40k = plt.boxplot(sim_data_40k, positions=positions - 0.25,       widths=box_width, showfliers=False,showmeans=False,flierprops=flierprops, zorder=-1, medianprops=medianprops, patch_artist=True, )
    bp20kk = plt.boxplot(sim_data_ref_20k, positions=positions + 0.75,  widths=box_width, showfliers=False,showmeans=False,flierprops=flierprops, zorder=-1, medianprops=medianprops_ref, patch_artist=True, )
    bp40kk = plt.boxplot(sim_data_ref_40k, positions=positions + 1.25,  widths=box_width, showfliers=False,showmeans=False,flierprops=flierprops, zorder=-1, medianprops=medianprops_ref, patch_artist=True, )

    sim_data_neat_summmary = [np.average(subarray) for subarray in sim_data_neat]
    plt.scatter(positions-0.5, sim_data_neat_summmary, marker='*', color='yellowgreen',zorder=1, s=100)   # Might use with ref gaits of some sort
    sim_data_ref_tripod  = [np.average(subarray) for subarray in sim_data_ref_tripod]
    plt.scatter(positions+1, sim_data_ref_tripod, marker='*', color='teal',zorder=1, s=100)   # Might use with ref gaits of some sort

    # Colourize
    set_box_color(bp20k, color_20k)
    set_box_color(bp40k, color_40k)
    set_box_color(bp20kk, color_ref_20k)
    set_box_color(bp40kk, color_ref_40k)

    custom_lines = [
        mpatches.Patch(color=color_20k), 
        mpatches.Patch(color=color_40k), 
        mlines.Line2D([], [], color='yellowgreen', marker='*', linestyle='None',markersize=10), 
        mpatches.Patch(color=color_ref_20k), 
        mpatches.Patch(color=color_ref_40k),
        mlines.Line2D([], [], color='teal', marker='*', linestyle='None',markersize=10), 
    ]
    plt.legend(custom_lines, [
        'CPG 20k',
        'CPG 40k',
        'CPG - No adapatation (avg)',
        'Reference 20k',
        'Reference 40k',
        'Reference - No adapatation (avg)',
    ])

    plt.xticks(range(0, len(ticks) * X_WIDTH_GAP, X_WIDTH_GAP), ticks)
    plt.xlim(-4, len(ticks) * X_WIDTH_GAP)
    plt.ylim(-.2,1.2)
    #plt.tight_layout(pad=0.1)
    
    plt.savefig(os.path.join(os.path.dirname(__file__), "..", "..", "figures", "performance_adaption", "Adaption Fitness.pdf"))
    plt.savefig(os.path.join(os.path.dirname(__file__), "..", "..", "figures", "performance_adaption", "Adaption Fitness.png"))
    plt.show()


plot_adaption_graph()