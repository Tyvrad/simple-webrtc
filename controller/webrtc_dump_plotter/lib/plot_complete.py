# Plots data from entire measurements. Combines data from the RELAY and the P2P phase

import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from definitions import *
from helpers import *

matplotlib.rcParams['lines.linewidth'] = 3
matplotlib.rcParams['font.size'] = 22


colors = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6']
linestyles = ['solid', 'dashed', 'dotted', 'dashdot']

# Plots the keys from list_keys
def plot_single_x(dict_p2p, dict_relay, list_keys, list_bw, name, **kwargs):
    print("Plotting complete - single x {0}".format(name))
    fig, ax = plt.subplots()
    # plt.locator_params(numticks=10)

    # ax.set_title("{0}".format(name))
    ax.set_xlabel("Measurement bandwidth in Mbit/s")
    # ax.set_ylabel("KPI")
    # ax.set_ylabel("AVG # of occurrences")
    fig.set_size_inches(10, 8)

    color_idx = 0

    i_max = 6

    for key in list_keys:
        values_p2p = dict_p2p["average"][key]
        errors_p2p = dict_p2p["errors"][key]

        ax.errorbar(np.arange(len(values_p2p)), values_p2p, yerr=errors_p2p, capsize=3, elinewidth=2,
                     label=dict_lookup[key] + " P2P", color=colors[color_idx], linestyle=linestyles[color_idx])

        color_idx = color_idx + 1
        tmp = max(values_p2p)
        if tmp > i_max:
            i_max = roundup(tmp * 1.2)

        values_relay = dict_relay["average"][key]
        errors_relay = dict_relay["errors"][key]

        ax.errorbar(np.arange(len(values_relay)), values_relay, yerr=errors_relay, capsize=3, elinewidth=2,
                     label=dict_lookup[key] + " RELAY", color=colors[color_idx], linestyle=linestyles[color_idx])

        color_idx += 1

        tmp = max(values_relay)
        if tmp > i_max:
            i_max = roundup(tmp * 1.2)

    # Ensures even spacing of the values
    ax.set_ylim([0, i_max])
    ax.set_xticks(np.arange(len(dict_p2p["average"][key])))
    ax.set_xticklabels(list_bw)

    handles, labels = ax.get_legend_handles_labels()
    # lgd = ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, columnspacing=1)
    ax.legend(loc="upper right")

    if "max" in kwargs:
        plt.gca().set_ylim(top=kwargs.get("max"))

    if "min" in kwargs:
        plt.gca().set_ylim(bottom=kwargs.get("min"))

    ax.grid()

    fig.tight_layout()

    str_output_filename_pdf = PATH_OUTPUT_COMPLETE / (name + ".pdf")
    # str_output_filename_png = PATH_OUTPUT_COMPLETE / (name + ".png")

    plt.savefig(str_output_filename_pdf, format='pdf')
    # plt.savefig(str_output_filename_png, format='png')





