"""
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("square", help="display a square of a given number",
                    type=int)
args = parser.parse_args()
print(args.square**2)
"""

"""
import asyncio
async def main():
    print('hello')
    await asyncio.sleep(1)
    print('world')
asyncio.run(main())
"""

"""
def consumer():
    status = True
    print("只在第一次send时调用")
    while True:
        n = yield status
        print(f"我拿到了{n}!")
        if n == 3:
            status = False

def producer(consumer):
    n = 5
    while n > 0:
    # yield给主程序返回消费者的状态
        yield consumer.send(n)
        n -= 1

if __name__ == '__main__':
    c = consumer()
    c.send(None)
    print("第一次send调用结束")
    p = producer(c)
    for status in p:
        if status == False:
            print("我只要3,4,5就行啦")
            break
    print("程序结束")
"""
"""
import asyncio

async def compute(x, y):
    print("Compute %s + %s ..." % (x, y))
    await asyncio.sleep(1.0)
    return x + y

async def print_sum(x, y):
    result = await compute(x, y)
    print("%s + %s = %s" % (x, y, result))

loop = asyncio.get_event_loop()
loop.run_until_complete(print_sum(1, 2))
loop.close()
"""

import asyncio
import time

async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)

async def main():
    print(f"started at {time.strftime('%X')}")

    await say_after(1, 'hello')
    await say_after(2, 'world')

    print(f"finished at {time.strftime('%X')}")

asyncio.run(main())