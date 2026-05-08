import asyncio
import functools
from typing import Any, Callable


class AsyncService:
    async def run_in_thread(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))
