import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from helpers import *

from definitions import *

matplotlib.rcParams['lines.linewidth'] = 3
matplotlib.rcParams['font.size'] = 22

linestyles = ['solid', 'dashed', 'dotted', 'dashdot']
dashList = [(3, 3, 2, 2), (5, 2, 20, 2), (2, 2), (3, 4), (10, 2)]
colors = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6']

__all__ = ["plot_avg_values_measurement", "plot_avg_values_measurement_multiple",
           "plot_avg_values_measurement_multiple_twiny"]


# Plot multiple lines of average data for a complete measurement
def plot_avg_values_measurement_multiple(values, errors, keys, name, xlabels, **kwargs):
    print("Plotting multiple {0}".format(name))
    fig, ax = plt.subplots()

    # ax.set_title("{0}".format(name))
    ax.set_xlabel("Measurement bandwidth in Mbit/s")
    # ax.set_ylabel("AVG # of occurrences")
    fig.set_size_inches(10, 8)

    linestyle_index = 0

    for key in keys:
        ax.errorbar(np.arange(len(values[key])), values[key], yerr=errors[key], capsize=3, elinewidth=2,
                    label=dict_lookup[key], linestyle=linestyles[linestyle_index])
        ax.locator_params(nbins=len(values[key]))
        linestyle_index = linestyle_index + 1

    # Ensures even spacing of the values
    ax.set_xticks(np.arange(len(values[key])))
    ax.set_xticklabels(xlabels)

    handles, labels = ax.get_legend_handles_labels()
    # ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.15))
    ax.legend(labels, loc='upper right')

    fig.tight_layout()

    if "max" in kwargs:
        plt.gca().set_ylim(top=kwargs.get("max"))

    if "min" in kwargs:
        plt.gca().set_ylim(bottom=kwargs.get("min"))

    ax.grid()

    str_output_filename_pdf = PATH_OUTPUT_COMPLETE_MULTIPLE / (name + ".pdf")
    # str_output_filename_png = PATH_OUTPUT_COMPLETE_MULTIPLE / (name + ".png")

    plt.savefig(str_output_filename_pdf, format='pdf')
    # plt.savefig(str_output_filename_png, format='png')

    plt.close()


# Plots multiple lines of average data for a complete measurement. keys1 = left Y, keys2 = right Y
def plot_avg_values_measurement_multiple_twiny(values, errors, keys1, keys2, name, xlabels, **kwargs):
    print("Plotting multiple - twinx {0}".format(name))
    fig, ax1 = plt.subplots()
    # plt.locator_params(numticks=10)

    # ax1.set_title("{0}".format(name))
    ax1.set_xlabel("Measurement bandwidth in Mbit/s")
    # ax.set_ylabel("AVG # of occurrences")
    fig.set_size_inches(10, 8)

    color_idx = 0

    for key in keys1:
        ax1.errorbar(np.arange(len(values[key])), values[key], yerr=errors[key], capsize=3, elinewidth=2,
                     label=dict_lookup[key], color=colors[color_idx], linestyle=linestyles[color_idx])
        ax1.locator_params(nbins=len(values[key]))
        color_idx += 1

    if "maxl" in kwargs:
        ax1.set_ylim(top=kwargs.get("maxl"))

    if "minl" in kwargs:
        ax1.set_ylim(bottom=kwargs.get("minl"))

    ax1.legend()
    ax2 = ax1.twinx()

    for key in keys2:
        ax2.errorbar(np.arange(len(values[key])), values[key], yerr=errors[key], capsize=3, elinewidth=2,
                     label=dict_lookup[key], color=colors[color_idx], dashes=dashList[color_idx])
        ax2.locator_params(nbins=len(values[key]))
        color_idx += 1

    ax2.legend()

    if "maxr" in kwargs:
        ax2.set_ylim(top=kwargs.get("maxr"))

    if "minr" in kwargs:
        ax2.set_ylim(bottom=kwargs.get("minr"))

    # Alternative: https://stackoverflow.com/questions/20243683/matplotlib-align-twinx-tick-marks
    # ax1.set_yticks(np.linspace(ax1.get_yticks()[0], ax1.get_yticks()[-1], len(ax2.get_yticks())))
    ax1.set_yticks(np.linspace(ax1.get_yticks()[0], ax1.get_yticks()[-1], 6))
    ax2.set_yticks(np.linspace(ax2.get_yticks()[0], ax2.get_yticks()[-1], 6))
    # ax2.set_yticks(np.linspace(ax2.get_yticks()[0], ax2.get_yticks()[-1], 6))

    ax1.set_xticks(np.arange(len(values[key])))
    ax1.set_xticklabels(xlabels)

    ax1.grid()

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    if "lowlegend" in kwargs and kwargs.get("lowlegend"):
        lgd = ax1.legend(handles1, labels1, loc='upper center', bbox_to_anchor=(0.17, -0.15))
        lgd = ax2.legend(handles2, labels2, loc='upper center', bbox_to_anchor=(0.83, -0.15))
    else:
        lgd = ax1.legend(handles1, labels1, loc='upper center', bbox_to_anchor=(0.5, -0.15))
        lgd = ax2.legend(handles2, labels2, loc='upper right')

    fig.tight_layout()
    # plt.show()

    str_output_filename_pdf = PATH_OUTPUT_COMPLETE_MULTIPLE / (name + ".pdf")
    # str_output_filename_png = PATH_OUTPUT_COMPLETE_MULTIPLE / (name + ".png")

    plt.savefig(str_output_filename_pdf, format='pdf')
    # plt.savefig(str_output_filename_png, format='png')

    plt.close()


