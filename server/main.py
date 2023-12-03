import asyncio

import uvicorn
from chatflow import Interpreter, Runtime
from fastapi import FastAPI, WebSocket

app = FastAPI()

code = r"""
flow origin {
    speak "Hello, world!"
    while true {
        listen for question
        speak question
    }
}
"""


async def timeout_checker(timeout):
    await asyncio.sleep(timeout)


async def listen(socket):
    async def a_read_input_with_timeout(timeout=None):
        """Reads input from the user with an optional timeout.

        Args:
            timeout (int, optional): The timeout value in seconds. Defaults to None.

        Returns:
            str: The input message from the user if received within the timeout, None otherwise.
        """
        if timeout is None:
            return await socket.receive_text()
        else:
            timeout_task = asyncio.create_task(timeout_checker(timeout))
            input_task = asyncio.create_task(socket.receive_text())

            done, pending = await asyncio.wait({timeout_task, input_task}, return_when=asyncio.FIRST_COMPLETED)

            if input_task in done:
                message = input_task.result()
                timeout_task.cancel()
                return message
            else:
                input_task.cancel()
                return None

    return a_read_input_with_timeout


async def speak(socket):
    async def aprint(*args, **kwargs):
        """Prints the given arguments to the console.

        Args:
            *args: The arguments to be printed.
            **kwargs: The keyword arguments to be printed.
        """
        message = " ".join(str(arg) for arg in args)
        await socket.send_text(message)

    return aprint


async def runtime_loop(interpreter, listen_func, speak_func):
    while True:
        await interpreter.arun(listen_func, speak_func)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    """
    await websocket.accept()

    # 定义 listen 和 speak 函数
    listen_func = await listen(websocket)
    speak_func = await speak(websocket)

    # 创建 Runtime
    interpreter = Interpreter(code=code)
    runtime = Runtime(interpreter, speak_function=speak_func, listen_function=listen_func)

    # 运行 Runtime
    await runtime.arun()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
