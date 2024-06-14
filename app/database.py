import asyncpg

class AsyncDatabaseConnection:
    def __init__(self, *args, **kwargs):
        self.connection = None
        self.args = args
        self.kwargs = kwargs

    async def __aenter__(self) -> asyncpg.Connection:
        self.connection = await asyncpg.connect(*self.args, **self.kwargs)
        return self.connection

    async def __aexit__(self, *_):
        await self.connection.close()