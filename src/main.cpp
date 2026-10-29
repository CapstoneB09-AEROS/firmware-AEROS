// VERSI 1.4 (29 Okt 2026): MVP CO2 saja (dokumentasi/keputusan/mvp-co2.md): MiCS dan ADS1115 diabaikan (CO_AKTIF = false);
//   ambang CO2 mode pengembangan (700/800/<700); pulsa buka jendela 10 detik; batas total waktu turun (ketik n setelah jendela
//   dinaikkan manual); perintah q<ppm> = simulasi CO2 (uji tanpa sensor).
// VERSI 1.3 (28 Okt 2026): v1.2 + serial ringkas ala v0 (bawaan), banner pendek, perintah i dan h yang lebih jelas.
// VERSI 1.2 (28 Okt 2026): v1.1 + penyesuaian ke skematik relay jendela (GPIO26 -> 470 ohm -> PN2222A -> relay 85/86; kontak 30/87 = motor ARAH TURUN saja): sistem sensor dan keluaran sesuai pseudocode (dokumentasi/keputusan/algoritma-firmware.md).
// Komunikasi (Wi-Fi, MQTT) BELUM ada di versi ini.
// Isi: SMA 6 pada Rs, validasi data, pemanasan 180 detik, aturan CO (uji arah) dan CO2, 5 status,
//      pola bunyi, LCD 16x2, sinyal jendela lewat TBout, serial CSV, mode pengembangan.
// ppm CO adalah ESTIMASI dari kurva datasheet dan R0 hasil ukur sensor ini (belum dikalibrasi gas referensi,
// belum dikompensasi suhu/RH). ppm CO2 dibaca langsung dari MH-Z19C lewat UART.
//
// WIRING (skematik 28 Okt 2026, dokumentasi/keputusan/diagram/skematik-pin-2026-10-28.png)
//   MiCS   : 5V, GND, AO -> ADS1115 A0
//   ADS1115: VDD -> 3V3, GND, SCL -> GPIO22, SDA -> GPIO21, ADDR -> GND (0x48), A0 <- AO MiCS
//   MH-Z19C: Vin -> 5V, GND, TX sensor -> GPIO16 (RX2), RX sensor -> GPIO17 (TX2)
//   LCD I2C: GND, 5V, SDA -> GPIO21, SCL -> GPIO22
//   Buzzer : GPIO27 -> buzzer -> GND
//   TBout  : GPIO26 -> TBout -> GND (sinyal jendela)
//   Catu   : TBin -> buck DC-DC -> 5V
//
// PERINTAH Serial Monitor (115200 baud, "New Line"):
//   r = ukur R0 MiCS (udara bersih, 120 detik)   d = R0 default
//   s = "Saya Tahu" (matikan bunyi)              o / c = uji sinyal jendela buka / tutup (manual)
//   p<angka> = simulasi CO dalam ppm, misalnya p40 (p0 = mati)   h = bantuan
//
// Library: Adafruit ADS1X15 (+ Adafruit BusIO), LiquidCrystal I2C (Frank de Brabander).
// Board: ESP32 Dev Module.

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include <Preferences.h>
#include <LiquidCrystal_I2C.h>
#include <math.h>

#define FW_VERSI "v1.4"

// =====================================================================
// MODE PENGEMBANGAN
// true  = ambang CO2 diturunkan dan jeda diperpendek supaya buka-tutup jendela bisa dicoba di ruang terbuka
//         (CO2 luar sekitar 500-650 ppm; napas ke sensor menaikkannya).
// false = nilai rancangan (pseudocode bagian 2.1).
// =====================================================================
const bool MODE_PENGEMBANGAN = true;

// MVP expo: hanya jalur CO2. false = MiCS dan ADS1115 tidak dibaca; tidak ada aturan, status, atau simulasi CO.
// (komponennya tetap ada di PCB; true mengembalikan perilaku v1.3)
const bool CO_AKTIF = false;

// ---------------- Pin ----------------
const int PIN_SDA    = 21;
const int PIN_SCL    = 22;
const int PIN_BUZZER = 27;
const int PIN_CO2_RX = 16;   // ESP32 RX2 <- TX sensor MH-Z19C
const int PIN_CO2_TX = 17;   // ESP32 TX2 -> RX sensor MH-Z19C

// ---------------- Sinyal jendela (TBout) ----------------
// Skematik relay (28 Okt 2026): GPIO26 (TBout) -> 470 ohm -> basis PN2222A; kolektor ke kumparan relay (pin 86).
//   GPIO26 HIGH = relay menarik = kontak 30-87 menyambung ke kabel motor ARAH TURUN (jendela turun/buka)
//                 SELAMA pin HIGH. Jadi lama HIGH = lama motor turun = besar bukaan. Bukan pemicu satu kali.
//   GPIO26 LOW  = relay lepas = motor berhenti (basis ditarik 10 kohm ke GND, aman saat boot atau reset).
// TIDAK ADA relay untuk arah NAIK (tutup) di skematik. Jadi tutup jendela belum bisa dilakukan oleh firmware:
//   PIN_JENDELA_TUTUP = -1 (nonaktif). Firmware hanya mencatat "tutup manual diperlukan" (LCD menampilkan M).
//   Bila hardware menambah relay naik: isi PIN_JENDELA_TUTUP, atur PULSA_TUTUP_MS, dan JANGAN pernah
//   menyalakan kedua relay bersamaan (perlu jeda antar arah).
const int PIN_JENDELA_BUKA  = 26;
const int PIN_JENDELA_TUTUP = -1;
const int LEVEL_AKTIF = HIGH;
const int LEVEL_DIAM  = LOW;
const unsigned long PULSA_BUKA_MS  = 10000;  // lama motor TURUN (bukaan), permintaan pengguna 29 Okt; waktu tempuh penuh belum diukur
const unsigned long PULSA_TUTUP_MS = 2000;   // dipakai hanya bila ada relay naik
const unsigned long PULSA_MAKS_MS  = 10000;  // batas keselamatan: relay tidak pernah menyala lebih lama dari ini dalam satu pulsa
// Batas TOTAL waktu relay turun sejak menyala (atau sejak perintah n). Firmware tidak tahu posisi jendela dan tidak bisa menutupnya,
// jadi pulsa berikutnya hanya memperpanjang motor tertahan di dasar. Setelah batas ini, pulsa ditolak sampai jendela dinaikkan
// manual dan pengguna mengetik n.
const unsigned long JENDELA_TOTAL_MAKS_MS = 10000;

// ---------------- LCD I2C ----------------
const uint8_t LCD_ADDR = 0x27;
const int LCD_COLS = 16;
const int LCD_ROWS = 2;
LiquidCrystal_I2C lcd(LCD_ADDR, LCD_COLS, LCD_ROWS);

// ---------------- Rangkaian MiCS ----------------
const float VCC    = 4.64;       // tetap sampai buck terpasang, lalu ubah sekali dan ukur R0 ulang
const float RL_OHM = 9970.0;
const float R0_DEFAULT_OHM = 1730000.0;   // satu nilai tetap, berlabel estimasi (keputusan B1)

// Kurva CO datasheet (25C, 50% RH): Rs/R0 = A * ppm^(-BETA); hasil digitalisasi piksel (keputusan 27 Okt)
const float A_COEF = 3.46;
const float BETA   = 0.840;

// ---------------- Parameter rancangan (pseudocode 2.1) ----------------
const unsigned long INTERVAL_SIKLUS_MS = 1000;
const int   PANJANG_FILTER_CO     = 6;
const int   MAKS_TIDAK_VALID      = 3;      // lebih dari ini berturut-turut: kosongkan buffer filter (B13)
const int   N_SAMPEL_ADS          = 16;

const float CO_AMBANG_WASPADA     = 35.0;   // ppm estimasi
const int   CO_KONFIRMASI_S       = 30;
const float CO_AMBANG_BAHAYA      = 87.0;
const int   CO_LAMA_UJI_ARAH_S    = 30;
const float CO_KRITERIA_NAIK      = 0.25;   // Rs turun lebih dari 25% = CO dari luar
const float CO_KRITERIA_TURUN     = 0.05;   // Rs naik lebih dari 5% = CO turun (sumber dalam); di antaranya = tidak jelas -> luar
const float CO_BATAS_SELESAI      = 30.0;
const int   CO_WAKTU_PEMULIHAN_S  = 60;

