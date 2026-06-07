from .worker import Worker

class WorkerManager:
    def create_worker(self, conn, max_message_count, worker:Worker):
        return Worker(conn, max_message_count)
    
    def destroy_worker(self, worker:type[Worker]):
        del worker
        
    async def worker_process(self, worker:Worker, conn):
        async for message in worker.run():
            #list[tuple]
            """
            Message Format
            ('1780784644853-0', 
            {'producer_id': '840183a7-5410-439c-b49c-3b9174c7afed', 
            'event_time': '2026-06-06T17:24:03.555080', 
            'payload': '1.2140508355420807'}
            )
            """
            parsed = {event[0]:event[1] for event in message}
            print(len(parsed))
            await conn.acknowledge_messages(list(parsed.keys()))