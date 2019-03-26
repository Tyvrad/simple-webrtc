import json
import time
from datetime import datetime, timedelta

# Entries from the logfile which will be ignored
used_strings_audio = ['googCurrentDelayMs', 'googJitterBufferMs', 'googPreferredJitterBufferMs',
                    'packetsReceivedPerSecond', 'packetsSentPerSecond', 'kbitsRecievedPerSecond', 'googRtt', 'googJitterReceived', 'googActiveConnection']
used_strings_video = ['send-packetsLost', 'googPlisSent', 'bweforvideo-googBucketDelay', 'bitsSentPerSecond', 'googFrameWidth', 'googFrameHeight', 'googFrameRateSent',
                'packetsPerSecond', 'googRtt', 'bitsReceivedPerSecond', 'packetsReceivedPerSecond', 'packetsSentPerSecond', 'googInterframeDelayMax', 'googFrameRateReceived', 'googFrameRateOutput', 'googDecodeMs',
                'googplisreceived']
used_strings_context = ['googEncodeUsagePercent']
used_strings_network = ['googAvailableSendBandwidth', 'googAvailableReceiveBandwidth', 'ipAddress', 'googRemoteAddress', 'googLocalAddress']

unused_strings = ['Cand-', 'Channel', 'googCertificate', 'googTrack', 'Cand', 'Conn-video']

gi_parsed_files_count = 0


# Parses single file for a measurement with 2 clients
# Returns a dict with one entry per connection. Each entry contains several entries (ssrcs)
def parse_file_2_clients(filename):
    global gi_parsed_files_count
    gi_parsed_files_count += 1
    # Load file
    file = open(filename, 'r')
    data = json.load(file)
    file.close()

    # dict_connections will contain one entry for each connection
    dict_connections = {}

    ##
    # Step 1: Cleanup data and remove invalid connections
    ##

    # If the updatLog contains a message 'ICEConnectionStateConnected', we have a correctly est. P2P connection
    # Additionally, we search for the RELAY connection that was used before the P2P connection
    str_p2p_connection_name = ""
    str_relay_connection_name = ""

    dict_possible_relay_connections = {}

    # Search for the P2P connection + all other RELAY connections
    for connection in list(data['PeerConnections']):
        for log_message in data['PeerConnections'][connection]['updateLog']:
            if log_message['value'] == "ICEConnectionStateConnected":
                str_p2p_connection_name = connection
            if log_message['value'] == "ICEConnectionStateFailed":
                str_p2p_connection_name = ''

        # Add found RELAY connection to dict for later evaluation
        if data['PeerConnections'][connection]['constraints'] != '' and str_p2p_connection_name != connection:
            dict_possible_relay_connections[connection] = len(data['PeerConnections'][connection]['stats'])

    # Longest RELAY connection is the used one
    i_max = 0
    for key in dict_possible_relay_connections:
        if dict_possible_relay_connections[key] > i_max:
            i_max = dict_possible_relay_connections[key]
            str_relay_connection_name = key

    # If we find both (RELAY + P2P), we can delete all other connections (unused)
    if str_p2p_connection_name != "" and str_relay_connection_name != "":
        print("\tPeer 2 Peer + RELAY connection found!")
        for connection in list(data['PeerConnections']):
            if connection != str_p2p_connection_name and connection != str_relay_connection_name:
                del data['PeerConnections'][connection]

    else:
        # Returning here ensures we only get "clean" connections where the RTC connection is 100% established
        # print("Skipping file")
        return {}

    connections = len(data['PeerConnections'])
    print('Processing file: {0}'.format(filename))
    print('Number of valid connections: ' + str(len(data['PeerConnections'])))
    print("==========")

    ##
    # Step 2: Actual parsing
    ##
    for connection in list(data['PeerConnections']):
        # tmp receives the media direction dict from parse_connection. It is only needed in the 3 client case
        dict_data, tmp = parse_connection(data['PeerConnections'][connection]['stats'], connection, 2)
        del tmp

        if dict_data == {}:
            del connection
            continue

        # Adapt saving name
        str_key = connection
        if connection == str_p2p_connection_name:
            str_key = "P2P_" + str_key
        elif connection == str_relay_connection_name:
            str_key = "RELAY_" + str_key
        dict_connections[str_key] = dict_data

    # Ensure presence of all required entries
    if len(dict_connections) != 2:
        return {}

    ##
    # Step 3: Unify all data from all files
    ##

    # After the actual parsing, adapt the data from the different files, in order to match time-wise (both dicts
    # for both files cover the same time period)

    # Cut RELAY connection at beginning of P2P connection
    str_p2p_connection_key = "P2P_" + str_p2p_connection_name
    str_relay_connection_key = "RELAY_" + str_relay_connection_name

    index = -1
    # Find timestamp, where first kbit is sent on p2p connection
    for entry in dict_connections[str_p2p_connection_key]['audio_send_bitsSentPerSecond']:
        if entry > 0:
            index = dict_connections[str_p2p_connection_key]['audio_send_bitsSentPerSecond'].index(entry)
            break

    i_p2p_start_ts = dict_connections[str_p2p_connection_key]['timestamp'][index]
    del index

    i_index_relay = -1
    # Cut the RELAY connection accordingly
    for ts in dict_connections[str_relay_connection_key]['timestamp']:
        if ts == i_p2p_start_ts:
            i_index_relay = dict_connections[str_relay_connection_key]['timestamp'].index(ts)

    for key in dict_connections[str_relay_connection_key]:
        dict_connections[str_relay_connection_key][key] = dict_connections[str_relay_connection_key][key][
                                                          :i_index_relay + 1]

    return dict_connections

