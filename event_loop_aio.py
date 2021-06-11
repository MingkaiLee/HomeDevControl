# 测试pyserial自带的异步功能
import asyncio
import serial
import serial_asyncio
from asyncio import transports
from queue import PriorityQueue
# 导入自定义模块
import sys
sys.path.append('D:\house app\物联网\lmk\IoTLab')
# 数据帧类及帧解析类
from myframe import MyFrame, FrameParse
from newdevice import Panel1

# asyncio.Protocol需要覆写
class Controller(asyncio.Protocol):
    def create_panel(self) -> object:
        # 创建面板对象
        panel = Panel1(999)

        # 可用设备地址
        # 传感器
        ss = 992
        # 灯具
        lps = [i for i in range(11, 27)]

        # 向面板中添加设备
        # 加入传感器
        panel.addDevice(sensor=ss)
        # 加入灯具
        panel.addDevice(lamp=lps)
        
        # 初始化完毕, 返回面板
        return panel

    def connection_made(self, transport: serial_asyncio.SerialTransport):
        # 自定义串口参数
        # 设置串口读入时延, 无时延时读入的帧会被打散
        transport.serial.timeout = 0.02
        transport.serial.rts = False
        self.transport = transport

        # 初始化数据帧解析器
        self.parser = FrameParse()
        
        # 初始化面板设备
        try:
            self.panel = self.create_panel()
        except BaseException:
            print("Can't get the panel instance.")
        print('port opened', transport)

    def data_received(self, data):
        print('data received', repr(data))
        self.parser.parse(data)
        self.parser.show()
        frames: list = self.panel.generateFrameFromData(self.parser.getData())
        # 改进: 考虑避免for循环
        # 改进: 考虑直接将整条数据写入一块
        # for frame in frames:

        for frame in frames:
            self.transport.serial.write(frame.toBytes())
        print("Writing task done.")
        """
        if b'\n' in data:
            self.transport.close()
        """

    def connection_lost(self, exc):
        print('port closed')
        self.transport.loop.stop()

    def pause_writing(self):
        print('pause writing')
        print(self.transport.get_write_buffer_size())

    def resume_writing(self):
        print(self.transport.get_write_buffer_size())
        print('resume writing')

if __name__ == '__main__':
    # 创建事件循环
    loop = asyncio.get_event_loop()
    # 创建协程
    coro = serial_asyncio.create_serial_connection(loop, Controller, 'COM5', baudrate=9600)
    # 事件循环运行
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()
