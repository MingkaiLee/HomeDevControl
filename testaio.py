from random import randint
import asyncio

count = 0


async def download(code, permit_download, no_concurrent, downloading_event):
    global count
    downloading_event.set()
    wait_time = randint(1, 3)
    print('downloading {} will take {} second(s)'.format(code, wait_time))
    await asyncio.sleep(wait_time)  # I/O, context will switch to main function
    print('downloaded {}'.format(code))
    count -= 1
    if count < no_concurrent and not permit_download.is_set():
        permit_download.set()


async def main(loop):
    global count
    permit_download = asyncio.Event()
    permit_download.set()
    downloading_event = asyncio.Event()
    no_concurrent = 3
    i = 0
    while i < 9:
        if permit_download.is_set():
            count += 1
            if count >= no_concurrent:
                permit_download.clear()
            loop.create_task(download(i, permit_download, no_concurrent, downloading_event))
            await downloading_event.wait()  # To force context to switch to download function
            downloading_event.clear()
            i += 1
        else:
            await permit_download.wait()
    await asyncio.sleep(9)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main(loop))
    finally:
        loop.close()
    
    asyncio.create_task()

import asyncio
import random
import time


async def worker(name, queue):
    while True:
        # Get a "work item" out of the queue.
        sleep_for = await queue.get()

        # Sleep for the "sleep_for" seconds.
        await asyncio.sleep(sleep_for)

        # Notify the queue that the "work item" has been processed.
        queue.task_done()

        print(f'{name} has slept for {sleep_for:.2f} seconds')


async def main():
    # Create a queue that we will use to store our "workload".
    queue = asyncio.Queue()

    # Generate random timings and put them into the queue.
    total_sleep_time = 0
    for _ in range(20):
        sleep_for = random.uniform(0.05, 1.0)
        total_sleep_time += sleep_for
        queue.put_nowait(sleep_for)

    # Create three worker tasks to process the queue concurrently.
    tasks = []
    for i in range(3):
        task = asyncio.create_task(worker(f'worker-{i}', queue))
        tasks.append(task)

    # Wait until the queue is fully processed.
    started_at = time.monotonic()
    await queue.join()
    total_slept_for = time.monotonic() - started_at

    # Cancel our worker tasks.
    for task in tasks:
        task.cancel()
    # Wait until all worker tasks are cancelled.
    await asyncio.gather(*tasks, return_exceptions=True)

    print('====')
    print(f'3 workers slept in parallel for {total_slept_for:.2f} seconds')
    print(f'total expected sleep time: {total_sleep_time:.2f} seconds')


asyncio.run(main())