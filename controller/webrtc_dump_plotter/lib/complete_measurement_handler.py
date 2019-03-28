import os
import shutil
from time import time
import numpy as np
import scipy.stats

from definitions import *
from helpers import *

import plot_multiple
import plot_complete

list_ignored_keys = [
    "bweforvideo-googAvailableReceiveBandwidth",
    "video-googRtt",
    "video-bitsSentPerSecond",
    "video-bitsReceivedPerSecond",
    "timestamp"
]

#
# SESSION PLOTS (Parameter lists)
#
data_connection_send = ['audio_bitsSentPerSecond','audio_send_bitsSentPerSecond','video_send_bitsSentPerSecond','bweforvideo-googAvailableSendBandwidth']
data_connection_receive = ['audio_bitsReceivedPerSecond','audio_recv_bitsReceivedPerSecond','video_recv_bitsReceivedPerSecond']
data_video_send = ['video_send_googFrameHeightSent','video_send_googFrameWidthSent']

# KPI Audiosync
#
# E-model influencing factors
data_e_model_ee = ['1_way_delay_audio_send']
# data_e_model_pl = ['audio_send_packetsLost', 'audio_recv_googJitterBufferMs']
data_e_model_pl = ['audio_packet_loss_percentage_send', 'audio_recv_googJitterBufferMs']

# E-model MOS estimation plot
data_e_model_r = ['e_model_audio_send']
data_e_model_mos = ['kpi_audio_synchronization']

# KPI Videosync
#
data_kpi_videosync = ['kpi_video_synchronization']

# Videosync influencing parameters
data_kpi_videosync_ee = ["1_way_delay_video_send"]
data_kpi_videosync_buffer = ['video_recv_googJitterBufferMs']

# KPI AV-Sync
#
data_avsync_delay = ["av_delay_send"]
data_avsync_delay_influencing = ["ear_ear_delay_audio_send", "eye_eye_delay_video_send"]

data_kpi_avsync = ["kpi_av_synchronization"]
# KPI Resolution
#
data_kpi_resolution_dbl = ["kpi_resolution_stability", "kpi_resolution_stability_norm"]
data_kpi_resolution_percentage_dbl = ["max_resolution_percentage", "max_resolution_percentage_norm"]

data_kpi_resolution = ["kpi_resolution_stability"]
data_kpi_resolution_percentage = ["max_resolution_percentage"]
data_kpi_resolution_width = ["video_recv_googFrameWidthReceived"]

# KPI fps
#
data_kpi_fps = ["kpi_fps_stability"]
data_kpi_fps_influencing = ["video_recv_googFrameRateOutput"]

# KPI QAudio
#
data_qaudio = ["kpi_q_audio"]
data_qaudio_influencing = ["audio_recv_kbitsReceivedPerSecond"]

# KPI QVideo
#
data_qvideo = ["kpi_q_video"]
data_qvideo_influencing = ["video_recv_kbitsReceivedPerSecond"]
data_qvideo_influencing_2 = ["video_recv_googFrameHeightReceived"]

# QoE simple
#
data_qoe_simple = ["qoe_simple_normal"]
data_qoe_simple_smooth = ["qoe_simple_smooth"]


# Load data for measurement configuration
def load_data_complete_measurement(str_path, filename):
    dict_data_complete = {}
    dict_data_avg = {}
    dict_data_errors = {}

    dict_combined = {}
    dict_combined["average"] = dict_data_avg
    dict_combined["errors"] = dict_data_errors
    dict_combined["aggregated"] = dict_data_complete


    list_filenames = []

    for measurement in os.listdir(str_path):
        list_filenames.append(os.path.join(str_path, measurement, filename))

    for avg_file in list_filenames:
        if not os.path.isfile(avg_file):
            print("ERROR: File '{0}' does not exist".format(avg_file))
            return {}
        with open(avg_file, 'r') as file:
            for line in file:
                values = line.split(",")
                key = values[0]
                values.pop(0)
                try:
                    values = list(map(float, values))
                except:
                    continue
                if key in dict_data_complete:
                    dict_data_complete[key].extend(values)
                else:
                    tmp = []
                    tmp.extend(values)
                    dict_data_complete[key] = tmp

    for key in dict_data_complete:
        # if key == "video_recv_googJitterBufferMs":
        #     print("stop")
        avg, error = mean_confidence_interval(dict_data_complete[key])

        dict_data_errors[key] = error
        dict_data_avg[key] = avg

    return dict_combined


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)

    return m, h


