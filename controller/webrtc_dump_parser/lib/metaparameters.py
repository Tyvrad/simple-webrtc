import math
import numpy as np

#
# File to do all the calculation of metaparameters
#


# measurement_data = dict containing one entry for each logfile
def add_metaparameters(measurement_data: dict, dict_media_directions: dict = {}):
    # For all files
    # For all connections in all files calculate the metaparameters

    #
    # 2 clients
    #
    if dict_media_directions == {}:
        for file in measurement_data:

            # Get data for both files
            # Data for which metaparameters are calculated
            local_file = measurement_data[file]
            # Data from other side is sometimes needed
            remote_file = _get_remote_file(measurement_data, local_file)

            for connection in local_file:
                local_data = local_file[connection]
                # Get corresponding connection at the other end
                remote_data = _get_remote_connection_data(remote_file, connection)

                # Utility parameters
                #
                measurement_data[file][connection]["1_way_delay_audio_send"] = \
                    calculate_1_way_delay_audio_send(local_data)
                measurement_data[file][connection]["1_way_delay_video_send"] = \
                    calculate_1_way_delay_video_send(local_data)
                measurement_data[file][connection]["ear_ear_delay_audio_send"] = \
                    calculate_ear_ear_delay_audio_send(local_data, remote_data)

                measurement_data[file][connection]["audio_recv_kbitsReceivedPerSecond"] = \
                    bit_to_kbit(local_data, "audio_recv_bitsReceivedPerSecond")

                measurement_data[file][connection]["video_recv_kbitsReceivedPerSecond"] = \
                    bit_to_kbit(local_data, "video_recv_bitsReceivedPerSecond")

                measurement_data[file][connection]["audio_packet_loss_percentage_send"] = calculate_audio_pl(local_data)

                # KPI Audiosync
                measurement_data[file][connection]["e_model_audio_send"] = \
                    calculate_e_model(local_data, remote_data)
                measurement_data[file][connection]["kpi_audio_synchronization"] = \
                    calculate_e_model_mos(local_data)

                # KPI Videosync
                v_delay, v_sync_kpi = calculate_video_synchronization(local_data, remote_data)
                measurement_data[file][connection]["eye_eye_delay_video_send"] = v_delay
                measurement_data[file][connection]["kpi_video_synchronization"] = v_sync_kpi

                # KPI AVSync
                av_delay, av_delay_kpi = calculate_av_synchronization_recv(local_data, remote_data)
                measurement_data[file][connection]["av_delay_send"] = av_delay
                measurement_data[file][connection]["kpi_av_synchronization"] = av_delay_kpi

                # KPI Resolution
                l_max_res, l_kpi_res, l_max_res_norm, l_kpi_res_norm = calculate_resolution_kpi(local_data)
                # Normal
                measurement_data[file][connection]["kpi_resolution_stability"] = l_kpi_res
                measurement_data[file][connection]["max_resolution_percentage"] = l_max_res
                # Max width = 960
                measurement_data[file][connection]["kpi_resolution_stability_norm"] = l_kpi_res_norm
                measurement_data[file][connection]["max_resolution_percentage_norm"] = l_max_res_norm

                # KPI FPS
                measurement_data[file][connection]["kpi_fps_stability"] = calculate_fps_kpi(local_data)

                #KPI QAudio
                measurement_data[file][connection]["kpi_q_audio"] = calculate_qaudio_kpi(local_data)

                # KPI QVideo
                measurement_data[file][connection]["kpi_q_video"] = calculate_qvideo_kpi(local_data)

                # FINAL STEP
                # not smooth
                measurement_data[file][connection]["qoe_simple_normal"] = calculate_qoe(local_data, connection)
                measurement_data[file][connection]["qoe_simple_smooth"] = calculate_qoe(local_data, connection, True)  # Ignores KPI_Qaudio to achieve more accurate results


        return measurement_data
    #
    # 3 clients
    #
    else:
        for file in measurement_data:
            dict_send_ssrcs = dict()

            for entry in dict_media_directions[file]:
                # We distinguish between different media directions, so we can find the corresponding sender/receiver
                if dict_media_directions[file][entry] == "audio_recv":
                    dict_receiver_data, dict_sender_data = get_data_receivers({'audio_recv': entry},
                                                                              dict_media_directions,
                                                                              measurement_data)

                    for connection in measurement_data[file]:
                        # Utility
                        measurement_data[file][connection]["audio_recv_kbitsReceivedPerSecond_{0}".format(entry)] = \
                            bit_to_kbit(dict_receiver_data[file], "audio_recv_bitsReceivedPerSecond")

                        # KPI Qaudio
                        measurement_data[file][connection]["kpi_q_audio_{0}".format(entry)] = \
                            calculate_qaudio_kpi(dict_receiver_data[file])


                elif dict_media_directions[file][entry] == "video_recv":
                    dict_receiver_data, dict_sender_data = get_data_receivers({'video_recv': entry}, dict_media_directions,
                                                                              measurement_data)

                    for connection in measurement_data[file]:
                        # Utility
                        measurement_data[file][connection]["video_recv_kbitsReceivedPerSecond_{0}".format(entry)] = \
                            bit_to_kbit(dict_receiver_data[file], "video_recv_bitsReceivedPerSecond")
                        # Add to working data, as it's needed for qvideo kpi
                        dict_receiver_data[file]["video_recv_kbitsReceivedPerSecond"] = \
                            bit_to_kbit(dict_receiver_data[file], "video_recv_bitsReceivedPerSecond")

                        # KPI resolution
                        l_max_res, l_kpi_res, l_max_res_norm, l_kpi_res_norm = calculate_resolution_kpi(dict_receiver_data[file])

                        measurement_data[file][connection]['kpi_resolution_stability_{0}'.format(entry)] = \
                            l_kpi_res
                        measurement_data[file][connection]['max_resolution_percentage_{0}'.format(entry)] = \
                            l_max_res

                        measurement_data[file][connection]['kpi_resolution_stability_norm_{0}'.format(entry)] = \
                            l_kpi_res
                        measurement_data[file][connection]['max_resolution_percentage_norm_{0}'.format(entry)] = \
                            l_max_res

                        # KPI fps
                        measurement_data[file][connection]['kpi_fps_stability_{0}'.format(entry)] = \
                            calculate_fps_kpi(dict_receiver_data[file])

                        # KPI QVideo
                        measurement_data[file][connection]["kpi_q_video_{0}".format(entry)] = \
                            calculate_qvideo_kpi(dict_receiver_data[file])

                elif dict_media_directions[file][entry] == "audio_send" or \
                        dict_media_directions[file][entry] == "video_send":
                    # The both send ssrcs are handled together

                    # Collect audio_send and video_send ssrc
                    dict_send_ssrcs[dict_media_directions[file][entry]] = entry

                    if len(dict_send_ssrcs) != 2:
                        continue

                    # Get a separate dict for every receiver
                    # Sender data contains data for all streams sent to the receiver
                    dict_receiver_data, dict_sender_data = get_data_receivers(dict_send_ssrcs, dict_media_directions,
                                                                              measurement_data)

                    # Counter to distinguish between receiver 1 und 2
                    i_nreceiver = 0

                    # Calculate values for each receiver
                    for receiver in dict_receiver_data:
                        # Hacky way to access the single connection
                        for connection in measurement_data[file]:
                            # Utility
                            measurement_data[file][connection][
                                '1_way_delay_audio_send_{0}_{1}'.format(entry, i_nreceiver)] = \
                                calculate_1_way_delay_audio_send(dict_sender_data)

                            measurement_data[file][connection][
                                '1_way_delay_video_send_{0}_{1}'.format(entry, i_nreceiver)] = \
                                calculate_1_way_delay_video_send(dict_sender_data)

                            measurement_data[file][connection][
                                "ear_ear_delay_audio_send_{0}_{1}".format(entry, i_nreceiver)] = \
                                calculate_ear_ear_delay_audio_send(dict_sender_data, dict_receiver_data[receiver])
                            measurement_data[file][connection][
                                "audio_packet_loss_percentage_send_{0}_{1}".format(entry, i_nreceiver)] = calculate_audio_pl(dict_sender_data)

                            # KPI Audiosync
                            list_e_audio = calculate_e_model(dict_sender_data, dict_receiver_data[receiver])

                            measurement_data[file][connection][
                                'e_model_audio_send_{0}_{1}'.format(entry, i_nreceiver)] = \
                                list_e_audio
                            measurement_data[file][connection][
                                'kpi_audio_synchronization_{0}_{1}'.format(entry, i_nreceiver)] = \
                                calculate_e_model_mos({'e_model_audio_send': list_e_audio})

                            # KPI Videosync
                            v_delay, v_sync_kpi = calculate_video_synchronization(dict_sender_data,
                                                                                  dict_receiver_data[receiver])
                            measurement_data[file][connection][
                                "eye_eye_delay_video_send_{0}_{1}".format(entry, i_nreceiver)] = v_delay
                            measurement_data[file][connection][
                                "kpi_video_synchronization_{0}_{1}".format(entry, i_nreceiver)] = v_sync_kpi

                            # KPI AVSync
                            av_delay, av_delay_kpi = calculate_av_synchronization_recv(dict_sender_data,
                                                                                       dict_receiver_data[receiver])
                            measurement_data[file][connection][
                                "av_delay_send_{0}_{1}".format(entry, i_nreceiver)] = av_delay
                            measurement_data[file][connection][
                                "kpi_av_synchronization_{0}_{1}".format(entry, i_nreceiver)] = av_delay_kpi

                            i_nreceiver = i_nreceiver + 1

        return measurement_data