const unsigned long PEMANASAN_CO_S  = 180;
const unsigned long PEMANASAN_CO2_S = 180;
const int   CO2_BACAAN_KONFIRMASI = 3;
const bool  DISABLE_ABC = true;             // kalibrasi otomatis MH-Z19C dimatikan (B16, perlu konfirmasi tim)

// Nilai rancangan dan nilai pengembangan
const int   CO2_PERINGATAN_RANCANGAN = 2500, CO2_PERINGATAN_DEV = 700;
const int   CO2_TINDAKAN_RANCANGAN   = 4000, CO2_TINDAKAN_DEV   = 800;
const int   CO2_SELESAI_RANCANGAN    = 2500, CO2_SELESAI_DEV    = 700;   // tutup bila di bawah ini
const int   CO2_PEMULIHAN_S          = 10;
const int   JENDELA_BUKA_MIN_S       = 20;
const int   JENDELA_BUKA_MAKS_RANCANGAN = 180, JENDELA_BUKA_MAKS_DEV = 120;
const unsigned long JEDA_JENDELA_RANCANGAN_S = 300, JEDA_JENDELA_DEV_S = 30;

int CO2_AMBANG_PERINGATAN, CO2_AMBANG_TINDAKAN, CO2_BATAS_SELESAI, JENDELA_BUKA_MAKS_S;
unsigned long JEDA_MINIMUM_JENDELA_S;

// Bunyi (pseudocode 2.10)
const int BUNYI_ULANG_CO_S      = 60;
const int BUNYI_ULANG_CO_MAKS_S = 300;

// Kalibrasi R0
const unsigned long CAL_SECONDS = 120;
const float CAL_MAX_SPREAD_PCT  = 10.0;

// =====================================================================
// Keadaan
// =====================================================================
Adafruit_ADS1115 ads;
Preferences prefs;
adsGain_t gains[3] = { GAIN_FOUR, GAIN_TWO, GAIN_ONE };
const float fsV[3] = { 1.024, 2.048, 4.096 };
int  gainIdx = 0;
bool adsAda = false;
unsigned long adsCobaLagiMs = 0;

float r0Ohm = R0_DEFAULT_OHM;
bool  r0Tersimpan = false;          // true bila R0 pernah diukur dan tersimpan di memori ESP32 (NVS)
float bufRs[PANJANG_FILTER_CO];
int   nBuf = 0, idxBuf = 0, tidakValidBeruntun = 0;

enum FaseCO  { CO_TIDAK_AKTIF, CO_UJI_ARAH, CO_SUMBER_DALAM, CO_SUMBER_LUAR };
enum FaseCO2 { CO2_NORMAL, CO2_PERINGATAN, CO2_TINDAKAN };
enum Level   { LV_NORMAL = 0, LV_WASPADA = 1, LV_BAHAYA = 2 };

FaseCO  faseCO  = CO_TIDAK_AKTIF;
FaseCO2 faseCO2 = CO2_NORMAL;
int   levelCO = LV_NORMAL, levelCO2 = LV_NORMAL;
float rsAwalUji = 0;
int   konfirmasiCO = 0, pemulihanCO = 0, waktuUji = 0;
int   atasPeringatan = 0, atasTindakan = 0, pemulihanCO2 = 0, lamaBuka = 0;
bool  co2TidakTurun = false;

bool  jendelaTerbuka = false;
bool  tutupManual = false;           // firmware meminta jendela ditutup manual (belum ada relay naik)
unsigned long tutupManualMs = 0;
unsigned long gerakTerakhirMs = 0;
bool  pernahGerak = false;
unsigned long pulsaSelesaiMs = 0;
int   pulsaPin = -1;

// Bunyi (tidak memblokir)
struct Seg { uint16_t on, off; };
const Seg POLA_WASPADA[] = { {300, 300}, {300, 300}, {300, 300} };
const Seg POLA_BAHAYA[]  = { {3000, 0} };
const Seg* polaAktif = nullptr;
int   nPola = 0, iPola = 0;
bool  segOn = false;
unsigned long segMulaiMs = 0;
bool  bunyiDiam = false;                // "Saya Tahu"
unsigned long coBunyiMulaiMs = 0, coBunyiTerakhirMs = 0;
const char* namaBunyi = "OFF";

// Kalibrasi
bool calActive = false;
unsigned long calStartMs = 0;
double calSum = 0;
long   calN = 0;
float  calMin = 1e12, calMax = 0;

// Simulasi CO (pengujian aturan tanpa gas)
float simCO = 0;   // 0 = mati
int   simCO2 = 0;  // simulasi CO2 (perintah q<ppm>), 0 = mati; melewati pemanasan agar uji meja cepat
unsigned long totalTurunMs = 0;   // jumlah lama pulsa relay turun yang sudah diberikan (batas: JENDELA_TOTAL_MAKS_MS)

String cmdBuf;
int  formatMode = 0;             // 0 = ringkas (seperti v0), 1 = tabel lengkap, 2 = CSV lengkap (perintah 'f' berganti urut)
int  barisSejakKepala = 0;

// =====================================================================
// Log kejadian ke serial (baris berawalan "# [detik] TAG: isi")
// =====================================================================
void cetakDetail();
float gPpm = 0, gRsHalus = NAN;
int   gCo2 = 0;

void ev(const char* tag, const String &s) {
  Serial.print(F("# ["));
  Serial.print(millis() / 1000UL);
  Serial.print(F("s] "));
  Serial.print(tag);
  Serial.print(F(": "));
  Serial.println(s);
}

String nilaiSaatIni() {
  return String("CO=") + String(gPpm, 0) + " ppm, CO2=" + String(gCo2) + " ppm";
}

// =====================================================================
// Pembantu: bunyi dan jendela
// =====================================================================
void mulaiBunyi(int level, bool dariCO) {
  if (level == LV_NORMAL) return;
  polaAktif = (level == LV_BAHAYA) ? POLA_BAHAYA : POLA_WASPADA;
  nPola = (level == LV_BAHAYA) ? 1 : 3;
  iPola = 0; segOn = true; segMulaiMs = millis();
  digitalWrite(PIN_BUZZER, HIGH);
  namaBunyi = (level == LV_BAHAYA) ? (dariCO ? "CO_BAHAYA" : "CO2_BAHAYA") : (dariCO ? "CO_WASPADA" : "CO2_WASPADA");
  ev("BUNYI", String(namaBunyi) + " mulai (" + (level == LV_BAHAYA ? "1 bip panjang 3 detik" : "3 bip pendek") + ")");
}

void hentikanBunyi() {
  if (polaAktif) ev("BUNYI", String(namaBunyi) + " dihentikan");
  polaAktif = nullptr; segOn = false;
  digitalWrite(PIN_BUZZER, LOW);
  namaBunyi = "OFF";
}

void servisBunyi() {
  if (!polaAktif) return;
  unsigned long now = millis();
  const Seg &s = polaAktif[iPola];
  if (segOn && now - segMulaiMs >= s.on) {
    digitalWrite(PIN_BUZZER, LOW); segOn = false; segMulaiMs = now;
  } else if (!segOn && now - segMulaiMs >= s.off) {
    iPola++;
    if (iPola >= nPola) {
      ev("BUNYI", String(namaBunyi) + " pola selesai");
      polaAktif = nullptr; segOn = false; digitalWrite(PIN_BUZZER, LOW); namaBunyi = "OFF";
      return;
    }
    digitalWrite(PIN_BUZZER, HIGH); segOn = true; segMulaiMs = now;
  }
}