def plot_all_data_avg():
    str_base_path_orig = str(PATH_OUTPUT_COMPLETE)

    str_base_path_output_complete = str(PATH_OUTPUT_COMPLETE) + '/P2P/'
    str_base_path_output_complete_cdf = os.path.join(str_base_path_output_complete + "/cdf/")
    str_base_path_output_complete_multiple = os.path.join(str_base_path_output_complete + "/multiple/")

    dict_p2pdata, list_bw = plot_data_avg('aggregated_data_P2P.csv')

    move_data_to_parent_directory(PATH_OUTPUT_COMPLETE, "P2P")


    str_base_path_output_complete = str_base_path_orig + '/RELAY/'
    str_base_path_output_complete_cdf = os.path.join(str_base_path_output_complete + "/cdf/")
    str_base_path_output_complete_multiple = os.path.join(str_base_path_output_complete + "/multiple/")

    dict_relaydata, list_bw = plot_data_avg('aggregated_data_RELAY.csv')

    move_data_to_parent_directory(PATH_OUTPUT_COMPLETE, "RELAY")

    shutil.rmtree(str(PATH_OUTPUT_COMPLETE))
    os.makedirs(str(PATH_OUTPUT_COMPLETE))
    os.rename(str(PATH_OUTPUT / "P2P"), str(PATH_OUTPUT_COMPLETE / "P2P"))
    os.rename(str(PATH_OUTPUT / "RELAY"), str(PATH_OUTPUT_COMPLETE / "RELAY"))

    #####
    #####
    ## Special complete measurement plot
    #####
    #####

    plot_combined_session(dict_p2pdata, dict_relaydata, list_bw)


