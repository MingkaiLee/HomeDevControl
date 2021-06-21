"""
# 设备模块0
代号0的设备, 由通信协议文档20200422定义

本模块抽象了办公室使用中的所有设备

Created by Li Mingkai on 21.06.18
""" 
import numpy as np
import sys
import os

path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path)
# 导入数据解析类
from frameparse import FrameParse

# 定义所有设备的接口
class Device:
    """
    所有设备的接口, 包含寄存器内容属性以及一些通用方法

    设备通用属性:
    - _addr: 设备地址
    - _data: 寄存器数据
    - _data_readable: (可选)用于调试, 可视的数据
    """
    def __init__(self, addr: int) -> None:
        self._addr: bytes = self.getReg(addr, True)
        self._data: np.ndarray = None
        self._data_readable: np.ndarray = None

    @property
    def addr(self):
        return self._addr
    
    @property
    def data(self):
        """
        返回设备寄存器的数据
        """
        return self._data
    
    @property
    def data_readable(self):
        """
        返回设备寄存器的可读数据
        """
        return self._data_readable

    def read_data_frame(self):
        """
        读取所有寄存器信息的帧接口, 子类需覆写
        """
        pass

    def parse_data_frame(self):
        """
        解析寄存器信息的帧接口, 子类需覆写
        """
        pass
    
    def getByte(self, val: int) -> bytes:
        """
        10进制整数转为bytes量, 不对输入合法性检验, 0-255为合法输入

        Parameters:
        - val: 输入的10进制整数
        """
        temp = hex(val)[2:]
        res = bytes.fromhex('0' * (2-len(temp)) + temp)

        return res
    
    def getReg(self, val: int, desc=False) -> bytes:
        """
        10进制整数转为寄存器量, 本设备中的寄存器为双字节, 不对输入合法性检验

        Parameters:
        - val: 输入的10进制整数
        - desc: default False, 高位在前低位在后, True则低位在前高位在后
        """
        x = hex(val)[2:]
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
                res = f"0{x[0]} {x[-2:]}"
            else:
                res = f"{x[:2]} {x[-2:]}"
        
        return bytes.fromhex(res)

# 定义设备灯类
class Lamp(Device):
    """
    适合本通信协议的灯类的接口

    """
    def __init__(self, addr) -> None:
        super().__init__(addr)
    
    def read_data(self) -> str:
        """
        生成读取该灯的全部寄存器数据的从命令域到数据域的内容
        """
        content = '24 5f' + self._addr.hex() + '01 03 00 00 00 03'
        return content