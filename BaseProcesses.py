# coding:utf-8
from osgeo import gdal

import json
import os

class BaseProcesses:
    
    @staticmethod
    def CreateNewImage(sFilePathNew, dGeoTransform, sGeoProjectionRef, iColumnRange, iRowRange, iBandNum, dtty):
        if os.path.splitext(sFilePathNew)[-1] == ".tif":
            sImageFormat = 'GTIFF'
        elif os.path.splitext(sFilePathNew)[-1] == ".png":
            sImageFormat = 'PNG'
        driver = gdal.GetDriverByName(sImageFormat)
        dataset = driver.Create(sFilePathNew, int(iColumnRange), int(iRowRange), int(iBandNum), dtty)
        dataset.SetGeoTransform(dGeoTransform)
        dataset.SetProjection(sGeoProjectionRef)
        return dataset

    @staticmethod
    def read_json_area(jsonpath):
        """
        根据一个多边形的geojson，得到该多边形的最小外接矩形
        输入：json路径；输出：矩形的左上、右下坐标
        """
        with open(jsonpath, encoding='utf8') as json_file:
            json_str = json_file.read()
        features = json.loads(json_str)["features"]
        x_max = features[0]['geometry']['coordinates'][0][0][0][0]
        x_min = features[0]['geometry']['coordinates'][0][0][0][0]
        y_max = features[0]['geometry']['coordinates'][0][0][0][1]
        y_min = features[0]['geometry']['coordinates'][0][0][0][1]
        for feature in  features:
            if feature['geometry']['type'] == "Polygon":
                for coordinate in feature['geometry']['coordinates']:
                    for coor2 in coordinate:
                        x_max = max(coor2[0], x_max)
                        x_min = min(coor2[0], x_min)
                        y_max = max(coor2[1], y_max)
                        y_min = min(coor2[1], y_min)
            if feature['geometry']['type'] == "MultiPolygon":
                for coordinate in feature['geometry']['coordinates']:
                    for coor1 in coordinate:
                        for coor2 in coor1:
                            x_max = max(coor2[0], x_max)
                            x_min = min(coor2[0], x_min)
                            y_max = max(coor2[1], y_max)
                            y_min = min(coor2[1], y_min)
        pWGSLT = {'dx':x_min, 'dy':y_max}
        pWGSRB = {'dx':x_max, 'dy':y_min}
        return pWGSLT, pWGSRB