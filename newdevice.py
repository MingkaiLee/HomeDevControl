"""
## 本模块抽象设备, 功能为抽象出设备后更方便地获取命令帧
## Attention: 确保在调用get开头的获取帧的方法后成功将帧发出
"""
import time
import numpy as np
import pandas as pd
import sys


sys.path.append('D:\house app\物联网\lmk\IoTLab\myframe.py')
from myframe import MyFrame


# 设备基类
class Device:
    """
    ### 设备基类
    #### Attributes:
    - _devId: 设备在控制端的识别码
    - _devAddr: 设备的目的地址
    - _lastCall: 上一次调用的查询命令的内容
    - _lastCallTime: 上一次调用的查询命令发送时间戳
    - _lastCallRes: 上一次调用的查询命令返回的内容
    - _lastCallResTime: 上一次调用的查询命令返回的时间戳
    """
    def __init__(self, devId, devAddr:int) -> None:
        self._devId = devId
        self._devAddr = self.getWordStr(devAddr, True)
        self._lastCall = None
        self._lastCallTime = None
        self._lastCallRes = None
        self._lastCallResTime = None
        self._data = None

    def getWordStr(self, addr: int, desc=False) -> str:
        """
        ### 10进制整数转表双字节的字符串, 输入范围不检验, 默认合法
        #### Parameters:
        - addr: 10进制设备地址
        - desc: 置为True时低位在前, 默认为False
        #### Returns:
        - res: 'xx xx'式表双字节字符串
        """
        x = hex(addr)[2:]
        res = None
        if desc:
            if len(x) == 1:
                res = f"0{x} 00"
            elif len(x) == 2:
                res = f"{x} 00"
            elif len(x) == 3:
                res = f"{x[-2:]} 0{x[0]}"
            else:
                res = f"{x[-2:]} {x[:2]}"
        else:
            if len(x) == 1:
                res = f"00 0{x}"
            elif len(x) == 2:
                res = f"00 {x}"
            elif len(x) == 3:
                res = f" 0{x[0]} {x[-2:]}"
            else:
                res = f"{x[:2]} {x[-2:]}"
        return res
    
    def getDevId(self) -> object:
        return self._devId
    
    def getDevAddr(self) -> str:
        return self._devAddr

    def generateCallFrame(self) -> str:
        """
        定义获取数据帧的接口, 子类需覆写
        """
        pass
    
    def getData(self) -> str:
        """
        定义获取设备数据的接口, 子类需覆写
        """
        pass

class Sensor(Device):
    """
    ### 传感器基类, 继承自设备基类
    #### Attributes:
    """
    def __init__(self, devId, devAddr: int) -> None:
        super().__init__(devId, devAddr)
        index = pd.Index(('温度', '湿度', 'PM2.5', 'CO2', '甲醛', 'VOC'), name='项目')
        self._data = pd.Series(np.zeros(6), index=index, dtype=np.float16)
    
    def generateCallFrame(self) -> object:
        """
        ### 生成获取所有参数的命令帧
        #### Returns:
        - _lastCall: 最新发送的命令
        """
        head = 'fe'
        cmd = '24 5f'
        data = super().getDevAddr() + ' 01 03 00 00 00 06'
        self._lastCall = MyFrame(head, cmd, data)
        return self._lastCall

    def generateValFrame(self, valType: int) -> object:
        """
        ### 生成获取某一个参数的命令帧
        #### Parameters:
        - valType: 获取的数据种类, int: 0-5
        #### Returns:
        - _lastCall: 最新发送的命令
        """
        if valType not in range(6):
            raise ValueError('Input out of range. Expected in [0, 5]')
        head = 'fe'
        cmd = '24 5f'
        data = super().getDevAddr() + ' 01 03 00 ' + super().getWordStr(valType) + ' 00 01'
        self._lastCall = MyFrame(head, cmd, data)
        return self._lastCall

class Lamp(Device):
    """
    ### 灯具类, 继承自设备基类
    #### Attributes:
    """
    def __init__(self, devId, devAddr: int) -> None:
        super().__init__(devId, devAddr)
        index = pd.Index(('开关', '亮度', '色温'), name='项目')
        self._data = pd.Series(np.zeros(3), index=index, dtype=np.int16)
        self._lastWrite = None
        self._lastWriteTime = None
        self._lastWriteRes = None
        self._lastWriteResTime = None
    
    def generateCallFrame(self) -> str:
        """
        ### 生成获取灯具状态的命令帧
        #### Returns:
        _lastCall: 最新发送的读取命令
        """
        head = 'fe'
        cmd = '24 5f'
        data = super().getDevAddr() + ' 01 03 00 00 00 03'
        self._lastCall = MyFrame(head, cmd, data)
        return super().generateCallFrame()
    
    def generateWriteFrame(self, switch=None, luminance=None, ct=None, vt=0, ddt=0, drt=0) -> str:
        """
        ### 生成修改灯具状态的命令帧
        注: 预期在值为None时进行保持, 还未实现, 目前需填入所有参数
        #### Parameters:
        - switch: 开关
        - luminance: 亮度
        - ct: 色温
        - vt: 变化时间
        - ddt: 延迟执行时间
        - drt: 延迟回复时间
        #### Returns:
        - _lastWrite: 最新发送的修改命令
        """
        head = 'fe'
        cmd = '24 5f'
        data = super().getDevAddr() + ' 01 10 00 00 00 06 0c'
        for item in [switch, luminance, ct, vt, ddt, drt]:
            data += ' ' + super().getWordStr(item)
        print(data)
        self._lastWrite = MyFrame(head, cmd, data)
        return self._lastWrite
    
class Curtain(Device):
    """
    ### 窗帘类, 继承自设备基类
    #### Attributes:
    """
    def __init__(self, devId, devAddr: int) -> None:
        super().__init__(devId, devAddr)
        # 开度
        self._data = 0
        self._lastWrite = None
        self._lastWriteTime = None
        self._lastWriteRes = None
        self._lastWriteResTime = None

        