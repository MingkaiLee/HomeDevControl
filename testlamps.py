"""
用于测试灯具控制
灯具地址11-26
Created by Li Mingkai on 2021/05/06
"""
import serial
import sys
import time
import asyncio
sys.path.append('D:\house app\物联网\lmk\IoTLab')
from myframe import MyFrame
from newdevice import Lamp
DEV_ADDR = range(11, 27)

# 10进制设备地址转字符串
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

async def switchLamp(ser:serial.Serial, lamp:Lamp, s, dd, dr):
    frame = lamp.generateWriteFrame(switch=s, luminance=90, ct=64, ddt=dd, drt=dr)
    ser.write(bytes.fromhex(frame.toBytes()))
    await asyncio.sleep(float(dr) / 1000.0)
    res = ser.read(13)
    print(res)

async def turnOn(ser:serial.Serial, lamps:list):
    task0 = asyncio.create_task(switchLamp(ser, lamps[0], 1, 300, 0))
    task1 = asyncio.create_task(switchLamp(ser, lamps[1], 1, 200, 10))
    task2 = asyncio.create_task(switchLamp(ser, lamps[2], 1, 100, 20))
    task3 = asyncio.create_task(switchLamp(ser, lamps[3], 1, 0, 30))
    await task0
    await task1
    await task2
    await task3

async def turnOff(ser:serial.Serial, lamps:list):
    task0 = asyncio.create_task(switchLamp(ser, lamps[0], 0, 300, 0))
    task1 = asyncio.create_task(switchLamp(ser, lamps[1], 0, 200, 10))
    task2 = asyncio.create_task(switchLamp(ser, lamps[2], 0, 100, 20))
    task3 = asyncio.create_task(switchLamp(ser, lamps[3], 0, 0, 30))
    await task0
    await task1
    await task2
    await task3

if __name__ == '__main__':
    port_name = 'COM3'
    ser = serial.Serial(port_name)
    if not ser.isOpen():
        ser.open()
    lamps_list = []
    for i in range(17, 21):
        lamps_list.append(Lamp(i, i))
    
    asyncio.run(turnOff(ser, lamps_list))
    time.sleep(1)
    asyncio.run(turnOn(ser, lamps_list))

    """
    for lamp in lamps_list:
        frame = lamp.generateWriteFrame(switch=1, luminance=90, ct=64)
        ser.write(bytes.fromhex(frame.toBytes()))
        res = ser.read(13)
        print(res)
    time.sleep(1)
    """

    """
    for i in range(11, 17):
        hexaddr = getAddrStr(i)
        cframe = MyFrame('fe', '24 5f', '{} 01 03 00 00 00 03'.format(hexaddr))
        ser.write(bytes.fromhex(cframe.toBytes()))
        res = ser.read(16)
        print(res)
    """
    ser.close()
    sys.exit()


