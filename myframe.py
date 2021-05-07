# 发送数据帧类, 方便构建基于zigbee模组设备的数据
def bytesStrStandardization(num) -> str:
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
    def __xorCalculator(self) -> bytes:
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

    def __init__(self, head, cmd, data) -> None:
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
        self.__xor = self.__xorCalculator()
    
    def reCommand(self, cmd) -> None:
        """
        ### 修改命令域内容
        #### Parameters:
        - cmd: 命令域内容, 16进制表示的str
        """
        if len(bytes.fromhex(cmd)) != 2:
            raise ValueError("Unexpected cmd input.")
        self.__cmd = bytes.fromhex(cmd)
        # 重新计算异或校验和
        self.__xor = self.__xorCalculator()
    
    def reData(self, data) -> None:
        """
        ### 修改数据域内容
        #### Parameters:
        - data: 数据域内容, 16进制表示的str
        """
        self.__data = bytes.fromhex(data)
        # 重新计算长度域
        self.__length = bytes.fromhex(bytesStrStandardization(len(self.__data)))
        # 重新计算异或校验和
        self.__xor = self.__xorCalculator()
    
    def toBytes(self) -> str:
        """
        ### 输出可供bytes.fromhex()化作字节串的字符串
        #### Returns:
        - res: 全帧的16进制字符串
        """
        return self.__head.hex() + self.__length.hex() + self.__cmd.hex() + self.__data.hex() + self.__xor.hex()
    
    def __str__(self) -> str:
        return self.__head.hex() + ':' + self.__length.hex() + ':' + self.__cmd.hex(':') + ':' + self.__data.hex(':') + ':' + self.__xor.hex()