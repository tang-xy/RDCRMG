# coding:utf-8
from SearchEngine import SearchEngine
from Stitching import Stitching
from GridCalculate import GridCalculate
from CoordinateAndProjection import CoordinateAndProjection
from DataStruct import basic_data_struct
from BaseProcesses import BaseProcesses
import NdviCompute 
import conf

from osgeo import gdal
import pandas as pd
import numpy as np
from PIL import Image

import os
import sys
from time import time
import shutil

def DealIn10km(sGridCode, sDateTime, iDataProduct, iModelId, iCloulLevel, sDatahomePath, sRslPath):
    '''根据 格网编码 日期 类型， 处理单个10km格网内的业务 ——以基本结构表示的某景影像
    1 根据格网序编号、日期、数据类型得到该网格内待处理数据列表 —Lbds
    2 2 根据待处理数据列表，完成该格网的业务处理                 —bds
    '''
    lbds10kmIn = SearchEngine.SearchByRgDttmDtpd(sGridCode, sDatahomePath, sDateTime, iDataProduct, iCloulLevel)
    if (len(lbds10kmIn) >= 1):
        bdsRlt = Stitching.StichingIn10km(lbds10kmIn,iDataProduct,iModelId,sRslPath)
    else:
        bdsRlt = basic_data_struct()
        bdsRlt.sPathName = "0"
    return bdsRlt

def ProcessInDataBlock(sGridCodeLT, sGridCodeRB, iPCSType, sDateTime, iDataProduct, iModelId, iCloulLevel, sDatahomePath, sRslPath):
    lsGridcode = GridCalculate.GridCodeToGridlist_iPCSType(sGridCodeLT, sGridCodeRB, iPCSType)
    lbdsRlt10kmBtw = []
    for sGridcode in lsGridcode:
        bdsTemp = DealIn10km(sGridcode, sDateTime, iDataProduct, iModelId,iCloulLevel, sDatahomePath, sRslPath)
        if bdsTemp.sPathName != '0':
            lbdsRlt10kmBtw.append(bdsTemp)
    if len(lbdsRlt10kmBtw) != 0:
        return Stitching.StichingBtwn10km(lbdsRlt10kmBtw, iModelId, sRslPath, iPCSType).sPathName
    else:
        return "0"
    
def warp_raster(input_raster_name, input_shape, sRslPath):
    input_raster = gdal.Open(input_raster_name)
    output_raster = os.path.join(sRslPath, os.path.basename(input_raster_name)[:-4] + "_1" + conf.output_format)
    if conf.output_format == ".tif":
        driver_format = "GTIFF"
    elif conf.output_format == ".png":
        driver_format = "GTIFF"
        output_raster = output_raster[:-5] + 't.tif'
    ds = gdal.Warp(output_raster,
              input_raster,
              format = driver_format,
              cutlineDSName = input_shape,      # or any other file format
              #cutlineWhere="FIELD = 'whatever'",# optionally you can filter your cutline (shapefile) based on attribute values
              dstNodata = 0)
    return ds, output_raster

