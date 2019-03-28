import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from definitions import *

matplotlib.rcParams['lines.linewidth'] = 3
matplotlib.rcParams['font.size'] = 22

__all__ = ["plot_video_stats_recv", "plot_media_stats_twin_y", "plot_media_stats_single_y"]

linestyles = ['solid', 'dashed', 'dotted', 'dashdot']
dashList = [(3, 3, 2, 2), (5, 2, 20, 2), (2, 2), (5, 2), (10, 2)]
colors = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6']


# Single measuremen
# Plots the given list_y1_values using the given labels
def plot_video_stats_recv(list_y1_values, list_y1_labels, media_type, type, target_path):
    fig, ax = plt.subplots()

    ax.set_xlabel("time (s)")
    ax.set_title('Frame Parameters for Received Video Stream', y=1.05)
    fig.set_size_inches(10, 8)

    for entry in list_y1_values:
        plt.plot(entry, label=list_y1_labels[list_y1_values.index(entry)])

    ax.legend()

    str_output_path = os.path.join(PATH_OUTPUT, target_path)
    str_output_filename_pdf = str_output_path + "/recv_{0}_{1}.pdf".format(media_type, type)
    str_output_filename_png = str_output_path + "/recv_{0}_{1}.png".format(media_type, type)

    if not os.path.isdir(str_output_path):
        os.makedirs(str_output_path)

    plt.savefig(str_output_filename_pdf, format='pdf')
    plt.savefig(str_output_filename_png, format='png')


# Single measuremen
# Two-axis plot y1 with y1_labels and y2 with y2_labels for media_type audio or video
def plot_media_stats_twin_y(list_y1_values: list, list_y1_labels: list, list_y2_values: list, list_y2_labels: list,
                            conn_type: str, media_type, direction, target_path, **kwargs):
    fig, ax1 = plt.subplots()

    ax1.set_xlabel("time (s)")
    fig.set_size_inches(10, 8)

    color_idx = 0

    for entry in list_y1_values:
        ax1.plot(entry, label=list_y1_labels[list_y1_values.index(entry)], color=colors[color_idx], linestyle=linestyles[color_idx])
        color_idx += 1

    if "maxl" in kwargs:
        ax1.set_ylim(top=kwargs.get("maxl"))

    if "minl" in kwargs:
        ax1.set_ylim(bottom=kwargs.get("minl"))

    ax1.legend()
    ax2 = ax1.twinx()

    for entry in list_y2_values:
        ax2.plot(entry, label=list_y2_labels[list_y2_values.index(entry)], color=colors[color_idx], linestyle="--", dashes=dashList[color_idx])
        color_idx += 1

    ax2.legend()

    if "maxr" in kwargs:
        ax2.set_ylim(top=kwargs.get("maxr"))

    if "minr" in kwargs:
        ax2.set_ylim(bottom=kwargs.get("minr"))

    # Parallel positioning of the y-tick labels
    ax1.set_yticks(np.linspace(ax1.get_yticks()[0], ax1.get_yticks()[-1], 6))
    ax2.set_yticks(np.linspace(ax2.get_yticks()[0], ax2.get_yticks()[-1], 6))
    ax2.legend()

    ax1.grid()

    # Legend
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    if "lowlegend" in kwargs and kwargs.get("lowlegend"):
        lgd = ax1.legend(handles1, labels1, loc='upper center', bbox_to_anchor=(0.17, -0.15))
        lgd = ax2.legend(handles2, labels2, loc='upper center', bbox_to_anchor=(0.83, -0.15))
    else:
        lgd = ax1.legend(handles1, labels1, loc='upper center', bbox_to_anchor=(0.5, -0.15))
        if len(list_y1_labels) <= 2:
            lgd = ax1.legend(handles1, labels1, loc='upper center', bbox_to_anchor=(0.5, -0.15))
        else:
            lgd = ax1.legend(handles1, labels1, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2,
                             columnspacing=0.5)
        lgd = ax2.legend(handles2, labels2, loc='upper right')

    fig.tight_layout()

    str_output_path = os.path.join(PATH_OUTPUT, target_path)

    if "subdir" in kwargs:
        str_output_path = os.path.join(str_output_path, kwargs.get("subdir"))
        if not os.path.exists(str_output_path):
            os.makedirs(str_output_path)

    str_output_filename_png = str_output_path + "/{0}_{1}_{2}_{3}.png".format(direction, conn_type, media_type,
                                                                              kwargs.get("bw"))
    str_output_filename_pdf = str_output_path + "/{0}_{1}_{2}_{3}.pdf".format(direction, conn_type, media_type,
                                                                              kwargs.get("bw"))

    if not os.path.isdir(str_output_path):
        os.makedirs(str_output_path)

    # plt.savefig(str_output_filename_png, format='png')
    plt.savefig(str_output_filename_pdf, format='pdf')

    plt.close()


# Single measuremen
# Normal x-y plot for audio/video parameters
def plot_media_stats_single_y(list_y1_values: list, list_y1_labels: list, conn_type: str, media_type, direction, target_path, **kwargs):
    fig, ax = plt.subplots()

    ax.set_xlabel("time (s)")

    fig.set_size_inches(10, 8)

    color_idx = 0

    # Actual plotting
    for entry in list_y1_values:
        ax.plot(entry, label=list_y1_labels[list_y1_values.index(entry)], color=colors[color_idx], linestyle=linestyles[color_idx])
        color_idx += 1

    # Legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(labels, loc='upper right')

    # Tight layout
    fig.tight_layout()

    # y-axis min/max
    if "max" in kwargs:
        plt.gca().set_ylim(top=kwargs.get("max"))

    if "min" in kwargs:
        plt.gca().set_ylim(bottom=kwargs.get("min"))

    # 6 evenly spaced y-ticks
    ax.set_yticks(np.linspace(ax.get_yticks()[0], ax.get_yticks()[-1], 6))

    # Grid
    ax.grid()

    str_output_path = os.path.join(PATH_OUTPUT, target_path)

    if "subdir" in kwargs:
        str_output_path = os.path.join(str_output_path, kwargs.get("subdir"))
        if not os.path.exists(str_output_path):
            os.makedirs(str_output_path)

    str_output_filename_pdf = str_output_path + "/{0}_{1}_{2}_{3}.pdf".format(direction, conn_type, media_type,
                                                                              kwargs.get("bw"))
    str_output_filename_png = str_output_path + "/{0}_{1}_{2}_{3}.png".format(direction, conn_type, media_type,
                                                                              kwargs.get("bw"))

    if not os.path.isdir(str_output_path):
        os.makedirs(str_output_path)

    plt.savefig(str_output_filename_pdf, format='pdf')
    # plt.savefig(str_output_filename_png, format='png')
