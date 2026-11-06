// AEROS - uji pin GPIO18 selalu HIGH (pengganti GPIO25 untuk membedakan pin rusak dan jalur rusak)
// Tujuan: memastikan pin GPIO18 ESP dan jalurnya mengeluarkan 3,3 V terus-menerus, tanpa urutan CO2, bip, atau timer.
// GPIO18 = HIGH sejak boot dan tidak pernah turun. GPIO26 = LOW terus (dua relay tidak boleh menyala bersamaan).
// PERHATIAN: GPIO18 tidak dipakai firmware utama. Jangan sambungkan ke relay yang terhubung ke motor jendela.
// Tidak ada perintah serial; cukup ukur GPIO18 dan GPIO26 terhadap GND. Tekan EN untuk mengulang.

#include <Arduino.h>

#define FW_VERSI "uji-gpio18-1"

const int PIN_NAIK  = 18;   // pin uji pengganti GPIO25 (di firmware utama GPIO25 = PIN_JENDELA_NAIK)
const int PIN_TURUN = 26;   // sama dengan PIN_JENDELA_BUKA di firmware utama
const int PIN_LED   = 2;    // LED bawaan ESP32: menyala selama pin uji HIGH
const unsigned long LAPOR_MS = 5000;

unsigned long laporTerakhirMs = 0;

void setup() {
  Serial.begin(115200);
  delay(300);
  pinMode(PIN_TURUN, OUTPUT);
  digitalWrite(PIN_TURUN, LOW);
  pinMode(PIN_NAIK, OUTPUT);
  digitalWrite(PIN_NAIK, HIGH);
  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, HIGH);
  Serial.println();
  Serial.println(F("=== AEROS uji GPIO18 selalu HIGH (" FW_VERSI ") ==="));
  Serial.println(F("# GPIO18 -> HIGH terus. GPIO26 -> LOW terus. Ukur GPIO18 terhadap GND: harus sekitar 3,3 V."));
  Serial.println(F("# Pin uji ini bukan pin firmware utama; jangan sambungkan ke relay motor."));
}

void loop() {
  if (millis() - laporTerakhirMs >= LAPOR_MS) {
    laporTerakhirMs = millis();
    Serial.print(F("# ["));
    Serial.print(millis() / 1000.0, 1);
    Serial.print(F("s] baca balik: GPIO18="));
    Serial.print(digitalRead(PIN_NAIK) ? F("HIGH") : F("LOW"));
    Serial.print(F(", GPIO26="));
    Serial.println(digitalRead(PIN_TURUN) ? F("HIGH") : F("LOW"));
  }
}
