#encoding:utf-8
import conf
import NdviCompute 
import pandas as pd
from osgeo import gdal
from PIL import Image
import os
import numpy as np
def clip_dataset_list_groupby_time(grid_list, time):
    '''输入相同时间的一组grid_list，对其进行拼接剪切
    '''
    conf.export_excel = pd.DataFrame({"id" : [], 'mean':[]})
    output_path = os.path.join(conf.sRslPath, conf.ID + time + '_1.tif')
    print(output_path)
    options=gdal.WarpOptions(format='GTiff', cutlineDSName = conf.jsonpath, dstSRS='EPSG:900913')
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
