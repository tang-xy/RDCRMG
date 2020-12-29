# coding:utf-8
import random
import time
import os
import csv
import shutil

from GridCalculate import GridCalculate
from SearchEngine import SearchEngine
from Stitching import Stitching

def ExtractSITSforEvery10kmGrid(lbds, iDataSet, iDataMap, sWorkSpace):
    '''''''''''''''''''''''''''''''''''''''''''''''''''''
    1 遍历格网集合，确保每个格网中任何一个影像的时相是唯一的
            //规则：
            //   (1) 选择覆盖满10km格网且云量最小的数据文件
            //   (2) 若无覆盖满的，则合并所有时相的数据文件

            //1-1 判断该格网是否含有样本数据，如果有，则截取影像部分的序列'''
    if lbds[0].iDataProduct == iDataMap:
        iStartIndex_Unique = 1
    else:
        iStartIndex_Unique = 0
    lbds_uniqueDate = Stitching.MakeUniqueForEveryDate(lbds[iStartIndex_Unique: ], iDataSet, iDataMap, sWorkSpace)

    if lbds[0].iDataProduct == iDataMap:
        lbds_uniqueDate.insert(0, lbds[0])
    
    lbdsFullCover = Stitching.ExpandToCoverEntire10kmGrid(lbds_uniqueDate, sWorkSpace)

    lbds = lbdsFullCover

    iZoneIndex = lbds[0].sPathName.index("326")
    sZoneName = lbds[0].sPathName[iZoneIndex: 5 + iZoneIndex]
    sRltOfSITSPath = sZoneName + lbds[0].sGridCode
    sRltPathFinaly = os.path.join(sWorkSpace, sRltOfSITSPath)
    os.mkdir(sRltPathFinaly)

    lsFilePathName = [i.sPathName for i in lbds]

    with open(os.path.join(sRltPathFinaly, 'filesPathName.txt'), 'w', encoding='utf8') as f:
        f.write('\n'.join(lsFilePathName))

    Stitching.ExtractTimeSeriesValueAndWritetofile(lbds, sRltPathFinaly)

    iImageSelected = (int)(len(lbds) / 2)

    sFileName = os.path.basename(lbds[iImageSelected].sPathName)

    shutil.copy(lbds[iImageSelected].sPathName, os.path.join(sRltPathFinaly, sFileName))

def GenerateSITSOfPixleLevel(bIrregular = True):
    _sDataHome = r"/mnt/datapool/RemoteSensingData1/DataWorking/"
    _sRslPath = r"./"
    # _sDataHome = "H:\\RDCRMG_test_data"
    sGridcodeTargetFile = r"./8_Manasi_grid_spl.csv"

    iDataSet = 1  #选择待分类数据产品类型，001：GF1-16M
    iDataMap = 664  #选择标签数据产品类型，004：作物样本数据的训练集  664：作物样本数据的测试集
    iCloudlevel = 9    # <100%  之所以云量的阈值如此高，在于发现云检测算法还无法区分雪与云
                        #在高程方差比较大的地方，高山积雪容易混淆，导致误检测而错误舍弃一些质量较好的影像，如西北

    sDateTimeBeg = "20180101"
    sDateTimeEnd = "20180930"

    RandKey = random.randint(1,999)

    sProcessType = "IrglSITS"
    if(not bIrregular):
        sProcessType = "RglSITS"
    IntToString = GridCalculate.IntToString
    sWorkSpaceName = time.strftime("%Y%m%d%H", time.localtime()) + "_"\
                              + sDateTimeBeg + "_"\
                              + sDateTimeEnd + "_"\
                              + sProcessType + "_" + IntToString(iDataSet, 3) + "-"\
                              + IntToString(iDataMap, 3) + "-"\
                              + IntToString(RandKey, 3)

    sWorkSpace = os.path.join(_sRslPath, sWorkSpaceName)
    os.mkdir(sWorkSpace)

    starttime = time.time()

    lsGridcode = []

    with open(sGridcodeTargetFile) as f:
        f_csv = csv.reader(f)
        for row in f_csv:
            grid = row[0]
            sZone = grid[0: 5]
            s100kmcode = grid[5: 9]
            s10kmcode = grid[9: 11]
            lsGridcode.append(os.path.join(sZone, s100kmcode, s10kmcode))
            if not os.path.exists(os.path.join(sWorkSpace, sZone)):
                os.mkdir(os.path.join(sWorkSpace, sZone))
    llbds = SearchEngine.SearchSatMap(lsGridcode, sDateTimeBeg, sDateTimeEnd, iDataSet, iDataMap, iCloudlevel, _sDataHome)
    if not bIrregular:
        Stitching.ObtainDateIntersectionAmongGridSet(llbds)


    for lbds in llbds:
        ExtractSITSforEvery10kmGrid(lbds, iDataSet, iDataMap, sWorkSpace)
    endtime = time.time()

    iNumGrid = len(llbds)
    sRltReport = "10km格网数目： " + str(iNumGrid) + "\n" + "结果目录： " + sWorkSpace + "\n耗时" + str(endtime - starttime) + " s"
    print(sRltReport)

if __name__ == "__main__":
    GenerateSITSOfPixleLevel()