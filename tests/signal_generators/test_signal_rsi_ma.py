import pytest
from unittest.mock import MagicMock
from src.signal_generator.signals.signal_rsi_ma import RsiMaCrossover
from src.events.events import SignalEvent, DataEvent
from src.data_provider.data_provider import DataProvider
from src.signal_generator.properties.signal_generator_properties import RsiMaCrossoverProperties


@pytest.fixture
def mock_properties():
    
    return RsiMaCrossoverProperties(
        rsi=MagicMock(),
        ma_crossover=MagicMock()
    )


@pytest.fixture
def valid_signal_event():
    return SignalEvent(
        event_type="SIGNAL",
        symbol="SOLUSDC",
        signal="BUY",
        target_order="MARKET",
        target_price=150.0,
        ref="MOCK",
        rsi=30.0,
        timeframe="1h"
    )


