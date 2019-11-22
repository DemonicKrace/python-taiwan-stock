# -*- coding: utf-8 -*-
"""
Created on 2019/11/14 15:37

@author: demonickrace
"""
import os
import json
import time
import random


def json_load_byteified(file_handle):
    return byteify(
        json.load(file_handle, object_hook=byteify),
        ignore_dicts=True
    )


def json_loads_byteified(json_text):
    return byteify(
        json.loads(json_text, object_hook=byteify),
        ignore_dicts=True
    )


def byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            byteify(key, ignore_dicts=True): byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data


#   full width to half width,（Ａ）=> (A)
def full_to_half(s):
    n = []
    s = s.decode('utf-8')
    for char in s:
        num = ord(char)
        if num == 0x3000:
            num = 32
        elif 0xFF01 <= num <= 0xFF5E:
            num -= 0xfee0
        num = unichr(num)
        n.append(num)
    return ''.join(n)


# create temp json if not exist
def init_json_file_if_not_exist(target_file):
    if not os.path.exists(target_file):
        with open(target_file, 'w') as temp_file:
            temp_file.write(json.dumps({}, indent=4))
            temp_file.close()


# get json obj from temp
def get_json_obj_from_temp_file(target_file):
    with open(target_file) as temp_file:
        json_obj = json_load_byteified(temp_file)
        # json_obj = json.load(temp_file)
        return json_obj


# check data, set column default value if not exist
def fill_default_value_if_column_not_exist(format_data=None, data=None, except_percent_column=None):
    if not format_data:
        format_data = {}
        print('fill_default_value_if_column_not_exist, input dict_format is None')

    if not data:
        data = {}
        print('fill_default_value_if_column_not_exist, input data is None')

    for key, value in format_data.items():
        if value not in data:
            data[value] = ''
            if value not in except_percent_column:
                percent_key = value + '_p'
                data[percent_key] = ''
    return data


def delay_seconds(min_wait_seconds=10, max_wait_seconds=20):
    seconds = random.randint(min_wait_seconds, max_wait_seconds)
    print('wait {} seconds...\n'.format(seconds))
    time.sleep(seconds)


if __name__ == '__main__':

    pass