# Parses single file for a measurement with 3 clients
# Returns a dict with one connection that contains several ssrcs
def parse_file_3_clients(filename):
    global gi_parsed_files_count
    gi_parsed_files_count += 1
    # Load file
    file = open(filename, 'r')
    data = json.load(file)
    file.close()

    # Used to save the data
    dict_data = {}

    print('Processing file: {0}'.format(filename))
    print("==========")

    ##
    # Step 1: Cleanup data and remove unused connections
    ##
    str_valid_connection_name = ""
    for connection in list(data['PeerConnections']):
        # Data shows, an empty connection has 56 entries
        if len(data['PeerConnections'][connection]['stats']) <= 56:
            del data['PeerConnections'][connection]
        else:
            str_valid_connection_name = connection

    del connection

    if len(data['PeerConnections']) != 1:
        print ("ERROR: Too many connections!")
        return {}, {}

    dict_data, dict_media_directions = parse_connection(data['PeerConnections'][str_valid_connection_name]['stats'],
                                                       str_valid_connection_name, 3)

    dict_all_data = dict()
    # Comatibility with writer/plotter
    dict_all_data["RELAY_" + str_valid_connection_name] = dict_data

    return dict_all_data, dict_media_directions


def parse_connection(dict_connection_data, connection_name, i_n_clients):
    # dict_data_series contains all info for one connection
    dict_data_series = {}

    # Contains a list of all ssrcs and their respective type
    dict_ssrc_types = {}

    i_max_length = 0

    # 1: Get time reference
    str_start_timestamp = dict_connection_data['bweforvideo-googAvailableSendBandwidth'][
                              'startTime'][:19]
    str_end_timestamp = dict_connection_data['bweforvideo-googAvailableSendBandwidth'][
                            'endTime'][:19]
    start_datetime = datetime.strptime(str_start_timestamp, '%Y-%m-%dT%H:%M:%S')
    end_datetime = datetime.strptime(str_end_timestamp, '%Y-%m-%dT%H:%M:%S')

    # 2: Parse data series
    for stat in dict_connection_data:
        # Determine media type for each ssrc
        if 'mediaType' in stat:
            ssrc = stat.split('_')[1]
            type = dict_connection_data[stat]['values'][1:-1].split(',')[0]
            type = ''.join(filter(str.isalpha, type))

            dict_ssrc_types[ssrc] = type

        if not __check_do_write_key(stat):
            continue

        values = __get_int_array_for_stat_line_time_corr(dict_connection_data[stat],
                                                         start_datetime, end_datetime)
        # Only add values which have been properly parsed
        if len(values) > 0:
            dict_data_series[stat] = values
            i_max_length = max(i_max_length, len(dict_data_series[stat]))

    # 3: Get timestamp list for data
    array_timestamps = []
    for i in range(i_max_length):
        array_timestamps.append(int(time.mktime(start_datetime.timetuple())))
        start_datetime += timedelta(0, 1)
    start_datetime -= timedelta(0, 1)

    dict_data_series['timestamp'] = array_timestamps

    # 4: Associate each ssrc info with the type of the ssrc. Result: ssrc_1234_googSth_video
    all_ssrcs = []  # for next step
    for key in list(dict_data_series):
        if 'ssrc' in key:
            ssrc = key.split('_')[1]
            if ssrc not in all_ssrcs:
                all_ssrcs.append(ssrc)
            try:
                key_new = key + '_' + dict_ssrc_types[ssrc]
                dict_data_series[key_new] = dict_data_series[key]
                del dict_data_series[key]
            except KeyError:
                print("Key error!")

    # 5: Remove ssrcs which do not carry information (bitrate always 0)
    dict_valid_ssrcs = {}
    if len(all_ssrcs) == 0:
        print("No ssrcs found!")
        return {}

    for entry in all_ssrcs:
        dict_valid_ssrcs[entry] = False
    del entry

    for ssrc in all_ssrcs:
        b_no_bitrate = True
        for key in dict_data_series:
            if ssrc in key:
                if dict_ssrc_types[ssrc] == 'audio' and (
                                'bitsReceivedPerSecond' in key or 'bitsSentPerSecond' in key):
                    for entry in dict_data_series[key]:
                        if entry != 0 and entry != -1:
                            b_no_bitrate = False
                    dict_valid_ssrcs[ssrc] = not b_no_bitrate

                if dict_ssrc_types[ssrc] == 'video' and 'FrameWidth' in key:
                    for entry in dict_data_series[key]:
                        if entry != 0 and entry != -1:
                            b_no_bitrate = False
                    dict_valid_ssrcs[ssrc] = not b_no_bitrate

    del key, ssrc, entry

    # Find number of valid ssrcs
    i_valid_ssrcs = 0
    for ssrc in dict_valid_ssrcs:
        if dict_valid_ssrcs[ssrc] == False:
            for key in list(dict_data_series):
                if ssrc in key:
                    del dict_data_series[key]
        else:
            i_valid_ssrcs += 1

    # Ensure correct number of ssrcs (2 per client in session)
    if i_valid_ssrcs != i_n_clients * 2:
        if i_valid_ssrcs < (i_n_clients * 2):
            print("ERROR: Too few valid ssrcs!")
        else:
            print("ERROR: Too many valid ssrcs!")
        return {}, {}

    # 5: Count resolution changes
    for entry in list(dict_data_series):
        if 'googFrameWidth' in entry and '_video' in entry:
            list_resolution_changes = []
            i_resolution_changes = 0
            i_current_value = dict_data_series[entry][0]
            for value in dict_data_series[entry]:
                if value != i_current_value:
                    i_resolution_changes += 1
                    i_current_value = value

                list_resolution_changes.append(i_resolution_changes)

            str_key_name = entry.replace('googFrameWidth', 'resolutionChanges')
            dict_data_series[str_key_name] = list_resolution_changes

    # 6: Remove audio connections where googActiveConnection is false
    list_inactive_audio_connections = []
    # Find the connections
    for entry in dict_data_series:
        if "Conn-audio" in entry and "googActiveConnection" in entry:
            b_connection_active = False
            for value in dict_data_series[entry]:
                if value == "ru":
                    b_connection_active = True
                    break
            if b_connection_active == False:
                list_inactive_audio_connections.append(entry[:-21])

    # Delete the inactive connections
    for entry in list(dict_data_series):
        for audio_connection in list_inactive_audio_connections:
            if audio_connection in entry:
                del dict_data_series[entry]
                break

    # Remove activity information from active connections
    for entry in list(dict_data_series):
        if "googActiveConnection" in entry:
            del dict_data_series[entry]

    # 7 Save the information about the media direction (video send/recv) as it is necessary for the metaparameters
    dict_media_directions = dict()
    for key in list(dict_data_series):
        if 'ssrc' in key:
            key_elements = key.split("_")
            dict_media_directions[key_elements[-3]] = key_elements[-1] + "_" + key_elements[-2].split("-")[0]

    # 8: Renaming of the keys to make everything more readable
    for key in list(dict_data_series):
        if 'ssrc' in key:
            key_elements = key.split("_")
            # Construct new key that is more readable
            if i_n_clients == 2:
                new_key = (key_elements[-1] + "_" + key_elements[-2]).replace('-', '_')
            if i_n_clients == 3:
                # 3 client case also contains the ssrc for future mapping
                new_key = (key_elements[-1] + "_" + key_elements[-2]).replace('-', '_') + "_" + key_elements[-3]

            # Extend already existing data series (should not happen)
            if new_key in dict_data_series:
                dict_data_series[new_key].extend(dict_data_series[key])
            else:
                dict_data_series[new_key] = dict_data_series[key]

            del dict_data_series[key]

        elif "Conn-audio" in key or 'Conn-video' in key:
            new_key = key.split('-')[4]
            if "Conn-audio" in key:
                new_key = 'audio_' + new_key
            else:
                new_key = 'video_' + new_key
            dict_data_series[new_key] = dict_data_series[key]
            del dict_data_series[key]

    # 9: Only add the stats for connections with the right remote ips
    b_found_address = False
    for entry in dict_data_series:
        if 'RemoteAddress' in entry:
            b_found_address = True

    if b_found_address:
        return dict_data_series, dict_media_directions


