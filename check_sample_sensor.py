'''
author: Loc Truong <loc@earable.ai>
date: 17May2021
brief: Analysing the streaming data.
'''
import pandas as pd
import numpy as np
import json
from matplotlib import pyplot as plt
import convert_bin_to_csv
PATH_TO_BIN = 'abc_EB_DEV575c_1621580882'
PATH_TO_CSV = convert_bin_to_csv.convert_to_csv(PATH_TO_BIN)
PATH_TO_DATA = 'abc_EB_DEV575c_1621580882/EEG_C7616304-815C.csv'
df = pd.read_csv(PATH_TO_CSV,names=['ts','c0','c1','c2','c3','c4','c5'],skiprows=1)
time_stamps = df['ts'].tolist()
cloud_data = [df['c0'].tolist(), df['c1'].tolist(), df['c2'].tolist(), df['c3'].tolist(), df['c4'].tolist(), df['c5'].tolist()]
sample_count = {}
sample_count_list = []
time_stamps_diff = []
prev_ts = time_stamps[0]
start_idx=0
count = 0
print("############################\n")
for idx, curr_ts in enumerate(time_stamps):
    if curr_ts != prev_ts:
        time_stamps_diff.append(abs(curr_ts - prev_ts))
        sample_count_list.append(count)
        if count in sample_count.keys():
            sample_count[count] += 1
        else:
            sample_count[count] = 1
        if count < 124 or count > 125:
            print(f'Line [{start_idx}:{idx}] has {count} samples')
        count = 0
        start_idx = idx
    count += 1
    prev_ts = curr_ts
# append the last second
if count in sample_count.keys():
    sample_count[count] += 1
else:
    sample_count[count] = 1
sample_count_list.append(count)
print("\n############################\n")
for key, value in sample_count.items():
    # print(f'sampling rate {key} : number of seconds = {value}')
    print(f'{value} seconds has the sampling rate of {key} Hz')
print("\n############################\n")
print(set(time_stamps_diff))
for datum in set(time_stamps_diff):
    print(f'timestampdiff = {datum}: count = {time_stamps_diff.count(datum)}')

plt.figure(figsize=(20,5))
plt.plot(time_stamps_diff);
plt.title("Difference of timestamps");
plt.xlabel('Time (s)');
plt.ylabel('Difference between 2 consecutive seconds');
plt.yticks(list(set(time_stamps_diff)));
plt.xticks(np.arange(0, len(time_stamps_diff), step=1000));
plt.figure(figsize=(20,5))
plt.plot(sample_count_list)
plt.title("Sample counts of each second")
plt.xlabel('Time (s)');
plt.ylabel('Number of Samples Per Second');
plt.yticks(list(set(sample_count_list)));
plt.xticks(np.arange(0, len(sample_count_list), step=1000));
plt.show()