# 3 client only: ssrcs are still in the data - this function removes them and packs the relevant data in a new dict
# This is done for the sender as well as for all receivers of the given stream
# Returns a dict containing all receiver data for the given ssrc_send
def get_data_receivers(ssrcs_send, dict_media_directions, measurement_data):

    list_receivers = list()

    # Might be unnecessary
    fn_sender = ""

    # Find all files where ssrc_send is received
    for file in dict_media_directions:
        for sent_stream in ssrcs_send:
            if ssrcs_send[sent_stream] in dict_media_directions[file]:
                if 'recv' in dict_media_directions[file][ssrcs_send[sent_stream]]:
                    list_receivers.append(file)
                elif 'send' in dict_media_directions[file][ssrcs_send[sent_stream]]:
                    fn_sender = file

    # Remove duplicates
    list_receivers = list(set(list_receivers))

    dict_receiver_data = dict()
    dict_sender_data = dict()

    # Get the data
    for file in measurement_data:
        # Receiver data
        if file in list_receivers:
            file_data = measurement_data[file]
            dict_receiver_data[file] = dict()

            for connection in file_data:
                dict_receiver_data[file]['timestamp'] = file_data[connection]['timestamp']
                for entry in file_data[connection]:
                    # Copy all data that was received from our sender
                    if any(ssrcs_send[media] in entry for media in ssrcs_send):
                        # Save relevant data series minus the ssrc into a new dict
                        dict_receiver_data[file][entry[:entry.rfind("_")]] = file_data[connection][entry]

        # Sender data
        else:
            file_data = measurement_data[file]
            for connection in file_data:
                dict_sender_data['timestamp'] = file_data[connection]['timestamp']
                for entry in file_data[connection]:
                    # Get all the send data
                    if any(ssrcs_send[media] in entry for media in ssrcs_send):
                        # Save relevant data series minus the ssrc into a new dict
                        dict_sender_data[entry[:entry.rfind("_")]] = file_data[connection][entry]

    return dict_receiver_data, dict_sender_data


