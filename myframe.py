# 数据帧类包, 方便构建基于zigbee模组设备的数据
def bytesStrStandardization(num: int) -> str:
    """
    ### 求整数的bytes.fromhex()的合法输入字符串
    #### Parameters:
    - num: 待求整数, 范围[0, 255], int
    #### Returns:
    - res: 可供bytes.fromhex()转化的字串
    """
    res = hex(num).lstrip('0x')
    if len(res) < 2:
        res = '0' + res
    return res


class MyFrame:
    """
    ### 按照16进制字符串构建的数据帧类
    #### Attributes:
    - __head: 帧头, 如"fe"
    - __cmd: 命令域, 如"24 5f"
    - __data: 数据域
    - __length: 长度域
    - __xor: 异或和
    - __content: 全帧
    """
    def __init__(self, head: str, cmd: str, data: str) -> None:
        """
        ### 构建发送帧
        #### Parameters:
        - head: 帧头内容, 16进制表示的str
        - cmd: 命令域内容, 16进制表示的str
        - data: 数据域内容, 16进制表示的str
        """ 

        self.__head = bytes.fromhex(head)
        self.__cmd = bytes.fromhex(cmd)
        self.__data = bytes.fromhex(data)
        # 帧长检查
        if len(self.__head) != 1:
            raise ValueError("Unexpected head input.")
        if len(self.__cmd) != 2:
            raise ValueError("Unexpected cmd input.")
        # 自动计算长度域
        self.__length = bytes.fromhex(bytesStrStandardization(len(self.__data)))
        # 自动计算异或校验和
        self.__xor = self._xorCalculator()
        # 自动生成16进制字符串
        self.__content = self._toHexStr()
    
    def _xorCalculator(self) -> bytes:
        """
        ### 计算异或校验和
        计算方法: 长度域, 命令域和数据域3个域按字节的异或和
        #### Returns:
        - res: 异或校验和计算结果, bytes
        """
        res = self.__length[0]
        for i in range(len(self.__cmd)):
            res = res ^ self.__cmd[i]
        for i in range(len(self.__data)):
            res = res ^ self.__data[i]
        return bytes.fromhex(bytesStrStandardization(res))
    
    def reCommand(self, cmd: str) -> None:
        """
        ### 修改命令域内容
        #### Parameters:
        - cmd: 命令域内容, 16进制表示的str
        """
        if len(bytes.fromhex(cmd)) != 2:
            raise ValueError("Unexpected cmd input.")
        self.__cmd = bytes.fromhex(cmd)
        # 重新计算异或校验和
        self.__xor = self._xorCalculator()
        # 重新生成整串
        self.__content = self._toHexStr()
    
    def reData(self, data: str) -> None:
        """
        ### 修改数据域内容
        #### Parameters:
        - data: 数据域内容, 16进制表示的str
        """
        self.__data = bytes.fromhex(data)
        # 重新计算长度域
        self.__length = bytes.fromhex(bytesStrStandardization(len(self.__data)))
        # 重新计算异或校验和
        self.__xor = self._xorCalculator()
        # 重新生成整串
        self.__content = self._toHexStr()
    
    def _toHexStr(self) -> str:
        """
        ### 输出可供bytes.fromhex()化作字节串的字符串
        #### Returns:
        - res: 全帧的16进制字符串
        """
        return self.__head.hex() + self.__length.hex() + self.__cmd.hex() + self.__data.hex() + self.__xor.hex()
    
    def toBytes(self) -> bytes:
        """
        ### 输出bytes数据
        #### Returns:
        - res: 全帧的bytes数据
        """
        return bytes.fromhex(self.__content)
    
    def __str__(self) -> str:
        return self.__head.hex() + ':' + self.__length.hex() + ':' + self.__cmd.hex(':') + ':' + self.__data.hex(':') + ':' + self.__xor.hex()

# 将输入命令解析出结果
class FrameParse:
    def __init__(self, frame: bytes) -> None:
        self._frame = frame
        self._frameStr = frame.hex()
        self._parse()

    def _parse(self) -> None:
        self._head = self._frameStr[:2]
        self._length = self._frameStr[2:4]
        self._cmd = self._frameStr[4:8]
        self._data = self._frameStr[8:-2]
        self._xor = self._frameStr[-2:]
    