from typing import Protocol, TypeAlias, cast

import redis.asyncio as aioredis

from iot_streaming_ingester.interfaces import RedisMessage, RedisStreamResponse


class Connector(Protocol):
    def __init__(self): ...
    async def read(
        self,
        worker_name: str,
        count: int,
        group: str = "iot_group",
        stream_name: str = "iot_events",
        block: int = 0,
    ) -> RedisStreamResponse: ...
    async def get_pending_messages(
        self,
        worker_name: str,
        count: int,
        group: str = "iot_group",
        stream_name: str = "iot_events",
    ) -> RedisStreamResponse: ...
    async def acknowledge_messages(
        self, messages: list, group: str = "iot_group", stream_name: str = "iot_events"
    ) -> None: ...


class RedisConnector(Connector):
    def __init__(self, host: str = "localhost", port: int = 6379):
        self.r = aioredis.Redis(host=host, port=port, decode_responses=True)

    async def create_group_if_not_exists(
        self, stream_name="iot_events", group: str = "iot_group"
    ):
        existing_groups = await self.r.xinfo_groups(stream_name)
        if not any(g["name"] == group for g in existing_groups):
            await self.r.xgroup_create(
                name=stream_name, groupname=group, id="$", mkstream=True
            )

    async def read(
        self,
        worker_name: str,
        count: int,
        group: str = "iot_group",
        stream_name: str = "iot_events",
        block: int = 0,
    ) -> RedisStreamResponse:
        # > means only send messages to worker that have never been processed
        # block = 0 means wait until a message is avaiilable
        messages = await self.r.xreadgroup(
            groupname=group,
            consumername=worker_name,
            streams={stream_name: ">"},
            count=count,
            block=block,
        )
        return cast(RedisStreamResponse, messages or {})

    async def get_pending_messages(
        self,
        worker_name: str,
        count: int,
        group: str = "iot_group",
        stream_name: str = "iot_events",
    ) -> RedisStreamResponse:
        pending_messages = await self.r.xreadgroup(
            groupname=group,
            consumername=worker_name,
            # 0 means fetch pending messages only
            streams={stream_name: "0"},
            count=count,
        )
        return cast(RedisStreamResponse, pending_messages or {})

    async def acknowledge_messages(
        self,
        messages: list[RedisMessage],
        group: str = "iot_group",
        stream_name: str = "iot_events",
    ):
        for message_id, _ in messages:
            await self.r.xack(stream_name, group, message_id)
