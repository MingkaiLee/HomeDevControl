"""
数据帧解析类模块
数据帧解析器负责构造和析构数据帧
"""
import prettytable as pt


class FrameParse:
    def __init__(self, head='fe'):
        """
        数据帧解析类, 用于构造和析构数据帧, 基于Modebus协议
        """
        # 帧头
        self.head: str = head
        self._frame: bytes = None
        self._frameStr: str = None
    
    @property
    def frame(self):
        return self._frame
    
    @property
    def frameStr(self):
        return self._frameStr
    
    def _xorStr(self, val: str) -> str:
        """
        计算异或校验和

        计算方法: 长度域, 命令域和数据域3个域按字节的异或和

        Returns:
        - res: 异或校验和计算结果, str
        """
        temp = bytes.fromhex(val)
        res = temp[0]
        for i in range(1, len(temp)):
            res = res ^ temp[i]
        return self._byteStr(res)
    
    def _byteStr(self, val: int) -> str:
        """
        求整数的十六进制两位表字节的字符串


        Parameters:
        - val: 待求整数值

        Returns:
        - res 'xx'十六进制字符串
        """
        res = hex(val)[2:]
        res = '0' * (2-len(res)) + res
        return res

    def construct(self, content: str) -> bytes:
        """
        构造数据帧对象, 可用于串口通信的bytes类型.
        自动加上帧头并计算长度域及异或和

        Parameters:
        - content: 从命令域到数据域的内容
        """
        # 长度域, 命令域与数据域合成
        self._frameStr = self._byteStr(int(len(content) / 2 - 2)) + content
        self._frameStr = self.head + self._frameStr + self._xorStr(self._frameStr)
        frame = bytes.fromhex(self._frameStr)
        self._frame = frame

        return frame
    
    def parse_show(self, val: bytes=None):
        """
        分割数据帧, 并在命令行打印关键信息, 在调试时使用

        请不要在刚创建parse对象且用其构建帧的情况下调用
        """
        if val is not None:
            self._frame = val
            self._frameStr = val.hex()
        table: pt.PrettyTable = pt.PrettyTable()
        # 写多寄存器的情况
        if self._frameStr[14:16] == '10':
            table.add_column('项目', ['长度域', '命令域', '目的地址', '功能码', '起始地址'])
            table.add_column('十六进制值', [self._frameStr[2:4],
            self._frameStr[4:8],
            self._frameStr[8:12],
            self._frameStr[12:16],
            self._frameStr[16:20]])
            # 获取寄存器数量
            num = int(self._frameStr[20:24], 16)
            table.add_column('项目', [f'寄存器{i}' for i in range(num)])
            table.add_column('十六进制值', [self._frameStr[25+2*(i-1):25+2*i] for i in range(num)])
        # 其他情况暂时只作简单分割
        else:
             table.add_column('项目', ['长度域', '命令域', '目的地址', '功能码', '数据'])
             table.add_column('十六进制值', [self._frameStr[2:4],
             self._frameStr[4:8],
             self._frameStr[8:12],
             self._frameStr[12:16],
             self._frameStr[16:-2]])
        print(table)
        return table
    
    def judge(self, val: str) -> int:
        """
        检验数据帧是否合法, 根据帧头及异或校验和判断

        Parameters:
        - val: 自上位机读到的数据帧, 转为十六进制字符串

        Returns:
        - res: 合法为0, 帧头出错为1, 异或校验和出错为2
        """
        if val[:2] != self.head:
            return 1
        if val[-2:] != self._xorStr(val[2:-2]):
            return 2
        return 0

    def partition(self, val: str) -> tuple:
        """
        对正确的数据帧进行分割, 并返回分割结果

        Parameters:
        - val: 自上位机读到的数据帧的数据域值

        Returns:
        - res: 三元组, 第一个元素为设备地址, 第二个元素为功能码, 第三个元素为功能码后的数据域内容

        Details:
        - 当合法时, 除数据域之外的信息都无效, 针对数据域
        """
        res = (val[:4], val[4:8], val[8:])
        return res
        
    def parse(self, val: bytes) -> tuple:
        """
        检验数据帧是否合法, 若合法则将其分割并返回, 若非法则将其输出

        Parameters:
        - val: 自上位机读到的数据帧

        Returns:
        - res: 二元组, 第一个元素为合法符, 第二个元素为输出结果

        Details:
        - 解析来自设备回复和面板控制命令的数据帧, 这些帧具有这样的共有特征:
        - 帧头fe, 命令域44 5f
        """
        val_str = val.hex()
        flag = self.judge(val_str)
        if flag == 0:
            # 直接传入数据域的内容
            res = (flag, self.partition(val_str[8:-2]))
        else:
            res = (flag, val)
        return res

    def recover(self, val: bytes):
        """
        试图将非法的数据帧信息恢复, 计划主要用于恢复自面板发出的控制命令
        """
        pass

# 功能测试
if __name__ == '__main__':
    parser = FrameParse()
    res = parser.construct('245f6700010300000003')
    print(type(parser.frame))
    parser.parse_show()