# Calculates a simplified e-model value (for the sender)
def calculate_e_model(local_data, remote_data):
    # local_data = local_file[connection]

        # Voice Over IP Performance Monitoring
        # https://www.researchgate.net/profile/Robert_Cole15/publication/234779571_Voice_Over_IP_Performance_Monitoring/links/57f3c64d08ae886b897dc7a0/Voice-Over-IP-Performance-Monitoring.pdf
        # equation R = 94.2 - I_d - I_ef

        # I_d = 0.024 * d + 0.11(d - 177.3) * H(d - 177.3)
        # d = audio_send/recv_googRtt / 2 (Half rtt)
        # H(x) = step-function
        #   H(x) = 0 if x < 0
        #   H(x) = 1 if x >= 0

        # Utility functions:
    def get_H(x):
        if x < 0:
            return 0
        else:
            return 1

    def get_I_d(index):
        # d = rtt/2
        try:
            d = (local_data['audio_send_googRtt'][index] / 2) + remote_data['audio_recv_googJitterBufferMs'][index]
        except:
            d = 100000
        if d < 0:
            d = 100000 # Fallback, causes a horrific e-value which is ignored later
        d_ret = 0.024 * d + 0.11 * (d - 177.3) * get_H(d - 177.3)
        return d_ret

    def get_I_ef(index):
        # Calculate packet loss
        loss = 0
        if index > 0:
            try:
                # Packets lost since last second
                lost_packets = local_data['audio_send_packetsLost'][index] - local_data['audio_send_packetsLost'][index - 1]
                if lost_packets < 0:
                    lost_packets = 0
                # Effective packet loss
                loss = lost_packets / local_data['audio_send_packetsSentPerSecond'][index]
            except:
                loss = 1

        # Parameters for G729a codec
        d_ret = 0 + 30 * math.log(1 + loss, math.e)
        return d_ret

    # Actual calculation:
    list_e = []

    for i in range(len(local_data['timestamp']) - 1):
        e = 94.2 - get_I_d(i) - get_I_ef(i)

        # Indicator for missing value somewhere -> skip
        if e < -10000:
            continue
        elif e < 0:
            e = 0

        list_e.append(e)

    return list_e


