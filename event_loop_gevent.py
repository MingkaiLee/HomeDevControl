# 基于gevent实现的事件循环

# 打入补丁
from gevent import monkey
monkey.patch_all()
# 导入标准库及第三方库
import gevent
import time
import serial
from queue import PriorityQueue as PQ
# 导入自编模块
MY_MODULE_PATH = 'D:\house app\物联网\lmk\IoTLab'
import sys
sys.path.append(MY_MODULE_PATH)
from newdevice import Sensor, Lamp, Curtain, Panel1
from myframe import MyFrame, FrameParse
# 串口号
PORT_NAME = 'COM5'

def initSerial(port_name: str) -> serial.Serial:
    """
    ### 创建一个串口实例
    #### Parameters:
    - port_name: 串口名称
    #### Returns:
    - ser: 串口实例
    """
    ser = None
    try:
        ser = serial.Serial(port_name, timeout=3)
    except ValueError:
        print("Wrong port_name.")
    return ser

def getPriorityGreenlet(func: function, priority: int, *args, **kargs) -> tuple:
    """
    ### 创建可加入优先级队列的Greenlet元组(prior, greenlet)
    #### Parameters:
    - func: 包装成Greenlet类实例的函数
    - prior: 该Greenlet类实例的优先级
    - args: 位置参数
    - kargs: 关键字参数
    #### Returns:
    - res: Greenlet实例二元组
    """

    gl = gevent.spawn(func, args, kargs)
    return (priority, gl)


if __name__ == '__main__':
    # 初始化优先级队列
    event_pq = PQ()

    # 初始化串口
    ser = initSerial(PORT_NAME)

    # 初始化面板
    p = Panel1(999)

    # 可用设备地址
    # 传感器
    ss = 992
    # 灯具
    lps = [i for i in range(11, 27)]
    
    # 向面板中添加设备
    # 加入传感器
    p.addDevice(sensor=ss)
    # 加入灯具
    p.addDevice(lamp=lps)

    # 打开串口并进入循环
    if not ser.isOpen():
        ser.open()
    while True:
        if event_pq.empty():
            ser.read()
        else:
            pass
    # 循环结束关闭串口
    ser.close() 
    # 程序退出
    sys.exit()