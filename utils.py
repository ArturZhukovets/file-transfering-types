import gzip
import io
from io import BytesIO

import brotli
from typing import Iterator

CHUNK_SIZE: int = 1 * 1024 * 1024  # 1MB


##################################################################

def get_brotli_stream(file_path: str) -> Iterator:
    br_buffer = io.BytesIO()
    br_file = brotli.Compressor(quality=9,)
    with open(file_path, 'rb') as f_obj:
        while True:
            chunk = f_obj.read(CHUNK_SIZE)

            if not chunk:
                br_buffer.write(br_file.finish())
                compressed_chunk = br_buffer.getvalue()
                br_buffer.close()
                yield compressed_chunk
                break
            br_buffer.write(br_file.process(chunk) + br_file.flush())
            compressed_chunk = br_buffer.getvalue()
            print(len(compressed_chunk))
            br_buffer.seek(0)
            br_buffer.truncate()
            yield compressed_chunk


def another_brotli_stream(file_path: str):
    br_buffer = io.BytesIO()
    with open(file_path, 'rb') as f_obj:
        while True:
            chunk = f_obj.read(CHUNK_SIZE)

            if not chunk:
                compressed_chunk = br_buffer.getvalue()
                br_buffer.close()
                if compressed_chunk:
                    yield compressed_chunk
                break

            br_buffer.write(brotli.compress(chunk, quality=9))
            compressed_chunk = br_buffer.getvalue()
            print(len(compressed_chunk))
            br_buffer.seek(0)
            br_buffer.truncate()
            yield compressed_chunk


def get_brotli_byte_string(file_path: str) -> bytes:

    with open(file_path, 'rb') as f_obj:
        file_content = f_obj.read()
        compressed_content = brotli.compress(file_content)
    return compressed_content

