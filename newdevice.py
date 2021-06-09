"""
## 本模块抽象设备, 功能为抽象出设备后更方便地获取命令帧
## Attention: 确保在调用get开头的获取帧的方法后成功将帧发出
"""
import numpy as np
import pandas as pd
import sys

path = '/Users/limingkai/vsCode/Python_WorkSpace/HomeDevControl'

sys.path.append(path)
from myframe import MyFrame

# 支持的设备的种类
DEVICE_CLASS = {"sensor", 
                "air", 
                "fresh", 
                "curtain", 
                "humidifier", 
                "ventilation", 
                "lamp"}

# 计算面板上寄存器的十进制地址在数据帧中的表示
def get_panel_reg_addr(addr: int) -> str:
    """
    ### 计算面板上寄存器的十进制地址在数据帧中的表示
    #### Attributes:
    - addr: 十进制的寄存器地址
    #### Returns:
    - x: "xxxx"式十六进制表示的地址
    """
    x = hex(addr)[2:]
    while len(x) < 4:
        x = "0" + x
    return x

# 面板1中所有单独灯具的地址
PANEL1_LAMP = [get_panel_reg_addr(i) for i in range(210, 274)]

# 设备基类
class Device:
    """
    ### 设备基类
    #### Attributes:
    - _devAddr: 设备的目的地址
    - _lastCall: 上一次调用的查询命令的内容
    - _lastCallTime: 上一次调用的查询命令发送时间戳
    - _lastCallRes: 上一次调用的查询命令返回的内容
    - _lastCallResTime: 上一次调用的查询命令返回的时间戳
    """
    def __init__(self, devAddr:int) -> None:
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
                res = f"0{x[0]} {x[-2:]}"
            else:
                res = f"{x[:2]} {x[-2:]}"
        return res

    def getByteStr(self, val: int) -> str:
        """
        ### 10进制整数转表单字节的字符串, 输入范围不检验, 默认合法
        #### Parameters:
        - val: 10进制数值
        #### Returns:
        - res: 'xx'式表单字节字符串
        """
        x = hex(val)[2:]
        if len(x) == 1:
            res = f"0{x}"
        return res
    
    def getRegStr(self, val: int) -> str:
        """
        ### 10进制整数转8位2进制字符串, 输入范围不检验, 默认合法
        #### Parameters:
        - val: 10进制数值, 0-255
        #### Returns:
        - res: 'xxxxxxxx'式表一字节寄存器内容的字符串
        """
        res = hex(val)[2:]
        while len(res) < 8:
            res = '0' + res
        return res
    
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

    def _generateFrame(self, cdata) -> object:
        """
        ### 生成数据帧的低层级接口, 从功能码到异或和之前的数据域自定义, 不改变对象内部属性
        #### Parameters:
        - cdata: 数据域从功能码开始的内容
        """
        head = 'fe'
        cmd = '24 5f'
        data = self.getDevAddr() + ' ' + cdata
        return MyFrame(head, cmd, data)

class Sensor(Device):
    """
    ### 传感器基类, 继承自设备基类
    #### Attributes:
    """
    def __init__(self, devAddr: int) -> None:
        super().__init__(devAddr)
        index = pd.Index(('温度', '湿度', 'PM2.5', 'CO2', '甲醛', 'VOC'), name='项目')
        self._data = pd.Series(np.zeros(6), index=index, dtype=np.float32)
    
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
    
    def updateData(self, data: str) -> None:
        """
        ### 由CallFrame发送后返回的内容更新数据
        #### Parameters:
        - data: 数据域在功能码0103之后的内容, 03为读保持寄存器功能码
        """
        # 注: 按照通信协议, 功能码后除去一byte字节数, 每个字中数据依次为:
        # 温度, 湿度, PM2.5, CO2, 甲醛, VOC

        # 转为byte便于计算
        x = bytes.fromhex(data)
        # 更新温度
        self._data['温度'] = (x[1]*256+x[2]) / 10.0
        # 更新湿度
        self._data['湿度'] = (x[3]*256+x[4]) / 10.0
        # 更新PM2.5
        self._data['PM2.5'] = x[5]*256 + x[6]
        # 更新CO2
        self._data['CO2'] = x[7]*256 + x[8]
        # 更新甲醛
        self._data['甲醛'] = x[9]*256 + x[10]
        # 更新VOC
        self._data['VOC'] = x[11]*256 + x[12]
    
    def getData(self) -> str:
        """
        ### 获取传感器数据
        """
        return self._data

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
    def __init__(self, devAddr: int) -> None:
        super().__init__(devAddr)
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
        return self._lastCall
    
    def generateWriteFrame(self, switch=None, luminance=None, ct=None, vt=0, ddt=0, drt=0) -> MyFrame:
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
        self._lastWrite = MyFrame(head, cmd, data)
        return self._lastWrite
    
