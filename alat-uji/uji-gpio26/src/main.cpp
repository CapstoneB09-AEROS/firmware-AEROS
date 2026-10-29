// AEROS - uji GPIO26 di meja: paksa HIGH terus-menerus lalu ukur dengan multimeter.
// Ukur antara GPIO26 (atau TBout) dan GND ESP32. Pasang multimeter tanpa beban dulu (lepas 470 ohm / PN2222A).
// Perintah di serial monitor + Enter: h = paksa HIGH, l = paksa LOW (untuk membandingkan angka multimeter).

#include <Arduino.h>
#include <esp_system.h>

#define FW_VERSI "uji-gpio26-1"

const int PIN_UJI = 26;   // sama dengan PIN_JENDELA_BUKA di firmware utama
const int PIN_LED = 2;    // LED bawaan ESP32: ikut menyala agar HIGH terlihat tanpa multimeter

int levelKini = HIGH;

const char* alasanReset() {
  switch (esp_reset_reason()) {
    case ESP_RST_POWERON:  return "POWERON (daya baru menyala)";
    case ESP_RST_EXT:      return "EXT (tombol EN)";
    case ESP_RST_SW:       return "SW (reset dari kode)";
    case ESP_RST_PANIC:    return "PANIC (kode crash)";
    case ESP_RST_INT_WDT:  return "INT_WDT (watchdog)";
    case ESP_RST_TASK_WDT: return "TASK_WDT (watchdog)";
    case ESP_RST_WDT:      return "WDT (watchdog)";
    case ESP_RST_BROWNOUT: return "BROWNOUT (tegangan turun: catu kurang kuat)";
    default:               return "tidak diketahui";
  }
}

void setLevel(int level) {
  levelKini = level;
  digitalWrite(PIN_UJI, level);
  digitalWrite(PIN_LED, level);
}

void setup() {
  Serial.begin(115200);
  delay(500);
  pinMode(PIN_UJI, OUTPUT);
  pinMode(PIN_LED, OUTPUT);
  setLevel(HIGH);   // paksa 3,3 V terus-menerus

  Serial.println();
  Serial.print(F("# AEROS uji GPIO26 ")); Serial.println(F(FW_VERSI));
  Serial.print(F("# Alasan reset: ")); Serial.println(alasanReset());
  Serial.println(F("# GPIO26 diset OUTPUT dan HIGH. Ukur GPIO26-GND: harapan sekitar 3,3 V (3,2-3,35 V)."));
  Serial.println(F("# Ketik h atau l + Enter untuk HIGH atau LOW."));
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == 'h' || c == 'H') { setLevel(HIGH); Serial.println(F("# Perintah: GPIO26 dipaksa HIGH")); }
    if (c == 'l' || c == 'L') { setLevel(LOW);  Serial.println(F("# Perintah: GPIO26 dipaksa LOW")); }
  }

  // digitalRead pada pin OUTPUT hanya membaca register keluaran, bukan tegangan di kabel.
  // Kalau di sini HIGH tetapi multimeter tidak 3,3 V, masalahnya di luar chip (kabel, beban, titik ukur).
  Serial.print(F("[")); Serial.print(millis() / 1000.0, 1); Serial.print(F("s] "));
  Serial.print(F("GPIO26 Status: ")); Serial.print(levelKini == HIGH ? F("HIGH") : F("LOW"));
  Serial.print(F(" | digitalRead=")); Serial.println(digitalRead(PIN_UJI));
  delay(1000);
}