# Plotter for entire measurements
def plot_data_avg(filename):
    dict_all_data = {}

    # Load data
    for bandwidth in os.listdir(PATH_DATA_COMPLETE):
        dict_aggregated_configuration = load_data_complete_measurement(os.path.join(PATH_DATA_COMPLETE, bandwidth), filename)
        if dict_aggregated_configuration["average"] == {}:
            print("{0} - No data for bandwidth {1}".format(filename, bandwidth))
            return {}, {}
            # raise FileNotFoundError("No data for bandwidth {0}".format(bandwidth))
        dict_all_data[bandwidth] = dict_aggregated_configuration

    list_bw = []
    for key in dict_all_data:
        i_bw = float(key[3:])
        list_bw.append(i_bw)
    list_bw.sort()

    if os.path.isdir(PATH_OUTPUT_COMPLETE):
        shutil.rmtree(PATH_OUTPUT_COMPLETE)
    os.mkdir(PATH_OUTPUT_COMPLETE)

    if os.path.isdir(PATH_OUTPUT_COMPLETE_CDF):
        shutil.rmtree(PATH_OUTPUT_COMPLETE_CDF)
    os.mkdir(PATH_OUTPUT_COMPLETE_CDF)

    if os.path.isdir(PATH_OUTPUT_COMPLETE_MULTIPLE):
        shutil.rmtree(PATH_OUTPUT_COMPLETE_MULTIPLE)
    os.mkdir(PATH_OUTPUT_COMPLETE_MULTIPLE)

    dict_bwplot_avg = {}
    dict_bwplot_errors = {}

    # for key in plot_keys:
    num_parameters = len(dict_aggregated_configuration["average"])
    i_current = 0

    for key in dict_aggregated_configuration["average"]:
        i_current = i_current + 1
        print("Plotting {0}/{1}".format(i_current, num_parameters))
        if key in list_ignored_keys:
            continue

        list_avg = []
        list_errors = []

        # CDF
        dict_cdf_data = {}
        list_keys = []

        idx = 0
        for bw in list_bw:
            str_key = "bw_"
            if bw < 1:
                str_key += str(bw)
            else :
                str_key += str(int(bw))


            # Normal plot
            list_avg.append(dict_all_data[str_key]["average"][key])
            list_errors.append(dict_all_data[str_key]["errors"][key])

            # CDF
            dict_cdf_data[str_key] = dict_all_data[str_key]["aggregated"]
            list_keys.append(str_key)

            idx += 1

        start = time()

        # Single data line plots
        plot_multiple.plot_avg_values_measurement(list_avg, list_errors, key, list_bw)
        plot_multiple.plot_cdf_measurement(dict_cdf_data, key, list_keys)

        end = time()
        duration1 = end - start
        print("Plotting took {:.2f}s".format(duration1))

        dict_bwplot_avg[key] = list_avg
        dict_bwplot_errors[key] = list_errors

    #
    # Actual fancy plots
    #
    start = time()

    phase = ""
    if "RELAY" in filename:
        phase = "_relay"
    else:
        phase = "_p2p"

    # KPI audiosync
    plot_multiple.plot_avg_values_measurement_multiple_twiny(dict_bwplot_avg, dict_bwplot_errors, data_e_model_ee,
                                                             data_e_model_pl, "e_model_influencing{0}".format(phase), list_bw, minl=0, minr=0, maxr=300)
    plot_multiple.plot_avg_values_measurement_multiple_twiny(dict_bwplot_avg, dict_bwplot_errors, data_e_model_r,
                                                             data_e_model_mos, "e_model_mos{0}".format(phase), list_bw, minl=0, maxl=100, minr=0, lowlegend=True)

    # KPI videosync
    plot_multiple.plot_avg_values_measurement_multiple(dict_bwplot_avg, dict_bwplot_errors, data_kpi_videosync,
                                                       "kpi_videosync{0}".format(phase), list_bw, min=0, max=6)

    plot_multiple.plot_avg_values_measurement_multiple_twiny(dict_bwplot_avg, dict_bwplot_errors, data_kpi_videosync_ee,
                                                             data_kpi_videosync_buffer, "kpi_videosync_influencing{0}".format(phase), list_bw, minl=0, maxl=2000, minr=0, maxr=300)
    plot_multiple.plot_avg_values_measurement_multiple_twiny(dict_bwplot_avg, dict_bwplot_errors, data_kpi_videosync_ee,
                                                             data_kpi_videosync_buffer,
                                                             "kpi_videosync_influencing_3clients{0}".format(phase), list_bw,
                                                             minl=0, minr=0, maxr=150)

    # KPI AVsync
    plot_multiple.plot_avg_values_measurement_multiple(dict_bwplot_avg, dict_bwplot_errors, data_kpi_avsync,
                                                       "kpi_avsync{0}".format(phase), list_bw, min=0, max=6)

    plot_multiple.plot_avg_values_measurement_multiple(dict_bwplot_avg, dict_bwplot_errors, data_avsync_delay,
                                                       "kpi_avsync{0}_delay".format(phase), list_bw)

    plot_multiple.plot_avg_values_measurement_multiple(dict_bwplot_avg, dict_bwplot_errors, data_avsync_delay_influencing,
                                                       "kpi_avsync{0}_influencing".format(phase), list_bw, max=2400)

    plot_multiple.plot_avg_values_measurement_multiple_twiny(dict_bwplot_avg, dict_bwplot_errors, data_avsync_delay, data_avsync_delay_influencing,
                                                       "kpi_avsync{0}_influencing2".format(phase), list_bw)

    # KPI Resolution
    # Both KPI (normal and norm)
    plot_multiple.plot_avg_values_measurement_multiple(dict_bwplot_avg, dict_bwplot_errors, data_kpi_resolution_dbl,
                                                       "kpi_resolution_dbl", list_bw, min=0, max=6)
    plot_multiple.plot_avg_values_measurement_multiple(dict_bwplot_avg, dict_bwplot_errors, data_kpi_resolution_percentage_dbl,
                                                       "kpi_resolution_percentage_dbl", list_bw, min=0, max=125)
    # Only the normal KPI
    plot_multiple.plot_avg_values_measurement_multiple(dict_bwplot_avg, dict_bwplot_errors, data_kpi_resolution,
                                                       "kpi_resolution", list_bw, min=0, max=6)
    plot_multiple.plot_avg_values_measurement_multiple(dict_bwplot_avg, dict_bwplot_errors,
                                                       data_kpi_resolution_percentage,
                                                       "kpi_resolution_percentage", list_bw, min=0, max=125)
    # Frame width received
    plot_multiple.plot_avg_values_measurement_multiple(dict_bwplot_avg, dict_bwplot_errors,
                                                       data_kpi_resolution_width,
                                                       "kpi_resolution_width", list_bw, max=700)

    # KPI fps
    #
    plot_multiple.plot_avg_values_measurement_multiple(dict_bwplot_avg, dict_bwplot_errors,
                                                       data_kpi_fps,
                                                       "kpi_fps{0}".format(phase), list_bw, min=0, max=6)

    plot_multiple.plot_avg_values_measurement_multiple(dict_bwplot_avg, dict_bwplot_errors,
                                                       data_kpi_fps_influencing,
                                                       "kpi_fps{0}_influencing".format(phase), list_bw, min=15, max=65)

    # KPI QAudio
    #
    plot_multiple.plot_avg_values_measurement_multiple(dict_bwplot_avg, dict_bwplot_errors,
                                                       data_qaudio,
                                                       "kpi_qaudio{0}".format(phase), list_bw, min=0, max=6)

    plot_multiple.plot_avg_values_measurement_multiple(dict_bwplot_avg, dict_bwplot_errors,
                                                       data_qaudio_influencing,
                                                       "kpi_qaudio_influencing{0}".format(phase), list_bw, min=5, max=40)

    # KPI QVideo
    #
    plot_multiple.plot_avg_values_measurement_multiple(dict_bwplot_avg, dict_bwplot_errors, data_qvideo, "kpi_qvideo",
                                                       list_bw, min=0, max=6)

    plot_multiple.plot_avg_values_measurement_multiple(dict_bwplot_avg, dict_bwplot_errors, data_qvideo_influencing,
                                                       "kpi_qvideo_influencing_relay", list_bw, min=0, max=1300)
    plot_multiple.plot_avg_values_measurement_multiple(dict_bwplot_avg, dict_bwplot_errors, data_qvideo_influencing,
                                                       "kpi_qvideo_influencing_p2p", list_bw, min=0, max=2700)

    # Optimized for P2P
    plot_multiple.plot_avg_values_measurement_multiple_twiny(dict_bwplot_avg, dict_bwplot_errors,
                                                             data_qvideo_influencing, data_qvideo_influencing_2,
                                                             "kpi_qvideo_influencing_dbl_p2p", list_bw, minl=0, maxl=2700, minr=0, maxr=800)
    # Optimized for RELAY
    plot_multiple.plot_avg_values_measurement_multiple_twiny(dict_bwplot_avg, dict_bwplot_errors,
                                                             data_qvideo_influencing, data_qvideo_influencing_2,
                                                             "kpi_qvideo_influencing_dbl_relay", list_bw, minl=0, maxl=1300, minr=0, maxr=800)

    # Optimized for 3 clients
    plot_multiple.plot_avg_values_measurement_multiple_twiny(dict_bwplot_avg, dict_bwplot_errors,
                                                             data_qvideo_influencing, data_qvideo_influencing_2,
                                                             "kpi_qvideo_influencing_dbl_3clients", list_bw, minl=0,
                                                             maxl=700, minr=0, maxr=500)

    end = time()
    duration = end - start
    print("Fancy plotting took {:.2f} seconds".format(duration))

    return {"average": dict_bwplot_avg, "errors": dict_bwplot_errors}, list_bw