class Curtain(Device):
    """
    ### 窗帘类, 继承自设备基类
    #### Attributes:
    """
    def __init__(self, devAddr: int) -> None:
        super().__init__(devAddr)
        # 开度
        self._data = 0
        self._lastWrite = None
        self._lastWriteTime = None
        self._lastWriteRes = None
        self._lastWriteResTime = None

    def generateCloseFrame(self) -> MyFrame:
        """
        ### 生成窗帘关闭的命令帧
        #### Returns:
        - _lastWrite: 最新发送的修改命令
        """
        head = 'fe'
        cmd = '24 5f'
        data = super().getDevAddr() + ' 01 06 11 03 00 01 00 00'
        self._lastWrite = MyFrame(head, cmd, data)
        return self._lastWrite

    def generateWriteFrame(self, degree, ddt, drt) -> MyFrame:
        """
        ### 生成控制窗帘开度的命令帧
        #### Parameters:
        - degree: 开度
        - ddt: 延迟执行时间
        - drt: 延迟回复时间
        #### Returns:
        - _lastWrite: 最新发送的修改命令
        """
        head = 'fe'
        cmd = '24 5f'
        data = super().getDevAddr() + ' 01 10 00 07 00 03 06'
        for item in [ddt, drt, degree]:
            data += ' ' + super().getWordStr(item)
        self._lastWrite = MyFrame(head, cmd, data)
        return self._lastWrite

