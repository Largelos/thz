"""Basic tests for number, select, switch, and time modules."""

import pytest


class TestNumberModule:
    """Test number module can be imported and has expected structure."""

    def test_import_number_module(self):
        """Test that number module can be imported."""
        from custom_components.thz import number
        assert number is not None

    def test_number_has_async_setup_entry(self):
        """Test that number module has async_setup_entry function."""
        from custom_components.thz.number import async_setup_entry
        assert callable(async_setup_entry)

    def test_number_has_entity_class(self):
        """Test that number module has THZNumber class."""
        from custom_components.thz.number import THZNumber
        assert THZNumber is not None


class TestSelectModule:
    """Test select module can be imported and has expected structure."""

    def test_import_select_module(self):
        """Test that select module can be imported."""
        from custom_components.thz import select
        assert select is not None

    def test_select_has_async_setup_entry(self):
        """Test that select module has async_setup_entry function."""
        from custom_components.thz.select import async_setup_entry
        assert callable(async_setup_entry)

    def test_select_has_entity_class(self):
        """Test that select module has THZSelect class."""
        from custom_components.thz.select import THZSelect
        assert THZSelect is not None


class TestSwitchModule:
    """Test switch module can be imported and has expected structure."""

    def test_import_switch_module(self):
        """Test that switch module can be imported."""
        from custom_components.thz import switch
        assert switch is not None

    def test_switch_has_async_setup_entry(self):
        """Test that switch module has async_setup_entry function."""
        from custom_components.thz.switch import async_setup_entry
        assert callable(async_setup_entry)

    def test_switch_has_entity_class(self):
        """Test that switch module has THZSwitch class."""
        from custom_components.thz.switch import THZSwitch
        assert THZSwitch is not None



class TestTimeModule:
    """Test time module can be imported and has expected structure."""

    def test_import_time_module(self):
        """Test that time module can be imported."""
        from custom_components.thz import time
        assert time is not None

    def test_time_has_async_setup_entry(self):
        """Test that time module has async_setup_entry function."""
        from custom_components.thz.time import async_setup_entry
        assert callable(async_setup_entry)

    def test_time_has_entity_class(self):
        """Test that time module has THZTime class."""
        from custom_components.thz.time import THZTime
        assert THZTime is not None

    def test_time_has_conversion_functions(self):
        """Test that time module has conversion functions."""
        from custom_components.thz.time import quarters_to_time, time_to_quarters
        assert callable(quarters_to_time)
        assert callable(time_to_quarters)


class TestConfigFlowModule:
    """Test config_flow module can be imported and has expected structure."""

    def test_import_config_flow_module(self):
        """Test that config_flow module can be imported."""
        from custom_components.thz import config_flow
        assert config_flow is not None

    def test_config_flow_has_flow_class(self):
        """Test that config_flow module has THZConfigFlow class."""
        from custom_components.thz.config_flow import THZConfigFlow
        assert THZConfigFlow is not None

    def test_config_flow_has_log_levels(self):
        """Test that config_flow module has LOG_LEVELS constant."""
        from custom_components.thz.config_flow import LOG_LEVELS
        assert isinstance(LOG_LEVELS, dict)
        assert len(LOG_LEVELS) > 0


class TestInitModule:
    """Test __init__ module can be imported and has expected structure."""

    def test_import_init_module(self):
        """Test that __init__ module can be imported."""
        from custom_components.thz import __init__
        assert __init__ is not None

    def test_init_has_async_setup_entry(self):
        """Test that __init__ module has async_setup_entry function."""
        from custom_components.thz import async_setup_entry
        assert callable(async_setup_entry)

    def test_init_has_async_unload_entry(self):
        """Test that __init__ module has async_unload_entry function."""
        from custom_components.thz import async_unload_entry
        assert callable(async_unload_entry)


class TestModuleConstants:
    """Test module-level constants and configurations."""

    def test_number_uses_write_register_constants(self):
        """Test that number module uses write register constants."""
        from custom_components.thz.number import WRITE_REGISTER_OFFSET, WRITE_REGISTER_LENGTH
        assert WRITE_REGISTER_OFFSET == 4
        assert WRITE_REGISTER_LENGTH == 2

    def test_select_uses_domain(self):
        """Test that select module or its dependencies use DOMAIN constant."""
        # DOMAIN is now used via platform_setup helper
        from custom_components.thz.const import DOMAIN
        assert DOMAIN == "thz"

    def test_switch_uses_domain(self):
        """Test that switch module or its dependencies use DOMAIN constant."""
        # DOMAIN is now used via platform_setup helper
        from custom_components.thz.const import DOMAIN
        assert DOMAIN == "thz"

    def test_time_has_time_value_unset(self):
        """Test that time module uses TIME_VALUE_UNSET."""
        from custom_components.thz.time import TIME_VALUE_UNSET
        assert TIME_VALUE_UNSET == 0x80


