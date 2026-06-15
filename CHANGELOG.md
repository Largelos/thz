# Changelog

All notable changes to the THZ integration are documented here.

---

## [Unreleased]

### New Features

- **Compressor/booster start counters restored** (firmware 4.39 / 5.39): Added back the
  `sHistory` (command `09`) sensors that were present in earlier FHEM-based versions —
  `compressor_starts_heating`, `compressor_starts_cooling`, `compressor_starts_dhw`,
  `booster_starts_dhw`, and `booster_starts_heating`.

### Bug Fixes

- **Switches and selects revert in the UI after a few seconds**: Toggling a switch or
  changing a select option updated the internal state but never pushed it to Home
  Assistant (`async_write_ha_state()` was missing), so the UI fell back to the stale
  value until the next poll. The same issue affected number and time entities. All of
  these now write the new state immediately for instant UI feedback.

- **Passive cooling select value always reads as "Unknown"** (#122): Fixed a byte-order
  encoding bug where the `passive_cooling` select type was decoded as big-endian
  (returning value 256 instead of 1). Now uses the same single-byte encoding as
  `2opmode`, matching the actual device protocol.

- **HA 2026.05 hang / serial reconnect on protocol error** (#118): A `RuntimeError`
  from a stale TCP socket (e.g. ser2net) previously raised immediately without
  attempting to reconnect. The integration now tries to reconnect and retry on
  `RuntimeError` the same way it does for `ConnectionError`.

- **Ventilator speed sensors show Hz instead of %** (#106): All ventilator speed sensors
  (`outputVentilatorSpeed`, `inputVentilatorSpeed`, `mainVentilatorSpeed`) now correctly
  report their unit as `%` to match the FHEM source. The `device_class: frequency` has
  been removed. ⚠️ **Breaking change for users with long-term statistics on these
  sensors** — HA may require manually migrating or clearing the old statistics.

---

## [0.3.0-alpha] – 2026-03-02

> **Alpha release** — tested on firmware 4.39 and 5.39. Please report any regressions
> or unexpected behaviour in the [issue tracker](https://github.com/bigbadoooff/thz/issues).

### New Features

#### Passive Cooling Support (firmware 4.39 / 5.39)
- New **select entity** `p75passiveCooling` for devices running firmware 4.39 or 5.39.
- Supports modes: `off`, `exhaust_air`, `supply_air`, `bypass`, and `sommerkassette`.
- Fully translated in English and German.
- Cooling energy sensor `sCoolHCTotal` (paired-block read) added for firmware 5.39.

#### Diagnostics Support
- The integration now exposes a **Download Diagnostics** option in the Home Assistant UI.
- The diagnostics file includes firmware version, connection type, coordinator status,
  last update timestamps, and redacted hex dumps of all currently-polled register
  blocks.
- Sensitive data (host, device path, serial number) is automatically redacted.

#### COP (Coefficient of Performance) Sensors
- Automatically created for devices with energy-monitoring support (firmware ≥ 4.39).
- Sensors cover **daily**, **monthly**, **yearly**, and **lifetime** COP for DHW,
  heating circuit, and combined total.
- Monthly and yearly sensors reset at the start of each new period and persist
  across Home Assistant restarts.

#### Energy Sensors via Paired-Block Reads (firmware 4.39 / 5.39)
- Heat-output and electricity-consumption sensors are now read using a two-command
  ("paired block") protocol that combines a high-word and a low-word to produce
  accurate 32-bit energy values in Wh.
- Sensors: `sHeatDHWDay`, `sHeatDHWTotal`, `sHeatHCDay`, `sHeatHCTotal`,
  `sElectrDHWDay`, `sElectrDHWTotal`, `sElectrHCDay`, `sElectrHCTotal`,
  `sCoolHCTotal` (5.39 only).

#### `thz.read_raw_register` Service
- New developer/debug service to read any raw register block directly from the
  heat pump.
- Returns results as a service response (usable in automations), a persistent
  notification, and an INFO-level log entry.
- See [docs/read-raw-register-service.md](docs/read-raw-register-service.md) for
  full documentation.

#### Per-Block Configurable Polling Intervals
- Each register block now has its own poll interval, configurable in the
  **Reconfigure** dialog.
- Fast-changing blocks (e.g., temperatures) can be polled frequently while
  slow-changing settings blocks can be polled less often.
- Default interval: 600 seconds.

#### Sensor Metadata in Register Maps
- Register map tuples now support an optional 6th element (a metadata dict)
  providing `unit`, `device_class`, `state_class`, `icon`, and `translation_key`
  inline.
- Module-level helpers (`_TEMP`, `_POWER`, `_ENERGY_TOTAL`, etc.) reduce
  repetition across firmware maps.

#### Smart Entity Visibility
- Advanced, rarely-needed entities are hidden by default to reduce initial clutter:
  - HC2 (heating circuit 2) entities
  - Time programme entities (`programDHW_*`, `programHC1_*`, `programHC2_*`)
  - Technical parameters p13 and above (gradient, hysteresis, integral, etc.)
- Hidden entities remain visible in the entity registry and can be re-enabled
  individually via **Settings → Devices & Services**.
- A one-time migration automatically hides these entities for users upgrading
  from older versions.

### Changes

- **Manifest version bumped to `0.3.0`.**
- `sensor_meta.py` is now a backward-compatibility stub. All sensor metadata lives
  inline in the register-map tuples. Do **not** add new entries to `sensor_meta.py`.
- `decode_value()` in `sensor.py` is now a thin wrapper around the canonical
  `decode_raw_value()` from `value_codec.py`. The `cop_sensor.py` module imports
  `decode_raw_value` directly.
- Write entities no longer use Home Assistant's class-level `SCAN_INTERVAL`
  polling. Instead they register a `async_track_time_interval` timer in
  `async_added_to_hass` (default 600 s) and cancel it in
  `async_will_remove_from_hass`.
- Updated firmware detection: `214j` variant is now recognised separately from
  `214`.
- Register map manager uses a data-driven `FIRMWARE_MAPS` dict; unknown firmware
  versions fall back gracefully to the `default` (5.39-like) configuration.

### Breaking Changes

> If you are upgrading from 0.2.x, read these carefully.

1. **Entity unique_id format has changed.**  
   Sensor unique IDs now follow the pattern `thz_{block}_{offset}_{name}`.  
   Write-entity unique IDs follow `thz_set_{command}_{name}`.  
   Upgrading will re-create any sensor or write entity whose name was previously
   stored under a different unique ID. You may need to update any automations or
   dashboards that reference those entities.

2. **`sensor_meta.py` is a stub.**  
   Any third-party extension that imported `SENSOR_META` from `sensor_meta` to
   add custom metadata must be updated to use the 6th-element dict in the
   register-map tuple instead.

3. **Calendar platform has been removed.**  
   Any existing `calendar.thz_*` entities from previous versions will no
   longer be available. Update or remove any automations, scripts, or
   dashboards that reference these calendar entities.

### Bug Fixes

- Fixed nibble-offset decoding for `length=1` registers at even offsets (FHEM
  compatibility): bit numbers are now shifted by +4 for the HIGH nibble.
- Fixed paired-block energy reads where the high word was incorrectly combined
  as `low*1000 + high` instead of `high*1000 + low`.
- Improved connection-timeout handling: TCP socket is now closed and re-opened
  on timeout rather than accumulating stale data.

---

## [0.2.2] – prior release

See the [0.2.x README note](README.md) for a summary of changes introduced in
the 0.2 series.