def SubProcessingForGetImg_Unit_Block_FirstLeftZone(pWGSLT, pWGSRB, iPCSType, sDateTime, iDataProduct, iModelId, iCloulLevel, sDatahomePath, sRslPath, input_shape):
    iXBlocksLth = iYBlocksLth = 100
    sGridCodeLT = CoordinateAndProjection.GeoCdnToGridCode(pWGSLT)
    sGridCodeRB = CoordinateAndProjection.GeoCdnToGridCode(pWGSRB)
    lsGridCodeLTRB = GridCalculate.DivideDataBlocks(sGridCodeLT, sGridCodeRB, iXBlocksLth, iYBlocksLth)
    for GridCodeLTRB in lsGridCodeLTRB:
        input_raster_name = ProcessInDataBlock(GridCodeLTRB[0], GridCodeLTRB[1], iPCSType, sDateTime, iDataProduct, iModelId, iCloulLevel, sDatahomePath, sRslPath)
        cli_raster, cli_raster_path = warp_raster(input_raster_name, input_shape, sRslPath)
        mean = NdviCompute.ndvi_compute_byds(cli_raster, cli_raster_path[:-6] + "_2" + conf.output_format, NdviCompute.IMAGE_TYPE_GF1)
        # del cli_raster
        # if conf.output_format == ".png":
        #     driver = gdal.GetDriverByName('PNG')
        #     cli_ras = gdal.Open(cli_raster_path, gdal.GA_Update)
        #     al_band = np.zeros((cli_ras.RasterXSize, cli_ras.RasterXSize), dtype=np.uint8) + 255
        #     cli_ras.GetRasterBand(4).WriteArray(al_band, 0, 0) 
        #     driver.CreateCopy(cli_raster_path[:-5] + "1.png", cli_ras)
        #     del cli_ras
        #     os.remove(cli_raster_path)
        if conf.output_format == ".png":
            iRowRange = cli_raster.RasterYSize
            iColumnRange = cli_raster.RasterXSize
            r_band = cli_raster.GetRasterBand(3).ReadAsArray(0, 0, iColumnRange, iRowRange)
            g_band = cli_raster.GetRasterBand(2).ReadAsArray(0, 0, iColumnRange, iRowRange)
            b_band = cli_raster.GetRasterBand(1).ReadAsArray(0, 0, iColumnRange, iRowRange)
            res = np.dstack((r_band, g_band, b_band))
            res = res * 1.0
            res = (res - np.min(res)) * 255 / np.max(res)
            im = Image.fromarray(np.uint8(res))
            im.save(cli_raster_path[:-5] + "1.png")
            del im, cli_raster
            os.remove(cli_raster_path)
        conf.export_excel.loc[len(conf.export_excel)] = [os.path.basename(cli_raster_path[:-6]), mean]

def SubProcessingForGetImg_Unit_Block_RightZone(pWGSLT, pWGSRB, pWGSLB, iPCSType, sDateTime, iDataProduct, iModelId, iCloulLevel, sDatahomePath, sRslPath, input_shape):
    iXBlocksLth = iYBlocksLth = 100
    sGridCodeLT = CoordinateAndProjection.GeoCdnToGridCode(pWGSLT)
    sGridCodeRB = CoordinateAndProjection.GeoCdnToGridCode(pWGSRB)
    sGridCodeLB = CoordinateAndProjection.GeoCdnToGridCode(pWGSLB)
    resGridCodeLT =  GridCalculate.LtPointRecaculate(sGridCodeLT, sGridCodeRB, sGridCodeLB)

    lsGridCodeLTRB = GridCalculate.DivideDataBlocks(resGridCodeLT, sGridCodeRB, iXBlocksLth, iYBlocksLth)
    for GridCodeLTRB in lsGridCodeLTRB:
        input_raster_name = ProcessInDataBlock(GridCodeLTRB[0], GridCodeLTRB[1], iPCSType, sDateTime, iDataProduct, iModelId, iCloulLevel, sDatahomePath, sRslPath)
        cli_raster, cli_raster_path = warp_raster(input_raster_name, input_shape, sRslPath)
        mean = NdviCompute.ndvi_compute_byds(cli_raster, cli_raster_path[:-6] + "_2" + conf.output_format, NdviCompute.IMAGE_TYPE_GF1)
        # del cli_raster
        # if conf.output_format == ".png":
        #     driver = gdal.GetDriverByName('PNG')
        #     cli_ras = gdal.Open(cli_raster_path, gdal.GA_Update)
        #     al_band = np.zeros((cli_ras.RasterXSize, cli_ras.RasterXSize), dtype=np.uint8) + 255
        #     cli_ras.GetRasterBand(4).WriteArray(al_band, 0, 0) 
        #     driver.CreateCopy(cli_raster_path[:-5] + "1.png", cli_ras)
        #     del cli_ras
        #     os.remove(cli_raster_path)
        if conf.output_format == ".png":
            iRowRange = cli_raster.RasterYSize
            iColumnRange = cli_raster.RasterXSize
            r_band = cli_raster.GetRasterBand(3).ReadAsArray(0, 0, iColumnRange, iRowRange)
            g_band = cli_raster.GetRasterBand(2).ReadAsArray(0, 0, iColumnRange, iRowRange)
            b_band = cli_raster.GetRasterBand(1).ReadAsArray(0, 0, iColumnRange, iRowRange)
            res = np.dstack((r_band, g_band, b_band))
            res = res * 1.0
            res = (res - np.min(res)) * 255 / np.max(res)
            im = Image.fromarray(np.uint8(res))
            im.save(cli_raster_path[:-5] + "1.png")
            del im, cli_raster
            os.remove(cli_raster_path)
        conf.export_excel.loc[len(conf.export_excel)] = [os.path.basename(cli_raster_path[:-6]), mean]


