# coding:utf-8
import math
class CoordinateAndProjection:
    sm_a = 6378137.0
    sm_b = 6356752.314
    UTMScaleFactor = 0.9996
    def __init__(self):
        pass 
    
    @staticmethod
    def LongitudeToUTMProjZone(dLon):
        return math.ceil((dLon + 180.0) / 6)

    @staticmethod 
    def GeoCdnToGridCode(point):
        '''由地理坐标，求算所在10km格网编码'''
        pPrjCdn = CoordinateAndProjection.GeoCdnToPrjCdn(point)
        return CoordinateAndProjection.PrjCdnToGridCode(pPrjCdn)

    @classmethod
    def PrjCdnToGridCode(cls, pInput):
        '''将UTM投影坐标转换为格网编码——输入一个投影坐标，返回一个6位的格网编码'''
        iaGridCode = [0] * 4
        iaGridCode[0] = int(pInput['dy'] / 100000)
        iaGridCode[1] = int(pInput['dx']/ 100000)
        iaGridCode[2] = int((pInput['dy'] - iaGridCode[0] * 100000) / 10000)
        iaGridCode[3] = int((pInput['dx'] - iaGridCode[1] * 100000) / 10000)
        IntToString = CoordinateAndProjection.IntToString
        sGridCode = IntToString(iaGridCode[0], 2) +\
                        IntToString(iaGridCode[1], 2) +\
                        IntToString(iaGridCode[2], 1) +\
                        IntToString(iaGridCode[3], 1)

        return sGridCode

    @staticmethod
    def IntToString(iInput, iResultLength):
        '''将一个整型转化为字符串型，且如果字符串长度小于指定的iResultLength，
           则在字符串首添加字符“0”，直到字符串长度等于iResultLength
           如int 3,经过该函数处理，变为“003”
        '''
        return str(iInput).rjust(iResultLength,'0')


    @classmethod 
    def GeoCdnToPrjCdn(cls, point):
        '''将WGS坐标转化为UTM投影坐标 '''
        if 'dx' not in point.keys() or 'dy' not in point.keys():
            raise TypeError("point参数不正确")

        lon = point['dx']
        lat = point['dy']

        zone = int((lon + 180.0) / 6) + 1
        cm = CoordinateAndProjection.UTMCentralMeridian(zone)
        xy = CoordinateAndProjection.MapLatLonToXY(lat / 180.0 * math.pi, lon / 180 * math.pi, cm)
        xy[0] = xy[0] * cls.UTMScaleFactor + 500000.0
        xy[1] = xy[1] * cls.UTMScaleFactor
        if xy[1] < 0.0:
                xy[1] = xy[1] + 10000000.0
        return {'dx' : xy[0], 'dy' : xy[1]}

    @classmethod
    def MapLatLonToXY(cls, phi, lam, lambda0):
        sm_a = cls.sm_a
        sm_b = cls.sm_b

        ep2 = (math.pow(sm_a, 2.0) - math.pow(sm_b, 2.0)) / math.pow(sm_b, 2.0)
        nu2 = ep2 * math.pow(math.cos(phi), 2.0)
        N = math.pow(sm_a, 2.0) / (sm_b * math.sqrt(1 + nu2))
        t = math.tan(phi)
        t2 = t * t

        l = lam - lambda0
        ''' Precalculate coefficients for l**n in the equations below
               so a normal human being can read the expressions for easting
               and northing
               -- l**1 and l**2 have coefficients of 1.0 '''
        l3coef = 1.0 - t2 + nu2
        l4coef = 5.0 - t2 + 9 * nu2 + 4.0 * (nu2 * nu2)
        l5coef = 5.0 - 18.0 * t2 + (t2 * t2) + 14.0 * nu2\
                - 58.0 * t2 * nu2
        l6coef = 61.0 - 58.0 * t2 + (t2 * t2) + 270.0 * nu2\
                - 330.0 * t2 * nu2
        l7coef = 61.0 - 479.0 * t2 + 179.0 * (t2 * t2) - (t2 * t2 * t2)
        l8coef = 1385.0 - 3111.0 * t2 + 543.0 * (t2 * t2) - (t2 * t2 * t2)

        res = [0] * 2
        res[0] = N * math.cos(phi) * l\
                + (N / 6.0 * math.pow(math.cos(phi), 3.0) * l3coef * math.pow(l, 3.0))\
                + (N / 120.0 * math.pow(math.cos(phi), 5.0) * l5coef * math.pow(l, 5.0))\
                + (N / 5040.0 * math.pow(math.cos(phi), 7.0) * l7coef * math.pow(l, 7.0))\

        res[1] = cls.ArcLengthOfMeridian(phi)\
                + (t / 2.0 * N * math.pow(math.cos(phi), 2.0) * math.pow(l, 2.0))\
                + (t / 24.0 * N * math.pow(math.cos(phi), 4.0) * l4coef * math.pow(l, 4.0))\
                + (t / 720.0 * N * math.pow(math.cos(phi), 6.0) * l6coef * math.pow(l, 6.0))\
                + (t / 40320.0 * N * math.pow(math.cos(phi), 8.0) * l8coef * math.pow(l, 8.0))

        return res


    @classmethod
    def ArcLengthOfMeridian(cls, phi):
        sm_a = cls.sm_a
        sm_b = cls.sm_b

        n = (sm_a - sm_b) / (sm_a + sm_b)
        alpha = ((sm_a + sm_b) / 2.0)\
               * (1.0 + (math.pow(n, 2.0) / 4.0) + (math.pow(n, 4.0) / 64.0))
        beta = (-3.0 * n / 2.0) + (9.0 * math.pow(n, 3.0) / 16.0)\
               + (-3.0 * math.pow(n, 5.0) / 32.0)
        gamma = (15.0 * math.pow(n, 2.0) / 16.0)\
                + (-15.0 * math.pow(n, 4.0) / 32.0)
        delta = (-35.0 * math.pow(n, 3.0) / 48.0)\
                + (105.0 * math.pow(n, 5.0) / 256.0)
        epsilon = (315.0 * math.pow(n, 4.0) / 512.0)

        return alpha\
                * (phi + (beta * math.sin(2.0 * phi))\
                    + (gamma * math.sin(4.0 * phi))\
                    + (delta * math.sin(6.0 * phi))\
                    + (epsilon * math.sin(8.0 * phi)))

    @staticmethod 
    def UTMCentralMeridian(zone):
        deg = -183.0 + (zone * 6.0)
        return deg / 180.0 * math.pi

