// AEROS - uji sensor CO2 MH-Z19C lewat kaki PWM (tanpa UART, tanpa sensor lain, tanpa Wi-Fi)
// Kabel: PWM sensor -> GPIO34 (input saja, belum dipakai di PCB), Vin sensor -> 5V, GND sensor -> GND ESP.
// Datasheet Winsen MH-Z19C v1.2: siklus 1004 ms, Cppm = rentang x (TH - 2 ms) / (T - 4 ms).
// Rentang PWM hanya bisa diubah lewat UART, jadi dicetak dua kemungkinan: 2000 dan 5000 ppm.
// Di udara luar (sekitar 420 ppm) yang benar adalah kolom yang menunjukkan sekitar 400-500.

#include <Arduino.h>

#define FW_VERSI "uji-mhz19c-pwm-1"

const int PIN_PWM = 34;
const unsigned long BATAS_US = 1500000;   // lebih dari satu siklus 1004 ms

void setup() {
  Serial.begin(115200);
  delay(300);
  pinMode(PIN_PWM, INPUT);
  Serial.println();
  Serial.println(F("=== AEROS uji MH-Z19C PWM (" FW_VERSI ") ==="));
  Serial.println(F("# PWM sensor -> GPIO34. Pemanasan sensor 1 menit (datasheet), bacaan awal boleh aneh."));
}

void loop() {
  unsigned long th = pulseIn(PIN_PWM, HIGH, BATAS_US);
  unsigned long tl = pulseIn(PIN_PWM, LOW, BATAS_US);
  if (th == 0 || tl == 0) {
    Serial.print(F("# TIDAK ADA PULSA, kaki diam di "));
    Serial.println(digitalRead(PIN_PWM) ? F("HIGH") : F("LOW"));
    delay(1000);
    return;
  }
  float thMs = th / 1000.0, tMs = (th + tl) / 1000.0;
  float r = (thMs - 2.0) / (tMs - 4.0);
  Serial.print(F("TH=")); Serial.print(thMs, 1);
  Serial.print(F(" ms  T=")); Serial.print(tMs, 1);
  Serial.print(F(" ms  -> rentang 2000: ")); Serial.print((int)(2000 * r));
  Serial.print(F(" ppm | rentang 5000: ")); Serial.print((int)(5000 * r));
  Serial.print(F(" ppm"));
  if (tMs < 950 || tMs > 1060) Serial.print(F("  (siklus di luar 1004 ms +-5%, curigai kabel/sensor)"));
  Serial.println();
}
