# 测试pyserial自带的异步功能
import asyncio
import serial
import serial_asyncio
from asyncio import transports
# 导入自定义模块
import sys
sys.path.append('D:\house app\物联网\lmk\IoTLab')
# 数据帧类及帧解析类
from myframe import MyFrame, FrameParse
from queue import PriorityQueue


# asyncio.Protocol需要覆写
class Output(asyncio.Protocol):
    def connection_made(self, transport: serial_asyncio.SerialTransport):
        # 设置串口读入时延, 无时延时读入的帧会被打散
        transport.serial.timeout = 0.01
        self.transport = transport
        # 初始化数据帧解析器
        self.parser = FrameParse()
        print('port opened', transport)
        transport.serial.rts = False  # You can manipulate Serial object via transport

    def data_received(self, data):
        print('data received', repr(data))
        self.parser.parse(data)
        self.parser.show()
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

    loop = asyncio.get_event_loop()
    coro = serial_asyncio.create_serial_connection(loop, Output, 'COM5', baudrate=9600)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()
