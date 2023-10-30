import gzip
import tempfile
from io import BytesIO

import brotli
from typing import Iterator

CHUNK_SIZE: int = 1 * 1024 * 1024  # 1MB


def iter_file_2(file_path) -> Iterator:
    with open(file_path, 'rb') as f_obj:
        yield from f_obj


def iter_file(file_path) -> Iterator:
    with open(file_path, 'rb') as f_obj:
        while True:
            chunk = f_obj.read(CHUNK_SIZE)
            if not chunk:
                break
            yield chunk


def iter_and_brotli_compress(file_path) -> Iterator:
    with open(file_path, 'rb') as f_obj:
        while True:
            chunk = f_obj.read(CHUNK_SIZE)
            if not chunk:
                break
            compressed_chunk = brotli.compress(chunk, mode=brotli.MODE_TEXT, quality=9)
            yield compressed_chunk


def iter_and_gzip_compress(file_path) -> Iterator:

    def gzip_chunk(payload: bytes) -> bytes:
        btsio = BytesIO()
        g = gzip.GzipFile(fileobj=btsio, mode='wb')
        g.write(payload)
        g.close()
        return btsio.getvalue()

    with open(file_path, 'rb') as f_obj:
        while chunk := f_obj.read(CHUNK_SIZE):
            yield gzip_chunk(chunk)


def compress_file_brotli(file_path: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False, ) as tmp_file:
        # tmp_file.name = file_path.split(".")[0] + ".tmp"
        with open(file_path, 'rb') as f_obj:
            while chunk := f_obj.read(CHUNK_SIZE):
                compressed_chunk = brotli.compress(chunk, mode=brotli.MODE_TEXT, quality=9)
                tmp_file.write(compressed_chunk)

        tmp_file.flush()
    return tmp_file.name


