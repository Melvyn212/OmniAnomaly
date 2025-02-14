# -*- coding: utf-8 -*-

import ast
import csv
import os
import sys
from pickle import dump

import numpy as np
from tfsnippet.utils import makedirs

if len(sys.argv) < 3:
    print("""
        Usage: python data_preprocess.py <dataset> <output_folder>
        where <dataset> should be one of ['SMD', 'SMAP', 'MSL']
        and <output_folder> is the directory to save processed files
        """)
    sys.exit(1)

dataset = sys.argv[1]
output_folder = sys.argv[2]

output_folder = 'processed'
makedirs(output_folder, exist_ok=True)


def load_and_save(category, filename, dataset, dataset_folder):
    temp = np.genfromtxt(os.path.join(dataset_folder, category, filename),
                         dtype=np.float32,
                         delimiter=',')
    print(dataset, category, filename, temp.shape)
    with open(os.path.join(output_folder, dataset + "_" + category + ".pkl"), "wb") as file:
        dump(temp, file)


def load_data(dataset):
    if dataset == 'SMD':
        dataset_folder = 'EdgeAI/MODEL/OmniAnomaly/ServerMachineDataset'
        file_list = os.listdir(os.path.join(dataset_folder, "train"))
        for filename in file_list:
            if filename.endswith('.txt'):
                load_and_save('train', filename, filename.strip('.txt'), dataset_folder)
                load_and_save('test', filename, filename.strip('.txt'), dataset_folder)
                load_and_save('test_label', filename, filename.strip('.txt'), dataset_folder)
    elif dataset == 'SMAP' or dataset == 'MSL':
        dataset_folder = 'EdgeAI/MODEL/OmniAnomaly/data'
        with open(os.path.join(dataset_folder, 'labeled_anomalies.csv'), 'r') as file:
            csv_reader = csv.reader(file, delimiter=',')
            res = [row for row in csv_reader][1:]
        res = sorted(res, key=lambda k: k[0])
        label_folder = os.path.join(dataset_folder, 'test_label')
        makedirs(label_folder, exist_ok=True)
        data_info = [row for row in res if row[1] == dataset and row[0] != 'P-2']
        labels = []
        for row in data_info:
            anomalies = ast.literal_eval(row[2])
            length = int(row[-1])
            label = np.zeros([length], dtype=np.bool)
            for anomaly in anomalies:
                label[anomaly[0]:anomaly[1] + 1] = True
            labels.extend(label)
        labels = np.asarray(labels)
        print(dataset, 'test_label', labels.shape)
        with open(os.path.join(output_folder, dataset + "_" + 'test_label' + ".pkl"), "wb") as file:
            dump(labels, file)

        def concatenate_and_save(category):
            data = []
            for row in data_info:
                filename = row[0]
                temp = np.load(os.path.join(dataset_folder, category, filename + '.npy'))
                data.extend(temp)
            data = np.asarray(data)
            print(dataset, category, data.shape)
            with open(os.path.join(output_folder, dataset + "_" + category + ".pkl"), "wb") as file:
                dump(data, file)

        for c in ['train', 'test']:
            concatenate_and_save(c)




# Autres parties du script restent inchangées

if __name__ == '__main__':
    if dataset in ['SMD', 'SMAP', 'MSL']:
        makedirs(output_folder, exist_ok=True)
        load_data(dataset)
    else:
        print("Dataset not recognized. Please choose from ['SMD', 'SMAP', 'MSL'].")
