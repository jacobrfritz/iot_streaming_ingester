import asyncio

from iot_streaming_ingester.connector import RedisConnector
from iot_streaming_ingester.worker_manager import WorkerManager
from iot_streaming_ingester.worker import Worker
from .measurement import Mean, EventsPerSecondMeasurement

async def run() -> None:
    try:
        conn = RedisConnector()
        await conn.create_group_if_not_exists()
        worker_manager = WorkerManager()
        workers = [worker_manager.create_worker(conn, 100, Worker) for _ in range(1)]#type: ignore

        tasks = [worker_manager.worker_process(worker, conn, []) for worker in workers]
        await asyncio.gather(*tasks)
        
    except asyncio.CancelledError:
        print("Shutdown signal received. Cancelling worker tasks...")
    finally:
        print("Closing database and Redis connections...")
        await conn.r.close() 
        print("Shutdown complete.")