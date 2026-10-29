// AEROS - uji pemindaian Wi-Fi: daftar jaringan 2,4 GHz yang terlihat ESP32 (modul Wi-Fi hidup atau tidak).
#include <Arduino.h>
#include <WiFi.h>

void setup() {
  Serial.begin(115200);
  delay(500);
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.disconnect(true);
  delay(200);
  Serial.println("\n# AEROS uji-wifi-scan: memindai jaringan 2,4 GHz tiap 8 detik");
}

void loop() {
  int n = WiFi.scanNetworks();
  if (n < 0) { Serial.printf("# SCAN GAGAL (kode %d): modul Wi-Fi bermasalah\n", n); }
  else {
    Serial.printf("# SCAN: %d jaringan terlihat\n", n);
    for (int i = 0; i < n; i++)
      Serial.printf("#  %2d | %-32s | ch %2d | %4d dBm | %s\n", i + 1, WiFi.SSID(i).c_str(), WiFi.channel(i), WiFi.RSSI(i),
                    WiFi.encryptionType(i) == WIFI_AUTH_OPEN ? "terbuka" : "terkunci");
  }
  WiFi.scanDelete();
  delay(8000);
}
