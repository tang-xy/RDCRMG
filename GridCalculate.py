# coding:utf-8
import numpy as np
import os.path
class GridCalculate:
    @staticmethod
    def IntToString(iInput, iResultLength):
        '''将一个整型转化为字符串型，且如果字符串长度小于指定的iResultLength，
           则在字符串首添加字符“0”，直到字符串长度等于iResultLength
           如int 3,经过该函数处理，变为“003”
        '''
        return str(iInput).rjust(iResultLength,'0')

    @staticmethod
    def GridCodeToGridlist_iPCSType(sGridCodeLT, sGridCodeRB, iPCSType):
        lsResult = GridCalculate.GridCodeToGridlist(sGridCodeLT, sGridCodeRB)
        return [os.path.join(str(iPCSType), sResult[0:4], sResult[-2:]) for sResult in lsResult]


    @staticmethod
    def LtPointRecaculate(sGridCodeLT, sGridCodeRB, sGridCodeLB):
        IntToString = GridCalculate.IntToString
        CaculateYNumOrXNum = GridCalculate.CaculateYNumOrXNum
        iaGridCodeBase = np.empty((4), dtype=int)
        iaGridCodeTemp = np.empty((4), dtype=int)
        iaGridCodeBase = GridCalculate.GetCodeOfGrid(sGridCodeLT)
        iaGridCodeTemp = GridCalculate.GetCodeOfGrid(sGridCodeLT)
        iTNumY = GridCalculate.CaculateYNumOrXNum(sGridCodeLT, sGridCodeRB, "y") + 1
        if (iTNumY > iaGridCodeTemp[2]):
            a = (iTNumY - iaGridCodeTemp[2]) / 10
            pass
        else:
            iaGridCodeTemp[2] = iaGridCodeTemp[2] - iTNumY - 1
        sGridTemp = IntToString(iaGridCodeTemp[0], 2) + IntToString(iaGridCodeTemp[1], 2)\
            + IntToString(iaGridCodeTemp[2], 1)\
            + IntToString(iaGridCodeTemp[3], 1)
        iTNumX = CaculateYNumOrXNum(sGridCodeLB, sGridTemp, "x") + 1
        if (iTNumX > iaGridCodeBase[3]):
            pass
        else:
            iaGridCodeBase[3] = iaGridCodeBase[3] - iTNumX - 1
        resGridCodeLT = IntToString(iaGridCodeBase[0], 2) + IntToString(iaGridCodeBase[1], 2)\
                                                               + IntToString(iaGridCodeBase[2], 1)\
                                                               + IntToString(iaGridCodeBase[3], 1)
        return resGridCodeLT

    @staticmethod
    def GridCodeToGridlist(sGridCodeLT, sGridCodeRB):
        '''由所求范围的左上角和右下角格网编码,求算其包含的格网序列'''
        IntToString = GridCalculate.IntToString
        CaculateYNumOrXNum = GridCalculate.CaculateYNumOrXNum
        GetCodeOfGrid = GridCalculate.GetCodeOfGrid
        lsResult = []

        iTNumY = CaculateYNumOrXNum(sGridCodeLT, sGridCodeRB, "y") + 1
        iTNumX = CaculateYNumOrXNum(sGridCodeLT, sGridCodeRB, "x") + 1
        iaGridCodeBase = GetCodeOfGrid(sGridCodeLT)
        iaGridCodeTemp = GetCodeOfGrid(sGridCodeLT)

        for j in range(iTNumY):
            for i in range(iTNumX):
                if i != 0:
                    iaGridCodeTemp[3] += 1
                    if iaGridCodeTemp[3] > 9:
                        iaGridCodeTemp[1] += 1
                        iaGridCodeTemp[3] = 0
                sGridTemp = IntToString(iaGridCodeTemp[0], 2) + IntToString(iaGridCodeTemp[1], 2)\
                    + IntToString(iaGridCodeTemp[2], 1) + IntToString(iaGridCodeTemp[3], 1)
                lsResult.append(sGridTemp)
            iaGridCodeTemp[2] -= 1
            if iaGridCodeTemp[2] < 0:
                iaGridCodeTemp[0] -= 1
                iaGridCodeTemp[2] = 9
            iaGridCodeTemp[1] = iaGridCodeBase[1]
            iaGridCodeTemp[3] = iaGridCodeBase[3]
        return lsResult

    @staticmethod
    def GetCodeOfGrid_with_type(sGridCode, sType):
        '''给定一个格网编码及对应的格网子项（HkmY，HkmX，TkmY，TkmX），返回该项的值'''
        if sType == "HkmY":
            iCodeTemp = int(sGridCode[0: 2])
        elif sType == "HkmX":
            iCodeTemp = int(sGridCode[2: 4])
        elif sType == "TkmY":
            iCodeTemp = int(sGridCode[4: 5])
        elif sType == "TkmX":
            iCodeTemp = int(sGridCode[5: 6])
        return iCodeTemp

    @staticmethod
    def CaculateYNumOrXNum(ssGridCode1, ssGridCode2, sDirection):
        '''给定两个格网编码及需求解的方向（string，y or x），返回它们间相隔10公里格网数'''
        GetCodeOfGrid = GridCalculate.GetCodeOfGrid_with_type
        if sDirection == "y":
            iHkmY_0 = GetCodeOfGrid(ssGridCode1, "HkmY")
            iTkmY_0 = GetCodeOfGrid(ssGridCode1, "TkmY")

            iHkmY_1 = GetCodeOfGrid(ssGridCode2, "HkmY")
            iTkmY_1 = GetCodeOfGrid(ssGridCode2, "TkmY")

            iResule = -(iTkmY_1 - iTkmY_0 + (iHkmY_1 - iHkmY_0) * 10)
        elif sDirection == "x":
            iHkmX_0 = GetCodeOfGrid(ssGridCode1, "HkmX")
            iTkmX_0 = GetCodeOfGrid(ssGridCode1, "TkmX")

            iHkmX_1 = GetCodeOfGrid(ssGridCode2, "HkmX")
            iTkmX_1 = GetCodeOfGrid(ssGridCode2, "TkmX")

            iResule = iTkmX_1 - iTkmX_0 + (iHkmX_1 - iHkmX_0) * 10
        return iResule

    @staticmethod
    def GetCodeOfGrid(sGridCode):
        '''给定一个格网编码,返回一个4位长度的整型数组，分别为HkmY，HkmX，TkmY，TkmX'''
        # iaGridCode = np.empty((4), dtype=int)
        iaGridCode = [0] * 4

        iaGridCode[0] = int(sGridCode[0: 2])
        iaGridCode[1] = int(sGridCode[2: 4])
        iaGridCode[2] = int(sGridCode[4: 5])
        iaGridCode[3] = int(sGridCode[5: 6])

        return iaGridCode

    @staticmethod
    def CalculateOffset(iHkmNum, iTkmNum, iDistance):
        ''' 给定百公里和10公里的编码，及对应方向的延伸长度，返回新的格网编码
            1 求算sum = y(x) + Δy(x) 
            2 求算qt(qutient) = sum/10,rd(remainder) = sum % 10
            3 判断 rd < 0 的真假
            3-1 真，qt -= 1, rd +=10
            3-2 假，qt，rd 不变
            4 HkmRlt = HkmNum + qt, TkmRlt = TkmNum + rd
        '''
        iSum = iTkmNum + iDistance
        # HTkmRlt = np.empty((2), dtype=int)
        HTkmRlt = [0] * 2
        iQt = int(iSum / 10)
        iRd = iSum % 10
        if iRd < 0:
            iQt -= 1
            iRd += 10
        HTkmRlt[0] = iHkmNum + iQt
        HTkmRlt[1] = iRd
        return HTkmRlt

    @staticmethod
    def DivideDataBlocks(sGridCodeLT, sGridCodeRB, iXBlocksLth = 100, iYBlocksLth = 100):
        ''' 将基准格网的各项(HkmY，HkmX，TkmY，TkmX)从字符创中取出，存为整型以供计算 
            2 获取初始范围的Δx,Δy
            3 Δx / iXBlocksLth,Δx % iXBlocksLth ;Δy / iYBlocksLth,Δy % iYBlocksLth
            4 确定x,y分块节点数
            5 求算x,y各分块节点的值
            6 根据分块节点值，组合各数据块的左上右下格网编码
        '''
        CalculateOffset = GridCalculate.CalculateOffset
        # iaQtRdX = np.empty((2), dtype=int) # 一维列数组，第1行：总格网数与块单元x方向的格网数的商；第2行：总格网数与块单元x方向的格网数的余数
        # iaQtRdY = np.empty((2), dtype=int) # 一维列数组，第1行：总格网数与块单元y方向的格网数的商；第2行：总格网数与块单元y方向的格网数的余数
        # iaGridCodeTempLT = np.empty((4), dtype=int)
        # iaGridCodeTempRB = np.empty((4), dtype=int)
        iaQtRdX = [0] * 2 # 一维列数组，第1行：总格网数与块单元x方向的格网数的商；第2行：总格网数与块单元x方向的格网数的余数
        iaQtRdY = [0] * 2 # 一维列数组，第1行：总格网数与块单元y方向的格网数的商；第2行：总格网数与块单元y方向的格网数的余数
        iaGridCodeTempLT = [0] * 4
        iaGridCodeTempRB = [0] * 4

        iaGridCodeLT = GridCalculate.GetCodeOfGrid(sGridCodeLT)
        iaGridCodeRB = GridCalculate.GetCodeOfGrid(sGridCodeRB)

        iTNumX = GridCalculate.CaculateYNumOrXNum(sGridCodeLT, sGridCodeRB, "x") + 1
        iTNumY = GridCalculate.CaculateYNumOrXNum(sGridCodeLT, sGridCodeRB, "y") + 1

        iaQtRdX[0] = int(iTNumX / iXBlocksLth)
        iaQtRdX[1] = iTNumX % iXBlocksLth
        iaQtRdY[0] = int(iTNumY / iYBlocksLth)
        iaQtRdY[1] = iTNumY % iYBlocksLth

        if iaQtRdX[1] != 0:
            iXBlocksNum = iaQtRdX[0] + 2
        else:
            iXBlocksNum = iaQtRdX[0] + 1
        iaXBlocks = np.empty((iXBlocksNum, 2), dtype=int)
        # iaXBlocks = [[0] * 2] * iXBlocksNum

        if iaQtRdY[1] != 0:
            iYBlocksNum = iaQtRdY[0] + 2
        else:
            iYBlocksNum = iaQtRdY[0] + 1
        iaYBlocks = np.empty((iYBlocksNum, 2), dtype=int)
        # iaYBlocks = [[0] * 2] * iYBlocksNum

        iaXBlocks[0][0] = iaGridCodeLT[1]
        iaXBlocks[0][1] = iaGridCodeLT[3]
        iaXBlocks[iXBlocksNum - 1][0] = iaGridCodeRB[1]
        iaXBlocks[iXBlocksNum - 1][1] = iaGridCodeRB[3]
        for i in range(1, iXBlocksNum - 1):
            iaXBlocks[i] = CalculateOffset(iaXBlocks[i - 1][0], iaXBlocks[i - 1][1], iXBlocksLth)

        iaYBlocks[0][0] = iaGridCodeLT[0]
        iaYBlocks[0][1] = iaGridCodeLT[2]
        iaYBlocks[iYBlocksNum - 1][0] = iaGridCodeRB[0]
        iaYBlocks[iYBlocksNum - 1][1] = iaGridCodeRB[2]
        for i in range(1, iYBlocksNum - 1):
            iaYBlocks[i] = CalculateOffset(iaYBlocks[i - 1][0], iaYBlocks[i - 1][1], -iYBlocksLth)
        lsGridCodeLTRB = []
        for j in range(iYBlocksNum - 1):
            for i in range(iXBlocksNum - 1):
                iaGridCodeTempLT[0] = iaYBlocks[j][0]
                iaGridCodeTempLT[2] = iaYBlocks[j][1]
                iaGridCodeTempLT[1] = iaXBlocks[i][0]
                iaGridCodeTempLT[3] = iaXBlocks[i][1]
                if i != (iXBlocksNum - 2) and j != (iYBlocksNum - 2):
                    iaTempY = CalculateOffset(iaYBlocks[j + 1][0], iaYBlocks[j + 1][1], 1)
                    iaTempX = CalculateOffset(iaXBlocks[i + 1][0], iaXBlocks[i + 1][1], -1)
                    iaGridCodeTempRB[0] = iaTempY[0]
                    iaGridCodeTempRB[2] = iaTempY[1]
                    iaGridCodeTempRB[1] = iaTempX[0]
                    iaGridCodeTempRB[3] = iaTempX[1]
                elif i == (iXBlocksNum - 2) and j != (iYBlocksNum - 2):
                    iaTempY = CalculateOffset(iaYBlocks[j + 1][0], iaYBlocks[j + 1][1], 1)
                    iaGridCodeTempRB[0] = iaTempY[0]
                    iaGridCodeTempRB[2] = iaTempY[1]
                    iaGridCodeTempRB[1] = iaXBlocks[i + 1][0]
                    iaGridCodeTempRB[3] = iaXBlocks[i + 1][1]
                elif i != (iXBlocksNum - 2) and j == (iYBlocksNum - 2):
                    iaTempX = CalculateOffset(iaXBlocks[i + 1][0], iaXBlocks[i + 1][1], -1)
                    iaGridCodeTempRB[1] = iaTempX[0]
                    iaGridCodeTempRB[3] = iaTempX[1]
                    iaGridCodeTempRB[0] = iaYBlocks[j + 1][0]
                    iaGridCodeTempRB[2] = iaYBlocks[j + 1][1]
                elif i == (iXBlocksNum - 2) and j == (iYBlocksNum - 2):
                    iaGridCodeTempRB[0] = iaYBlocks[j + 1][0]
                    iaGridCodeTempRB[2] = iaYBlocks[j + 1][1]
                    iaGridCodeTempRB[1] = iaXBlocks[i + 1][0]
                    iaGridCodeTempRB[3] = iaXBlocks[i + 1][1]
                sGridCodeTempLTRB = [''] * 2
                sGridCodeTempLTRB[0] = GridCalculate.IntToString(iaGridCodeTempLT[0], 2)
                sGridCodeTempLTRB[0] += GridCalculate.IntToString(iaGridCodeTempLT[1], 2)
                sGridCodeTempLTRB[0] += GridCalculate.IntToString(iaGridCodeTempLT[2], 1)
                sGridCodeTempLTRB[0] += GridCalculate.IntToString(iaGridCodeTempLT[3], 1)

                sGridCodeTempLTRB[1] = GridCalculate.IntToString(iaGridCodeTempRB[0], 2)
                sGridCodeTempLTRB[1] += GridCalculate.IntToString(iaGridCodeTempRB[1], 2)
                sGridCodeTempLTRB[1] += GridCalculate.IntToString(iaGridCodeTempRB[2], 1)
                sGridCodeTempLTRB[1] += GridCalculate.IntToString(iaGridCodeTempRB[3], 1)

                lsGridCodeLTRB.append(sGridCodeTempLTRB)

        return lsGridCodeLTRB

