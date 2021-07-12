#%%
# 检查可用串口
from os import name
import re
from traceback import extract_stack
from serial.serialutil import Timeout
import serial.tools.list_ports
res = serial.tools.list_ports.comports()
for port in res:
    print(port)

# %%
# 激活面板
import os
import sys
import serial
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
from myframe import MyFrame, FrameParse
from newdevice import Panel1

port_name = 'COM5'
ser = serial.Serial(port_name, timeout=3)
if not ser.isOpen():
    ser.open()
p1 = Panel1(999)
# 帧功能: 点亮设备总开关
frame = p1.generateFrame('01 06 00 00 00 01 00 00')
print(frame)
ser.write(frame.toBytes())
res = ser.read(15)
print(res)
ser.close()
# %%
# 调取传感器数据, 检测传感器可用性和控制器可用性
import sys
import serial
sys.path.append('D:\house app\物联网\lmk\IoTLab')

from myframe import MyFrame, FrameParse
from newdevice import Sensor

port_name = 'COM5'
ser = serial.Serial(port_name, timeout=3)
if not ser.isOpen():
    ser.open()
# 创建帧解析类
# 创建传感器对象
s = Sensor(992)
# 帧功能: 获取传感器的所有数据
frame = s.generateCallFrame()
print(frame)
ser.write(frame.toBytes())
res = ser.read(22)
print(res)
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
port_name = 'COM5'
ser = serial.Serial(port_name)
if ser.isOpen() == False:
    ser.open()

# 获取传感器的全部数据
frame = MyFrame('fe', '24 5f', 'e0 03 01 03 00 00 00 06')
# frame = MyFrame('fe', '24 5f', 'e1 03 01 03 00 00 00 06')

# 获取传感器的某个数据
frame = MyFrame('fe', '24 5f', 'e0 03 01 03 00 01 00 01')

ser.write(frame.toBytes())
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
x = bytes.fromhex('fe 0a 24 5f d0 07 01 06 15 00 00 01 4c 06 9f')
print(x.hex()[8:-2])
# %%
# 测试关键字参数传递效果
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
# 测试设置timeout后, 在一段时间内通过面板反复向控制器发送指令的结果
import serial
# 创建串口实例
ser = serial.Serial('COM5', timeout=3)
# 打开串口
if not ser.isOpen():
    ser.open()
# 测试read方法
# res = ser.read(999)
# 测试readline方法
# res = ser.readline()
# 测试readlines方法
res = ser.readlines()
# 测试readall方法
# res = ser.readall()
# 打印输出
print(res)
ser.close()
# %%
# 测试地址计算函数
def get_panel_reg_addr(addr: int) -> str:
    x = hex(addr)[2:]
    while len(x) < 4:
        x = "0" + x
    return x
print(get_panel_reg_addr(209))
print(get_panel_reg_addr(0))
print([get_panel_reg_addr(i) for i in range(210, 274)])
x = bytes.fromhex("9000")
print(x[0])
# %%
# 测试获取传感器数据并更新面板的函数
# 每次面板重启, 在测试前请运行代码块2
import sys
import serial
sys.path.append('D:\house app\物联网\lmk\IoTLab')
from myframe import MyFrame, FrameParse
from newdevice import Sensor, Panel1
# 创建串口实例
ser = serial.Serial('COM5', timeout=3)
# 打开串口
if not ser.isOpen():
    ser.open()
# 创建解析工具实例
fp = FrameParse()
# 创建面板实例
p = Panel1(999)
# 传感器实例添加入面板中
p.addDevice(sensor=992)
# 面板驱动传感器实例生成数据更新帧
frame = p.generateSensorQuery()
# 发送该帧
ser.write(frame.toBytes())
# 接收数据
res = ser.read(22)
print(res)
# 解析结果
fp.parse(res)
# 传感器实例更新数据
p.getDevice(name='sensor').updateData(fp.getData())
# 打印最新数据
print(p.getDevice(name='sensor').getData())
# 面板生成更新数据的帧
frame = p.pushSensorFrame()
print(frame)
# 发送该帧
ser.write(frame.toBytes())
# 接收数据
res = ser.readall()
# 解析回复
fp.parse(res)
# 展示解析结果
fp.show()
# 关闭串口
# %%
# 21.07.12测试开发代码
addr_book = {
    "sensor": [],
    "lamps": [],
    "airs": [],
    "curtains": [],
    "purifiers": [],
    "humidifiers": [],
    "ventilations": []
}
addr_book['sensor'].append(72)
# %%
