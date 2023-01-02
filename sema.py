# import asyncio
# import concurrent.futures
from threading import Semaphore

import psutil

TH = 0
AS = 0


class MemoSemaphore(Semaphore):
    def __init__(self, max_memo=2048):
        self._memory = psutil.virtual_memory().used
        self._max_memo = max_memo * 1024 ** 2
        super().__init__()

    def acquire(self, *args, **kwargs):
        print("threads", self._value)
        super().acquire(*args, **kwargs)
        if self._can_release():
            self.release()

    __enter__ = acquire

    def _can_release(self):
        _used = psutil.virtual_memory().used
        return _used - self._memory < self._max_memo

# semaphore = MemoSemaphore()
#
#
# # semaphore.release()
#
#
# def th_worker(*_):
#     global TH
#     with semaphore:
#         TH += 1
#
#
# async def as_worker():
#     global AS
#     with semaphore:
#         AS += 1
#
#
# async def main():
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         executor.map(th_worker, range(10))
#
#     await asyncio.gather(*[as_worker() for _ in range(10)])
#
#
# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
#     loop.close()
#
#     print("TH", TH)
#     print("AS", AS)
