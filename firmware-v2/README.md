# AEROS ESP32 -> HiveMQ Cloud (TLS + HMAC + LWT)

## Requirements
- ESP32 DevKit V1, USB data cable, stable power, Wi-Fi 2.4 GHz
- VS Code + PlatformIO, ESP32 Arduino framework
- Active HiveMQ Cloud MQTT broker endpoint and MQTT user/password

## Set up in PlatformIO
1. Extract the project folder and open it with VS Code.
2. Copy `include/secrets.h.example` to `include/secrets.h`.
3. Change Wi-Fi SSID/password, HiveMQ cluster **hostname** (without protocol or port), MQTT user/password.
4. Generate a different random HMAC secret per physical device: `python -c "import secrets; print(secrets.token_hex(32))"`.
5. Replace HMAC_SECRET in `include/secrets.h` with this 64-character string.
6. Edit `upload_port=COM3` / `monitor_port=COM3` if needed.
7. Build, Upload, Serial Monitor (115200). Use stable power; don't bypass brownout.

## Topics
- `aeros/data` : non-retained sensor JSON at 10-second intervals (QoS 0, default PubSubClient)
- `aeros/AEROS_01/status` : retained ONLINE / OFFLINE (birth QoS 0; LWT QoS 1)

LWT is emitted by the broker when it detects an unexpected MQTT disconnect, not immediately when power disappears.

## TLS
`include/root_ca.h` embeds the public ISRG Root X1 certificate; verify that the certificate chain of your actual HiveMQ Cloud hostname terminates in this root. Source: https://letsencrypt.org/certs/isrgrootx1.pem . A public CA certificate is not a client private key. Never call `setInsecure()` to bypass verification. SNTP time sync must succeed first.

## HMAC anti-spoofing
The signed UTF-8 bytes are precisely:
`device_id|timestamp|nonce|co_ppm|co2_ppm`
Example: `AEROS_01|1792400000|8a41b2c3d4e5f607|35|1200`
- signature: lowercase hex HMAC-SHA256 of that string, keyed by HMAC_SECRET.
- secret is not sent to HiveMQ in the payload; keep it in the ESP32 and the verifying worker only.
- worker must validate timestamp, reject previously used nonces, check HMAC in constant time, and restrict MQTT publish ACLs.
- if a client or secret is compromised, these checks do not guarantee integrity of physical sensor readings.

## Optional worker demo
1. In `worker_example`, copy `.env.example` to `.env`.
2. Put in MQTT broker credentials (prefer separate worker/subscriber credentials) and SAME `HMAC_SECRET` as ESP32.
3. Run `npm install mqtt dotenv` then `node verify.js`.
4. Observe `[ACCEPTED]` for genuine messages and `[REJECTED]` for invalid/replayed ones.

For a production worker with multiple replicas, use shared/persistent nonce storage (Redis/DB with expiration), provisioning/rotation of per-device secrets, and least-privilege MQTT authorization. This is a demo, not a complete device security stack.

## Debugging
- `WiFi` never connects: check 2.4 GHz SSID/password, signal strength, and power.
- `NTP` waiting: ensure internet/DNS/UDP 123 NTP reachable, correct clock needed to verify TLS.
- MQTT `state=-2`: connection/TLS/host/port/DNS possible (inspect certificate chain).
- MQTT `state=4` or `5`: usually credentials/authorization MQTT (look up PubSubClient definitions).
- Browser/cloud UI shows messages but worker rejects: compare exact HMAC_SECRET and canonicalization, timestamp, nonce handling.

## Misc
ESP32 directly connects to HiveMQ Cloud; a laptop remains only the development/serial monitoring machine, not an internet gateway.
