"""
# 设备模块0
代号0的设备, 由通信协议文档20200422定义

本模块抽象了办公室使用中的所有设备

Created by Li Mingkai on 21.06.18
""" 
import sys
import os
import numpy as np

path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path)
# 导入数据解析类
from frameparse import FrameParse

# 本通信协议中支持的设备的种类
DEVICE_CLASS = {"sensor", 
                "air", 
                "purifier", 
                "curtain", 
                "humidifier", 
                "ventilation", 
                "lamp"}

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
        self._data: list = None
        self._data_readable: dict = None

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
                res = f"0{x}00"
            elif len(x) == 2:
                res = f"{x}00"
            elif len(x) == 3:
                res = f"{x[-2:]}0{x[0]}"
            else:
                res = f"{x[-2:]}{x[:2]}"
        else:
            if len(x) == 1:
                res = f"000{x}"
            elif len(x) == 2:
                res = f"00{x}"
            elif len(x) == 3:
                res = f"0{x[0]}{x[-2:]}"
            else:
                res = f"{x[:2]}{x[-2:]}"
        
        return bytes.fromhex(res)

# 定义传感器设备类
class Sensor(Device):
    """
    适合本通信协议的传感器类的接口
    """
    def __init__(self, addr: int) -> None:
        super().__init__(addr)
        self._data = [self.getReg(0)] * 6
        self._data_readable = {'温度': 0, 
        '湿度': 0,
        'PM2.5':0,
        'CO2': 0,
        '甲醛': 0,
        'VOC': 0}
    
    def read_data(self) -> str:
        """
        生成读取该传感器的全部数据的从命令域到数据域的内容
        """
        content = '245f' + self._addr.hex() + '010300000006'
        
        return content

# 定义设备灯类
class Lamp(Device):
    """
    适合本通信协议的灯类的接口

    """
    def __init__(self, addr: int) -> None:
        """
        Parameters:
        - addr: 设备地址
        """
        super().__init__(addr)
        self._data = [self.getReg(0)] * 3
        self._data_readable = {'开关': 0, '亮度': 0, '色温': 0}
    
    def read_data(self) -> str:
        """
        生成读取该灯的全部寄存器数据的从命令域到数据域的内容
        """
        content = '245f' + self._addr.hex() + '010300000003'
        return content
    
    def update_data(self):
        """
        根据返回给的上位机的响应查询的数据帧修改从
        """
        pass

    def write_data(self, reg: int, val: int, *args) -> str:
        """
        生成写入该灯的某个寄存器数据的从命令域到数据域的内容

        Parameters:
        - reg: 寄存器的编号
        - val: 寄存器的十进制值

        Details:
        - 0号寄存器控制开关, 1号寄存器控制亮度, 2号寄存器控制色温
        - reg只允许输入{0, 1, 2}中的数字, 未引入输入检错及异常处理机制
        """
        # 更改对象中存储的寄存器的值
        self._data[reg] = self.getReg(val)
        self._data_readable
        content = '245f' 
        + self._addr.hex()
        + '0110000000060c'
        + self._data[0]
        + self._data[1]
        + self._data[2]
        + args[0]
        + args[1]
        + args[2]

        return content
    
# 定义面板类
class Panel(Device):
    """
    适合本通信协议的控制面板类
    """
    def __init__(self, addr: int, frame_parse: FrameParse) -> None:
        """
        Parameters:
        - addr: 设备地址
        - frame_parse: 数据帧解析器
        """
        super().__init__(addr)
        self._data = [self.getReg(0)] * 433
        # 每个面板都控制一个帧解析器来生成或解析数据帧
        self.frame_parse = frame_parse
        # 面板下的设备
        # 传感器
        self._sensor = None
        # 灯具
        self._lamps = []
        # 空调
        self._airs = []
        # 窗帘
        self._curtains = []
        # 空气净化器
        self._purifiers = []
        # 加湿器
        self._humidifiers = []
        # 新风机
        self._ventilations = []
    
    @property
    def devices(self) -> dict:
        res = {'sensor': self._sensor,
        'lamp': self._lamps,
        'air': self._airs,
        'curtain': self._curtains,
        'purifier': self._purifiers,
        'humidifier': self._humidifiers,
        'ventilation': self._ventilations}
        return res
    
    def add_dev(self, **kargs):
        """
        向面板中添加可控设备, 可一次性添加任意数量的设备, 注意输入范式
        
        Details:
        - 可用关键字及含义:

            - sensor: 六合一传感器
            - air: 空调
            - purifier: 空气净化器
            - curtian: 窗帘
            - humidifier: 加湿器
            - ventilation: 新风机
            - lamp: 灯具

        - 参数输入规范:
        int, tuple of ints, list of ints like: 11, [11, 12, 13](iterable object)
        表示设备的通信目的地址
        """
        # 输入关键字不合法抛出异常
        if not DEVICE_CLASS.issuperset(kargs.keys()):
            raise ValueError("Unknown keywords. Please check your inputs.")
        for key, val in kargs.items():
            # 输入参数不合法抛出异常
            if type(val) not in {int, tuple, list}:
                raise ValueError("Wrong value. Please check your inputs.")
            # 添加设备
            # 添加传感器, 只有1个, 重新添加会覆盖
            if key == 'sensor':
                if type(val) is int:
                    self._sensor = Sensor(val)
                else:
                    raise ValueError("Wrong value. Only one sensor allowed.")
            elif key == 'air':
                pass
            elif key == 'purifier':
                pass
            elif key == 'curtain':
                pass
            elif key == 'humidifier':
                pass
            elif key == 'ventilation':
                pass
            # 添加灯具, 创建实例对象加入列表
            else:
                if type(val) is int:
                    self._lamps.append(Lamp(val))
                else:
                    for addr in val:
                        self._lamps.append(Lamp(addr))
    
    def recv_data(self, frame: bytes):
        """
        面板接收到数据后修改相应寄存器中的值
        """
        pass
        
if __name__ == '__main__':
    pass