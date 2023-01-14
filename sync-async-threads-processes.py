import requests
from time import time
import concurrent.futures
import aiohttp
import asyncio
from asyncio import Semaphore

URL = 'https://loremflickr.com/320/240'
COUNT_IMAGES = 2000
COUNT_THREADS = 15
COUNT_PROCESSES = 5
COUNT_ASYNC = 100


def download_image(number_image, method):
    print(f'Началась загрузка картинки №{number_image}\n')
    response = requests.get(URL, allow_redirects=True)
    filename = f"{method}/{int((time())*1000)}.jpeg"
    with open(filename, 'wb') as file:
        file.write(response.content)
        print(f'Закончилась загрузка картинки №{number_image}\n')


def sync():
    for number_image in range(COUNT_IMAGES):
        download_image(number_image, method='sync')


def thread():
    with concurrent.futures.ThreadPoolExecutor(COUNT_THREADS) as executor:
        futures = []
        for i in range(COUNT_IMAGES):
            futures.append(executor.submit(download_image, number_image=i, method='thread'))


def processes():
    with concurrent.futures.ProcessPoolExecutor(COUNT_PROCESSES) as executor:
        futures = []
        for i in range(COUNT_IMAGES):
            futures.append(executor.submit(download_image, number_image=i, method='processes'))


async def async_download_image(semaphore, url, session, number_image):
    await semaphore.acquire()
    print(f'Начинается скачивание {number_image}')
    async with session.get(url, allow_redirects=True) as response:
        filename = f'async/file-{int(time() * 1000)}.jpeg'
        with open(filename, 'wb') as file:
            file.write(await response.read())
        print(f'Заканчивается скачивание {number_image}')
        semaphore.release()


async def async_function():
    tasks = list()
    semaphore = Semaphore(COUNT_ASYNC)
    async with aiohttp.ClientSession() as session:
        for number_image in range(COUNT_IMAGES):
            task = asyncio.create_task(async_download_image(semaphore, URL, session, number_image))
            tasks.append(task)
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    start_time = time()

    sync()
    # thread()
    # processes()
    # asyncio.run(async_function())

    print(f'TIME:{time() - start_time}')
