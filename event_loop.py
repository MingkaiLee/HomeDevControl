# Created on 21.07.15
# 新版架构的事件循环
import serial_asyncio
import asyncio
# 导入自定义模块
import sys
sys.path.append('D:\house app\物联网\lmk\IoTLab')
# 数据帧类及帧解析类
from devices0 import Panel
from frameparse import FrameParse

# asyncio.Protocol需要覆写
class Controller(asyncio.Protocol):
    def create_panel(self) -> object:
        # 创建帧解析器对象
        parser = FrameParse()

        # 创建面板对象
        panel = Panel(999, parser)

        # 加入传感器
        panel.add_dev(sensor=992)
        # 加入灯具
        panel.add_dev(lamp=[i for i in range(11, 27)])
        
        # 初始化完毕, 返回面板
        return panel

    def connection_made(self, transport: serial_asyncio.SerialTransport):
        # 自定义串口参数
        # 设置串口读入时延, 无时延时读入的帧会被打散
        transport.serial.timeout = 0.01
        transport.serial.rts = False
        self.transport = transport
        
        # 初始化面板设备
        try:
            self.panel = self.create_panel()
        except BaseException:
            # 出现异常则退出事件循环
            print("Can't get the panel instance.")
            self.transport.loop.stop()
            sys.exit()
        print('port opened', transport)

    def data_received(self, data):
        print('data received', data.hex(' '))
        res = self.panel.recv_data(data)
        print('data sent', res.hex(' '))
        self.transport.serial.write(res)

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