// Mengembalikan false bila pulsa ditolak (batas total waktu turun tercapai); tidak ada sinyal yang dikirim.
bool pulsaJendela(int pin, unsigned long ms) {
  if (pin < 0) return false;
  if (ms > PULSA_MAKS_MS) { ev("SINYAL", String("lama ") + ms + " ms melebihi batas keselamatan, dipotong ke " + PULSA_MAKS_MS + " ms"); ms = PULSA_MAKS_MS; }
  if (pin == PIN_JENDELA_BUKA) {
    if (totalTurunMs + ms > JENDELA_TOTAL_MAKS_MS) {
      static unsigned long tolakTerakhirMs = 0;
      if (tolakTerakhirMs == 0 || millis() - tolakTerakhirMs >= 10000UL) {
        tolakTerakhirMs = millis();
        ev("SINYAL", String("DITOLAK: total waktu turun ") + totalTurunMs + " ms + " + ms + " ms melebihi batas " + JENDELA_TOTAL_MAKS_MS + " ms. Naikkan jendela manual, lalu ketik n");
      }
      return false;
    }
    totalTurunMs += ms;
  }
  if (pulsaPin >= 0) digitalWrite(pulsaPin, LEVEL_DIAM);   // pulsa sebelumnya dihentikan
  digitalWrite(pin, LEVEL_AKTIF);
  pulsaPin = pin;
  pulsaSelesaiMs = millis() + ms;
  ev("SINYAL", String("GPIO") + pin + " -> " + (LEVEL_AKTIF == HIGH ? "HIGH" : "LOW") + " selama " + ms + " ms (" + (pin == PIN_JENDELA_BUKA ? "motor TURUN (buka)" : "motor NAIK (tutup)") + ") | total turun " + totalTurunMs + "/" + JENDELA_TOTAL_MAKS_MS + " ms");
  return true;
}

void servisJendela() {
  if (pulsaPin >= 0 && (long)(millis() - pulsaSelesaiMs) >= 0) {
    digitalWrite(pulsaPin, LEVEL_DIAM);
    ev("SINYAL", String("GPIO") + pulsaPin + " -> " + (LEVEL_DIAM == HIGH ? "HIGH" : "LOW") + " (pulsa selesai)");
    pulsaPin = -1;
  }
}

unsigned long sisaJedaS() {
  if (!pernahGerak) return 0;
  unsigned long lewat = (millis() - gerakTerakhirMs) / 1000UL;
  return lewat >= JEDA_MINIMUM_JENDELA_S ? 0 : JEDA_MINIMUM_JENDELA_S - lewat;
}

bool bolehBukaLagi() {
  if (!pernahGerak) return true;
  return millis() - gerakTerakhirMs >= JEDA_MINIMUM_JENDELA_S * 1000UL;
}

// abaikanJeda = true untuk CO (keselamatan didahulukan)
void bukaJendela(bool abaikanJeda, const char* alasan) {
  if (jendelaTerbuka) return;
  if (!abaikanJeda && !bolehBukaLagi()) {
    static unsigned long pesanTerakhir = 0;
    if (millis() - pesanTerakhir >= 10000UL) {
      pesanTerakhir = millis();
      ev("JENDELA", String("buka DITUNDA (") + alasan + "): jeda minimum, sisa " + sisaJedaS() + " detik");
    }
    return;
  }
  if (!pulsaJendela(PIN_JENDELA_BUKA, PULSA_BUKA_MS)) return;   // ditolak: keadaan jendela tidak diubah
  jendelaTerbuka = true; lamaBuka = 0; tutupManual = false;
  gerakTerakhirMs = millis(); pernahGerak = true;
  ev("JENDELA", String("BUKA (motor turun ") + PULSA_BUKA_MS + " ms), alasan: " + alasan + (abaikanJeda ? " (jeda diabaikan)" : "") + " | " + nilaiSaatIni());
}

void tutupJendela(const char* alasan) {
  if (!jendelaTerbuka) return;
  if (PIN_JENDELA_TUTUP < 0) {
    jendelaTerbuka = false;
    tutupManual = true; tutupManualMs = millis();
    gerakTerakhirMs = millis(); pernahGerak = true;
    ev("JENDELA", String("TUTUP diminta, alasan: ") + alasan + " | TIDAK ADA keluaran penutup (relay hanya arah turun): TUTUP JENDELA MANUAL | terbuka " + lamaBuka + " detik | " + nilaiSaatIni());
    return;
  }
  pulsaJendela(PIN_JENDELA_TUTUP, PULSA_TUTUP_MS);
  jendelaTerbuka = false;
  gerakTerakhirMs = millis(); pernahGerak = true;
  ev("JENDELA", String("TUTUP, alasan: ") + alasan + " | terbuka " + lamaBuka + " detik | " + nilaiSaatIni());
}

void servis() { servisBunyi(); servisJendela(); }

// =====================================================================
// Sensor
// =====================================================================
bool readCO2(int &ppm) {
  static const uint8_t cmd[9] = {0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};
  while (Serial2.available()) Serial2.read();
  Serial2.write(cmd, 9);
  uint8_t buf[9];
  int n = 0;
  unsigned long t0 = millis();
  while (n < 9 && millis() - t0 < 500) {
    if (Serial2.available()) buf[n++] = Serial2.read();
    else servis();
  }
  if (n < 9 || buf[0] != 0xFF || buf[1] != 0x86) return false;
  uint8_t cs = 0;
  for (int i = 1; i < 8; i++) cs += buf[i];
  cs = 0xFF - cs + 1;
  if (cs != buf[8]) return false;
  ppm = buf[2] * 256 + buf[3];
  return true;
}

void setAbc(bool on) {
  uint8_t cmd[9] = {0xFF, 0x01, 0x79, on ? (uint8_t)0xA0 : (uint8_t)0x00, 0, 0, 0, 0, 0};
  uint8_t cs = 0;
  for (int i = 1; i < 8; i++) cs += cmd[i];
  cmd[8] = 0xFF - cs + 1;
  Serial2.write(cmd, 9);
}

float bacaAds(bool &sat) {
  long sum = 0;
  for (int i = 0; i < N_SAMPEL_ADS; i++) { sum += ads.readADC_SingleEnded(0); servis(); }
  float avg = sum / (float)N_SAMPEL_ADS;
  sat = (fabs(avg) >= 32000.0);
  return ads.computeVolts((int16_t)avg);
}

// Baca tegangan MiCS; bila saturasi: naikkan gain dan BACA ULANG saat itu juga (pseudocode langkah 1)
float bacaMics(bool &valid) {
  bool sat;
  float v = bacaAds(sat);
  while ((sat || fabs(v) > 0.92 * fsV[gainIdx]) && gainIdx < 2) {
    gainIdx++;
    ads.setGain(gains[gainIdx]);
    ev("ADS1115", String("gain dinaikkan (rentang ") + String(fsV[gainIdx], 3) + " V), dibaca ulang");
    v = bacaAds(sat);
  }
  if (gainIdx > 0 && fabs(v) < 0.40 * fsV[gainIdx - 1]) {   // turunkan gain untuk siklus berikutnya
    gainIdx--;
    ads.setGain(gains[gainIdx]);
    ev("ADS1115", String("gain diturunkan (rentang ") + String(fsV[gainIdx], 3) + " V)");
  }
  valid = !sat && v >= 0.0005 && v <= VCC - 0.001;
  return v;
}

// =====================================================================
// Kalibrasi R0 dan perintah serial
// =====================================================================
void kosongkanFilter() { nBuf = 0; idxBuf = 0; }

void startCalibration() {
  calActive = true; calStartMs = millis();
  calSum = 0; calN = 0; calMin = 1e12; calMax = 0;
  ev("R0", "kalibrasi dimulai: jaga sensor MiCS di udara bersih selama 120 detik (alarm CO ditahan)");
}

void finishCalibration() {
  calActive = false;
  if (calN < 60) { ev("R0", "kalibrasi gagal: data terlalu sedikit (" + String(calN) + " titik)"); return; }
  float mean = calSum / calN;
  float spread = (calMax - calMin) / mean * 100.0;
  ev("R0", "kalibrasi selesai: Rs rata-rata " + String(mean / 1000.0, 1) + " kOhm, simpangan max-min " + String(spread, 1) + " % dari " + String(calN) + " titik");
  if (spread > CAL_MAX_SPREAD_PCT) {
    ev("R0", "DITOLAK: Rs masih bergerak atau terganggu; R0 tidak diubah (" + String(r0Ohm / 1000.0, 1) + " kOhm)");
    return;
  }
  r0Ohm = mean;
  prefs.putFloat("r0", r0Ohm);
  r0Tersimpan = true;
  ev("R0", "baru disimpan di memori ESP32: " + String(r0Ohm / 1000.0, 1) + " kOhm (tetap ada setelah dimatikan atau upload ulang)");
}

