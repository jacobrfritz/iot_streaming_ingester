# src/base_python_project/main.py
from iot_streaming_ingester.connector import RedisConnector
from iot_streaming_ingester.worker import Worker


async def run() -> None:
    conn = RedisConnector()
    await conn.create_group_if_not_exists()

    worker = Worker(conn, 10)
    async for message in worker.run(10):
        print(message)
