// AEROS - uji relay jendela di meja (tanpa sensor)
// Yang dibutuhkan: ESP32 + rangkaian GPIO26 -> 470 ohm -> PN2222A -> relay (keputusan/algoritma-firmware.md bagian 5.1).
// HIGH = motor turun selama HIGH, LOW = berhenti. Tidak ada relay naik: jendela tidak bisa ditutup dari firmware.
// Perintah diketik di serial monitor + Enter: o, o<ms>, x, s, n, h.

#include <Arduino.h>
#include <esp_system.h>

#define FW_VERSI "uji-relay-1"

const int PIN_RELAY = 26;   // sama dengan PIN_JENDELA_BUKA di firmware utama
const int PIN_LED   = 2;    // LED bawaan ESP32: ikut menyala agar pulsa terlihat tanpa relay
const int LEVEL_AKTIF = HIGH;
const int LEVEL_DIAM  = LOW;

const unsigned long PULSA_DEFAULT_MS = 2000;   // sama dengan PULSA_BUKA_MS di firmware utama
const unsigned long PULSA_MIN_MS     = 100;
const unsigned long PULSA_MAKS_MS    = 5000;   // batas pengaman, sama dengan PULSA_MAKS_MS di firmware utama

bool aktif = false;
unsigned long mulaiMs = 0, durasiMs = 0;
unsigned long totalMs = 0;   // jumlah waktu motor menyala sejak boot atau sejak 'n'
int jumlahPulsa = 0;
String baris;

void ev(const String& pesan) {
  Serial.print(F("# ["));
  Serial.print(millis() / 1000.0, 1);
  Serial.print(F("s] "));
  Serial.println(pesan);
}

const char* alasanReset() {
  switch (esp_reset_reason()) {
    case ESP_RST_POWERON:  return "POWERON (daya baru menyala)";
    case ESP_RST_EXT:      return "EXT (tombol EN)";
    case ESP_RST_SW:       return "SW (reset dari kode)";
    case ESP_RST_PANIC:    return "PANIC (kode crash)";
    case ESP_RST_INT_WDT:  return "INT_WDT (watchdog)";
    case ESP_RST_TASK_WDT: return "TASK_WDT (watchdog)";
    case ESP_RST_WDT:      return "WDT (watchdog)";
    case ESP_RST_DEEPSLEEP:return "DEEPSLEEP";
    case ESP_RST_BROWNOUT: return "BROWNOUT (tegangan turun: catu kurang kuat)";
    default:               return "tidak diketahui";
  }
}

void setRelay(int level) {
  digitalWrite(PIN_RELAY, level);
  digitalWrite(PIN_LED, level);
}

void mulai(unsigned long ms) {
  if (aktif) { ev("DITOLAK: relay sedang aktif, ketik x untuk berhenti dulu"); return; }
  if (ms < PULSA_MIN_MS) { ev("DITOLAK: minimal " + String(PULSA_MIN_MS) + " ms"); return; }
  if (ms > PULSA_MAKS_MS) { ev("pulsa " + String(ms) + " ms dipotong ke batas pengaman " + String(PULSA_MAKS_MS) + " ms"); ms = PULSA_MAKS_MS; }
  durasiMs = ms;
  mulaiMs = millis();
  aktif = true;
  setRelay(LEVEL_AKTIF);
  ev(String("SINYAL: GPIO") + PIN_RELAY + " -> HIGH selama " + ms + " ms (relay klik, motor TURUN). Ukur sekarang.");
}

void selesai(const char* alasan) {
  setRelay(LEVEL_DIAM);
  unsigned long nyata = millis() - mulaiMs;
  aktif = false;
  totalMs += nyata;
  jumlahPulsa++;
  ev(String("SINYAL: GPIO") + PIN_RELAY + " -> LOW (" + alasan + "), menyala nyata " + nyata + " ms | pulsa ke-" + jumlahPulsa + " | total turun " + totalMs + " ms");
}

void cetakBantuan() {
  Serial.println(F("# Perintah (ketik di monitor + Enter):"));
  Serial.println(F("#   o        relay aktif 2000 ms (motor turun)"));
  Serial.println(F("#   o<ms>    relay aktif sekian ms, contoh o500 atau o3000 (maks 5000)"));
  Serial.println(F("#   x        hentikan sekarang"));
  Serial.println(F("#   s        status dan total waktu turun"));
  Serial.println(F("#   n        nolkan total (setelah jendela dinaikkan manual ke atas)"));
  Serial.println(F("#   h        daftar ini"));
}

void jalankan(String c) {
  c.trim();
  if (c.length() == 0) return;
  ev("PERINTAH: diterima '" + c + "'");
  char k = c.charAt(0);
  if (k == 'o') {
    unsigned long ms = c.length() > 1 ? (unsigned long)c.substring(1).toInt() : PULSA_DEFAULT_MS;
    mulai(ms);
  } else if (k == 'x') {
    if (aktif) selesai("dihentikan x"); else ev("relay sudah diam (LOW)");
  } else if (k == 's') {
    ev(String("STATUS: relay ") + (aktif ? "AKTIF" : "diam") + " | pulsa " + jumlahPulsa + " | total turun " + totalMs + " ms");
  } else if (k == 'n') {
    totalMs = 0; jumlahPulsa = 0;
    ev("total dinolkan");
  } else if (k == 'h') {
    cetakBantuan();
  } else {
    ev("perintah tidak dikenal, ketik h");
  }
}

void setup() {
  pinMode(PIN_RELAY, OUTPUT);   // pertama: pastikan relay diam sebelum hal lain
  pinMode(PIN_LED, OUTPUT);
  setRelay(LEVEL_DIAM);
  Serial.begin(115200);
  delay(300);
  Serial.println();
  Serial.println(F("# AEROS uji relay jendela " FW_VERSI " | tanpa sensor | GPIO26 = relay jendela (HIGH = turun)"));
  ev(String("alasan reset: ") + alasanReset());
  ev("relay diam (LOW). Ketik h + Enter untuk daftar perintah, o + Enter untuk uji 2 detik.");
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { jalankan(baris); baris = ""; }
    else if (baris.length() < 20) baris += ch;
  }
  if (aktif && millis() - mulaiMs >= durasiMs) selesai("waktu habis");
}