void cetakBantuan() {
  Serial.println(F("# ===== PERINTAH: ketik hurufnya di jendela serial monitor, lalu tekan Enter ====="));
  if (CO_AKTIF) {
    Serial.println(F("#  r    ukur R0 sensor CO (udara bersih, 2 menit; jangan bernapas dekat sensor)"));
    Serial.println(F("#  p40  pura-pura CO = 40 ppm untuk uji logika CO (p0 = matikan)"));
  } else Serial.println(F("#  (perintah CO r, p, d tidak aktif: versi MVP hanya CO2)"));
  Serial.print(F("#  o    uji relay jendela: motor TURUN ")); Serial.print(PULSA_BUKA_MS / 1000); Serial.println(F(" detik (dihitung ke batas total)"));
  Serial.println(F("#  x    hentikan relay sekarang"));
  Serial.println(F("#  n    nolkan batas total setelah jendela dinaikkan manual (tanpa ini pulsa berikutnya ditolak)"));
  Serial.println(F("#  q900 pura-pura CO2 = 900 ppm untuk uji tanpa sensor (q0 = matikan)"));
  Serial.println(F("#  s    \"Saya Tahu\": matikan bunyi"));
  Serial.println(F("#  f    ganti tampilan data: ringkas / tabel lengkap / CSV lengkap"));
  Serial.println(F("#  i    tampilkan semua parameter    h  bantuan ini    d  R0 kembali ke default    c  (penutup jendela belum ada)"));
}

void jalankanPerintah(const String &c) {
  if (c.length() == 0) return;
  char k = tolower(c[0]);
  ev("PERINTAH", String("diterima: '") + c + "'");
  if ((k == 'r' || k == 'd' || k == 'p') && !CO_AKTIF) ev("PERINTAH", "perintah CO tidak aktif di versi MVP (CO_AKTIF = false)");
  else if (k == 'r') startCalibration();
  else if (k == 'd') { r0Ohm = R0_DEFAULT_OHM; prefs.putFloat("r0", r0Ohm); ev("R0", "dikembalikan ke default " + String(r0Ohm / 1000.0, 1) + " kOhm"); }
  else if (k == 's') { bunyiDiam = true; hentikanBunyi(); ev("SAYA TAHU", "bunyi dimatikan; alarm dan jendela tetap berjalan sesuai aturan"); }
  else if (k == 'o') {
    if (pulsaJendela(PIN_JENDELA_BUKA, PULSA_BUKA_MS)) { jendelaTerbuka = true; lamaBuka = 0; tutupManual = false; ev("UJI MANUAL", "sinyal buka dikirim (motor turun " + String(PULSA_BUKA_MS) + " ms)"); }
  }
  else if (k == 'x') {
    if (pulsaPin >= 0) { digitalWrite(pulsaPin, LEVEL_DIAM); ev("SINYAL", String("GPIO") + pulsaPin + " -> LOW (dihentikan perintah x)"); pulsaPin = -1; }
    else ev("SINYAL", "relay sudah diam (LOW)");
  }
  else if (k == 'n') { totalTurunMs = 0; jendelaTerbuka = false; tutupManual = false; ev("JENDELA", "total waktu turun dinolkan (jendela dianggap sudah dinaikkan manual)"); }
  else if (k == 'q') { simCO2 = c.substring(1).toInt(); ev("SIMULASI CO2", simCO2 > 0 ? String(simCO2) + " ppm (aktif; melewati pemanasan; q0 = mati)" : String("mati, kembali ke sensor MH-Z19C")); }
  else if (k == 'c') {
    if (PIN_JENDELA_TUTUP < 0) ev("UJI MANUAL", "tidak ada keluaran penutup di skematik (relay hanya arah turun); tidak ada yang dikirim");
    else { pulsaJendela(PIN_JENDELA_TUTUP, PULSA_TUTUP_MS); jendelaTerbuka = false; ev("UJI MANUAL", "sinyal tutup dikirim"); }
  }
  else if (k == 'p') { simCO = c.substring(1).toFloat(); ev("SIMULASI CO", simCO > 0 ? String(simCO, 0) + " ppm (aktif; Rs untuk uji arah dihitung dari kurva)" : String("mati, kembali ke sensor")); }
  else if (k == 'f') { formatMode = (formatMode + 1) % 3; barisSejakKepala = 0; ev("FORMAT", formatMode == 0 ? "ringkas (seperti v0)" : (formatMode == 1 ? "tabel lengkap" : "CSV lengkap (untuk skrip analisis)")); }
  else if (k == 'i') cetakDetail();
  else if (k == 'h') cetakBantuan();
  else ev("PERINTAH", "tidak dikenal (h = bantuan)");
}

void handleSerial() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { jalankanPerintah(cmdBuf); cmdBuf = ""; }
    else if (cmdBuf.length() < 16) cmdBuf += ch;
  }
}

// =====================================================================
// LCD (pseudocode 2.10)
// =====================================================================
void lcdLine(int row, const char* text) {
  char buf[24];
  snprintf(buf, sizeof(buf), "%-*.*s", LCD_COLS, LCD_COLS, text);
  lcd.setCursor(0, row);
  lcd.print(buf);
}

const char* tagLevel(int lv) { return lv == LV_BAHAYA ? "DANG" : (lv == LV_WASPADA ? "WARN" : "OK"); }

void perbaruiLcd(bool coSiap, bool coValid, float ppm, bool co2Siap, bool co2Valid, int co2) {
  char val[8], line[24];
  if (!CO_AKTIF) {   // MVP: baris atas = CO2, baris bawah = keadaan jendela
    const char* tC2;
    if (!co2Valid)     { tC2 = "ERR";  snprintf(val, sizeof(val), " n/a"); }
    else if (!co2Siap) { tC2 = "WARM"; snprintf(val, sizeof(val), "----"); }
    else               { tC2 = tagLevel(levelCO2); snprintf(val, sizeof(val), "%4d", constrain(co2, 0, 9999)); }
    if (tutupManual && millis() - tutupManualMs > 120000UL) tutupManual = false;
    char ind = simCO2 > 0 ? 'S' : (jendelaTerbuka ? 'J' : (tutupManual ? 'M' : ' '));
    snprintf(line, sizeof(line), "CO2%sppm %-4s%c", val, tC2, ind);
    lcdLine(0, line);
    const char* t1 = pulsaPin >= 0 ? "Jendela TURUN" : (jendelaTerbuka ? "Jendela terbuka" :
                     (totalTurunMs >= JENDELA_TOTAL_MAKS_MS ? "Naikkan,ketik n" : "Jendela siap"));
    lcdLine(1, t1);
    return;
  }
  const char* tCO;
  if (calActive)            { tCO = "CAL";  snprintf(val, sizeof(val), "----"); }
  else if (!coValid)        { tCO = "ERR";  snprintf(val, sizeof(val), " n/a"); }
  else if (!coSiap)         { tCO = "WARM"; snprintf(val, sizeof(val), "----"); }
  else {
    tCO = (faseCO == CO_SUMBER_LUAR) ? "LUAR" : tagLevel(levelCO);
    snprintf(val, sizeof(val), "%4d", (int)constrain(ppm, 0, 9999));
  }
  if (tutupManual && millis() - tutupManualMs > 120000UL) tutupManual = false;
  char ind = simCO > 0 ? 'S' : (jendelaTerbuka ? 'J' : (tutupManual ? 'M' : ' '));
  snprintf(line, sizeof(line), "CO %sppm %-4s%c", val, tCO, ind);
  lcdLine(0, line);

  const char* tCO2;
  if (!co2Valid)            { tCO2 = "ERR";  snprintf(val, sizeof(val), " n/a"); }
  else if (!co2Siap)        { tCO2 = "WARM"; snprintf(val, sizeof(val), "----"); }
  else { tCO2 = tagLevel(levelCO2); snprintf(val, sizeof(val), "%4d", constrain(co2, 0, 9999)); }
  snprintf(line, sizeof(line), "CO2%sppm %-4s", val, tCO2);
  lcdLine(1, line);
}

