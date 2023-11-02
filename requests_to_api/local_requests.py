import brotli
import time
from typing import Optional

import requests
import re
import os

CUR_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(CUR_DIR, "data")

_CHUNK_SIZE = 1 * 1024 * 1024   # 5 MB

def _handle_chunk(chunk: bytes) -> bytes:
    return brotli.decompress(chunk)

def download(url, stream: bool = True, headers: Optional[dict] = None) -> str:
    with requests.get(url, stream=stream, headers=headers,) as response:
        print("Request headers:", response.request.headers)
        print("Response headers:", response.headers)
        response.raise_for_status()
        _total_size = response.headers.get("content-length")
        print(f"{_total_size = }")
        if _total_size:
            _total_size = int(_total_size)
        _downloaded_size = 0

        if "content-disposition" in response.headers:
            _, params = response.headers['content-disposition'].split(";")
            filename = params.split("filename=")[1].strip('"')
            filename = re.sub("/", "_", filename)
        else:
            filename = "result.txt"

        chunk_counter = 0
        if response.headers.get("Content-Encoding") == "brotli-custom-header":
            with open(os.path.join(DATA_DIR, filename), mode="wb") as file:
                for chunk in response.iter_content(chunk_size=_CHUNK_SIZE):
                    _downloaded_size += len(chunk)
                    chunk = _handle_chunk(chunk)
                    file.write(chunk)
                    chunk_counter += 1
        else:
            with open(os.path.join(DATA_DIR, filename), mode="wb") as file:
                for chunk in response.iter_content(chunk_size=None):
                    file.write(chunk)
                    _downloaded_size += len(chunk)
                    print(len(chunk))
                    chunk_counter += 1
        print(chunk_counter)
        print(f"{_downloaded_size = }")

    return file.name


def request_brotli_stream():
    url = "http://0.0.0.0:8036/brotli_stream/"
    result = download(url)
    print("File downloaded")


def request_brotli_bytes():
    url = "http://0.0.0.0:8036/brotli_bytes/"
    result = download(url)
    print("File downloaded")


def request_django_files(url):
    file_path = "datasets/2800_combined_from.txt"
    url = url
    result = download(url)
    print("File downloaded")


if __name__ == '__main__':
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)

    time_start = time.time()
    request_django_files("http://127.0.0.1:8000/files/simple-file/datasets/big_file.txt/")
    time_end = time.time() - time_start
    print(f"Simple file time: {time_end}")

    time_start = time.time()
    request_django_files("http://127.0.0.1:8000/files/brotli/datasets/big_file.txt/")
    time_end = time.time() - time_start
    print(f"brotli time: {time_end}")

    time_start = time.time()
    request_django_files("http://127.0.0.1:8000/files/gzip/datasets/big_file.txt/")
    time_end = time.time() - time_start
    print(f"gzip time: {time_end}")
