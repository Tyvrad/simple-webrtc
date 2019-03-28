import shutil
from pathlib import Path
import os

from helpers import *
from definitions import *

# Actual plotter
import plot_single


#
# SINGLE PLOTS (Parameter lists)
#

# Video plots
video_data_recv_1 = ['video_recv_googFrameHeightReceived',
                     'video_recv_googFrameWidthReceived',
                     'video_recv_bitsReceivedPerSecond']

video_data_recv_2 = ['video_recv_googFrameRateReceived',
                     'video_recv_googFrameRateOutput']

video_data_send_1 = ['video_send_googFrameHeightSent',
                     'video_send_googFrameWidthSent',
                     'video_send_bitsSentPerSecond']
video_data_send_2 = ['video_send_googFrameRateSent']

# Audio plots
audio_data_send_1 = ['audio_send_bitsSentPerSecond']
audio_data_recv_1 = ['audio_recv_bitsReceivedPerSecond']
audio_data_recv_2 = ['audio_recv_googJitterBufferMs',
                     'audio_recv_googPreferredJitterBufferMs']


def plot_single_measurement():
    data_total = load_data_absolute(PATH_DATA_SINGLE)
    if len(data_total) == 2:
        plot_data_total_2_clients(data_total)
    elif len(data_total) == 3:
        print(help)
        plot_data_total_3_clients(data_total)


# Load data for a single measurement
def load_data_absolute(path):
    filenames = []

    dict_all_data = {}

    for file in os.listdir(path):
        directory = os.path.join(path, file)
        if not os.path.isdir(directory):
            continue

        dict_all_data[file] = {}

        for single_file in os.listdir(directory):
            if not single_file.endswith("_avg"):

                filename = os.path.join(directory, single_file)
                filenames.append(filename)

    for filename in filenames:
        dict_single_file = {}
        file = open(filename, 'r')
        for line in file:
            data = line.split(",")
            data_name = data[0]
            data.pop(0)
            try:
                data = list(map(float, data))
            except:
                print("Error in file: {0}, key {1}".format(filename, data_name))
            dict_single_file[data_name] = data

        tmp = filename.split("/")
        key_name = tmp[len(tmp)-2] + "/" + tmp[len(tmp)-1]
        # dict_all_data[key_name] = dict_single_file
        dict_all_data[filename.split('/')[-2]][filename.split('/')[-1]] = dict_single_file

    return dict_all_data


