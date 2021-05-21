import glob
import pandas as pd
import numpy as np
from scipy.signal import butter
from scipy import signal
from datetime import datetime, timezone
import pyedflib
import os
from path import Path

def butter_bandpass_filter(data, lowcut, highcut, fs, order=1):
    b, a = butter(order, [lowcut, highcut], btype='band', fs=fs)
    y = signal.filtfilt(b, a, data)
    return y

def butter_lowpass_filter(data, cutoff_fs, fs, order=1):
    b, a = butter(order, cutoff_fs, btype='low', fs=fs)
    y = signal.filtfilt(b, a, data)
    return y

def butter_highpass_filter(data, cutoff_fs, fs, order=1):
    b, a = butter(order, cutoff_fs, btype='high', fs=fs)
    y = signal.filtfilt(b, a, data)
    return y

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def count_offset(combined_data):
    count = 0
    prev_value = -1
    list_count_offset = []
    for i in range(np.shape(combined_data)[0]):
        value = combined_data[i]
        if prev_value == -1:
            count += 1
            prev_value = combined_data[i]
        else:
            if value - prev_value == 0:
                count += 1
                prev_value = combined_data[i]
            elif value - prev_value == 1 or abs(value - prev_value) == 255:
                list_count_offset.append(count)
                count = 1
                prev_value = combined_data[i]
    list_count_offset.append(count)
    return list_count_offset


def convert_to_csv(fpath):
    # fpath = 'Pycharm/IntTest/test1'
    fnames_path = sorted(glob.glob(fpath + '/*'))
    CHANNEL_NAMES = ['ch1_LF5-FpZ', 'ch2_OTE_L-FpZ', 'ch3_BE_L-FpZ', 'ch4_RF6-FpZ', 'ch5_OTE_R-FpZ', 'ch6_BE_R-FpZ']
    is_first_file = True
    saved_time_start = 0
    sample_bytes_length = np.asarray([3, 3, 3, 3, 3, 3, 1])  # bytes of [channel1; channel2;...; channel6; offset]
    list_sample = []
    list_offset = []
    bandpass_filter = True
    ep_frequency = 125
    patientID = 'no_name'
    channel_map = {cname: idx for idx, cname in enumerate(CHANNEL_NAMES)}
    dimension = {cname: 'uV' for cname in CHANNEL_NAMES}
    signal_headers = [''] * len(channel_map)
    print('Start reading binary files...')
    for fname in fnames_path:
        with open(fname, mode='rb') as file:  # b -> binary
            fileContent = file.read()
        if not fileContent:
            print(f'file {Path(fname).name} is empty!!!')
            break
        time_start = int.from_bytes(fileContent[:4], byteorder='little',
                                    signed=False)  # get first line as time_open_file
        if is_first_file:  # store start time of FIRST FILE as the start time of recording
            saved_time_start = time_start
            is_first_file = False

        start_index = 4

        number_of_sample = int(
            (len(fileContent) - 8) / 19)  # 8 is bytes of timestamp first and last line, 19 is bytes in 1 line
        for sample_index in range(number_of_sample):
            sample = []
            for i in sample_bytes_length:
                if i == 1:  # byte of offset
                    offset = int.from_bytes(fileContent[start_index: start_index + i], byteorder='little', signed=False)
                    list_offset.append(offset)
                    start_index += i
                else:  # the rest bytes is for channels data
                    sample_ele = int.from_bytes(fileContent[start_index: start_index + i], byteorder='little',
                                                signed=True)
                    sample.append(sample_ele)
                    start_index += i
            list_sample.append(sample)

    # list_offset_count = count_offset(list_offset) # count data that collected in 1s
    # np_list_sample = np.asarray(list_sample)

    df_channel = pd.DataFrame(list_sample)
    df_offset = pd.DataFrame(list_offset)
    df_csv = pd.concat([df_offset, df_channel], axis=1)

    name_csv = 'EEG_{}.csv'.format('C7616304-815C')
    output_csv = '{}/{}'.format(fpath, name_csv)
    df_csv.to_csv(output_csv, index=False)
    return output_csv