# Plots average values for an entire measurement
def plot_avg_values_measurement(values, errors, key, xlabels):
    key = key.replace(".", "_")
    print("Plotting {0}".format(key))
    fig, ax = plt.subplots()

    # ax.set_title("Parameter {0} change".format(key))
    ax.set_xlabel("Measurement bandwidth in Mbit/s")
    ax.set_ylabel(dict_lookup[key])
    fig.set_size_inches(10, 8)

    ax.errorbar(np.arange(len(values)), values, yerr=errors, capsize=3, elinewidth=2)
    ax.locator_params(nbins=len(values))

    # Ensures even spacing of the values
    ax.set_xticks(np.arange(len(values)))
    ax.set_xticklabels(xlabels)

    ax.grid()

    fig.tight_layout()
    # plt.show()

    str_output_filename_pdf = PATH_OUTPUT_COMPLETE / (key + ".pdf")
    # str_output_filename_png = PATH_OUTPUT_COMPLETE / (key + ".png")

    plt.savefig(str_output_filename_pdf, format='pdf')
    # plt.savefig(str_output_filename_png, format='png')
    plt.close()


# Plots data from a measurement into a CDF plot
def plot_cdf_measurement(values, key, xlabels):
    key_out = key.replace(".", "_")
    print("Plotting {0} - CDF ".format(key))
    fig, ax = plt.subplots()

    fig.set_size_inches(10, 8)

    n_bins = 500

    ax.grid()

    for bw in xlabels:
        try:
            # norm = [float(i) / sum(values[bw][key]) for i in values[bw][key]]
            norm = values[bw][key]
        except:
            return

        data_label = bw.split("_")[1]
        if data_label.find(".") == -1:
            data_label = data_label + ".0"
        data_label = data_label + " Mbit/s"


        n, bins, patches = ax.hist(norm, n_bins, density=True, histtype='step',
                                   cumulative=True, label=data_label, linewidth=2)

    ax.set_ylabel("Empirical CDF")
    ax.set_xlabel(dict_lookup[key])


    handles, labels = ax.get_legend_handles_labels()

    columns = 3
    if len(values) == 2 or len(values) == 4:
        columns = 2
    elif len(values) == 3 or len(values) == 6:
        columns = 3

    lgd = ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=3)

    fig.tight_layout()

    str_output_filename_pdf = PATH_OUTPUT_COMPLETE_CDF / (key_out + "_cdf" + ".pdf")
    # str_output_filename_png = PATH_OUTPUT_COMPLETE_CDF / (key_out + "_cdf" + ".png")
    # helper_write_data(key, key_out, values)

    # plt.savefig(str_output_filename_pdf, format='pdf', bbox_extra_artists=(lgd,), bbox_inches='tight')
    # plt.savefig(str_output_filename_png, format='png')
    plt.savefig(str_output_filename_pdf, format='pdf')
    plt.close()
