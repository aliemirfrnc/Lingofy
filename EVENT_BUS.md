# Event Bus Architecture

## Abstraction
We employ an Interface-driven Event Bus (`IEventBus`) architecture to decouple cross-domain business actions from side effects like metrics logging or notifications.

## Implementation
Currently, `MemoryEventBus` handles pub/sub synchronously or via async `asyncio.create_task` fire-and-forget. The codebase is prepared for future `FutureKafkaEventBus` or `FutureRedisEventBus` drops.

## Defined Events
A central `constants.py` tracks all permissible events like `USER_LOGIN`, `AI_REQUEST_STARTED`, and avoids magic strings.