# Plot audio/video send/recv for single measurements
def plot_data_total_2_clients(dict_data):
    # Delete all previous plots while keeping the directories
    for single_file_dir in os.listdir("plots/"):
        if single_file_dir != "complete_measurement":
            dir = Path("plots/") / single_file_dir

            if dir.is_dir():
                for plot in dir.glob("*"):
                    if plot.is_file():
                        plot.unlink()
                    else:
                        shutil.rmtree(str(plot))


    #
    # For each media direction (audio send, audio recv, video send, video recv), 2 presets are defined
    # Each preset is tailored to the results of one measurement (specified by bw)
    # In order to get the right plots:
    # - Place one of the parsed measurement in the single_session directory
    # - Run the plotter
    # - From the directories at the sender (.8) and receiver (.9) move the plots with the matching bw to the writing dir

    #
    # Video Receive
    #
    for file in dict_data:
        for connection in dict_data[file]:
            list_data_1, list_labels_1 = get_data_for_keys(video_data_recv_1, dict_data[file][connection])
            list_data_2, list_labels_2 = get_data_for_keys(video_data_recv_2, dict_data[file][connection])

            # video recv relay for both bws
            if "RELAY" in connection:
                plot_single.plot_media_stats_twin_y(list_data_1, list_labels_1, list_data_2, list_labels_2,
                                                    connection.split("_")[0], 'video', 'recv', file, bw="0_25_18_13",
                                                    minl=0, maxl=600, minr=0, maxr=100, subdir="relay")

                plot_single.plot_media_stats_twin_y(list_data_1, list_labels_1, list_data_2, list_labels_2,
                                                    connection.split("_")[0], 'video', 'recv', file, bw="50_00_27",
                                                    minl=0, maxl=3500, minr=0, maxr=100, subdir="relay")

            # video recv p2p for both bws
            else:
                plot_single.plot_media_stats_twin_y(list_data_1, list_labels_1, list_data_2, list_labels_2,
                                                    connection.split("_")[0], 'video', 'recv', file, bw="0_25_18_13",
                                                    minl=0, maxl=2000, minr=0, maxr=160, subdir="p2p")
                plot_single.plot_media_stats_twin_y(list_data_1, list_labels_1, list_data_2, list_labels_2,
                                                    connection.split("_")[0], 'video', 'recv', file, bw="50_00_27",
                                                    minl=0, maxl=3500, minr=0, maxr=100, subdir="p2p")

            del list_data_1, list_data_2, list_labels_1, list_labels_2

    #
    # Video Send
    #
    for file in dict_data:
        for connection in dict_data[file]:
            list_data_1, list_labels_1 = get_data_for_keys(video_data_send_1, dict_data[file][connection])
            list_data_2, list_labels_2 = get_data_for_keys(video_data_send_2, dict_data[file][connection])

            if "RELAY" in connection:
                plot_single.plot_media_stats_twin_y(list_data_1, list_labels_1, list_data_2, list_labels_2,
                                                    connection.split("_")[0], 'video', 'send', file, bw="0_25_18_13",
                                                    minl=0, maxl=600, minr=0, maxr=100, subdir="relay")

                plot_single.plot_media_stats_twin_y(list_data_1, list_labels_1, list_data_2, list_labels_2,
                                                    connection.split("_")[0], 'video', 'send', file, bw="50_00_27",
                                                    minl=0, maxl=3200, minr=0, maxr=100, subdir="relay")

            else:
                plot_single.plot_media_stats_twin_y(list_data_1, list_labels_1, list_data_2, list_labels_2,
                                                    connection.split("_")[0], 'video', 'send', file, bw="0_25_18_13",
                                                    minl=0, maxl=2000, minr=0, maxr=100, subdir="p2p")

                plot_single.plot_media_stats_twin_y(list_data_1, list_labels_1, list_data_2, list_labels_2,
                                                    connection.split("_")[0], 'video', 'send', file, bw="50_00_27",
                                                    minl=0, maxl=3200, minr=0, maxr=100, subdir="p2p")

            del list_data_1, list_data_2, list_labels_1, list_labels_2

    #
    # Audio Receive
    #
    for file in dict_data:
        for connection in dict_data[file]:
            list_data_1, list_labels_1 = get_data_for_keys(audio_data_recv_1, dict_data[file][connection])
            list_data_2, list_labels_2 = get_data_for_keys(audio_data_recv_2, dict_data[file][connection])

            if "RELAY" in connection:
                plot_single.plot_media_stats_twin_y(list_data_2, list_labels_2, list_data_1, list_labels_1,
                                                    connection.split("_")[0], 'audio', 'recv', file, bw="0_25_18_13",
                                                    minl=0, maxl=1200, minr=0, maxr=38, subdir="relay")

                plot_single.plot_media_stats_twin_y(list_data_2, list_labels_2, list_data_1, list_labels_1,
                                                    connection.split("_")[0], 'audio', 'recv', file, bw="50_00_27",
                                                    minl=0, maxl=600, minr=0, maxr=38, subdir="relay")

            else:
                plot_single.plot_media_stats_twin_y(list_data_2, list_labels_2, list_data_1, list_labels_1,
                                                    connection.split("_")[0], 'audio', 'recv', file, bw="0_25_18_13",
                                                    minl=0, maxl=1200, minr=0, maxr=38, subdir="p2p")

                plot_single.plot_media_stats_twin_y(list_data_2, list_labels_2, list_data_1, list_labels_1,
                                                    connection.split("_")[0], 'audio', 'recv', file, bw="50_00_27",
                                                    minl=0, maxl=50, minr=0, maxr=38, subdir="p2p")

            del list_data_1, list_data_2, list_labels_1, list_labels_2

    #
    # Audio Send
    #
    for file in dict_data:
        for connection in dict_data[file]:
            list_data_1, list_labels_1 = get_data_for_keys(audio_data_send_1, dict_data[file][connection])

            if "RELAY" in connection:
                plot_single.plot_media_stats_single_y(list_data_1, list_labels_1, connection.split("_")[0], 'audio',
                                                      'send', file, bw="0_25_18_13", min=0, max=45, subdir="relay")

                # TODO: Change max to 45?
                plot_single.plot_media_stats_single_y(list_data_1, list_labels_1, connection.split("_")[0], 'audio',
                                                      'send', file, bw="50_00_27", min=0, max=38, subdir="relay")
            else:
                # TODO: Change max to 45?
                plot_single.plot_media_stats_single_y(list_data_1, list_labels_1, connection.split("_")[0], 'audio',
                                                      'send', file, bw="50_00_27", min=0, max=38, subdir="p2p")
                plot_single.plot_media_stats_single_y(list_data_1, list_labels_1, connection.split("_")[0], 'audio',
                                                      'send', file, bw="0_25_18_13", min=0, max=45, subdir="p2p")


