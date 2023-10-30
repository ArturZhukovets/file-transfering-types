import os
from typing import Iterator

import uvicorn

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from starlette.responses import FileResponse

from utils import iter_file, iter_file_2, iter_and_brotli_compress, iter_and_gzip_compress, compress_file_brotli


BASE_PATH = os.getcwd()

if not os.path.exists(os.path.join(BASE_PATH, "static")):
    os.mkdir(os.path.join(BASE_PATH, "static"))


FILEPATH = os.path.join(BASE_PATH, "static/big_file.txt")
print(FILEPATH)


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/download_stream/", name="download_stream")
def download_large_file_streaming_response():
    response = StreamingResponse(iter_file(FILEPATH), media_type="application/octet-stream")
    response.headers["Content-Disposition"] = f"attachment; filename={os.path.basename(FILEPATH)}"
    return response


@app.get("/download_file-response/", name="download_file-response")
def download_large_file_file_response():
    return FileResponse(FILEPATH, media_type="application/octet-stream", filename=os.path.basename(FILEPATH))

@app.get("/download_compressed/", name="download_brotli")
def download_large_file_compressed(request: Request):
    accept_encoding = request.headers.get("Accept-encoding")
    if accept_encoding and "br" in accept_encoding:
        response = StreamingResponse(iter_and_brotli_compress(FILEPATH), media_type="application/octet-stream")
        response.headers["Content-Disposition"] = f"attachment; filename={os.path.basename(FILEPATH)}"
        response.headers["Content-Encoding"] = "br"
    elif accept_encoding and "gzip" in accept_encoding:
        response = StreamingResponse(iter_and_gzip_compress(FILEPATH), media_type="application/octet-stream")
        response.headers["Content-Disposition"] = f"attachment; filename={os.path.basename(FILEPATH)}"
        response.headers["Content-Encoding"] = "gzip"
    else:
        response = StreamingResponse(iter_file(FILEPATH), media_type="application/octet-stream")
        response.headers["Content-Disposition"] = f"attachment; filename={os.path.basename(FILEPATH)}"
    return response


@app.get("/download_compressed_custom_header/", name="download_custom_brotli")
def download_large_file_using_custom_brotli_header(request: Request):
    accept_encoding = request.headers.get("Accept-encoding")
    if accept_encoding and "br" in accept_encoding:
        response = StreamingResponse(iter_and_brotli_compress(FILEPATH), media_type="application/octet-stream")
        response.headers["Content-Disposition"] = f"attachment; filename={os.path.basename(FILEPATH)}"
        response.headers["Content-Encoding"] = "brotli-custom-header"
    else:
        response = StreamingResponse(iter_file(FILEPATH), media_type="application/octet-stream")
    return response

@app.get("/download_compressed_brotli_no_stream/", name="download_brotli_no_stream")
def download_large_file_brotli_no_stream(request: Request):
    accept_encoding = request.headers.get("Accept-encoding")
    if accept_encoding and "br" in accept_encoding:
        file_path = compress_file_brotli(FILEPATH)
        response = FileResponse(file_path, media_type="application/octet-stream")
        response.headers["Content-Disposition"] = f"attachment; filename={os.path.basename(FILEPATH)}"
        response.headers["Content-Encoding"] = "br"
    else:
        response = FileResponse(FILEPATH, media_type="application/octet-stream")
    return response


if __name__ == "__main__":

    if not os.path.exists(FILEPATH):
        with open(FILEPATH, 'wb') as file:
            for i in range(1_000):
                file.write(b"Hello world. " * 10_000 + b"\n")

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8036,
        reload=True
    )