// =====================================================================
// Aturan CO (pseudocode 2.4)
// =====================================================================
void naikLevelCO(int lv) {
  if (lv <= levelCO) return;
  levelCO = lv;
  ev("STATUS CO", String("naik ke ") + (lv == LV_BAHAYA ? "BAHAYA" : "WASPADA") + " | " + nilaiSaatIni());
  bunyiDiam = false;                 // naik level selalu berbunyi lagi
  mulaiBunyi(lv, true);
  coBunyiTerakhirMs = millis();
  if (coBunyiMulaiMs == 0) coBunyiMulaiMs = millis();
}

void aturanCO(float ppm, float rsHalus) {
  if (faseCO == CO_TIDAK_AKTIF) {
    bool aktifkan = false;
    int lv = LV_WASPADA;
    if (ppm >= CO_AMBANG_BAHAYA) { aktifkan = true; lv = LV_BAHAYA; }
    else if (ppm >= CO_AMBANG_WASPADA) {
      konfirmasiCO++;
      if (konfirmasiCO >= CO_KONFIRMASI_S) aktifkan = true;
    } else {
      if (konfirmasiCO > 0) ev("CO", "turun di bawah ambang, konfirmasi diulang dari 0 (sempat " + String(konfirmasiCO) + " detik)");
      konfirmasiCO = 0;
    }
    if (ppm >= CO_AMBANG_WASPADA && ppm < CO_AMBANG_BAHAYA && konfirmasiCO == 1) {
      ev("CO", "ppm >= " + String(CO_AMBANG_WASPADA, 0) + ", konfirmasi " + CO_KONFIRMASI_S + " detik dimulai | " + nilaiSaatIni());
    }

    if (aktifkan) {
      ev("CO", String(lv == LV_BAHAYA ? "ppm >= ambang bahaya (tanpa konfirmasi)" : "konfirmasi selesai") + ": UJI ARAH mulai, Rs awal uji = " + String(rsHalus / 1000.0, 1) + " kOhm");
      faseCO = CO_UJI_ARAH;
      rsAwalUji = rsHalus; waktuUji = 0; pemulihanCO = 0;
      coBunyiMulaiMs = 0;
      naikLevelCO(lv);
      bukaJendela(true, "CO, uji arah");
    }
    return;
  }

  if (ppm >= CO_AMBANG_BAHAYA) naikLevelCO(LV_BAHAYA);

  if (faseCO == CO_UJI_ARAH) {
    waktuUji++;
    if (waktuUji >= CO_LAMA_UJI_ARAH_S) {
      float perubahan = (rsHalus - rsAwalUji) / rsAwalUji;   // negatif = Rs turun = CO naik
      String rincian = String("Rs awal ") + String(rsAwalUji / 1000.0, 1) + " -> sekarang " + String(rsHalus / 1000.0, 1) + " kOhm, perubahan " + String(perubahan * 100.0, 1) + "% (batas luar: turun > " + String(CO_KRITERIA_NAIK * 100.0, 0) + "%, batas dalam: naik > " + String(CO_KRITERIA_TURUN * 100.0, 0) + "%)";
      if (perubahan > CO_KRITERIA_TURUN) {
        faseCO = CO_SUMBER_DALAM;
        ev("UJI ARAH", "HASIL: CO turun, sumber DALAM, jendela tetap terbuka | " + rincian);
      } else {
        // Rs turun > 25% (CO dari luar) atau tidak jelas: anggap luar dan tutup (lebih aman)
        faseCO = CO_SUMBER_LUAR;
        ev("UJI ARAH", String(perubahan < -CO_KRITERIA_NAIK ? "HASIL: CO naik, sumber LUAR" : "HASIL: tidak jelas, dianggap sumber LUAR") + ", jendela ditutup | " + rincian);
        naikLevelCO(LV_BAHAYA);
        tutupJendela("CO dari luar");
      }
    }
  }

  if (ppm < CO_BATAS_SELESAI) {
    pemulihanCO++;
    if (pemulihanCO >= CO_WAKTU_PEMULIHAN_S) {
      faseCO = CO_TIDAK_AKTIF; levelCO = LV_NORMAL;
      konfirmasiCO = pemulihanCO = waktuUji = 0;
      coBunyiMulaiMs = 0;
      ev("CO", String("SELESAI: di bawah ") + String(CO_BATAS_SELESAI, 0) + " ppm selama " + CO_WAKTU_PEMULIHAN_S + " detik | " + nilaiSaatIni());
      hentikanBunyi();
      if (faseCO2 != CO2_TINDAKAN) tutupJendela("CO selesai");
    }
  } else pemulihanCO = 0;

  // Pengulangan bunyi CO: tiap 60 detik, maksimal 5 menit, kecuali "Saya Tahu"
  unsigned long now = millis();
  if (levelCO > LV_NORMAL && !bunyiDiam && coBunyiMulaiMs != 0 &&
      now - coBunyiMulaiMs < BUNYI_ULANG_CO_MAKS_S * 1000UL &&
      now - coBunyiTerakhirMs >= BUNYI_ULANG_CO_S * 1000UL) {
    ev("BUNYI", "pengulangan CO (tiap 60 detik, maksimum 5 menit)");
    mulaiBunyi(levelCO, true);
    coBunyiTerakhirMs = now;
  }
}

// =====================================================================
// Aturan CO2 (pseudocode 2.5), hanya bila aturan CO tidak aktif
// =====================================================================
void aturanCO2(int co2) {
  if (co2 >= CO2_AMBANG_TINDAKAN) atasTindakan++; else atasTindakan = 0;
  if (co2 >= CO2_AMBANG_PERINGATAN) atasPeringatan++; else atasPeringatan = 0;

  if (atasTindakan >= CO2_BACAAN_KONFIRMASI) {
    if (faseCO2 != CO2_TINDAKAN) {
      faseCO2 = CO2_TINDAKAN; co2TidakTurun = false;
      ev("CO2", String("TINDAKAN: >= ") + CO2_AMBANG_TINDAKAN + " ppm selama " + CO2_BACAAN_KONFIRMASI + " bacaan | CO2=" + co2);
      if (levelCO2 < LV_BAHAYA) { levelCO2 = LV_BAHAYA; bunyiDiam = false; mulaiBunyi(LV_BAHAYA, false); }
    }
  } else if (atasPeringatan >= CO2_BACAAN_KONFIRMASI && faseCO2 == CO2_NORMAL) {
    faseCO2 = CO2_PERINGATAN;
    ev("CO2", String("PERINGATAN: >= ") + CO2_AMBANG_PERINGATAN + " ppm selama " + CO2_BACAAN_KONFIRMASI + " bacaan | CO2=" + co2);
    if (levelCO2 < LV_WASPADA) { levelCO2 = LV_WASPADA; mulaiBunyi(LV_WASPADA, false); }
  }

  // Buka saat TINDAKAN (tunggu bila jeda minimum belum lewat); tidak dibuka lagi setelah dipaksa tutup
  if (faseCO2 == CO2_TINDAKAN && !jendelaTerbuka && !co2TidakTurun) bukaJendela(false, "CO2 tindakan");

  if (faseCO2 == CO2_TINDAKAN && jendelaTerbuka) {
    lamaBuka++;
    if (lamaBuka >= JENDELA_BUKA_MAKS_S) {
      ev("CO2", "tidak turun dalam batas lama buka (" + String(JENDELA_BUKA_MAKS_S) + " detik), jendela dipaksa tutup dan tidak dibuka lagi sampai CO2 normal");
      tutupJendela("CO2 tidak turun (batas lama buka)");
      co2TidakTurun = true;
    }
  }

  if (faseCO2 != CO2_NORMAL) {
    // syarat lama buka minimal hanya berlaku bila jendela memang terbuka
    bool cukupLama = !jendelaTerbuka || lamaBuka >= JENDELA_BUKA_MIN_S;
    if (co2 < CO2_BATAS_SELESAI && cukupLama) {
      pemulihanCO2++;
      if (pemulihanCO2 >= CO2_PEMULIHAN_S) {
        ev("CO2", String("SELESAI: di bawah ") + CO2_BATAS_SELESAI + " ppm selama " + CO2_PEMULIHAN_S + " detik | CO2=" + co2);
        faseCO2 = CO2_NORMAL; levelCO2 = LV_NORMAL;
        atasPeringatan = atasTindakan = pemulihanCO2 = 0;
        co2TidakTurun = false;
        hentikanBunyi();
        tutupJendela("CO2 aman");
      }
    } else pemulihanCO2 = 0;
  }
}