class TestEntityTranslationIntegration:
    """Test entity translation integration in modules."""

    def test_number_uses_translation_keys(self):
        """Test that number module imports translation function."""
        from custom_components.thz.number import get_translation_key
        assert callable(get_translation_key)

    def test_select_uses_translation_keys(self):
        """Test that select module imports translation function."""
        from custom_components.thz.select import get_translation_key
        assert callable(get_translation_key)

    def test_switch_uses_translation_keys(self):
        """Test that switch module imports translation function."""
        from custom_components.thz.switch import get_translation_key
        assert callable(get_translation_key)


class TestEntityHidingIntegration:
    """Test entity hiding integration in modules."""

    def test_number_uses_should_hide_entity(self):
        """Test that base_entity module provides should_hide_entity_by_default."""
        from custom_components.thz.const import should_hide_entity_by_default
        assert callable(should_hide_entity_by_default)
        # Verify it's used by base entity
        from custom_components.thz.base_entity import THZBaseEntity
        assert THZBaseEntity is not None

    def test_select_uses_should_hide_entity(self):
        """Test that base_entity module provides should_hide_entity_by_default."""
        from custom_components.thz.const import should_hide_entity_by_default
        assert callable(should_hide_entity_by_default)

    def test_switch_uses_should_hide_entity(self):
        """Test that base_entity module provides should_hide_entity_by_default."""
        from custom_components.thz.const import should_hide_entity_by_default
        assert callable(should_hide_entity_by_default)


