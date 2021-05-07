import pandas as pd
import numpy as np

    
# 响应数据帧类, 方便解析设备的响应数据
class ResFrame:
    def __sensorAnalyze(self) -> pd.Series:
        temperature = (self.__raw[9]*256 + self.__raw[10]) / 10
        humidity = (self.__raw[11]*256 + self.__raw[12]) / 10
        pm25 = self.__raw[13] + self.__raw[14]
        co2 = self.__raw[15] + self.__raw[16]
        hcho = self.__raw[17] + self.__raw[18]
        voc = self.__raw[19] + self.__raw[20]
        index = pd.Index(('温度', '湿度', 'PM2.5', 'CO2', '甲醛', 'VOC'), name='项目')
        data = pd.Series(np.zeros(6), index=index, dtype=np.float32)
        data[0] = temperature
        data[1] = humidity
        data[2] = pm25
        data[3] = co2
        data[4] = hcho
        data[5] = voc

        return data

    def __init__(self, raw, dev) -> None:
        """
        #### Parameters:
        - raw: 串口返回的原始bytes, bytes
        - dev: 设备类型码, int
        """
        self.__raw = raw
        self.__dev = dev
        self.__data = None
        # 从原始bytes中析出数据
        # 六合一传感器
        if dev == 2:
            self.__data = self.__sensorAnalyze()
    
    def getData(self):
        return self.__data
        