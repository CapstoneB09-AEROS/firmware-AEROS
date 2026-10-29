#pragma once

#include <Arduino.h>

// Snapshot pembacaan yang sudah dihitung kode sensor asli. Tidak mengubah
// kalibrasi, warm-up, filter, alarm CO, ataupun kontrol LCD milik sketch asli.
struct SensorSnapshot {
  int coPpm = 0;
  int co2Ppm = 0;
  bool coAlarm = false;
  uint8_t co2Level = 0;  // 0=baik/sedang, 1=tinggi, 2=bahaya
  uint32_t sampledAtMs = 0;
  bool simulated = false;   // nilai berasal dari simulasi (q<ppm>), bukan sensor: dikirim dengan demo = true
  uint8_t windowState = 0;  // 0=ATAS_LOW 1=TURUN_HIGH 2=BAWAH_LOW 3=NAIK_HIGH (kolom jendela inti v2.0)
};

// Jalankan kode sensor asli di task terpisah supaya satu siklus 1 detiknya
// tidak terhambat oleh TLS, MQTT, portal, atau upaya reconnect Wi-Fi.
bool sensorBridgeStart();
bool sensorBridgeActive();
bool sensorBridgeGet(SensorSnapshot &out);
// Drain each valid 1 Hz sample, including samples captured while MQTT/TLS blocks.
// Returns false when no new sample is queued.
bool sensorBridgePop(SensorSnapshot &out);
void sensorBridgeSetMuted(bool muted);
bool sensorBridgeBuzzerOn();