// =====================================================================
// setup / loop
// =====================================================================
void cetakDetail() {
  Serial.println(F("# ================= AEROS ================="));
  Serial.print(F("# firmware ")); Serial.print(F(FW_VERSI)); Serial.print(F(" | dikompilasi ")); Serial.print(F(__DATE__)); Serial.print(' '); Serial.println(F(__TIME__));
  Serial.println(MODE_PENGEMBANGAN ? F("# MODE: PENGEMBANGAN (ambang CO2 diturunkan, jeda dipendekkan)") : F("# MODE: rancangan"));
  Serial.print(F("# PIN: buzzer GPIO")); Serial.print(PIN_BUZZER);
  Serial.print(F(", jendela buka GPIO")); Serial.print(PIN_JENDELA_BUKA);
  Serial.print(F(", jendela tutup GPIO")); Serial.print(PIN_JENDELA_TUTUP);
  Serial.print(F(", CO2 RX/TX GPIO")); Serial.print(PIN_CO2_RX); Serial.print('/'); Serial.print(PIN_CO2_TX);
  Serial.print(F(", I2C SDA/SCL GPIO")); Serial.print(PIN_SDA); Serial.print('/'); Serial.println(PIN_SCL);
  Serial.print(F("# RELAY JENDELA (TBout GPIO26 -> PN2222A -> relay): HIGH = motor TURUN selama HIGH, LOW = berhenti | lama turun per buka ")); Serial.print(PULSA_BUKA_MS);
  Serial.print(F(" ms, batas satu pulsa ")); Serial.print(PULSA_MAKS_MS); Serial.print(F(" ms, batas total ")); Serial.print(JENDELA_TOTAL_MAKS_MS); Serial.println(F(" ms (nolkan dengan n)"));
  Serial.println(CO_AKTIF ? F("# JALUR CO: aktif") : F("# JALUR CO: NONAKTIF (MVP CO2 saja; MiCS dan ADS1115 tidak dibaca)"));
  Serial.println(PIN_JENDELA_TUTUP < 0 ? F("# PENUTUP JENDELA: TIDAK ADA (relay arah naik belum ada). Firmware hanya mencatat 'TUTUP JENDELA MANUAL' dan menampilkan M di LCD") : F("# PENUTUP JENDELA: ada"));
  Serial.print(F("# R0 aktif = ")); Serial.print(r0Ohm / 1000.0, 1); Serial.print(r0Tersimpan ? F(" kOhm (tersimpan di memori ESP32)") : F(" kOhm (DEFAULT: belum pernah dikalibrasi di board ini, kirim 'r' di udara bersih)")); Serial.print(F(" | VCC ")); Serial.print(VCC, 2);
  Serial.print(F(" V | kurva A=")); Serial.print(A_COEF, 2); Serial.print(F(" beta=")); Serial.println(BETA, 3);
  Serial.print(F("# FILTER: SMA ")); Serial.print(PANJANG_FILTER_CO); Serial.print(F(" pada Rs | CO2 tanpa filter | pemanasan ")); Serial.print(PEMANASAN_CO_S); Serial.println(F(" detik (CO dan CO2)"));
  Serial.print(F("# CO: waspada >= ")); Serial.print(CO_AMBANG_WASPADA, 0); Serial.print(F(" ppm selama ")); Serial.print(CO_KONFIRMASI_S);
  Serial.print(F(" detik, bahaya >= ")); Serial.print(CO_AMBANG_BAHAYA, 0); Serial.print(F(" ppm, uji arah ")); Serial.print(CO_LAMA_UJI_ARAH_S);
  Serial.print(F(" detik (luar bila Rs turun > ")); Serial.print(CO_KRITERIA_NAIK * 100, 0); Serial.print(F("%), selesai < ")); Serial.print(CO_BATAS_SELESAI, 0);
  Serial.print(F(" ppm selama ")); Serial.print(CO_WAKTU_PEMULIHAN_S); Serial.println(F(" detik"));
  Serial.print(F("# CO2: peringatan >= ")); Serial.print(CO2_AMBANG_PERINGATAN); Serial.print(F(", tindakan (buka jendela) >= ")); Serial.print(CO2_AMBANG_TINDAKAN);
  Serial.print(F(", selesai (tutup) < ")); Serial.print(CO2_BATAS_SELESAI); Serial.print(F(" selama ")); Serial.print(CO2_PEMULIHAN_S);
  Serial.print(F(" detik, konfirmasi ")); Serial.print(CO2_BACAAN_KONFIRMASI); Serial.println(F(" bacaan"));
  Serial.print(F("# JENDELA: buka minimal ")); Serial.print(JENDELA_BUKA_MIN_S); Serial.print(F(" detik, maksimum ")); Serial.print(JENDELA_BUKA_MAKS_S);
  Serial.print(F(" detik, jeda minimum ")); Serial.print(JEDA_MINIMUM_JENDELA_S); Serial.println(F(" detik"));
  Serial.println(F("# Format serial: tabel per detik (header diulang tiap 20 baris). Perintah f = CSV untuk skrip analisis."));
  Serial.println(F("# Baris berawalan '#' = kejadian atau info; baris lain = data per detik. Rs yang ditampilkan = Rs setelah SMA 6."));
}

