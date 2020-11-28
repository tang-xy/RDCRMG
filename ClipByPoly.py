# coding:utf-8
import sys
import os
import shutil
from time import time
import numpy as np
import pandas as pd

from SearchEngine import SearchEngine
from Stitching import Stitching
from GridCalculate import GridCalculate
from CoordinateAndProjection import CoordinateAndProjection
from DataStruct import basic_data_struct
from BaseProcesses import BaseProcesses
import conf
from clip_dataset_list_groupby_time import clip_dataset_list_groupby_time

def set_conf(jsonpath, task_id, search_time):

    
    conf.jsonpath = jsonpath
    # conf.jsonpath = r"./2020-11-09.json"
    # conf.jsonpath = r"H:\32652\out.geo.json"
    conf.ID = task_id
    # conf.ID = '45'
    # conf.sDatahomePath = "/mnt/datapool/RemoteSensingData1/DataWorking/"
    conf.sDatahomePath = "H:\\RDCRMG_test_data"
    conf.search_time = search_time
    # conf.search_time = "all"
    # conf.sRslPath = "/mnt/datapool/RemoteSensingData/liudiyou20140/rlt_RDCRMG/" + conf.search_time + "_" + conf.ID
    conf.sRslPath = "H:\\32652/" + conf.search_time + "_" + conf.ID
    conf.output_format = '.png' # available value: .png .tif
    conf.export_excel = pd.DataFrame({"id" : [], 'mean':[]})
    conf.iDataProduct = 1
    conf.iCloulLevel = 9

def get_unitblock_list(pWGSLT, pWGSRB):
    ''' 根据左上、右下角坐标，计算每条带的左上、右下格网号
        返回格式：[dic];resPCS_type:条带号,sGridCodeLT:左上格网编码,sGridCodeRB:右下格网编码
    '''
    iaZoneL = CoordinateAndProjection.LongitudeToUTMProjZone(pWGSLT['dx'])
    iaZoneR = CoordinateAndProjection.LongitudeToUTMProjZone(pWGSRB['dx'])
    result = []
    for bd_number in range(iaZoneL, iaZoneR + 1):
        temp_res = {}
        temp_res['iPCSType'] = 32600 + bd_number
        pWGSRB_temp = {}
        pWGSLT_temp = {}
        pWGSLB_temp = {}

        pWGSLT_temp['dx'] = max(pWGSLT['dx'], (bd_number - 1) * 6 - 179.99)
        pWGSLT_temp['dy'] = pWGSLT['dy']

        pWGSRB_temp['dx'] = min(pWGSRB['dx'], bd_number * 6 - 180.01)
        pWGSRB_temp['dy'] = pWGSRB['dy']
        pWGSLB_temp['dx'] = pWGSLT_temp['dx']
        pWGSLB_temp['dy'] = pWGSRB['dy']
        sGridCodeLT = CoordinateAndProjection.GeoCdnToGridCode(pWGSLT_temp)
        sGridCodeRB = CoordinateAndProjection.GeoCdnToGridCode(pWGSRB_temp)
        sGridCodeLB = CoordinateAndProjection.GeoCdnToGridCode(pWGSLB_temp)
        resGridCodeLT =  GridCalculate.LtPointRecaculate(sGridCodeLT, sGridCodeRB, sGridCodeLB)
        if bd_number == iaZoneL:
            temp_res['sGridCodeLT'] = sGridCodeLT
        else:
            temp_res['sGridCodeLT'] = resGridCodeLT
        temp_res['sGridCodeRB'] = sGridCodeRB
        

        result.append(temp_res)
    return result


def clip_poly(jsonpath, task_id, search_time):
    start = time()
    set_conf(jsonpath, task_id, search_time)
    os.mkdir(conf.sRslPath)
    temppath = os.path.join(conf.sRslPath ,"temp")
    os.mkdir(temppath)

    pWGSLT, pWGSRB  = BaseProcesses.read_json_area(conf.jsonpath)
    unitblock_list = get_unitblock_list(pWGSLT, pWGSRB)
    grid_dic = {}
    for unitblock in unitblock_list:
        lsGridcode = GridCalculate.GridCodeToGridlist_iPCSType(unitblock['sGridCodeLT'],\
         unitblock['sGridCodeRB'], unitblock['iPCSType'])
        for sGridCode in lsGridcode:
            lbds10kmIn = SearchEngine.SearchByRgDttmDtpd(sGridCode, conf.sDatahomePath, conf.search_time,
             conf.iDataProduct, conf.iCloulLevel)
            for lbd_time in lbds10kmIn:
                if lbd_time not in grid_dic.keys():
                    grid_dic[lbd_time] = [lbd.sPathName for lbd in lbds10kmIn[lbd_time]]
                else:
                    grid_dic[lbd_time] += [lbd.sPathName for lbd in lbds10kmIn[lbd_time]]


    for lbd_time in grid_dic:
        clip_dataset_list_groupby_time(grid_dic[lbd_time], lbd_time)
    grid_dic = None
    shutil.rmtree(temppath)
    end = time()
    print("任务{1}耗时{0}，涉及{2}个格网".format(end-start, task_id, len(unitblock_list)))
