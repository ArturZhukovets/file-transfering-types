import os
from typing import Iterator

import uvicorn
from brotli_asgi import BrotliMiddleware

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, Response, JSONResponse
from starlette.responses import FileResponse

from utils import get_brotli_stream, get_brotli_byte_string

BASE_PATH = os.getcwd()

if not os.path.exists(os.path.join(BASE_PATH, "static")):
    os.mkdir(os.path.join(BASE_PATH, "static"))


FILEPATH = os.path.join(BASE_PATH, "static/big_file.txt")

app = FastAPI()
# app.add_middleware(
#     BrotliMiddleware,
#     quality=4,
#     mode="text",
#     lgwin=22,
#     lgblock=0,
#     minimum_size=400,
#     gzip_fallback=True
# )

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/brotli_stream/")
def brotli_stream(request: Request):
    accept_encoding = request.headers.get("Accept-encoding")
    if accept_encoding and "br" in accept_encoding:
        content = get_brotli_stream(file_path=FILEPATH)
        response = StreamingResponse(content=content, media_type="application/octet-stream")
        response.headers["Content-Encoding"] = "br"
        response.headers["Vary"] = "Accept-Encoding"
        return response
    return Response(status_code=400)


@app.get("/brotli_bytes/")
def brotli_bytes_response(request: Request):
    accept_encoding = request.headers.get("Accept-encoding")
    if accept_encoding and "br" in accept_encoding:
        content = get_brotli_byte_string(file_path=FILEPATH)
        response = Response(content=content, media_type="application/octet-stream")
        response.headers["Content-Encoding"] = "br"
        return response
    return Response(status_code=400)


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
