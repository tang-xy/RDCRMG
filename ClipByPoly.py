# coding:utf-8
import sys
import os
import shutil
from time import time
import numpy as np
import pandas as pd
from osgeo import gdal
from PIL import Image

from SearchEngine import SearchEngine
from Stitching import Stitching
from GridCalculate import GridCalculate
from CoordinateAndProjection import CoordinateAndProjection
from DataStruct import basic_data_struct
from BaseProcesses import BaseProcesses
import NdviCompute 
import conf

def set_conf(jsonpath, task_id, search_time):

    
    conf.jsonpath = jsonpath
    # conf.jsonpath = r"./2020-11-09.json"
    # conf.jsonpath = r"H:\32652\out.geo.json"
    conf.ID = task_id
    # conf.ID = '45'
    conf.sDatahomePath = "/mnt/datapool/RemoteSensingData1/DataWorking/"
    # conf.sDatahomePath = "H:\\RDCRMG_test_data"
    conf.search_time = search_time
    # conf.search_time = "all"
    conf.sRslPath = "/mnt/datapool/RemoteSensingData/liudiyou20140/rlt_RDCRMG/" + conf.search_time + "_" + conf.ID
    # conf.sRslPath = "H:\\32652/" + conf.search_time + "_" + conf.ID
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

def clip_dataset_list_groupby_time(grid_list, time):
    '''输入相同时间的一组grid_list，对其进行拼接剪切
    '''
    conf.export_excel = pd.DataFrame({"id" : [], 'mean':[]})
    output_path = os.path.join(conf.sRslPath, conf.ID + time + '_1.tif')
    print(output_path)
    options=gdal.WarpOptions(format='GTiff', dstSRS='EPSG:900913')
    print("options")
    tif_list = [gdal.Open(path) for path in grid_list]
    print("opened")
    tif_dataset = gdal.Warp(output_path, tif_list, options=options)
    print("warped")
    tif_list = None
    mean = NdviCompute.ndvi_compute_byds(tif_dataset, os.path.join(conf.sRslPath, conf.ID + time + '_2' + conf.output_format), NdviCompute.IMAGE_TYPE_GF1)
    print("ndvi")
    if conf.output_format == '.png':
        iRowRange = tif_dataset.RasterYSize
        iColumnRange = tif_dataset.RasterXSize
        r_band = tif_dataset.GetRasterBand(3).ReadAsArray(0, 0, iColumnRange, iRowRange)
        g_band = tif_dataset.GetRasterBand(2).ReadAsArray(0, 0, iColumnRange, iRowRange)
        b_band = tif_dataset.GetRasterBand(1).ReadAsArray(0, 0, iColumnRange, iRowRange)
        res = np.dstack((r_band, g_band, b_band)) * 1.0
        res = (res - np.min(res)) * 255 / np.max(res)
        im = Image.fromarray(np.uint8(res))
        im.save(output_path[:-5] + "1.png")
        del im, tif_dataset
        os.remove(output_path)

    conf.export_excel.loc[len(conf.export_excel)] = [conf.ID, mean]
    conf.export_excel.to_excel(os.path.join(conf.sRslPath, conf.ID + time +".xlsx"))

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
