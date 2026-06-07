from typing import Protocol, cast

import redis.asyncio as aioredis

from iot_streaming_ingester.interfaces import RedisMessage, RedisStreamResponse


class Connector(Protocol):
    def __init__(self): ...
    
    async def read(
        self,
        worker_name: str,
        count: int,
        block: int = 0,
    ) -> RedisStreamResponse: ...
    
    async def ack(
        self,
        message_id:str
        )->bool:...
    
    async def get_pending_messages(
        self,
        worker_name: str,
        count: int,
    ) -> RedisStreamResponse: ...
    
    async def acknowledge_messages(
        self, messages: list
    ) -> bool: ...


class RedisConnector(Connector):
    def __init__(self, host: str = "localhost", port: int = 6379, stream_name="iot_events", group: str = "iot_group"):
        self.r = aioredis.Redis(host=host, port=port, decode_responses=True)

        self.stream_name = stream_name
        self.group = group

    async def create_group_if_not_exists(self):
        existing_groups = await self.r.xinfo_groups(self.stream_name)
        if not any(g["name"] == self.group for g in existing_groups):
            await self.r.xgroup_create(
                name=self.stream_name, groupname=self.group, id="$", mkstream=True
            )

    async def read(
        self,
        worker_name: str,
        count: int,
        block: int = 0,
    ) -> RedisStreamResponse:
        # > means only send messages to worker that have never been processed
        # block = 0 means wait until a message is avaiilable
        messages = await self.r.xreadgroup(
            groupname=self.group,
            consumername=worker_name,
            streams={self.stream_name: ">"},
            count=count,
            block=block,
        )
        return cast(RedisStreamResponse, messages or {})

    async def ack(self, message_id:str):
        await self.r.xack(self.stream_name, self.group, message_id)
        
    async def acknowledge_messages(
        self,
        messages: list[str]
    ):
        if messages:
            await self.r.xack(self.stream_name, self.group, *messages)
    
    async def get_pending_messages(
        self,
        worker_name: str,
        count: int
    ) -> RedisStreamResponse:
        pending_messages = await self.r.xreadgroup(
            groupname=self.group,
            consumername=worker_name,
            # 0 means fetch pending messages only
            streams={self.stream_name: "0"},
            count=count,
        )
        return cast(RedisStreamResponse, pending_messages or {})
