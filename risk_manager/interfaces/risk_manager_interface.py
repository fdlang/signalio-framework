from typing import Protocol
from events.events import SignalEvent


class IRiskManager(Protocol):
     
     def asset_order(self, sizing_event: SignalEvent) -> float | None:
          ...