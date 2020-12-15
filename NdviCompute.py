# coding:utf-8

from osgeo import gdal
import pandas as pd
import numpy as np
from PIL import Image
import os

from BaseProcesses import BaseProcesses

import conf
IMAGE_TYPE_GF1 = 1

color_list = [[194, 82, 60], [217, 116, 39], [237, 167, 17], [250, 226, 7],\
    [180, 245, 0], [33, 222, 0], [17, 189, 83], [32, 153, 143]]

def div0( a, b ):
    """ ignore / 0, div0( [-1, 0, 1], 0 ) -> [0, 0, 0] """
    with np.errstate(divide='ignore', invalid='ignore'):
        c = np.true_divide( a, b )
        c[ ~ np.isfinite( c )] = 0  # -inf inf NaN
    return c

def ndvi_compute_byfile(input_path, output_path, image_type):
    input_dataset = gdal.Open(input_path)
    mean = ndvi_compute_byds(input_dataset, output_path, image_type)
    del input_dataset
    return mean

def ndvi_compute_byds(input_dataset, output_path, image_type):
    dGeoTransform = list(input_dataset.GetGeoTransform())
    sGeoProjectionRef = input_dataset.GetProjectionRef()
    iColumnRange = input_dataset.RasterXSize
    iRowRange = input_dataset.RasterYSize
    if image_type == IMAGE_TYPE_GF1:
        r_band = input_dataset.GetRasterBand(3).ReadAsArray(0, 0, iColumnRange, iRowRange)
        nr_band = input_dataset.GetRasterBand(4).ReadAsArray(0, 0, iColumnRange, iRowRange)
    ndvi_band = div0(((nr_band * 1.0 - r_band * 1.0) ), ((nr_band * 1.0 + r_band * 1.0)))
    mean = ndvi_band.mean()
    if os.path.splitext(output_path)[-1] == ".tif":
        dataset_res = BaseProcesses.CreateNewImage(output_path, dGeoTransform, sGeoProjectionRef, iColumnRange, iRowRange, 1, gdal.GDT_Float32)
        dataset_res.GetRasterBand(1).WriteArray(ndvi_band, 0, 0)
        del dataset_res
    elif os.path.splitext(output_path)[-1] == ".png":
        # ndvi_band = (ndvi_band - np.min(ndvi_band)) * 255 / np.max(ndvi_band)
        # im = Image.fromarray(np.uint8(ndvi_band))
        # im.save(output_path)
        output_band = np.zeros((iRowRange, iColumnRange, 4), dtype = np.uint8)
        for i in range(iRowRange):
            for j in range(iColumnRange):
                output_band[i, j, :] = np.array(color_list[int((ndvi_band[i, j] + 1) * 4 - 0.0001)] + [255])
                if ndvi_band[i, j] == 0:
                    output_band[i, j, :] = np.array([0, 0, 0, 0])
        im = Image.fromarray(output_band)
        im.save(output_path)
    return mean