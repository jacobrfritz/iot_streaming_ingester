from typing import TypeAlias

# A single message is a tuple of (message_id, field_value_dict)
RedisMessage: TypeAlias = tuple[str, dict[str, str]]

# Based on your actual runtime data, xreadgroup is yielding a flat list of these messages
RedisStreamResponse: TypeAlias = list[RedisMessage]