def calculate_audio_pl(local_data):

    list_pl = list()

    for i in range(len(local_data['timestamp']) - 1):
        try:
            # Packets lost since last second
            lost_packets = local_data['audio_send_packetsLost'][i] - local_data['audio_send_packetsLost'][i - 1]
            if lost_packets < 0:
                lost_packets = 0
            # Effective packet loss
            loss = (lost_packets / local_data['audio_send_packetsSentPerSecond'][i]) * 100
            list_pl.append(loss)
        except:
            a = 1

    return list_pl


# Calculates the MOS scores corresponding to the e-model values (see calculate_e_model for reference)
def calculate_e_model_mos(local_data):
    # local_data = local_file[connection]

    # Actual calculation:
    list_mos = []

    for i in range(len(local_data['e_model_audio_send'])):
        e = local_data["e_model_audio_send"][i]

        mos = -1

        if e < 0:
            mos = 1
        elif e > 100:
            mos = 4.5
        else:
            mos = 1 + 0.035 * e + (7 * pow(10, -6)) * e * (e-60) * (100 - e)

        list_mos.append(mos)

    return list_mos


# Calculates the one way delay of the audio send ssrc
def calculate_1_way_delay_audio_send(local_data):
    list_delay = []
    for i in range(len(local_data['audio_send_googRtt'])):
        list_delay.append(local_data['audio_send_googRtt'][i] / 2)

    return list_delay


# Calculates the ear to ear delay of the sent audio stram
def calculate_ear_ear_delay_audio_send(local_data, remote_data):
    list_ee_delay = []
    len_sender = len(local_data['timestamp'])
    len_receiver = len(remote_data['timestamp'])

    for i in range(min([len_sender, len_receiver])):

        delay = (local_data['audio_send_googRtt'][i] / 2) + remote_data['audio_recv_googJitterBufferMs'][i]

        list_ee_delay.append(delay)

    return list_ee_delay


# Calculates the one way delay for the sent video
def calculate_1_way_delay_video_send(local_data):
    list_delay = []
    for i in range(len(local_data['video_send_googRtt'])):
        list_delay.append(local_data['video_send_googRtt'][i] / 2)

    return list_delay


