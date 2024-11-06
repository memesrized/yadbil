import asyncio


class TelegramAsync:
    # TODO: deal with existing event loop, like in notebook
    # now it doesn't work in notebook

    # def run(self):
    #     try:
    #         loop = asyncio.get_running_loop()
    #     except RuntimeError:  # 'RuntimeError: There is no current event loop...'
    #         loop = None

    #     if loop is None:
    #         asyncio.run(self._run())
    #     else:
    #         tsk = loop.create_task(self._run())
    #         # loop.run_until_complete(tsk)
    def run(self):
        asyncio.run(self._run())
