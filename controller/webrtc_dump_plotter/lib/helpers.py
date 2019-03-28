import math
from pathlib import Path
import shutil
import os

from definitions import *

__all__ = ["get_max_value_list_of_lists", "helper_is_key_in_list", "helper_bit_to_kbit_list", "get_data_for_keys",
           "roundup", "move_data_to_parent_directory", "get_data_for_keys_3clients"]


# Finds the maximum value in a list of lists
def get_max_value_list_of_lists(list_values):
    i_max = 1

    for list in list_values:
        for entry in list:
            if entry > i_max:
                i_max = entry

    return i_max


def helper_is_key_in_list(list_target, key):
    for entry in list_target:
        if entry in key:
            return list_target.index(entry)
    return -1


def helper_bit_to_kbit_list (list_src):
    tmp = []
    for i in list_src:
        tmp.append(i / 1024)
    return tmp


# Returns data and corresponding labels for the given list of keys
def get_data_for_keys(list_keys: list, dict_data: dict):
    list_data = list()
    list_data_labels = list()

    for entry in list_keys:
        if 'bits' in entry or 'Bandwidth' in entry:
            series_kbit = helper_bit_to_kbit_list(dict_data[entry])
            list_data.append(series_kbit)
        else:
            list_data.append(dict_data[entry])

        list_data_labels.append(dict_lookup[entry])

    return list_data, list_data_labels


# Generates plottable data for 3 client measurements
# Finds all ocurrences of the elements in list_keys and groups them by the ssrc
def get_data_for_keys_3clients(list_keys: list, dict_data: dict):
    ssrc_directions = dict()

    for key in dict_data:
        if len(key.split("_")) == 4 and key.startswith("audio") or key.startswith("video"):
            key_elements = key.split("_")
            ssrc_directions[key_elements[-1]] = key_elements[0] + "_" + key_elements[1]

    # Contains one entry for each ssrc
    dict_media_data = dict()
    for ssrc in ssrc_directions:
        dict_media_data[ssrc] = dict()

    list_data_labels = list()

    for entry in list_keys:

        # For each key, save the data to the corresponding entry in the dict_media_data
        for ssrc in ssrc_directions:
            entry_new = entry + "_{0}".format(ssrc)

            if entry_new in dict_data:
                if 'bits' in entry or 'Bandwidth' in entry:
                    dict_data[entry_new] = helper_bit_to_kbit_list(dict_data[entry_new])

                # list_data.append(dict_data[entry])
                dict_media_data[ssrc][entry] = dict_data[entry_new]

                if dict_lookup[entry] not in list_data_labels:
                    list_data_labels.append(dict_lookup[entry])

    for entry in list(dict_media_data):
        if len(dict_media_data[entry]) == 0:
            del dict_media_data[entry]

    return dict_media_data, list_data_labels


# Rounds x to the nearest full digit in its dimension (231 -> 300), (77 -> 100)
def roundup(x):
    if x < 100:
        tmp = int(math.ceil(x / 10.0)) * 10
    elif 100 < x < 1000:
        tmp = int(math.ceil(x / 100.0)) * 100
    else:
        tmp = int(math.ceil(x / 1000.0)) * 1000

    return tmp

# Moves the plots from complete_measurements to a parent directory str_dirname (either P2P or RELAY")
def move_data_to_parent_directory(dir_source: Path, str_dirname: str):
    if (dir_source.parent / str_dirname).exists():
        shutil.rmtree(str(dir_source.parent / str_dirname))
    os.makedirs(str((dir_source.parent / str_dirname)))

    for file in dir_source.glob("*"):
        if file.is_dir():
            shutil.copytree(str(file), "{0}/{1}/{2}".format(str(PATH_OUTPUT), str_dirname, file.name))
        else:
            shutil.copy2(str(file), "{0}/{1}/".format(str(PATH_OUTPUT), str_dirname))
