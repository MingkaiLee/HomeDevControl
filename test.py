#%%
# 检查可用串口
from traceback import extract_stack
import serial.tools.list_ports
res = serial.tools.list_ports.comports()
for port in res:
    print(port)

# %%
# 串口通信测试
import serial


port_name = 'COM3'
ser = serial.Serial(port_name)
# %%
if ser.isOpen() == False:
    ser.open()
frame = bytes.fromhex('fe 01 21 2b 1e 15')
# ser.write(b'\xfe\x01\x21\x2b\x1e\x15')
ser.write(frame)
res = ser.read(7)
print(res)
ser.close()
# %%
# 传感器控制测试
import serial
import time


port_name = 'COM3'
ser = serial.Serial(port_name, timeout=5)
if ser.isOpen() == False:
    ser.open()
frame = bytes.fromhex('fe 08 24 5f e0 03 01 03 00 00 00 03 91')
ser.write(frame)
print('Written')
start = time.time()
res = ser.read(15)
end = time.time()
print(end - start)
print(str(res))
ser.close()
# %%
# 测试命令帧抽象
import sys
import serial
sys.path.append('D:\house app\物联网\lmk\IoTLab\myframe.py')
from myframe import MyFrame
port_name = 'COM3'
ser = serial.Serial(port_name)
if ser.isOpen() == False:
    ser.open()

# 获取传感器的全部数据
frame = MyFrame('fe', '24 5f', 'e0 03 01 03 00 00 00 06')
# frame = MyFrame('fe', '24 5f', 'e1 03 01 03 00 00 00 06')

# 获取传感器的某个数据
frame = MyFrame('fe', '24 5f', 'e0 03 01 03 00 01 00 01')

ser.write(bytes.fromhex(frame.toBytes()))
res = ser.read(12)
ser.close()
# %%
# 测试数据响应帧抽象
from resframe import ResFrame
rf = ResFrame(res, 2)
info = rf.getData()
# %%
# 4.26测试设备抽象
import sys
import serial
import pandas as pd
import numpy as np
sys.path.append('D:\house app\物联网\lmk\IoTLab')
from device import Sensor
s0 = Sensor(0, 'e0 03')
s1 = Sensor(0, 'e1 03')
ser = serial.Serial('COM3')
if ser.isOpen() == False:
    ser.open()

ser.write(bytes.fromhex(s0.getValsFrame().toBytes()))
res = ser.read(22)
ser.close

from resframe import ResFrame
rf = ResFrame(res, 2)
info = rf.getData()
# %%
# Event对象, 用于以一定条件为线程施加阻塞
from threading import Thread, Event
import time

# Code to execute in an independent thread
def countdown(n, started_evt):
    print('countdown starting')
    started_evt.set()
    while n > 0:
        print('T-minus', n)
        n -= 1
        time.sleep(5)

# Create the event object that will be used to signal startup
started_evt = Event()

# Launch the thread and pass the startup event
print('Launching countdown')
t = Thread(target=countdown, args=(10,started_evt))
t.start()

# Wait for the thread to start
started_evt.wait()
print('countdown is running')
# %%
import threading
def worker(n, sema):
    # Wait to be signaled
    sema.acquire()

    # Do some work
    print('Working', n)

# Create some threads
sema = threading.Semaphore(0)
nworkers = 10
for n in range(nworkers):
    t = threading.Thread(target=worker, args=(n, sema,))
    t.start()
# %%
import sys
print(sys.version_info[:3])
# %%
import asyncio
async def main():
    print('hello')
    await asyncio.sleep(1)
    print('world')
asyncio.run(main())
# %%
g = (x**x for x in range(10))
# %%
# 测试与灯具的通信
if not ser.isOpen():
    ser.open()
import sys
sys.path.append('D:\house app\物联网\lmk\IoTLab\myframe.py')
from myframe import MyFrame
# 获取灯具状态信息
frame = MyFrame('fe', '24 5f', '0b 00 01 03 00 00 00 03')
ser.write(bytes.fromhex(frame.toBytes()))
res = ser.read(16)
ser.close()
# %%
def getAddrStr(addr: int) -> str:
    """
    10进制设备地址转字符串, 输入范围不检验
    """
    x = hex(addr).lstrip('0x')
    res = None
    if len(x) == 1:
        res = f"0{x} 00"
    elif len(x) == 2:
        res = f"{x} 00"
    elif len(x) == 3:
        res = f"{x[-2:]} 0{x[0]}"
    else:
        res = f"{x[-2:]} {x[:2]}"
    return res
print(getAddrStr(0))
# %%
import html

def make_element(name, value, **attrs):
    keyvals = [' %s="%s"' % item for item in attrs.items()]
    attr_str = ''.join(keyvals)
    element = '<{name}{attrs}>{value}</{name}>'.format(
                name=name,
                attrs=attr_str,
                value=html.escape(value))
    return element

# Example
# Creates '<item size="large" quantity="6">Albatross</item>'
make_element('item', 'Albatross', size='large', quantity=6)

# Creates '<p>&lt;spam&gt;</p>'
make_element('p', '<spam>')
# %%
x = bytes.fromhex('fe 0a 24 5f d0 07 01 06 15 00 00 01 4c 06 9f')
print(x.hex()[8:-2])
# %%
device_CLASS = {"sensor", 
                "air", 
                "fresh", 
                "curtain", 
                "humidifier", 
                "ventilation", 
                "lamp"}
def addDevice(x: set, **kargs) -> None:
    print(x.issuperset(kargs.keys()))
    for key, val in kargs.items():
        if type(val) in {int, tuple, list}:
            print(type(key))
            print(type(val))
    print(kargs.values())
addDevice(device_CLASS, lamp=(1, 2, 3), air=2)

# %%