# Determines whether the given key should be written to the csv file
def __check_do_write_key(key):
    for entry in unused_strings:
        if entry in key:
            return False

    for entry in used_strings_audio:
        if entry in key:
            return True
    for entry in used_strings_video:
        if entry in key:
            return True
    for entry in used_strings_context:
        if entry in key:
            return True
    for entry in used_strings_network:
        if entry in key:
            return True

    return False


# Parses a given line to an int array adding -1 in order to fit the given start/end timestamp
def __get_int_array_for_stat_line_time_corr(statLine, start_timestamp_logfile, end_timestamp_logfile):
    # Find start time for data series:
    str_start_timestamp = statLine['startTime'][:19]
    start_datetime = datetime.strptime(str_start_timestamp, '%Y-%m-%dT%H:%M:%S')

    ret = []

    # Insert -1 at the beginning, to ensure proper starting point
    while start_datetime > start_timestamp_logfile:
        ret.append(-1)
        start_datetime -= timedelta(0,1)
    # Now that the time difference is corrected, we are at the actual starting point of the data series
    start_datetime = datetime.strptime(str_start_timestamp, '%Y-%m-%dT%H:%M:%S')

    values = statLine['values'][1:-1].split(',')
    for value in values:
        if value == "null":
            value = 0
        try:
            ret.append(float(value))
        except ValueError:
            ret.append(value[1:-1])
        start_datetime += timedelta(0, 1)

    # Insert -1 at the end, so all stat lines have the same length
    while start_datetime < start_timestamp_logfile:
        ret.append(-1)
        start_datetime += timedelta(0,1)

    return ret