def GetImg_Unit_Block(pWGSLT, pWGSRB, sDateTime, iDataProduct, iModelId, iCloulLevel, sDatahomePath, sRslPath, input_shape):
    iaZone = [0,0]
    iaZone[0] = CoordinateAndProjection.LongitudeToUTMProjZone(pWGSLT['dx'])
    iaZone[1] = CoordinateAndProjection.LongitudeToUTMProjZone(pWGSRB['dx'])

    if (iaZone[0] == iaZone[1]):
        iPCSType = int("32600") + iaZone[0]
        if os.path.exists(sRslPath):
            os.mkdir(os.path.join(sRslPath ,"temp"))
            os.mkdir(os.path.join(sRslPath ,str(iPCSType)))
        SubProcessingForGetImg_Unit_Block_FirstLeftZone(pWGSLT, pWGSRB, iPCSType, sDateTime, iDataProduct, iModelId, iCloulLevel,sDatahomePath, sRslPath, input_shape)
        shutil.rmtree(os.path.join(sRslPath ,"temp"))
        shutil.rmtree(os.path.join(sRslPath ,str(iPCSType)))
    else:
        iaNumLonBtw = iaZone[1] - iaZone[0]
        if iaNumLonBtw == 1:
            iaPCSType = [32600+i for i in iaZone]
            iLonBtw = iaZone[0] * 6 - 180
            pWGSRB_temp = {}
            pWGSLT_temp = {}
            pWGSLB = {}
            pWGSRB_temp['dx'] = iLonBtw - 0.01
            pWGSRB_temp['dy'] = pWGSRB['dy']
            pWGSLT_temp['dx'] = iLonBtw + 0.01
            pWGSLT_temp['dy'] = pWGSLT['dy']
            pWGSLB['dx'] = pWGSLT_temp['dx']
            pWGSLB['dy'] = pWGSRB['dy']
            if os.path.exists(sRslPath):
                os.mkdir(os.path.join(sRslPath ,"temp"))
                os.mkdir(os.path.join(sRslPath ,str(iaPCSType[1])))
                os.mkdir(os.path.join(sRslPath ,str(iaPCSType[0])))
            SubProcessingForGetImg_Unit_Block_FirstLeftZone(pWGSLT, pWGSRB_temp, iaPCSType[0], sDateTime, iDataProduct, iModelId, iCloulLevel, sDatahomePath, sRslPath, input_shape)
            SubProcessingForGetImg_Unit_Block_RightZone(pWGSLT_temp, pWGSRB, pWGSLB, iaPCSType[1], sDateTime, iDataProduct, iModelId, iCloulLevel, sDatahomePath, sRslPath, input_shape)
            shutil.rmtree(os.path.join(sRslPath ,str(iaPCSType[1])))
            shutil.rmtree(os.path.join(sRslPath ,str(iaPCSType[0])))
            shutil.rmtree(os.path.join(sRslPath ,"temp"))
        else:
            iaZoneBtw = []
            iaPCSType = [0, 0]
            pWGSRB_temp = {}
            pWGSLT_temp = {}
            iLonBtw = iaZone[0] * 6 - 180
            pWGSRB_temp['dx'] = iLonBtw - 0.01
            pWGSRB_temp['dy'] = pWGSRB['dy']
            iaPCSType[0] = 32600 + iaZone[0]
            if os.path.exists(sRslPath):
                os.mkdir(os.path.join(sRslPath ,"temp"))
                os.mkdir(os.path.join(sRslPath ,str(iaPCSType[0])))
            SubProcessingForGetImg_Unit_Block_FirstLeftZone(pWGSLT, pWGSRB_temp, iaPCSType[0], sDateTime, iDataProduct, iModelId, iCloulLevel, sDatahomePath, sRslPath, input_shape)
            shutil.rmtree(os.path.join(sRslPath ,"temp"))
            shutil.rmtree(os.path.join(sRslPath ,str(iaPCSType[0])))
            for i in range(iaNumLonBtw):
                iaZoneBtw.append(iaZone[0] + 1 + i)
                iLfLon = iaZoneBtw[i] * 6 - 180 - 6
                if (i != iaNumLonBtw):
                    daiRB = {}
                    daiRB['dx'] = iLfLon + 6 - 0.01
                    daiRB['dy'] = pWGSRB['dy']
                    daiLT = {}
                    daiLT['dx'] = iLfLon + 0.01
                    daiLT['dy'] = pWGSLT['dy']
                    pWGSLB = {}
                    pWGSLB['dx'] = daiLT['dx']
                    pWGSLB['dy'] = daiRB['dy']
                    iaPCSTypeA = 32600 + iaZoneBtw[i]
                    if os.path.exists(sRslPath):
                        os.mkdir(os.path.join(sRslPath ,str(iaPCSType[i])))
                    SubProcessingForGetImg_Unit_Block_RightZone(daiLT, daiRB,pWGSLB, iaPCSTypeA, sDateTime, iDataProduct, iModelId, iCloulLevel, sDatahomePath, sRslPath, input_shape)
                    shutil.rmtree(os.path.join(sRslPath ,str(iaPCSType[i])))
            lastLT = {}
            lastLB = {}
            lastLT['dx'] = (iaZone[0] + iaNumLonBtw) * 6 - 180 - 6 + 0.01
            lastLT['dy'] = pWGSLT['dy']
            lastLB['dx'] = (iaZone[0] + iaNumLonBtw) * 6 - 180 - 6 + 0.01
            lastLB['dy'] = pWGSLB['dy']
            iaPCSType[1] = 32600 + (iaZone[0] + iaNumLonBtw)
            if os.path.exists(sRslPath):
                os.mkdir(os.path.join(sRslPath ,str(iaPCSType[1])))
            SubProcessingForGetImg_Unit_Block_RightZone(lastLT, pWGSRB, lastLB, iaPCSType[1], sDateTime, iDataProduct, iModelId, iCloulLevel, sDatahomePath, sRslPath, input_shape)
            shutil.rmtree(os.path.join(sRslPath ,str(iaPCSType[1])))

if __name__ == "__main__": 
    start = time()
    # if len(sys.argv) != 3:
    #     exit()
    
    #conf.jsonpath = sys.argv[1]
    conf.jsonpath = r"H:\32652\out.geo.json"
    #conf.ID = sys.argv[2]
    conf.ID = '456'
    conf.sDatahomePath = "H:\\RDCRMG_test_data"
    conf.search_time = "20180627"
    conf.sRslPath = "H:\\32652\\2020103100_Data001_" + conf.search_time + "_" + conf.ID
    conf.output_format = '.tif' # available value: .png .tif
    conf.export_excel = pd.DataFrame({"id" : [], 'mean':[]})
    os.mkdir(conf.sRslPath)


    pWGSLT, pWGSRB  = BaseProcesses.read_json_area(conf.jsonpath)
    GetImg_Unit_Block(pWGSLT, pWGSRB, conf.search_time, 1, 0, 6,
     conf.sDatahomePath, conf.sRslPath,
     conf.jsonpath)

    conf.export_excel.to_excel(os.path.join(conf.sRslPath, conf.ID + ".xlsx"))
    end = time()
    print("耗时{0}".format(end-start))