void setup() {
  // Keluaran relay jendela dijadikan LOW paling awal (LOW = relay lepas = motor berhenti)
  pinMode(PIN_JENDELA_BUKA, OUTPUT);
  digitalWrite(PIN_JENDELA_BUKA, LEVEL_DIAM);
  Serial.begin(115200);
  delay(500);
  pinMode(PIN_BUZZER, OUTPUT);
  digitalWrite(PIN_BUZZER, LOW);
  pinMode(PIN_JENDELA_BUKA, OUTPUT);
  digitalWrite(PIN_JENDELA_BUKA, LEVEL_DIAM);
  if (PIN_JENDELA_TUTUP >= 0 && PIN_JENDELA_TUTUP != PIN_JENDELA_BUKA) {
    pinMode(PIN_JENDELA_TUTUP, OUTPUT);
    digitalWrite(PIN_JENDELA_TUTUP, LEVEL_DIAM);
  }

  if (MODE_PENGEMBANGAN) {
    CO2_AMBANG_PERINGATAN = CO2_PERINGATAN_DEV; CO2_AMBANG_TINDAKAN = CO2_TINDAKAN_DEV;
    CO2_BATAS_SELESAI = CO2_SELESAI_DEV; JENDELA_BUKA_MAKS_S = JENDELA_BUKA_MAKS_DEV;
    JEDA_MINIMUM_JENDELA_S = JEDA_JENDELA_DEV_S;
  } else {
    CO2_AMBANG_PERINGATAN = CO2_PERINGATAN_RANCANGAN; CO2_AMBANG_TINDAKAN = CO2_TINDAKAN_RANCANGAN;
    CO2_BATAS_SELESAI = CO2_SELESAI_RANCANGAN; JENDELA_BUKA_MAKS_S = JENDELA_BUKA_MAKS_RANCANGAN;
    JEDA_MINIMUM_JENDELA_S = JEDA_JENDELA_RANCANGAN_S;
  }

  Serial2.begin(9600, SERIAL_8N1, PIN_CO2_RX, PIN_CO2_TX);
  if (DISABLE_ABC) setAbc(false);

  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.beginTransmission(LCD_ADDR);
  if (Wire.endTransmission() != 0) Serial.println(F("# PERINGATAN: LCD tidak terdeteksi (coba 0x3F)"));
  lcd.init();
  lcd.backlight();
  lcdLine(0, "AEROS " FW_VERSI);
  lcdLine(1, MODE_PENGEMBANGAN ? "Mode pengembang" : "Starting...");

  if (CO_AKTIF) {
    adsAda = ads.begin(0x48);
    if (adsAda) { ads.setGain(gains[gainIdx]); Serial.println(F("# ADS1115 terdeteksi di 0x48")); }
    else Serial.println(F("# PERINGATAN: ADS1115 tidak terdeteksi di 0x48: CO tidak dibaca, dicoba lagi tiap 5 detik"));
  }

  prefs.begin("mics", false);
  r0Tersimpan = prefs.isKey("r0");
  r0Ohm = prefs.getFloat("r0", R0_DEFAULT_OHM);

  Serial.print(F("# AEROS ")); Serial.print(F(FW_VERSI));
  Serial.print(MODE_PENGEMBANGAN ? F(" | MODE PENGEMBANGAN (ambang CO2 diturunkan)") : F(" | mode rancangan"));
  if (CO_AKTIF) {
    Serial.print(F(" | R0 = ")); Serial.print(r0Ohm / 1000.0, 0);
    Serial.println(r0Tersimpan ? F(" kOhm (tersimpan)") : F(" kOhm (DEFAULT, belum dikalibrasi: ketik r)"));
  } else Serial.println(F(" | MVP CO2 SAJA (CO nonaktif)"));
  Serial.print(F("# Relay jendela GPIO26: HIGH ")); Serial.print(PULSA_BUKA_MS / 1000); Serial.print(F(" detik saat CO2 >= ")); Serial.print(CO2_AMBANG_TINDAKAN);
  Serial.print(F(" ppm; total maksimum ")); Serial.print(JENDELA_TOTAL_MAKS_MS / 1000); Serial.println(F(" detik sampai perintah n"));
  Serial.println(F("# Pemanasan 3 menit. Ketik h + Enter untuk daftar perintah, i + Enter untuk semua parameter."));
  Serial.println(F("# Baris berawalan '#' = kejadian atau info. Baris lain = data per detik (ketik f untuk tampilan lain)."));
}

String pad(String s, int w, bool kanan = false) {
  while ((int)s.length() < w) s = kanan ? (" " + s) : (s + " ");
  return s;
}

void cetakKepalaTabel() {
  Serial.println(F("# Penghitung: k=konfirmasi CO (detik), p=pemulihan CO, u=waktu uji arah | a=bacaan CO2 di atas ambang peringatan/tindakan, p=pemulihan CO2, b=lama jendela buka, j=sisa jeda (detik)"));
  Serial.println(F("detik |   CO | CO2   | Rs kOhm  | Rs/R0 | status CO | status CO2 | fase CO      | jendela  | bunyi      | k  p  u  | a/a   p  b   j"));
  Serial.println(F("------+------+-------+----------+-------+-----------+------------+--------------+----------+------------+----------+----------------"));
  barisSejakKepala = 0;
}

// Pelacak perubahan untuk log kejadian
String stCOlama = "", stCO2lama = "";
bool coValidLama = true, co2BacaLama = true, coSiapLama = false, co2SiapLama = false, filterPenuhLama = false, placeholderDicatat = false;

