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

async def main(ser:serial.Serial, lamps:list):
    lamp_num = len(lamps)
    queue = asyncio.Queue()
    for i in range(lamp_num):
        ddt = 300*(lamp_num-1) - 300*i
        drt = 10*i
        lamp = lamps[i]
        frame = lamp.generateWriteFrame(switch=0, luminance=90, ct=64, ddt=ddt, drt=drt)
        queue.put_nowait(frame)
    for i in range(lamp_num):
        ddt = 1000+300*(lamp_num-1) - 300*i
        drt = 10*i
        lamp = lamps[i]
        frame = lamp.generateWriteFrame(switch=1, luminance=90, ct=64, ddt=ddt, drt=drt)
        queue.put_nowait(frame)
    started_at = time.monotonic()
    while not queue.empty():
        frame = await queue.get()
        ser.write(frame.toBytes())
        await asyncio.sleep(0.3)
        print(ser.read(13))
        queue.task_done()
    await queue.join()
    total_recvtime = time.monotonic() - started_at
    print(f'total_recvtime:{total_recvtime:.2f}')

# 异步串口灯控制, 帧与事件队列作用
async def writeFrame(ser:serial.Serial, frames:list):
    # 创建事件队列
    queue = asyncio.Queue()
    # 创建数据帧解析工具
    fp = FrameParse()
    for frame in frames:
        queue.put_nowait(frame)
    while not queue.empty():
        frame = await queue.get()
        ser.write(frame.toBytes())
        await asyncio.sleep(0.3)
        res = ser.read(13)
        fp.parse(res)
        fp.show()
        queue.task_done()
    await queue.join()

if __name__ == '__main__':
    port_name = 'COM4'
    ser = serial.Serial(port_name, timeout=5)
    if not ser.isOpen():
        ser.open()
    print(ser.isOpen())
    # 创建面板
    panel = Panel1(999)
    # 将可控的灯添加到面板中
    panel.addDevice(lamp=[i for i in range(11, 26)])
    # 接收面板数据
    res = ser.read()
    print(res)
    fp = FrameParse()
    fp.parse(res)
    # 展示面板数据
    fp.show()
    # 根据面板数据生成数据帧
    frames = panel.generateFrameFromData(fp.getData())
    fp.parse(frames[0])
    fp.show()
    ser.close()
    sys.exit()
    asyncio.run(writeFrame(ser, frames))
    ser.close()