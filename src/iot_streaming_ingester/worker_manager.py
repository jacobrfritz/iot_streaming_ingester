from datetime import datetime
import time

from .worker import Worker
from.measurement import Measurement


class WorkerManager:
    def create_worker(self, conn, max_message_count, worker:type[Worker]):
        return worker(conn, max_message_count)
    
    async def worker_process(self, worker: Worker, conn, measurements:list[Measurement]):
        total_processed = 0
        last_report_time = time.time()
        
        async for message in worker.run():
            start_time = time.time()  # 1. Capture the start time here!
            
            parsed = {event[0]: event[1] for event in message}
            out = []
            for stream_id, inner_dict in parsed.items():
                flattened_data = {'stream_id': stream_id, 'receipt_time': datetime.now().isoformat(), **inner_dict}
                out.append(flattened_data)
            
            total_processed += len(parsed)
            if start_time - last_report_time >= 1.0:
                rate = total_processed / (start_time - last_report_time)
                print(f"Throughput: {rate:.2f} msgs/sec (Processed: {total_processed})")
                total_processed = 0
                last_report_time = start_time
            
            metrics = [measure.measure(out) for measure in measurements]
            
            if metrics:
                print(metrics)
            await conn.acknowledge_messages(list(parsed.keys()))