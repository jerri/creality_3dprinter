# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-11-10

### Added

- Websocket receive and close timeouts, so an unresponsive printer cannot block Home Assistant.
- A configuration URL on the printer device that links to its web interface.
- A test suite covering the config flow, setup/unload, availability transitions, and sensor helpers.
- pytest and ruff configuration, plus test and lint requirements.
- A troubleshooting section in the README.
- Descriptions for the host and port fields in the config flow, in English and German.

### Changed

- **Behavior change:** sensors now become `unavailable` when the printer is off. The synthetic `offline` state and placeholder `0 °C` values have been removed. Automations that matched the `offline` state should use an availability trigger or `unavailable` instead.
- Polling runs every 30 seconds normally and every 5 seconds while printing. A failed poll resets the interval to 30 seconds.
- New config entries store the port as an integer. Existing entries with a string port keep working because the client converts it.
- Device registry metadata no longer registers the hostname as a MAC address, serial number, or firmware version.
- Manifest metadata, URLs, translations, and HACS installation instructions were corrected.

### Fixed

- A printer that accepted the websocket connection but never sent data could block the coordinator indefinitely.
- Connection failures were returned as fake status data, so Home Assistant did not mark entities unavailable and recorded misleading values.
- Missing printer fields could raise `KeyError` during state updates.
- `printLeftTime` could raise `TypeError` when the printer reported `null`.
- The config flow now falls back to the configured host when the printer does not report a hostname.
- Adding the same printer twice is now detected by hostname.
- The configuration flow tests were blueprint leftovers and could not run.

### Removed

- The duplicate root `manifest.json`.
- The fake `OFFLINE_STATUS` fallback data.
- The unused `CrealityPrinterHub` helper and `InvalidAuth` exception.
- The unused `invalid_auth` and `offline` translations.

[0.1.0]: https://github.com/jerri/creality_3dprinter/releases/tag/v0.1.0
