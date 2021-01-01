# coding:utf-8

import os

rootpath1 = "/mnt/datapool/RemoteSensingData/remoteSensingDataset/XjGs_Allgrids_2018_irSITS/7_Shihezi"
rootpath2 = "./2020122916_20180101_20180930_IrglSITS_001-004-733"

filedic = {}
for root, dirnames, filenames in os.walk(rootpath2):
    for filename in filenames:
        filedic[filename] = os.path.join(root, filename)

for root, dirnames, filenames in os.walk(rootpath1):
    for filename in filenames:
        path1 = os.path.join(root, filename)
        if filename not in filedic.keys():
            print(path1 + " not exist")
            continue
        path2 = filedic[filename]
        if open(path1).read() != open(path2).read():
            print(path1 + " error")

print("well done")