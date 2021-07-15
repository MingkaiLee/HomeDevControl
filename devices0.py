"""
# 设备模块0
代号0的设备, 由通信协议文档20200422定义

本模块抽象了办公室使用中的所有设备

Created by Li Mingkai on 21.06.18
""" 
import sys
import os
from queue import SimpleQueue
import serial

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

# 本通信协议中面板寄存器功能分组

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

        Returns:
        - res: str or bytes
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
    
    def getBin(self, val: int) -> str:
        """
        10进制整数转8位2进制字符串, 输入范围不检验, 默认合法

        Parameters:
        - val: 10进制数值, 0-255

        Returns:
        - res: 'xxxxxxxx'式表一字节寄存器内容的字符串
        """
        # 将输入转为二进制字符串
        res = bin(val)[2:]
        res = '0' * (8-len(res)) + res
        return res

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
        self._data = [self.getReg(0), self.getReg(100), self.getReg(100)]
        self._data_readable = {'开关': 0, '亮度': 0, '色温': 0}
    
    def read_data(self) -> str:
        """
        生成读取该灯的全部寄存器数据的从命令域到数据域的内容
        """
        content = '245f' + self._addr.hex() + '010300000003'
        return content
    
    def update_data(self) -> None:
        """
        根据返回给的上位机的响应查询的数据帧修改存储在上位机中的数据
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
        - args可分别输入变化时间, 延迟执行时间, 延迟回复时间, 均为int类型
        """
        # 更改对象中存储的寄存器的值
        self._data[reg] = self.getReg(val)

        # 将十进制的时间参数转为寄存器字符量
        i = 0
        b_args = []
        while i < len(args):
            b_args.append(self.getReg(args[i]).hex())
            i += 1
        b_args = b_args + ['0000'] * (3-i)

        # 构造结果
        # print(self._addr.hex())
        content = '245f'+self._addr.hex()+'0110000000060c'+self._data[0].hex()+self._data[1].hex()+self._data[2].hex()+b_args[0]+b_args[1]+b_args[2]

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
        self.frame_parse: FrameParse = frame_parse

        # 面板会拥有一个队列来存储待发送的响应数据帧

        # 面板会拥有一个简易队列来存储出错的数据帧
        self.error_queue = SimpleQueue()

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

        # 设备通讯录, 存放设备地址的字典
        self.addr_book: dict = {
            "panel": [self._addr],
            "sensor": [],
            "lamp": [],
            "air": [],
            "curtain": [],
            "purifier": [],
            "humidifier": [],
            "ventilation": []
        }

        # 创建面板中的寄存器变量列表, 共433个寄存器
        self._panel_regs: list = [bytes.fromhex('00 00')] * 433
    
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
        向面板中添加可控设备, 可一次性添加任意数量的设备, 注意输入范式, 同时会维护设备通讯录
        
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
                    self.addr_book['sensor'] = [val]
                else:
                    raise ValueError("Wrong value. Only one sensor allowed.")
            elif key == 'air':
                if type(val) is int:
                    self._airs.append(Lamp(val))
                    self.addr_book['air'].append(val)
                else:
                    for addr in val:
                        self._airs.append(Lamp(addr))
                        self.addr_book['air'].append(addr)
            elif key == 'purifier':
                if type(val) is int:
                    self._purifiers.append(Lamp(val))
                    self.addr_book['purifier'].append(val)
                else:
                    for addr in val:
                        self._purifiers.append(Lamp(addr))
                        self.addr_book['purifier'].append(addr)
            elif key == 'curtain':
                if type(val) is int:
                    self._curtains.append(Lamp(val))
                    self.addr_book['curtain'].append(val)
                else:
                    for addr in val:
                        self._curtains.append(Lamp(addr))
                        self.addr_book['curtain'].append(addr)
            elif key == 'humidifier':
                if type(val) is int:
                    self._humidifiers.append(Lamp(val))
                    self.addr_book['humidifier'].append(val)
                else:
                    for addr in val:
                        self._humidifiers.append(Lamp(addr))
                        self.addr_book['humidifier'].append(addr)
            elif key == 'ventilation':
                if type(val) is int:
                    self._ventilations.append(Lamp(val))
                    self.addr_book['ventilation'].append(val)
                else:
                    for addr in val:
                        self._ventilations.append(Lamp(addr))
                        self.addr_book['ventilation'].append(addr)
            # 添加灯具, 创建实例对象加入列表
            elif key == 'lamp':
                if type(val) is int:
                    self._lamps.append(Lamp(val))
                    self.addr_book['lamp'].append(val)
                else:
                    for addr in val:
                        self._lamps.append(Lamp(addr))
                        self.addr_book['lamp'].append(addr)
            else:
                raise ValueError("Unexpected input arguments. Please check your inputs.")
    
    def recv_data(self, frame: bytes):
        """
        面板接收到数据后修改相应寄存器中的值

        Parameters:
        - frame: 接收到的设备传递给上位机的数据帧

        Returns:
        - res: 响应该数据帧的命令帧

        Details:
        1. 第一步, 判断传来的数据帧是否合法, 非法则终止并压入一个错误处理队列中
        2. 第二步, 判断合法的数据帧来源于何种设备
        3. 第三步, 针对特定的设备作出对应响应, 主要处理来自面板的数据
        """
        # 解析数据帧并得到结果
        parse_res = self.frame_parse.parse(frame)
        # step1, 判断数据帧合法性
        if parse_res[0] != 0:
            # 将非法的帧压入队列
            self.error_queue.put(frame)
            return 0
        # step2, 判断合法数据帧的设备类型
        type_name: str = None
        for key, val in self.addr_book.items():
            if bytes.fromhex(parse_res[1][0]) in val:
                type_name = key
                break
        # step3, 针对特定的设备作出响应
        if type_name == 'panel':
            # 来自面板的命令功能码均为46, 只修改单个寄存器的内容, 2字节
            reg_addr = int(parse_res[1][2][:4], 16)
            reg_content = parse_res[1][2][4:8]
            self._panel_regs[reg_addr] = bytes.fromhex(reg_content)
            return self._dev_control_frame(reg_addr, reg_content)
        else:
            return 1
            

    
    def _dev_control_frame(self, addr: int, content: str):
        """
        解析面板发送的数据域的数据并返回响应的数据帧

        Parameters:
        - addr: 数据帧中面板寄存器的地址
        - content: 数据帧中面板寄存器的内容

        Returns:
        - res:
        """

        # 数据帧结果
        res: bytes = bytes()

        # 首页大按钮的修改
        if addr == 0:
            pass
        elif addr ==1:
            pass
        elif addr == 2:
            pass
        elif addr == 3:
            pass
        elif addr == 4:
            pass
        # 全部灯具的修改
        elif addr == 209:
            # 当灯数量较少时采用以下方式能够快速控制
            """
            # 单个灯单位的执行时延
            exc_interval = 1
            # 单个灯单位的回复时延
            res_interval = 20
            # 单个灯寄存器应修改的值
            change_info = self._lamp_control(content)
            for i in range(len(self._lamps)):
                # 调用灯实例的方法写从命令域到数据域的内容
                temp_res = self._lamps[i].write_data(change_info[0], change_info[1],
                 1,
                 exc_interval*i,
                 res_interval*i )
                res = self.frame_parse.construct(temp_res) + res
            """
            # 灯的数量较多时采用以下方式保证感官上的同步
            # 单个灯单位的执行时延(考虑zigbee模块数据帧的发送间隔)
            exc_interval = 20
            # 单个灯单位的回复时延
            res_interval = 20

        # 单个灯具的修改
        elif addr in range(210, 274):
            # 单个灯寄存器应修改的值, 立即执行
            change_info = self._lamp_control(content)
            temp_res = self._lamps[addr-210].write_data(change_info[0], change_info[1], 
             1, 
             0,
             10)
            print(temp_res)
            res = self.frame_parse.construct(temp_res)

        return res

    def _lamp_control(self, content: str) -> tuple:
        """
        根据面板传入的修改灯状态信息的帧内容, 产生除目的地址外的内容
        (设计考虑到一键控制多个设备的功能, 该应用场景下无需多次计算)

        Parameters:
        - content: 数据帧中面板寄存器的内容

        Returns:
        - res: (int, int)自使能信号所允许修改的寄存器及其相应的值
        """

        # 转为bytes后自动计算其各字节的数值
        content = bytes.fromhex(content)
        # 得到从高到低的两个字节各位值的字符串
        bin_bits = self.getBin(content[0]) + self.getBin(content[1])
        # 使能信号判断
        enable = 0
        for i in range(3):
            if bin_bits[i] == '1':
                enable = i
                break
        # 得到使能信号后只分析其对应的位
        if enable == 0:
            res = int(bin_bits[3], 2)
        elif enable == 1:
            res = int(bin_bits[4:9], 2) * 5
        else:
            res = int(bin_bits[9:14], 2) * 5
        
        return (enable, res)

        
            
# 测试用代码
if __name__ == '__main__':
    # 21.07.14测试对灯的集群控制
    port_name = 'COM5'
    ser = serial.Serial(port_name, timeout=3)
    if not ser.isOpen():
        ser.open()

    # 创建面板
    parser = FrameParse()
    p: Panel = Panel(999, parser)
    # 向面板中添加灯具
    p.add_dev(lamp=[i for i in range(11, 27)])
    # 因面板无响应, 构造一个虚拟面板帧测试
    virtual_frame = parser.construct('445fe703014600d19a5042a0')
    res_frame = p.recv_data(virtual_frame)
    print(ser)
    print(res_frame.hex(' '))
    print(type(res_frame))
    # 串口命令发送
    ser.write(res_frame)
    # 关闭串口
    res = ser.read(16)
    print(res.hex('-'))
    ser.close()
    sys.exit()

    
    