#

# Plot data from P2P and RELAY phase of entire measurements
def plot_combined_session(dict_p2p, dict_relay, list_bw):
    if dict_p2p == {} or dict_relay == {}:
        return

    # KPI videosync
    plot_complete.plot_single_x(dict_p2p, dict_relay, data_kpi_videosync, list_bw, "kpi_videosync", min=0, max=6.5)
    # KPI avsync
    plot_complete.plot_single_x(dict_p2p, dict_relay, data_kpi_avsync, list_bw, "kpi_avsync", min=0, max=6.5)
    # KPI fps
    plot_complete.plot_single_x(dict_p2p, dict_relay, data_kpi_fps, list_bw, "kpi_fps", min=0, max=6.5)
    # KPI qaudio
    plot_complete.plot_single_x(dict_p2p, dict_relay, data_qaudio, list_bw, "kpi_qaudio")
    # KPI qvideo
    plot_complete.plot_single_x(dict_p2p, dict_relay, data_qvideo, list_bw, "kpi_qvideo")
    plot_complete.plot_single_x(dict_p2p, dict_relay, data_qvideo_influencing, list_bw, "kpi_qvideo_influencing")
    plot_complete.plot_single_x(dict_p2p, dict_relay, data_qvideo_influencing_2, list_bw, "kpi_qvideo_influencing_2")

    # QoE simple
    plot_complete.plot_single_x(dict_p2p, dict_relay, data_qoe_simple, list_bw, "qoe_simple")
    plot_complete.plot_single_x(dict_p2p, dict_relay, data_qoe_simple_smooth, list_bw, "qoe_simple_smooth")