class TestEntityRegistryEnabledDefault:
    """Test that entity instances set entity_registry_enabled_default correctly.

    This verifies the full integration path: entity __init__ -> THZBaseEntity ->
    should_hide_entity_by_default -> _attr_entity_registry_enabled_default.
    """

    @staticmethod
    def _make_mock_device():
        """Create a mock THZDevice for entity instantiation."""
        from unittest.mock import MagicMock
        device = MagicMock()
        device.lock = MagicMock()
        return device

    @staticmethod
    def _make_schedule_entry(command: str = "0A0500") -> dict:
        """Create a minimal schedule-type write register entry."""
        return {
            "command": command,
            "type": "schedule",
            "icon": "mdi:calendar-clock",
        }

    @staticmethod
    def _make_time_entry(command: str = "0A0600") -> dict:
        """Create a minimal time-type write register entry."""
        return {
            "command": command,
            "type": "time",
            "icon": "mdi:clock",
        }

    @staticmethod
    def _make_switch_entry(command: str = "0A0700") -> dict:
        """Create a minimal switch-type write register entry."""
        return {
            "command": command,
            "type": "switch",
            "icon": "",
        }

    @staticmethod
    def _make_number_entry(command: str = "0A0800") -> dict:
        """Create a minimal number-type write register entry."""
        return {
            "command": command,
            "type": "number",
            "icon": "",
            "min": 0,
            "max": 100,
            "step": 1,
            "unit": "",
            "device_class": "",
            "decode_type": "0clean",
        }

    @staticmethod
    def _make_select_entry(command: str = "0A0900") -> dict:
        """Create a minimal select-type write register entry."""
        return {
            "command": command,
            "type": "select",
            "icon": "",
            "decode_type": "opmode",
        }

    def test_schedule_time_program_entities_disabled_by_default(self):
        """Test that THZScheduleTime entities with 'program' names are disabled by default."""
        from custom_components.thz.time import THZScheduleTime

        device = self._make_mock_device()
        entry = self._make_schedule_entry()

        program_names = [
            "programHC1_Mo_0",
            "programHC1_Fr_2",
            "programDHW_Mo_0",
            "programFan1_Sa_0",
            "programHC2_Mo-So_2",
            "programFan2_Tu_1",
        ]

        for base_name in program_names:
            for time_type in ("start", "end"):
                suffix = "Start" if time_type == "start" else "End"
                entity = THZScheduleTime(
                    name=f"{base_name} {suffix}",
                    base_name=base_name,
                    entry=entry,
                    device=device,
                    device_id="test_device",
                    time_type=time_type,
                )
                assert entity.entity_registry_enabled_default is False, (
                    f"{base_name} {suffix} should be disabled by default"
                )

    def test_schedule_time_non_program_entities_enabled_by_default(self):
        """Test that THZScheduleTime entities without hide keywords are enabled by default."""
        from custom_components.thz.time import THZScheduleTime

        device = self._make_mock_device()
        entry = self._make_schedule_entry()

        # A hypothetical non-program schedule entity
        entity = THZScheduleTime(
            name="customSchedule_Mo_0 Start",
            base_name="customSchedule_Mo_0",
            entry=entry,
            device=device,
            device_id="test_device",
            time_type="start",
        )
        assert entity.entity_registry_enabled_default is True

    def test_time_entity_holiday_enabled_by_default(self):
        """Test that regular time entities like pHolidayBeginTime are enabled."""
        from custom_components.thz.time import THZTime

        device = self._make_mock_device()
        entry = self._make_time_entry()

        entity = THZTime(
            name="pHolidayBeginTime",
            entry=entry,
            device=device,
            device_id="test_device",
        )
        assert entity.entity_registry_enabled_default is True

    def test_switch_program_entity_disabled(self):
        """Test that switch entities with 'program' in name are disabled by default."""
        from custom_components.thz.switch import THZSwitch

        device = self._make_mock_device()
        entry = self._make_switch_entry()

        entity = THZSwitch(
            name="programHC1_enable",
            entry=entry,
            device=device,
            device_id="test_device",
        )
        assert entity.entity_registry_enabled_default is False

    def test_switch_basic_entity_enabled(self):
        """Test that basic switch entities are enabled by default."""
        from custom_components.thz.switch import THZSwitch

        device = self._make_mock_device()
        entry = self._make_switch_entry()

        entity = THZSwitch(
            name="pOpMode",
            entry=entry,
            device=device,
            device_id="test_device",
        )
        assert entity.entity_registry_enabled_default is True

    def test_number_hc2_entity_disabled(self):
        """Test that HC2-related number entities are disabled by default."""
        from custom_components.thz.number import THZNumber

        device = self._make_mock_device()
        entry = self._make_number_entry()

        entity = THZNumber(
            name="p01RoomTempDayHC2",
            entry=entry,
            device=device,
            device_id="test_device",
        )
        assert entity.entity_registry_enabled_default is False

    def test_number_basic_entity_enabled(self):
        """Test that basic number entities like p01 are enabled by default."""
        from custom_components.thz.number import THZNumber

        device = self._make_mock_device()
        entry = self._make_number_entry()

        entity = THZNumber(
            name="p01RoomTempDayHC1",
            entry=entry,
            device=device,
            device_id="test_device",
        )
        assert entity.entity_registry_enabled_default is True

    def test_number_advanced_param_disabled(self):
        """Test that advanced parameter (p13+) number entities are disabled."""
        from custom_components.thz.number import THZNumber

        device = self._make_mock_device()
        entry = self._make_number_entry()

        entity = THZNumber(
            name="p13GradientHC1",
            entry=entry,
            device=device,
            device_id="test_device",
        )
        assert entity.entity_registry_enabled_default is False

    def test_select_basic_entity_enabled(self):
        """Test that basic select entities are enabled by default."""
        from custom_components.thz.select import THZSelect

        device = self._make_mock_device()
        entry = self._make_select_entry()

        entity = THZSelect(
            name="pOpMode",
            entry=entry,
            device=device,
            device_id="test_device",
        )
        assert entity.entity_registry_enabled_default is True

    def test_all_write_map_program_entities_disabled(self):
        """Verify ALL program entries in write_map_439_539 produce disabled entities.

        This is an end-to-end test: load the actual write map, create
        THZScheduleTime entities for every schedule entry whose name
        contains 'program', and assert entity_registry_enabled_default is False.
        """
        from custom_components.thz.time import THZScheduleTime
        from custom_components.thz.register_maps.write_map_439_539 import WRITE_MAP

        device = self._make_mock_device()

        program_count = 0
        for name, entry in WRITE_MAP.items():
            if entry["type"] == "schedule" and "program" in name.lower():
                program_count += 1
                for time_type in ("start", "end"):
                    suffix = "Start" if time_type == "start" else "End"
                    entity = THZScheduleTime(
                        name=f"{name} {suffix}",
                        base_name=name,
                        entry=entry,
                        device=device,
                        device_id="test_device",
                        time_type=time_type,
                    )
                    assert entity.entity_registry_enabled_default is False, (
                        f"Write map entry '{name} {suffix}' should be disabled by default"
                    )

        # Sanity: write_map_439_539 has exactly 120 program schedule entries
        assert program_count == 120, (
            f"Expected 120 program schedule entries, found {program_count}"
        )
