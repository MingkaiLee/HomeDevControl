"""
测试面板与单个灯的通讯及通讯时延
Created on 2021.06.15
"""
import serial
import sys
import time
import asyncio
# path = '/Users/limingkai/vsCode/Python_WorkSpace/HomeDevControl'
path = 'D:\house app\物联网\lmk\IoTLab'
sys.path.append(path)
from myframe import MyFrame
from newdevice import Panel1, Lamp

if __name__ == '__main__':
    port_name = 'COM5'
    ser = serial.Serial(port_name, timeout=3)
    if not ser.isOpen():
        ser.open()
    # 创建面板
    panel = Panel1(999)
    # 灯具
    lps = [i for i in range(11, 27)]
    # 加入灯具
    panel.addDevice(lamp=lps)
    

    ser.close()
    sys.exit()


