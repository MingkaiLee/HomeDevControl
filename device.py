import time
import numpy as np
import pandas as pd
import sys

path = "/Users/limingkai/vsCode/Python_WorkSpace/HomeDevControl"

from pandas.core.series import Series
sys.path.append(path)
from myframe import MyFrame


# 设备控制基类
class Device:
    def __init__(self, devId, devAddr) -> None:
        self.__devId = devId
        self.__devAddr = devAddr
    
    def getDevId(self) -> int:
        return self.__devId
    
    def getDevAddr(self) -> str:
        return self.__devAddr
    
    def getTime(self) -> np.datetime64:
        """
        ### 获取当前的时间戳
        #### Returns:
        - timestamp: 调用该方法的时间戳, np.datetime64
        """
        return np.datetime64(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

class Sensor(Device):
    def __init__(self, devId, devAddr) -> None:
        """
        #### Parameters:
        - devId: 设备的ID, int
        - devAddr: 设备的目的地址, str
        """
        super().__init__(devId, devAddr)
        index = pd.Index(('温度', '湿度', 'PM2.5', 'CO2', '甲醛', 'VOC'), name='项目')
        self.__data = pd.Series(np.zeros(6), index=index, dtype=np.float16)
        # 最后一次查询调用的命令内容
        self.__lastCallContents = None
        # 最后一次查询调用的时间戳
        self.__lastCallTime = pd.Series(np.full(6, super().getTime()), index=index)
        # 最后一次收到查询调用回复的时间戳
        # 设备创建时执行一次查询

    def getValFrame(self, valType):
        """
        ### 生成获取某一个参数的命令帧
        #### Parameters:
        - valType: 获取的数据种类, int
        #### Returns:
        - __lastCallContents: 最新发送的命令
        """
        if valType not in range(6):
            raise ValueError('Un')
        head = 'fe'
        cmd = '24 5f'
        data = super().getDevAddr() + ' 01 03 00 0' + hex(valType).lstrip('0x') + ' 00 01'
        self.__lastCallContents = MyFrame(head, cmd, data)
        return self.__lastCallContents

    def getValsFrame(self):
        """
        ### 生成获取所有参数的命令帧
        #### Returns:
        - __lastCallContents: 最新发送的命令
        """
        head = 'fe'
        cmd = '24 5f'
        data = super().getDevAddr() + ' 01 03 00 00 00 06'
        self.__lastCallContents = MyFrame(head, cmd, data)
        return self.__lastCallContents
    
    def getData(self) -> pd.Series:
        """
        ### 获取当前的结果
        #### Returns:
        - __data: 数据, pd.Series
        """
        return self.__data
    
    def getCallTime(self) -> pd.Series:
        """
        ### 获取获取当前结果的命令发送时对应的时间戳
        #### Returns:
        - __lastCallTime
        """
        return self.__lastCallTime

class Lamp(Device):
    def __init__(self, devId, devAddr) -> None:
        """
        #### Parameters:
        - devID: 设备的ID, int
        - devAddr: 设备的目的地址, str
        """
        super().__init__(devId, devAddr)
        index = pd.Index(('开关', '亮度', '色温'), name='项目')
        self.__data = pd.Series(np.zeros(0, dtype=np.int32), index=index)
        # 最后一次查询调用的命令的内容
        self.__lastCallContents = None
        # 最后一次查询调用的时间戳
        self.__lastCallTime = super().getTime()
        # 最后一次收到查询调用回复的时间戳
        self.__lastCallConfirmTime = super().getTime()
        # 最后一次更改调用的命令的内容
        self.__lastCtlContents = None
        # 最后一次更改调用的命令的时间戳
        self.__lastCtlTime = super().getTime()
    
    def getValsFrame(self):
        """
        ### 生成获取所有参数的命令帧
        #### Returns:
        - __lastCallContents: 最新发送的状态查询命令
        """
        head = 'fe'
        cmd = '24 5f'
        data = super().getDevAddr() + ' 01 03 00 00 00 03'
        self.__lastCallContents = MyFrame(head, cmd, data)
        return self.__lastCallContents
    
    def writeValsFrame(self, switch=None, luminance=None, ct=None, vt=0, ddt=0, drt=0):
        """
        ### 生成更改灯具状态的命令帧
        对于灯的状态参数, 无输入时表示维持; 对于时间参数, 无输入时表示为0
        #### Parameters:
        - switch: 开关
        - luminance: 亮度
        - ct: 色温
        - vt: 变化时间
        - ddt: 延迟执行时间
        - drt: 延迟回复时间
        #### Returns:
        - __lastCtlContents: 最新发送的状态更改命令
        """
        head = 'fe'
        cmd = '24 5f'
        data = super().getDevAddr() + ' 01 10 00 00 00 06 0c'
        

if __name__ == '__main__':
    print('debug')