void loop() {
  unsigned long loopStart = millis();
  handleSerial();
  unsigned long tS = millis() / 1000UL;

  // ---------- 1-2. BACA dan VALIDASI ----------
  int co2 = 0;
  bool co2Baca = readCO2(co2);
  bool co2Siap = tS >= PEMANASAN_CO2_S;   // selama pemanasan nilai (termasuk 410/500 palsu) dicetak tetapi tidak dipakai aturan
  if (simCO2 > 0) { co2 = simCO2; co2Baca = true; co2Siap = true; }   // simulasi (q<ppm>) menggantikan sensor dan melewati pemanasan

  if (CO_AKTIF && !adsAda && millis() - adsCobaLagiMs >= 5000) {
    adsCobaLagiMs = millis();
    adsAda = ads.begin(0x48);
    if (adsAda) { ads.setGain(gains[gainIdx]); Serial.println(F("# ADS1115 terdeteksi kembali")); }
  }
  bool coValid = false;
  float v = 0, rs = NAN;
  if (adsAda) {
    v = bacaMics(coValid);
    if (coValid) rs = RL_OHM * (VCC - v) / v;
  }

  gCo2 = co2Baca ? co2 : gCo2;
  if (!co2Siap && co2Baca && (co2 == 410 || co2 == 500) && !placeholderDicatat) {
    placeholderDicatat = true;
    ev("CO2", "nilai " + String(co2) + " ppm = placeholder MH-Z19C saat pemanasan; dicatat di serial tetapi tidak dipakai aturan");
  }
  if (co2Baca != co2BacaLama) {
    ev("CO2", co2Baca ? "sensor terbaca kembali" : "GANGGUAN: bacaan MH-Z19C gagal (cek TX/RX, catu 5 V)");
    co2BacaLama = co2Baca;
  }
  if (coValid != coValidLama && adsAda) {
    ev("CO", coValid ? "tegangan MiCS valid kembali" : "tegangan MiCS TIDAK valid (saturasi atau di luar rentang), V=" + String(v * 1000.0, 1) + " mV");
    coValidLama = coValid;
  }

  // ---------- 3. HITUNG (SMA 6 pada Rs) ----------
  float rsHalus = NAN, ratio = NAN, ppm = 0;
  if (coValid) {
    tidakValidBeruntun = 0;
    bufRs[idxBuf] = rs; idxBuf = (idxBuf + 1) % PANJANG_FILTER_CO;
    if (nBuf < PANJANG_FILTER_CO) nBuf++;
    if (calActive) {
      calSum += rs; calN++;
      if (rs < calMin) calMin = rs;
      if (rs > calMax) calMax = rs;
      if (millis() - calStartMs >= CAL_SECONDS * 1000UL) finishCalibration();
    }
  } else if (++tidakValidBeruntun > MAKS_TIDAK_VALID) {
    if (nBuf > 0) ev("FILTER", "buffer SMA dikosongkan: lebih dari " + String(MAKS_TIDAK_VALID) + " sampel berturut-turut tidak valid");
    kosongkanFilter();
  }
  if ((nBuf == PANJANG_FILTER_CO) != filterPenuhLama) {
    filterPenuhLama = (nBuf == PANJANG_FILTER_CO);
    ev("FILTER", filterPenuhLama ? String("SMA ") + PANJANG_FILTER_CO + " terisi penuh, ppm CO mulai dihitung" : "SMA belum penuh, ppm CO belum dihitung");
  }
  if (nBuf == PANJANG_FILTER_CO) {
    double s = 0;
    for (int i = 0; i < PANJANG_FILTER_CO; i++) s += bufRs[i];
    rsHalus = s / PANJANG_FILTER_CO;
    ratio = rsHalus / r0Ohm;
    ppm = (ratio >= 0.5) ? 0.0 : pow(A_COEF / ratio, 1.0 / BETA);
  }
  // Simulasi: ppm diganti nilai perintah p<ppm>, dan Rs untuk uji arah dihitung balik dari kurva,
  // sehingga uji arah bisa dicoba (misalnya p40 lalu p20 = sumber dalam, p40 lalu p60 = sumber luar).
  bool sim = simCO > 0;
  float rsAturan = rsHalus;
  if (sim) { ppm = simCO; rsAturan = r0Ohm * A_COEF * pow(simCO, -BETA); }
  bool coSiap = CO_AKTIF && tS >= PEMANASAN_CO_S && !calActive && (sim || !isnan(rsHalus));
  bool coDipakai = CO_AKTIF && (coValid || sim) && coSiap;
  gPpm = ppm; gRsHalus = rsHalus;
  if (coSiap != coSiapLama) { coSiapLama = coSiap; if (coSiap) { ev("PEMANASAN", "CO selesai: aturan CO aktif sekarang"); if (!r0Tersimpan) ev("R0", "PERINGATAN: masih memakai R0 default " + String(r0Ohm / 1000.0, 0) + " kOhm; ppm CO belum bermakna sebelum kirim 'r' di udara bersih"); } }
  if (co2Siap != co2SiapLama) { co2SiapLama = co2Siap; if (co2Siap) ev("PEMANASAN", "CO2 selesai: aturan CO2 aktif sekarang"); }
  static bool simLama = false;
  if (sim != simLama) { simLama = sim; if (!sim) ev("SIMULASI CO", "dimatikan, ppm kembali dari sensor"); }

  // ---------- 4. KEADAAN SENSOR ----------
  bool gangguan = CO_AKTIF ? (!coValid && !co2Baca) : !co2Baca;
  bool co2DipakaiAturan = co2Baca && co2Siap;

  // ---------- 5-6. ATURAN ----------
  if (!gangguan) {
    if (coDipakai) aturanCO(ppm, rsAturan);
    if (faseCO == CO_TIDAK_AKTIF && co2DipakaiAturan) aturanCO2(co2);
  }

  // ---------- 8. KELUARAN ----------
  perbaruiLcd(coSiap, coValid || sim, ppm, co2Siap, co2Baca, co2);
  if (gangguan) { lcdLine(1, "SENSOR GANGGUAN"); }

  const char* stCO = !CO_AKTIF ? "OFF" : gangguan ? "GANGGUAN" : (!(coValid || sim) ? "ERR" : (calActive ? "KALIBRASI" : (!coSiap ? "WARMUP" :
                     (faseCO == CO_SUMBER_LUAR ? "LUAR" : (levelCO == LV_BAHAYA ? "BAHAYA" : (levelCO == LV_WASPADA ? "WASPADA" : "OK"))))));
  const char* stCO2 = gangguan ? "GANGGUAN" : (!co2Baca ? "ERR" : (!co2Siap ? "WARMUP" :
                      (levelCO2 == LV_BAHAYA ? "BAHAYA" : (levelCO2 == LV_WASPADA ? "WASPADA" : "OK"))));
  const char* fCO = faseCO == CO_UJI_ARAH ? "UJI_ARAH" : (faseCO == CO_SUMBER_DALAM ? "SUMBER_DALAM" : (faseCO == CO_SUMBER_LUAR ? "SUMBER_LUAR" : "TIDAK_AKTIF"));
  const char* fCO2 = faseCO2 == CO2_TINDAKAN ? "TINDAKAN" : (faseCO2 == CO2_PERINGATAN ? "PERINGATAN" : "NORMAL");

  {
    String a = stCO, b = stCO2;
    if (a != stCOlama || b != stCO2lama) {
      ev("STATUS", String("CO: ") + (stCOlama.length() ? stCOlama : String("-")) + " -> " + a + " | CO2: " + (stCO2lama.length() ? stCO2lama : String("-")) + " -> " + b);
      stCOlama = a; stCO2lama = b;
    }
  }

  const char* stCOtampil = (strcmp(stCO, "OK") == 0 && ppm < 1) ? "OK(<10ppm)" : stCO;
  if (formatMode == 1) {
    if (barisSejakKepala % 20 == 0) cetakKepalaTabel();
    barisSejakKepala++;
    String rsStr = isnan(rsHalus) ? String("n/a") : String(rsHalus / 1000.0, 1);
    String rasioStr = isnan(ratio) ? String("n/a") : String(ratio, 2);
    String co2Str = co2Baca ? String(co2) : String("n/a");
    String baris = pad(String(tS), 5, true) + " | " + pad(String((int)ppm), 4, true) + " | " + pad(co2Str, 5, true) + " | " + pad(rsStr, 8, true) + " | " + pad(rasioStr, 5, true)
      + " | " + pad(stCOtampil, 10) + " | " + pad(stCO2, 10) + " | " + pad(fCO, 12) + " | " + pad(jendelaTerbuka ? "TERBUKA" : "TERTUTUP", 8) + " | " + pad(namaBunyi, 10)
      + " | " + pad(String(konfirmasiCO), 2, true) + " " + pad(String(pemulihanCO), 2, true) + " " + pad(String(waktuUji), 2, true)
      + " | " + String(atasPeringatan) + "/" + String(atasTindakan) + "  " + pad(String(pemulihanCO2), 2, true) + " " + pad(String(lamaBuka), 3, true) + " " + pad(String(sisaJedaS()), 3, true)
      + (sim ? "  [SIMULASI CO]" : "");
    Serial.println(baris);
  } else if (formatMode == 2) {
    if (barisSejakKepala == 0) { Serial.println(F("t_s,V_mV,Rs_kohm,Rs_per_R0,CO_ppm_est,CO2_ppm,status_CO,status_CO2,fase_co,fase_co2,jendela,buzzer,sim,rs_halus_kohm,gain_ads,konf_co,pulih_co,waktu_uji,atas_peringatan,atas_tindakan,pulih_co2,lama_buka,jeda_sisa,mode")); barisSejakKepala = 1; }
    Serial.print(tS); Serial.print(',');
    Serial.print(v * 1000.0, 2); Serial.print(',');
    if (isnan(rs)) Serial.print(F("n/a")); else Serial.print(rs / 1000.0, 1);
    Serial.print(',');
    if (isnan(ratio)) Serial.print(F("n/a")); else Serial.print(ratio, 3);
    Serial.print(',');
    Serial.print(ppm, 0); Serial.print(',');
    if (co2Baca) Serial.print(co2); else Serial.print(F("n/a"));
    Serial.print(','); Serial.print(stCO);
    Serial.print(','); Serial.print(stCO2);
    Serial.print(','); Serial.print(fCO);
    Serial.print(','); Serial.print(fCO2);
    Serial.print(','); Serial.print(jendelaTerbuka ? F("TERBUKA") : F("TERTUTUP"));
    Serial.print(','); Serial.print(namaBunyi);
    Serial.print(','); Serial.print(sim ? 1 : 0);
    Serial.print(','); if (isnan(rsHalus)) Serial.print(F("n/a")); else Serial.print(rsHalus / 1000.0, 1);
    Serial.print(','); Serial.print(gainIdx);
    Serial.print(','); Serial.print(konfirmasiCO);
    Serial.print(','); Serial.print(pemulihanCO);
    Serial.print(','); Serial.print(waktuUji);
    Serial.print(','); Serial.print(atasPeringatan);
    Serial.print(','); Serial.print(atasTindakan);
    Serial.print(','); Serial.print(pemulihanCO2);
    Serial.print(','); Serial.print(lamaBuka);
    Serial.print(','); Serial.print(sisaJedaS());
    Serial.print(','); Serial.println(MODE_PENGEMBANGAN ? F("DEV") : F("RANCANGAN"));
  } else {
    if (barisSejakKepala == 0) { Serial.println(F("t_s,V_mV,Rs_kohm,Rs_per_R0,CO_ppm_est,CO2_ppm,status_CO,status_CO2,jendela,bunyi")); barisSejakKepala = 1; }
    Serial.print(tS); Serial.print(',');
    Serial.print(v * 1000.0, 2); Serial.print(',');
    if (isnan(rsHalus)) Serial.print(F("n/a")); else Serial.print(rsHalus / 1000.0, 1);
    Serial.print(',');
    if (isnan(ratio)) Serial.print(F("n/a")); else Serial.print(ratio, 3);
    Serial.print(',');
    Serial.print(ppm, 0); Serial.print(',');
    if (co2Baca) Serial.print(co2); else Serial.print(F("n/a"));
    Serial.print(','); Serial.print(stCOtampil);
    Serial.print(','); Serial.print(stCO2);
    Serial.print(','); Serial.print(jendelaTerbuka ? F("TERBUKA") : F("TERTUTUP"));
    Serial.print(','); Serial.println(namaBunyi);
  }

  // ---------- 10. TUNGGU tepat 1 detik (bunyi dan pulsa jendela tetap dilayani) ----------
  while (millis() - loopStart < INTERVAL_SIKLUS_MS) { servis(); delay(2); }
}
