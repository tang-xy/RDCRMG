# coding:utf-8
import sys
import os
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

def set_conf():
    # if len(sys.argv) != 3:
    #     exit()
    
    #conf.jsonpath = sys.argv[1]
    conf.jsonpath = r"H:\Json\2020-11-09.json"
    # conf.jsonpath = r"H:\32652\out.geo.json"
    #conf.ID = sys.argv[2]
    conf.ID = '45'
    conf.sDatahomePath = "H:\\RDCRMG_test_data"
    conf.search_time = "20180627"
    # conf.search_time = "all"
    conf.sRslPath = "H:\\32652\\2020103100_Data001_" + conf.search_time + "_" + conf.ID
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
    output_path = os.path.join(conf.sRslPath, conf.ID + time + '_1.tif')
    options=gdal.WarpOptions(format='GTiff', cutlineDSName = conf.jsonpath, dstSRS='EPSG:900913')
    tif_dataset = gdal.Warp(output_path, grid_list, options=options)
    mean = NdviCompute.ndvi_compute_byds(tif_dataset, os.path.join(conf.sRslPath, conf.ID + time + '_2' + conf.output_format), NdviCompute.IMAGE_TYPE_GF1)
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

if __name__ == "__main__":
    start = time()
    set_conf()
    os.mkdir(conf.sRslPath)

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
                    grid_dic[lbd_time] = [gdal.Open(lbd.sPathName) for lbd in lbds10kmIn[lbd_time]]
                else:
                    grid_dic[lbd_time] += [gdal.Open(lbd.sPathName) for lbd in lbds10kmIn[lbd_time]]

    for lbd_time in grid_dic:
        clip_dataset_list_groupby_time(grid_dic[lbd_time], lbd_time)
    end = time()
    print("耗时{0}".format(end-start))
