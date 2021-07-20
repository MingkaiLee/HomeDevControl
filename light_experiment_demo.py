# -*- encoding=utf-8 -*-
import time
import struct
import asyncio
import serial_asyncio


class Output(asyncio.Protocol):
    point_list = [46]

    def __init__(self):
        super().__init__()
        self.reply_data = {}
        self._data = []
        self._buffer = set()
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        self._data.extend(data)
        k = 0
        for j in range(0, len(self._data) - 1):
            if j < k:
                continue
            k = j
            if self._data[j] != 0xFE:
                continue
            if len(self._data) - j >= self._data[j + 1] + 5:
                if self._data[j + 2] == 0x44 and self._data[j + 3] == 0x5F:
                    z = 0
                    for x in self._data[j + 1:j + self._data[j + 1] + 4]:
                        z = z ^ x
                    if z == self._data[j + self._data[j + 1] + 4]:
                        key = self._data[j + 4] + (self._data[j + 5] << 8)
                        if key in self.reply_data:
                            self.reply_data[key] = time.time() - self.reply_data[key]
                        k = j + self._data[j + 1] + 5
            else:
                break
        self._data = self._data[k:]

    def connection_lost(self, exc):
        self.transport.loop.stop()

    @asyncio.coroutine
    def send_data(self, onoff, brightness, ct, transition):
        # prepare query
        query_list = []
        delay_execute = 600  # according to total num,
        delay_reply = 2000  # according to total num
        delay_interval = int(600 / 16)
        for addr in self.point_list:
            query_data = [0xfe, 0, 0x24, 0x5f]
            cmd = 0x10
            query_data.extend(struct.pack('<H', addr))
            query_data.extend(struct.pack('BB', 1, cmd))
            query_data.extend(struct.pack('>HH', 0, 6))  # start addr, register quatity
            query_data.extend(struct.pack('B', 6 * 2))
            query_data.extend(struct.pack('>HHHHHH', onoff, brightness, ct, transition, delay_execute, delay_reply))
            query_data[1] = len(query_data) - 4
            query_list.append(query_data)
            delay_execute = delay_execute - delay_interval
            delay_reply = delay_reply + delay_interval
            if delay_execute < 0:
                delay_execute = 0
        # process query
        for query in query_list:
            key = query[4] + (query[5] << 8)
            y = 0
            for x in query[1:]:
                y = y ^ x
            query.append(y)
            self.transport.write(query)
            self.reply_data[key] = time.time()
            yield from asyncio.sleep(delay_interval / 1000)
        yield from asyncio.sleep(delay_reply / 1000 + 2)
        # finish
        self.transport.close()


def adjust(onoff, brightness=100, ct=0, transition=0):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    coro = serial_asyncio.create_serial_connection(loop, Output, 'COM13', baudrate=9600)
    transport, protocol = loop.run_until_complete(coro)
    loop.run_until_complete(protocol.send_data(onoff, brightness, ct, transition))
    # loop.run_forever()
    print(protocol.reply_data)
    loop.close()


if __name__ == '__main__':
    print('START')
    start = time.time()
    adjust(1, 100, 70, 1)  # onoff, brightness, ct, transition
    print('END')
    print(time.time() - start)
    pass