class Panel(Device):
    """
    ### 面板类, 独立于设备基类的控制面板
    #### Attributes:

    """
    def __init__(self, devAddr: int) -> None:
        super().__init__(devAddr)
        # 在线可控传感器
        self._sensor = None
        # 在线可控灯具数量
        self._lampNum = 0
        # 在线可控灯具列表
        self._lamps = []
    
    def generateCallFrame(self) -> str:
        """
        ### 获取面板基础信息
        """
        pass

    def getDevice(self, name: str):
        """
        ### 获取某类设备列表
        #### 可用关键字及含义:
        - sensor: 六合一传感器
        - air: 空调
        - fresh: 空气净化器
        - curtian: 窗帘
        - humidifier: 加湿器
        - ventilation: 新风机
        - lamp: 灯具
        """
        if name not in DEVICE_CLASS:
            raise ValueError("Unknown keywords. Please check your inputs.")
        if name == 'lamp':
            return self._lamps
        elif name == 'sensor':
            return self._sensor

    def addDevice(self, **kargs) -> None:
        """
        ### 向面板中添加可控设备, 可一次性添加任意数量的设备, 注意输入范式
        ### Details:
        #### 可用关键字及含义:
        - sensor: 六合一传感器
        - air: 空调
        - fresh: 空气净化器
        - curtian: 窗帘
        - humidifier: 加湿器
        - ventilation: 新风机
        - lamp: 灯具
        #### 参数输入规范:
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
            elif key == 'fresh':
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
                    self._lampNum += 1
                    self._lamps.append(Lamp(val))
                else:
                    self._lampNum += len(val)
                    for addr in val:
                        self._lamps.append(Lamp(addr))

class Panel1(Panel):
    """
    ### 面板型号1, 控制面板4.0
    #### Attributes:
    """
    def __init__(self, devAddr: int) -> None:
        super().__init__(devAddr)

    def generateFrame(self, cdata):
        self._lastCall = super()._generateFrame(cdata)
        return self._lastCall

    def parseRegister(self, regData: bytes, type: str):
        """
        ### 解析寄存器中的内容
        #### Parameters:
        - regData: 寄存器中内容, bytes类型
        - type: 该寄存器的类型
        #### type可用值及含义:
        - lamps: 灯具类设备的修改

        """
        # 获取寄存器的高八位和低八位
        reg_hi = super().getRegStr(regData[0])
        reg_lo = super().getRegStr(regData[1])

        # 返回结果, 字典形式, 因设备而异
        res = dict()

        if type == 'lamps':
            res.update({'switch': 0, 'luminance':100, 'ct':100})
            # 开关使能1, 修改开关状态
            if reg_hi[0] == '1':
                res['switch'] = int(reg_hi[3])
            # 亮度使能1, 修改亮度
            if reg_hi[1] == '1':
                luminance_bin = reg_hi[4:] + reg_lo[0]
                res['luminance'] = int(luminance_bin, 2) * 5
            # 色温使能1, 修改色温
            if reg_hi[2] == '1':
                ct_bin = reg_lo[1:6]
                res['ct'] = int(ct_bin, 2) * 5
        return res
    
    def generateFrameFromData(self, panel_data: str) -> list:
        """
        ### 按照控制面板4.0的V1.5协议解析命令, 并生成相应的控制数据帧，收到来自面板的帧后调用
        #### Parameters:
        - panel_data: 数据域在功能码0146之后的内容, 46为扩展功能码
        #### Returns:
        - frames: 根据面板传入的命令, 对设备的控制数据帧
        """
        # 寄存器地址
        regAddr = panel_data[:4]
        # 寄存器内容
        regData = panel_data[4:-4]

        # 返回的数据帧列表
        frames = list()

        # 控制全部灯具
        if regAddr == '00d1':
            # 将十六进制字符串转为bytes方便解析
            parseRes = self.parseRegister(bytes.fromhex(regData), 'lamps')
            # 根据解析值生成命令帧
            r = 0
            for lamp in self._lamps:
                ddt = 280*(self._lampNum - 1 - r)
                drt = 10 * r
                r += 1
                frames.append(lamp.generateWriteFrame(
                    switch = parseRes['switch'],
                    luminance = parseRes['luminance'],
                    ct = parseRes['ct'],
                    ddt = ddt,
                    drt = drt
                ))
        # 控制某个灯具
        elif regAddr in PANEL1_LAMP:
            parseRes = self.parseRegister(bytes.fromhex(regData), 'lamps')
            #

        return frames
    
    def generateSensorQuery(self) -> object:
        """
        ### 驱使传感器对象生成更新传感器数据内容的帧
        #### Returns:
        - frame: 向在线传感器获取数据的帧
        """
        # 传感器未被加入时抛出异常
        if self._sensor is None:
            raise RuntimeError("Sensor hasn't been added.")
        return self._sensor.generateCallFrame() 
    
    def pushSensorFrame(self) -> object:
        """
        ### 生成面板更新传感器数据的帧
        #### Returns:
        - frame: 更新面板上数据的帧
        """
        # 传感器未被加入时抛出异常
        if self._sensor is None:
            raise RuntimeError("Sensor hasn't been added.")
        # 从传感器中获取数据
        dataRaw = self._sensor.getData()
        head = 'fe'
        cmd = '24 5f'
        # 数据域结构: 地址, 功能码0110写多个寄存器, 起始地址, 寄存器数量, 字节数, 寄存器值, 校验码
        data = super().getDevAddr() + '01 10' + '00 05' + '00 06' + '0c'
        # 定义一个温度计算的函数
        t = lambda x: int(10*x) + 400
        data += super().getWordStr(t(dataRaw['温度']))
        data += super().getWordStr(round(dataRaw['湿度']))
        data += super().getWordStr(round(dataRaw['PM2.5']))
        data += super().getWordStr(round(dataRaw['CO2']))
        data += super().getWordStr(round(dataRaw['甲醛']))
        data += super().getWordStr(round(dataRaw['VOC']))
        # 任意输入校验码
        data += '00 00'
        return MyFrame(head, cmd, data)


if __name__ == '__main__':
    p1 = Panel1(999)

    pass