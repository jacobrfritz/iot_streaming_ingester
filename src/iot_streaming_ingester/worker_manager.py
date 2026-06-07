from .worker import Worker
import time

class WorkerManager:
    def create_worker(self, conn, max_message_count, worker:Worker):
        return Worker(conn, max_message_count)
    
    def worker_offline(self, worker:type[Worker]):
        """
        Worker stops emitting events to simulate going offline
        """
        ...
        
    def worker_online(self, worker:type[Worker]):
        """
        Worker start emitting events to simulate going coming back online
        """
        ...
        
    import time

    async def worker_process(self, worker: Worker, conn):
        total_processed = 0
        last_report_time = time.time()
        
        async for message in worker.run():
            start_time = time.time()  # 1. Capture the start time here!
            
            parsed = {event[0]: event[1] for event in message}
            total_processed += len(parsed)
            
            await conn.acknowledge_messages(list(parsed.keys()))
            
            # Report throughput once per second
            now = time.time()
            if now - last_report_time >= 1.0:
                rate = total_processed / (now - last_report_time)
                print(f"Throughput: {rate:.2f} msgs/sec (Processed: {total_processed})")
                total_processed = 0
                last_report_time = now
                
            loop_duration = time.time() - start_time  # 2. Compare against start_time
            if loop_duration > 0.05: 
                print(f"⚠️ Micro-hitch detected: Batch of {len(parsed)} took {loop_duration*1000:.1f}ms")