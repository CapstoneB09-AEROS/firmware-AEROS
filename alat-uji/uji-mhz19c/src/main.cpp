// AEROS - uji sensor CO2 MH-Z19C (tanpa sensor lain, tanpa Wi-Fi)
// Mengirim perintah baca (0xFF 0x01 0x86 ...) dan mencetak 9 byte jawaban mentah.
// Urutan normal sama dengan firmware utama: ESP RX2 = GPIO16 <- TX sensor, ESP TX2 = GPIO17 -> RX sensor.
// Tiap putaran mencoba normal, lalu bersilang (16/17 ditukar), supaya terlihat kalau kabel TX/RX tertukar.

#include <Arduino.h>

#define FW_VERSI "uji-mhz19c-1"

const int PIN_A = 16;
const int PIN_B = 17;
const uint8_t CMD[9] = {0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};

uint8_t cek(const uint8_t* b) {
  uint8_t s = 0;
  for (int i = 1; i < 8; i++) s += b[i];
  return 0xFF - s + 1;
}

void coba(const char* nama, int rx, int tx) {
  Serial2.end();
  Serial2.begin(9600, SERIAL_8N1, rx, tx);
  delay(100);
  while (Serial2.available()) Serial2.read();
  Serial2.write(CMD, 9);
  uint8_t buf[9];
  int n = 0;
  unsigned long t0 = millis();
  while (n < 9 && millis() - t0 < 1000) if (Serial2.available()) buf[n++] = Serial2.read();
  Serial.print(F("# ")); Serial.print(nama); Serial.print(F(" (RX=GPIO")); Serial.print(rx); Serial.print(F(", TX=GPIO")); Serial.print(tx); Serial.print(F("): "));
  if (n == 0) { Serial.println(F("TIDAK ADA JAWABAN")); return; }
  Serial.print(n); Serial.print(F(" byte:"));
  for (int i = 0; i < n; i++) { Serial.print(' '); if (buf[i] < 16) Serial.print('0'); Serial.print(buf[i], HEX); }
  if (n == 9 && buf[0] == 0xFF && buf[1] == 0x86 && buf[8] == cek(buf)) {
    Serial.print(F(" -> VALID, CO2 = ")); Serial.print(buf[2] * 256 + buf[3]); Serial.println(F(" ppm"));
  } else if (n == 9) {
    Serial.println(F(" -> jawaban ada tetapi tidak valid (header atau checksum salah)"));
  } else {
    Serial.println(F(" -> jawaban terpotong"));
  }
}

void setup() {
  Serial.begin(115200);
  delay(300);
  Serial.println();
  Serial.println(F("=== AEROS uji MH-Z19C (" FW_VERSI ") ==="));
  Serial.println(F("# Sensor harus dapat 5 V dan GND bersama ESP. TX sensor -> GPIO16, RX sensor -> GPIO17."));
}

void loop() {
  coba("NORMAL  ", PIN_A, PIN_B);
  coba("BERSILANG", PIN_B, PIN_A);
  Serial.println(F("#"));
  delay(3000);
}
