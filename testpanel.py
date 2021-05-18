"""
测试第一类控制面板
面板地址999
Created by Li Mingkai on 2021/05/18
"""
import serial
import sys
import time
import asyncio
path = 'D:\house app\物联网\lmk\IoTLab'
sys.path.append(path)
from myframe import MyFrame, FrameParse
from newdevice import Lamp, Panel1

if __name__ == '__main__':
    port_name = 'COM3'
    ser = serial.Serial(port_name, timeout=5)
    if not ser.isOpen():
        ser.open()
    # 创建面板
    panel = Panel1(999)
    # 创建可控制灯的列表
    lamp_list = []
    for i in range(11, 26):
        lamp_list.append(Lamp(i))
    
    # 未加入异步操作的试验
    frame = panel.generateFrame('01 06 00 d2 90 00 b4 3c')
    ser.write(frame.toBytes())
    res = ser.read(15)
    fp = FrameParse()
    fp.parse(res)
    fp.show()
    ser.close()