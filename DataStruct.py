# coding:utf-8 
import os
class DataStruct():

    @staticmethod
    def JudgeLengthOfPixelRang(sPathName):
        '''输入一个不含文件格式的文件名，判断其像元定位元素的位长
        '''
        sFilename,t = os.path.splitext(sPathName)
        return int((len(sFilename) - 21) / 4)#21 = 6（格网编码） + 8(日期) + 3(空间分辨率) + 1(云级别) + 3（数据类型） ; 4:因为像元定位元素有四部分组成，每部分位数等长

    @staticmethod
    def GetBasicDataInforList(lsFilePathname):
        lBds = []
        for sPathName in lsFilePathname:
            bds = basic_data_struct()
            bds.sPathName = sPathName
            sFilename = os.path.basename(sPathName)
            bds.sGridCode = sFilename[0: 6]
            bds.sTimeYear = sFilename[6: 10]
            bds.sTimeDeail = sFilename[6: 14]
            print(sFilename)
            iMarkPixelRang = DataStruct.JudgeLengthOfPixelRang(sFilename)

            bds.iColumnBeg =  int(sFilename[14: 14 + iMarkPixelRang])
            bds.iRowBeg =  int(sFilename[14 + iMarkPixelRang: 14 + 2 * iMarkPixelRang])
            bds.iColumnRange =  int(sFilename[14 + 2 * iMarkPixelRang: 14 + 3 * iMarkPixelRang])
            bds.iRowRange =  int(sFilename[14 + 3 * iMarkPixelRang: 14 + 4 * iMarkPixelRang])
            bds.iResolution = int(sFilename[14 + 4 * iMarkPixelRang: 17 + 4 * iMarkPixelRang])
            bds.iCloudLevel = int(sFilename[14 + 4 * iMarkPixelRang + 3: 18 + 4 * iMarkPixelRang])
            bds.iDataProduct = int(sFilename[14 + 4 * iMarkPixelRang + 4: 21 + 4 * iMarkPixelRang])
            if bds.iResolution == 999:
                bds.iResolution = 1000
            lBds.append(bds)
        return lBds

class basic_data_struct():

    def __init__(self, sPathName = '', sTimeYear = '', sGridCode = '', sTimeDeail = '',\
            ColumnBeg = 0, RowBeg = 0, ColumnRange = 0, RowRange = 0,\
            Resolution = 0, CloudLevel = 0, DataProduct = 0):
        '''iCloudLevel:值域[0,1,2,3,…,9]  0:[0%,10%)  1:[10%,20%)
           iDataProduct:值域：“1”：GF-1 16m
                              “11”:GF-1 8m  
                              “21”:GF-1 2m  
                              “3”：MODIS TDVI干旱产品(1个波段)
                              “13”：MOD11A1_Land surface Temperature_10:30
                              “23”：MYD11A1_Land surface Temperature_13:30
                              “4”：作物类型样本数据 （2个波段，第1个波段为样本编号，第2个波段为样本代表的作物类型）
                              “994”：耕地样本数据
                              “009”：DEM高程数据_30m（1个波段，int16）
        '''
        self.sPathName = sPathName
        self.sTimeYear = sTimeYear
        self.sGridCode = sGridCode
        self.sTimeDeail = sTimeDeail
        self.__iColumnBeg = int(ColumnBeg)
        self.__iRowBeg = int(RowBeg)
        self.__iColumnRange = int(ColumnRange)
        self.__iRowRange = int(RowRange)
        self.__iResolution = int(Resolution)
        self.__iCloudLevel = int(CloudLevel)
        self.__iDataProduct = int(DataProduct)

            