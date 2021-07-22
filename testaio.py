# 根据demo修改后的异步I/O事件循环控制
# rewritten on 21.07.21
import time
import asyncio
import serial_asyncio
# 导入自定义模块
import sys
sys.path.append('D:\house app\物联网\lmk\IoTLab')
# 数据帧类及帧解析类
from devices0 import Panel
from frameparse import FrameParse

class Controller(asyncio.Protocol):
    def __init__(self) -> None:
        super().__init__()
        self.reply_data = {}
        self._current_data = None
        self._data = []
        self._buffer = set()
        self.transport = None
        self._update_flag = False
    
    def create_panel(self) -> object:
        # 创建解析器对象
        parser = FrameParse()

        # 创建面板对象
        panel = Panel(999, parser)

        # 添加传感器
        panel.add_dev(sensor=992)
        # 添加灯具
        panel.add_dev(lamp=[i for i in range(11, 27)])

        # 初始化完毕, 返回面板
        return panel
    
    def connection_made(self, transport: serial_asyncio.SerialTransport) -> None:
        self.transport = transport

        # 初始化面板
        try:
            self.panel = self.create_panel()
        except BaseException:
            print("Can't get the panel instance.")
            self.transport.loop.stop()
            sys.exit()
        print("port opened successfully.", transport)

    def data_received(self, data: bytes) -> None:
        """
        数据帧拼接
        """
        self._data.extend(data)
        # 帧完整性标志
        full_flag = False
        k = 0
        for j in range(len(self._data) - 1):
            if j < k:
                continue
            k = j
            # 若数据帧的帧头不为fe则j+1并进入下一轮循环
            if self._data[j] != 0xfe:
                continue
            if len(self._data) - j >= self._data[j + 1] + 5:
                if self._data[j + 2] == 0x44 and self._data[j + 3] == 0x5f:
                    z = 0
                    for x in self._data[j + 1: j + self._data[j + 1] + 4]:
                        z = z ^ x
                    # 帧检验成功
                    if z == self._data[j + self._data[j + 1] + 4]:
                        key = self._data[j + 4] + (self._data[j +5] << 8)
                        full_flag = True
                        if key in self.reply_data:
                            self.reply_data[key] = time.time() - self.reply_data[key]
                        k = j + self._data[j + 1] + 5
                        
            else:
                break
        # 若检测到完整的数据帧, 开始执行控制指令
        if full_flag:
            self._current_data = self._data[:k]
            self._data = self._data[k:]
            self._update_flag = True
            print('1')
        
    async def send_data(self):
        while True:
            if self._update_flag:
                print('2')
                data_recv = bytes(self._current_data)
                res = self.panel.recv_data(data_recv)
                if type(res) != list:
                    self.transport.serial.write(res)
                else:
                    for query in res[1]:
                        key = query[4] + (query[5] << 8)
                        self.transport.write(query)
                        self.reply_data[key] = time.time()
                        await asyncio.sleep(res[0] / 1000)
                    await asyncio.sleep(2000 / 1000 + 2)
                    self._update_flag = False
    
    def connection_lost(self, exc) -> None:
        print('port closed')
        self.transport.loop.stop()
    
    def pause_writing(self) -> None:
        print('pause writing')
        print(self.transport.get_write_buffer_size())
    
    def resume_writing(self) -> None:
        print(self.transport.get_write_buffer_size())
        print('resume writing')

if __name__ == '__main__':
    # 创建事件循环
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    # 创建协程
    coro = serial_asyncio.create_serial_connection(loop, Controller, 'COM5', baudrate=9600)
    # 事件循环运行
    transport, protocol = loop.run_until_complete(coro)
    # newloop = asyncio.new_event_loop()
    # newloop.run_until_complete(protocol.send_data())
    loop.run_forever()
    loop.close()