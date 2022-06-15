import asyncio
import json
from typing import (
    List,
    Union,
)

from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData
from django.conf import settings

from injector import inject


class EventHubService:
    @inject
    def __init__(self, producer: EventHubProducerClient = settings.EVENT_HUB):
        self.producer = producer
        super().__init__()

    async def send_data(self, data: Union[List[dict], dict]):
        async with self.producer:
            if isinstance(data, list):
                event_data_batch = await self.producer.create_batch()
                for row in data:
                    event_data_batch.add(EventData(json.dumps(row)))
                    await self.producer.send_batch(event_data_batch)

            elif isinstance(data, dict):
                await self.producer.send_event(EventData(json.dumps(data)))


loop = asyncio.get_event_loop()