# Parses the key in local data to the next magnitude (bit->kbit->mbit)
def bit_to_kbit(local_data, key):

    list_kbit = list()

    for i in local_data[key]:

        kbit = int(i / 1024)
        list_kbit.append(kbit)

    return list_kbit


# Calculates the video synchronization (for the sender)
def calculate_video_synchronization(local_data, remote_data):
    # Necessary: sender googRtt + receiver googJitterBufferMs
    # Actual video delay
    list_sync = list()
    # Resulting KPI
    list_sync_kpi = list()

    len_sender = len(local_data['timestamp'])
    len_receiver = len(remote_data['timestamp'])

    for i in range(min([len_sender, len_receiver])):

        delay = (local_data['video_send_googRtt'][i] / 2) + remote_data['video_recv_googJitterBufferMs'][i]

        kpi = -1
        if delay < 100:
            kpi = 5
        elif 100 < delay < 400:
            kpi = 5 - ((delay - 100) / 100) * (4/3)
        else:
            kpi = 1

        list_sync.append(delay)
        list_sync_kpi.append(kpi)

    return list_sync, list_sync_kpi


# Calculates the audio-video synchronization (for the sender)
def calculate_av_synchronization_recv(local_data, remote_data):
    len_sender = len(local_data['timestamp'])
    len_receiver = len(remote_data['timestamp'])

    list_avsync = list()
    list_avsync_kpi = list()

    for i in range(min([len_sender, len_receiver])):
        delay_video = (local_data['video_send_googRtt'][i] / 2) + remote_data['video_recv_googJitterBufferMs'][i]
        delay_audio = (local_data['audio_send_googRtt'][i] / 2) + remote_data['audio_recv_googJitterBufferMs'][i]

        # Positive if delay video smaller than delay audio -> video arrives earlier
        delay_difference = delay_audio - delay_video
        kpi = -1

        if delay_difference <= -185:
            kpi = 1
        elif -185 < delay_difference < -125:
            kpi = ((delay_difference + 125) / 60) * 4 + 5
        elif -125 <= delay_difference <= 45:
            kpi = 5
        elif 45 < delay_difference < 90:
            kpi = 5 - ((delay_difference - 45) / 50) * 4
        elif 90 <= delay_difference:
            kpi = 1

        list_avsync.append(delay_difference)
        list_avsync_kpi.append(kpi)

    return list_avsync, list_avsync_kpi


def calculate_resolution_kpi(local_data):
    # Maximum width
    max_width = max(local_data['video_recv_googFrameWidthReceived'])
    max_width_normalized = max_width
    if max_width >= 960:
        max_width_normalized = 960

    # Count the time spent on the highest resolution
    counter = 0
    counter_normalized = 0
    for i in local_data['video_recv_googFrameWidthReceived']:
        if i == max_width:
            counter = counter + 1

        if i >= max_width_normalized:
            counter_normalized = counter_normalized + 1

    percentage_max_resolution = (counter / len(local_data['video_recv_googFrameWidthReceived'])) * 100
    percentage_max_resolution_normalized = (counter_normalized / len(local_data['video_recv_googFrameWidthReceived'])) * 100

    # Actual KPI
    kpi_resolution = 0.003 * math.pow(math.e, (0.064 * percentage_max_resolution)) + 2.498
    kpi_resolution_normalized = 0.003 * math.pow(math.e, (0.064 * percentage_max_resolution_normalized)) + 2.498

    list_percentage = [percentage_max_resolution] * len(local_data['timestamp'])
    list_kpi_resolution = [kpi_resolution] * len(local_data['timestamp'])

    list_percentage_normalized = [percentage_max_resolution_normalized] * len(local_data['timestamp'])
    list_kpi_resolution_normalized = [kpi_resolution_normalized] * len(local_data['timestamp'])

    return list_percentage, list_kpi_resolution, list_percentage_normalized, list_kpi_resolution_normalized


def calculate_fps_kpi(local_data):
    list_kpi = list()

    for fps in local_data['video_recv_googFrameRateOutput']:
        kpi = -1

        if fps < 2:
            kpi = 1
        elif 2 <= fps <= 30:
            kpi = 1.07504 * math.log(3.42171 * fps)
        else:
            kpi = 5

        list_kpi.append(kpi)

    return list_kpi


