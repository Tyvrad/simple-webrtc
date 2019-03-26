import copy


def get_session_avg(session_infos):
    dict_tmp = {}
    dict_avg = {}

    # Aggregate in temp dict
    for file in session_infos:
        for key in session_infos[file]:
            tmp = []
            try:
                tmp = dict_tmp[key]
                tmp.append(session_infos[file][key])

            except KeyError:
                tmp.append(session_infos[file][key])
            dict_tmp[key] = tmp

    # Calculate avg
    for key in dict_tmp:
        sum_entries = 0
        try:
            for i in dict_tmp[key]:
                try:
                    sum_entries += i
                except TypeError:
                    continue
            avg = sum_entries / len(dict_tmp[key])
        except TypeError:
            # Special case: only one connection -> copy value
            avg = dict_tmp[key]

        dict_avg[key] = avg
    return dict_avg


# What's the point of this?
# Deprecated!
def get_configuration_averages(dict_measurement_averages):
    dict_aggregated_values = {}
    dict_averages = {}

    for measurement in dict_measurement_averages:
        for key in dict_measurement_averages[measurement]:

            if key in dict_aggregated_values:
                dict_aggregated_values[key].append(dict_measurement_averages[measurement][key])
            else:
                tmp = []
                tmp.append(dict_measurement_averages[measurement][key])
                dict_aggregated_values[key] = tmp

    for key in dict_aggregated_values:
        sum_entries = 0
        avg = 0
        try:
            for i in dict_aggregated_values[key]:
                try:
                    sum_entries += i
                except TypeError:
                    continue
            avg = sum_entries / len(dict_aggregated_values[key])
        except TypeError:
            # Special case: only one connection -> copy value
            avg = dict_aggregated_values[key]

        dict_averages[key] = avg

    return dict_averages


# Aggregates the data from the single clients in a single measurement and aggregates the data
# Result: aggregated_data_RELAY/P2P.csv
def get_session_aggregated(session_infos):
    dict_session_data_aggregated_relay = {}
    dict_session_data_aggregated_p2p = {}
    dict_session_data_aggregated = {}

    dict_session_data_aggregated["RELAY"] = dict_session_data_aggregated_relay
    dict_session_data_aggregated["P2P"] = dict_session_data_aggregated_p2p

    for file in session_infos:
        for connection in session_infos[file]:
            if "P2P" in connection:
                for key in session_infos[file][connection]:
                    tmp = []

                    # Suppport for 3 clients: remove trailing ssrc number
                    new_key = key
                    if len(session_infos) > 2 and len(key.split("_")) >= 4:
                        new_key = key[:key.rfind("_")]

                    try:
                        tmp = dict_session_data_aggregated_p2p[new_key]
                        tmp.extend(session_infos[file][connection][key])

                    except KeyError:
                        # Deep copy necessary in order to avoid playing with references, which causes strange things
                        tmp = copy.deepcopy(session_infos[file][connection][key])
                        dict_session_data_aggregated_p2p[new_key] = tmp
                    del tmp
            if "RELAY" in connection:
                for key in session_infos[file][connection]:
                    tmp = []

                    # Suppport for 3 clients: remove trailing ssrc number
                    new_key = key
                    if len(session_infos) > 2 and len(key.split("_")) >= 4:
                        # Send metaparameters have a trailing _0 or _1 to distinguish between receiver 0 and 1
                        # Remove it for the aggregated data
                        if key.endswith("_0") or key.endswith("_1"):
                            new_key = key[:-2]
                            new_key = new_key[:new_key.rfind("_")]
                        else:
                            new_key = key[:key.rfind("_")]

                    try:
                        tmp = dict_session_data_aggregated_relay[new_key]
                        tmp.extend(session_infos[file][connection][key])

                    except KeyError:
                        # Deep copy necessary in order to avoid playing with references, which causes strange things
                        tmp = copy.deepcopy(session_infos[file][connection][key])
                        dict_session_data_aggregated_relay[new_key] = tmp
                    del tmp

    # Purge -1 values as they are not important in our case
    # for key in dict_session_data_aggregated_relay:
    #     dict_session_data_aggregated_relay[key][:] = \
    #         (el for el in dict_session_data_aggregated_relay[key] if el is not -1)
    #
    # for key in dict_session_data_aggregated_p2p:
    #     dict_session_data_aggregated_p2p[key][:] = \
    #         (el for el in dict_session_data_aggregated_p2p[key] if el is not -1)

    return dict_session_data_aggregated


def get_connection_avg(file_infos):
    dict_connections_avg = {}

    for connection in file_infos:
        dict_connections_avg[connection] = {}
        for key in file_infos[connection]:

            new_key = key
            sum_entries = 0

            for i in file_infos[connection][key]:
                try:
                    sum_entries += i
                except TypeError:
                    continue

            avg = sum_entries / len(file_infos[connection][key])
            dict_connections_avg[connection][new_key] = avg

    return dict_connections_avg
