# Creality 3D Printer

Consider this at the moment as an alpha version of the integration. It might break your home assistant setup, so be careful with what you are doing.

I didn't find any usable integration for my Creality Ender3 V3 KE printer and decided to just create my own integration. The code is definitely not finished. Creating an integration for Home Assistant proved more complicated than expected. I will try to work towards a more complete implementation, though.

Right now this integration only provides some sensors which can be read from the websocket interface the Ender3 v3 KE provides on port 9999. This is on a untouched Creality Ender3 V3 KE. I don't know if other printers provide the same kind of websocket. I don't own any other Creality Printer, so I am not sure. But it might be worth a try.

I am planing to add "buttons" to this integration to pause and stop the printer. But first I want to make things work properly.

Any suggestions or optimizations, always happy to get feedback.

I have no connection to Creality myself. I am just creating this integration based on my own printer at the moment just for myself.

## Installation

### HACS Installation (Recommended)

The easiest way to install **Creality 3D Printer** is via **[HACS (Home Assistant Community Store)](https://hacs.xyz/)**.

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jerri&repository=creality_3dprinter&category=integration)

#### Steps:

1. Ensure **[HACS](https://hacs.xyz/docs/setup/download)** is installed in Home Assistant.
2. Go to **HACS → Integrations**.
3. Open the three-dot menu and choose **Custom repositories**.
4. Add `https://github.com/jerri/creality_3dprinter` with category **Integration**.
5. Install **Creality 3D Printer** from HACS.
6. Restart Home Assistant.

## Troubleshooting

- When the printer is powered off, the sensors show as `unavailable`. The integration retries every 30 seconds and recovers automatically when the printer is switched on.
- If Home Assistant started while the printer was off, the device model may be empty until the integration is reloaded while the printer is online.