# Plots single client data for the measurements with 3 clients
def plot_data_total_3_clients(data):
    # Delet all previous plots while keeping the directories
    for single_file_dir in os.listdir("plots/"):
        if single_file_dir != "complete_measurement":
            dir = Path("plots/") / single_file_dir

            if dir.is_dir():
                for plot in dir.glob("*"):
                    if plot.is_file():
                        plot.unlink()
                    else:
                        shutil.rmtree(str(plot))

    #
    # Video recv
    #
    for file in data:
        for connection in data[file]:
            dict_data_1, list_labels_1 = get_data_for_keys_3clients(video_data_recv_1, data[file][connection])
            dict_data_2, list_labels_2 = get_data_for_keys_3clients(video_data_recv_2, data[file][connection])

            for ssrc in dict_data_1:
                plot_single.plot_media_stats_twin_y(list(dict_data_1[ssrc].values()), list_labels_1,
                                                    list(dict_data_2[ssrc].values()), list_labels_2,
                                                    "3clients", 'video', 'recv', file, bw="low_{0}".format(ssrc),
                                                    minl=0, maxl=600, minr=0, maxr=100, subdir="relay")

                plot_single.plot_media_stats_twin_y(list(dict_data_1[ssrc].values()), list_labels_1,
                                                    list(dict_data_2[ssrc].values()), list_labels_2,
                                                    "3clients", 'video', 'recv', file, bw="high_{0}".format(ssrc),
                                                    minl=0, maxl=1300, minr=0, maxr=100, subdir="relay")

    #
    # Video send
    #
    for file in data:
        for connection in data[file]:
            dict_data_1, list_labels_1 = get_data_for_keys_3clients(video_data_send_1, data[file][connection])
            dict_data_2, list_labels_2 = get_data_for_keys_3clients(video_data_send_2, data[file][connection])
            for ssrc in dict_data_1:
                plot_single.plot_media_stats_twin_y(list(dict_data_1[ssrc].values()), list_labels_1,
                                                    list(dict_data_2[ssrc].values()), list_labels_2,
                                                    "3clients", 'video', 'send', file, bw="low_{0}".format(ssrc),
                                                    minl=0, maxl=600, minr=0, maxr=100, subdir="relay")

                plot_single.plot_media_stats_twin_y(list(dict_data_1[ssrc].values()), list_labels_1,
                                                    list(dict_data_2[ssrc].values()), list_labels_2,
                                                    "3clients", 'video', 'send', file, bw="high_{0}".format(ssrc),
                                                    minl=0, maxl=1900, minr=0, maxr=100, subdir="relay")

    #
    # Audio recv
    #
    for file in data:
        for connection in data[file]:
            dict_data_1, list_labels_1 = get_data_for_keys_3clients(audio_data_recv_1, data[file][connection])
            dict_data_2, list_labels_2 = get_data_for_keys_3clients(audio_data_recv_2, data[file][connection])
            for ssrc in dict_data_1:
                plot_single.plot_media_stats_twin_y(list(dict_data_2[ssrc].values()), list_labels_2,
                                                    list(dict_data_1[ssrc].values()), list_labels_1,
                                                    "3clients", 'audio', 'recv', file, bw="low_{0}".format(ssrc),
                                                    minl=0, maxl=1100, minr=0, maxr=60, subdir="relay")

                plot_single.plot_media_stats_twin_y(list(dict_data_2[ssrc].values()), list_labels_2,
                                                    list(dict_data_1[ssrc].values()), list_labels_1,
                                                    "3clients", 'audio', 'recv', file, bw="high_{0}".format(ssrc),
                                                    minl=0, maxl=800, minr=0, maxr=60, subdir="relay")

    #
    # Audio send
    #
    for file in data:
        for connection in data[file]:
            dict_data_1, list_labels_1 = get_data_for_keys_3clients(audio_data_send_1, data[file][connection])
            for ssrc in dict_data_1:
                plot_single.plot_media_stats_single_y(list(dict_data_1[ssrc].values()), list_labels_1,
                                                      "3clients", 'audio', 'send', file, bw="low_{0}".format(ssrc),
                                                      min=0, max=30, subdir="relay")

                plot_single.plot_media_stats_single_y(list(dict_data_1[ssrc].values()), list_labels_1,
                                                      "3clients", 'audio', 'send', file, bw="high_{0}".format(ssrc),
                                                      min=0, max=45, subdir="relay")
