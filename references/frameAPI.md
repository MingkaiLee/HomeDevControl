# Frame API Reference

Created by Li Mingkai on 2021.06.03

**[说明]** 本文档将记录myframe.py文件中实现的类及其接口的功能, 方便后续开发查阅及更改, 本部分只记录方法功能, 具体输入输出规范已在注释中。

## 1. 数据帧类

### 1.1. MyFrame

该类为本文件中的数据帧基类, 可按照16进制字符串构建完整的Modbus数据帧, 构造时需要提供**帧头**, **命令域**, **数据域**三个部分的内容, 长度域和异或校验和会自动计算, 本项目中, 该类的实例一般在newdevice中的设备类产生数据帧的方法中返回。

|方法名称|方法功能|
|-|-|
|reCommand|修改命令域内容|
|reData|修改数据域内容|
|toBytes|输出bytes数据|
---

## 2. 数据帧解析器

### 2.1. FrameParse

该类将构造一个可复用的数据帧解析实例, 能将从串口读入的bytes类的数据帧解析, 分割出**帧头, 长度域, 命令域, 数据域, 异或和**等部分, 并能够对**数据域**再作细分。

|方法名称|方法功能|
|-|-|
|parse|解析bytes数据|
|show|按序打印帧头, 长度域, 命令域, 数据域, 异或和, 地址, 功能码, 数据|
|getData|获取数据域的功能码之后的内容|
|\_\_str\_\_|覆写的魔术方法, print会按序打印帧头, 长度域, 命令域, 数据域, 异或和|
