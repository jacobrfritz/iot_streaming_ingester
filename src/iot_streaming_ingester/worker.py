import uuid
from collections.abc import AsyncGenerator

from iot_streaming_ingester.connector import Connector
from iot_streaming_ingester.interfaces import RedisMessage, RedisStreamResponse

"""
Processes stream chunks from orchestrator
"""


class Worker:
    def __init__(self, conn: Connector, max_message_count: int):
        self.conn = conn
        self.max_message_count = max_message_count
        self.worker_name: str = str(uuid.uuid4())

    async def run(
        self
    ) -> AsyncGenerator[list[RedisMessage], None]:
        pending_messages = await self.conn.get_pending_messages(
            worker_name=self.worker_name, count=self.max_message_count
        )
        #if pending_messages:
            #self.get_metrics(pending_messages)
        while True:
            groups = await self.conn.read(
                worker_name=self.worker_name, count=self.max_message_count
            )
            # since there is only one group we are going to
            # assume we don't need to know the group
            if groups:
                messages = groups[0][1]
                if messages:
                    yield messages
                    #     metrics = self.get_metrics(messages)
                    #     yield metrics
