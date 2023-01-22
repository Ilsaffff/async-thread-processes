import requests
from time import time
import concurrent.futures
import aiohttp
import asyncio
from asyncio import Semaphore
from aiofile import AIOFile

URL = 'https://loremflickr.com/320/240'
COUNT_IMAGES = 100
COUNT_THREADS = 15
COUNT_PROCESSES = 5
COUNT_ASYNC = 100


class Downloader:
    def __init__(self, method_str):
        self.method_str = method_str

    def download_image(self, number_image):
        """This method for sync functions"""
        print(f'Началась загрузка картинки №{number_image}\n')
        response = requests.get(URL, allow_redirects=True)
        filename = f"{self.method_str}/{int((time()) * 1000)}.jpeg"
        with open(filename, 'wb') as file:
            file.write(response.content)
            print(f'Закончилась загрузка картинки №{number_image}\n')

    async def async_download_image(self, semaphore, url, session, number_image):
        """This method for async functions"""
        await semaphore.acquire()
        print(f'Начинается скачивание {number_image}')
        async with session.get(url, allow_redirects=True) as r:
            filename = f'{self.method_str}/file-{int(time() * 1000)}.jpeg'
            async with AIOFile(filename, 'wb') as f:
                data = await r.read()
                await f.write(data)
                await f.fsync()
                print(f'Заканчивается скачивание {number_image}')
            semaphore.release()


def sync():
    downloader = Downloader('sync')
    for number_image in range(COUNT_IMAGES):
        downloader.download_image(number_image)


def thread():
    downloader = Downloader('thread')
    with concurrent.futures.ThreadPoolExecutor(COUNT_THREADS) as executor:
        executor.map(downloader.download_image, range(COUNT_IMAGES))


def processes():
    downloader = Downloader('processes')
    with concurrent.futures.ProcessPoolExecutor(COUNT_PROCESSES) as executor:
        executor.map(downloader.download_image, range(COUNT_IMAGES))


async def async_function():
    downloader = Downloader(method_str='async')
    tasks = list()
    semaphore = Semaphore(COUNT_ASYNC)
    async with aiohttp.ClientSession() as session:
        for number_image in range(COUNT_IMAGES):
            task = asyncio.create_task(downloader.async_download_image(semaphore, URL, session, number_image))
            tasks.append(task)
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    start_time = time()

    sync()
    # thread()
    # processes()
    # asyncio.run(async_function())

    print(f'TIME:{time() - start_time}')
