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


# 功能测试
if __name__ == '__main__':
    parser = FrameParse()
    res = parser.construct('245f6700010300000003')
    print(type(parser.frame))
    parser.parse_show()