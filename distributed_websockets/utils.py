import asyncio


def clear_task(task: asyncio.Task) -> None:
    if task.done():
        task.result()
    else:
        task.cancel()