def calculate_qaudio_kpi(local_data):

    list_kpi = list()

    for i in local_data['audio_recv_bitsReceivedPerSecond']:

        # Kbit
        i = i / 1024

        kpi = -1

        if i < 9.6:
            kpi = 1
        elif 9.6 <= i < 16.0:
            kpi = 2
        elif 16.0 <= i < 24.0:
            kpi = 3
        elif 24.0 <= i <= 32.0:
            kpi = 4
        else:
            kpi = 5

        list_kpi.append(kpi)

    return list_kpi


def calculate_qvideo_kpi(local_data):

    list_kpi = list()

    for entry in range(len(local_data["timestamp"])):
        # Current resolution
        image_height = local_data["video_recv_googFrameHeightReceived"][entry]

        # Select right curve for the current resolution
        if image_height <= 396:
            list_bw = [0.13, 0.2, 0.5, 0.8, 1.5, 2.0]
            list_mos = [1.4, 1.8, 3.3, 3.7, 3.9, 3.8]

        elif 397 <= image_height <= 509:

            list_bw = [0.2, 0.5, 0.8, 1.5, 2.0]
            list_mos = [1.7, 3.35, 3.75, 3.8, 3.9]

        elif 510 <= image_height <= 653:

            list_bw = [0.5, 0.8, 1.5, 2.0, 2.5]
            list_mos = [3.2, 3.35, 4.0, 4.1, 4.1]

        elif 654 <= image_height <= 720:

            list_bw = [0.8, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
            list_mos = [3.1, 4.0, 3.9, 4.1, 4.15, 4.15, 4.25]

        else:
            raise NotImplementedError("Unknown frame height {0}".format(image_height))

        # Current bandwidth
        current_bw = round(local_data["video_recv_kbitsReceivedPerSecond"][entry] / 1024, 2)

        # Interpolate the value between the available dat
        kpi = np.interp(current_bw, list_bw, list_mos, left=-1, right=-1)

        if kpi != -1:
            list_kpi.append(kpi)

        # if kpi == -1:
        #     print("Discarding data points with bitrate {0} and height {1}".format(current_bw, image_height))
        # else:
        #     list_kpi.append(kpi)

    return list_kpi


def calculate_qoe(local_data, connection, smooth: bool = False):
    list_qoe = list()

    shortest_entry = min([len(ls) for ls in local_data.values()])
    for i in range(shortest_entry):

        # Relay
        if "RELAY" in connection:
            sync = (local_data['kpi_audio_synchronization'][i] + local_data['kpi_video_synchronization'][i] + local_data[
                'kpi_av_synchronization'][i]) / 3
            stab = 4.5
            if not smooth:
                qua = (2 + local_data['kpi_q_video'][i]) / 2
            else:
                qua = local_data['kpi_q_video'][i]

        # P2P
        else:
            sync = (local_data['kpi_audio_synchronization'][i] + local_data['kpi_video_synchronization'][i] + local_data[
                'kpi_av_synchronization'][i]) / 3
            stab = (2.5 + local_data['kpi_fps_stability'][i]) / 2
            if not smooth:
                qua = (2.5 + local_data['kpi_q_video'][i]) / 2
            else:
                qua = local_data['kpi_q_video'][i]

        qoe = (sync + stab + qua) / 3

        list_qoe.append(qoe)

    return list_qoe


# Returns the dict representing the other file during metaparameter calculation
def _get_remote_file(dict_measurement_data: dict, dict_current_file_info: dict):
    for entry in dict_measurement_data:
        if dict_measurement_data[entry] != dict_current_file_info:
            return dict_measurement_data[entry]


# Returns the current connection dict during metaparameter connection
def _get_remote_connection_data(dict_file_infos, str_current_connection: str):
    for connection in dict_file_infos:
        if connection[:3] == str_current_connection[:3]:
            return dict_file_infos[connection]
