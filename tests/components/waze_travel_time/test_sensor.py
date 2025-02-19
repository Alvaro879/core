"""Test Waze Travel Time sensors."""

from WazeRouteCalculator import WRCError
import pytest

from homeassistant.components.waze_travel_time.const import DOMAIN

from .const import MOCK_CONFIG

from tests.common import MockConfigEntry


@pytest.fixture(name="mock_config")
async def mock_config_fixture(hass, data):
    """Mock a Waze Travel Time config entry."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=data,
        entry_id="test",
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()


@pytest.fixture(name="mock_update_wrcerror")
def mock_update_wrcerror_fixture(mock_wrc):
    """Mock an update to the sensor failed with WRCError."""
    obj = mock_wrc.return_value
    obj.calc_all_routes_info.side_effect = WRCError("test")
    yield


@pytest.fixture(name="mock_update_keyerror")
def mock_update_keyerror_fixture(mock_wrc):
    """Mock an update to the sensor failed with KeyError."""
    obj = mock_wrc.return_value
    obj.calc_all_routes_info.side_effect = KeyError("test")
    yield


@pytest.mark.parametrize(
    "data",
    [MOCK_CONFIG],
)
@pytest.mark.usefixtures("mock_update", "mock_config")
async def test_sensor(hass):
    """Test that sensor works."""
    assert hass.states.get("sensor.waze_travel_time").state == "150"
    assert (
        hass.states.get("sensor.waze_travel_time").attributes["attribution"]
        == "Powered by Waze"
    )
    assert hass.states.get("sensor.waze_travel_time").attributes["duration"] == 150
    assert hass.states.get("sensor.waze_travel_time").attributes["distance"] == 300
    assert hass.states.get("sensor.waze_travel_time").attributes["route"] == "My route"
    assert (
        hass.states.get("sensor.waze_travel_time").attributes["origin"] == "location1"
    )
    assert (
        hass.states.get("sensor.waze_travel_time").attributes["destination"]
        == "location2"
    )
    assert (
        hass.states.get("sensor.waze_travel_time").attributes["unit_of_measurement"]
        == "min"
    )
    assert hass.states.get("sensor.waze_travel_time").attributes["icon"] == "mdi:car"


@pytest.mark.usefixtures("mock_update_wrcerror")
async def test_sensor_failed_wrcerror(hass, caplog):
    """Test that sensor update fails with log message."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert hass.states.get("sensor.waze_travel_time").state == "unknown"
    assert "Error on retrieving data: " in caplog.text


@pytest.mark.usefixtures("mock_update_keyerror")
async def test_sensor_failed_keyerror(hass, caplog):
    """Test that sensor update fails with log message."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert hass.states.get("sensor.waze_travel_time").state == "unknown"
    assert "Error retrieving data from server" in caplog.text
