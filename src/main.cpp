// Monitor CO (estimasi) + CO2 + LCD I2C: ESP32 + ADS1115 + MiCS-5524 + MH-Z19C
// ppm CO adalah ESTIMASI dari kurva datasheet dan R0 hasil ukur sensor ini (belum dikalibrasi gas referensi,
// belum dikompensasi suhu/RH). ppm CO2 dibaca langsung dari MH-Z19C lewat UART.
//
// WIRING
//   MICS   : 5V -> ESP32 5V, GND -> GND, EN -> kosong, AO -> ADS1115 A0 (resistor seri 10k disarankan)
//   ADS1115: VDD -> 3V3, GND -> GND, SDA -> GPIO21, SCL -> GPIO22, ADDR -> GND (0x48)
//   MH-Z19C: Vin -> 5V, GND -> GND,
//            TX sensor -> GPIO16 (RX2 ESP32), RX sensor -> GPIO17 (TX2 ESP32)   [menyilang]
//   LCD I2C: VCC -> 5V, GND -> GND, SDA -> GPIO21, SCL -> GPIO22 (satu jalur I2C dengan ADS1115)
//   Buzzer aktif (opsional): GPIO25 -> buzzer -> GND
//
// PERINTAH Serial Monitor (115200 baud, "New Line"):
//   r = ukur R0 MiCS sekarang (sensor HARUS di udara bersih, tunggu 120 detik). Disimpan ke memori ESP32.
//   d = kembalikan R0 ke nilai default di kode
//
// Library: Adafruit ADS1X15 (+ Adafruit BusIO), LiquidCrystal I2C (Frank de Brabander).
// Board: ESP32 Dev Module.

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include <Preferences.h>
#include <LiquidCrystal_I2C.h>

// ---------------- Pin ----------------
const int PIN_SDA    = 21;
const int PIN_SCL    = 22;
const int PIN_BUZZER = 25;
const int PIN_CO2_RX = 16;   // ESP32 RX2 <- TX sensor MH-Z19C
const int PIN_CO2_TX = 17;   // ESP32 TX2 -> RX sensor MH-Z19C

// ---------------- LCD I2C ----------------
const uint8_t LCD_ADDR = 0x27;   // jika kosong/tidak tampil, coba 0x3F atau jalankan I2C scanner
const int LCD_COLS = 16;         // ganti 20 jika LCD 20x4
const int LCD_ROWS = 2;          // ganti 4 jika LCD 20x4 (baris 3-4 menampilkan status)
LiquidCrystal_I2C lcd(LCD_ADDR, LCD_COLS, LCD_ROWS);

// ---------------- Rangkaian MiCS ----------------
const float VCC    = 4.64;       // ukur tegangan pin 5V modul MICS saat menyala; perbarui bila berubah
const float RL_OHM = 9970.0;     // RL (R2) terukur

const float R0_DEFAULT_OHM = 1730000.0;   // SEMENTARA, ukur ulang dengan perintah 'r' di udara bersih

// ---------------- Kurva CO datasheet (25C, 50% RH): Rs/R0 = A * ppm^(-BETA) ----------------
const float A_COEF = 3.7;
const float BETA   = 0.856;

// ---------------- Alarm CO (berbasis ppm ESTIMASI) ----------------
const float ALARM_PPM = 35.0;
const float CLEAR_PPM = 25.0;           // histeresis
const int   ALARM_CONFIRM_S = 10;       // dihitung per detik (loop berjalan 1 Hz)
const int   CLEAR_CONFIRM_S = 30;
const unsigned long WARMUP_S = 300UL;   // 5 menit setelah boot, alarm CO belum aktif

// ---------------- Kalibrasi R0 ----------------
const unsigned long CAL_SECONDS = 120UL;
const float CAL_MAX_SPREAD_PCT  = 10.0;

// ---------------- Pembacaan MiCS ----------------
const int   N_SAMPEL = 16;
const float EMA_ALPHA = 0.2;

// ---------------- MH-Z19C ----------------
const unsigned long CO2_WARMUP_S = 180UL;   // pemanasan sensor 3 menit
const bool DISABLE_ABC = false;             // true = matikan auto-baseline (untuk ruang yang tidak pernah kena udara luar)

Adafruit_ADS1115 ads;
Preferences prefs;
adsGain_t gains[3] = { GAIN_FOUR, GAIN_TWO, GAIN_ONE };
const float fsV[3] = { 1.024, 2.048, 4.096 };
int gainIdx = 0;

float r0Ohm = R0_DEFAULT_OHM;
float rsEma = 0.0;
bool  alarmOn = false;
int   lowCnt = 0, highCnt = 0;

bool calActive = false;
unsigned long calStartMs = 0;
double calSum = 0.0;
long calN = 0;
float calMin = 1e12, calMax = 0.0;

// ================= LCD =================
void lcdLine(int row, const char* text) {
  if (row >= LCD_ROWS) return;
  char buf[24];
  snprintf(buf, sizeof(buf), "%-*.*s", LCD_COLS, LCD_COLS, text);   // padding spasi agar sisa teks lama terhapus
  lcd.setCursor(0, row);
  lcd.print(buf);
}

const char* tagCO(const char* st) {
  if (strncmp(st, "ALARM", 5) == 0)     return "ALRM";
  if (strncmp(st, "WARMUP", 6) == 0)    return "WARM";
  if (strncmp(st, "KALIBRASI", 9) == 0) return "CAL";
  if (strncmp(st, "ADC", 3) == 0)       return "ERR";
  if (strncmp(st, "DI_ATAS", 7) == 0)   return "HIGH";
  return "";
}

const char* tagCO2(const char* st) {
  if (strncmp(st, "WARMUP", 6) == 0)  return "WARM";
  if (strncmp(st, "BAIK", 4) == 0)    return "OK";
  if (strncmp(st, "SEDANG", 6) == 0)  return "MID";
  if (strncmp(st, "TINGGI", 6) == 0)  return "HIGH";
  if (strncmp(st, "BAHAYA", 6) == 0)  return "!!!";
  return "ERR";
}

void updateLcd(float coPpm, bool coValid, int co2, bool co2Ok, const char* stCO, const char* stCO2) {
  char val[8], line[24];

  if (coValid) snprintf(val, sizeof(val), "%4d", (int)constrain(coPpm, 0, 9999));
  else         snprintf(val, sizeof(val), "%4s", "n/a");
  snprintf(line, sizeof(line), "CO: %sppm %-4s", val, tagCO(stCO));
  lcdLine(0, line);

  if (co2Ok) snprintf(val, sizeof(val), "%4d", co2);
  else       snprintf(val, sizeof(val), "%4s", "n/a");
  snprintf(line, sizeof(line), "CO2:%sppm %-4s", val, tagCO2(stCO2));
  lcdLine(1, line);

  if (LCD_ROWS >= 4) {          // LCD 20x4: tampilkan teks status lengkap
    lcdLine(2, stCO);
    lcdLine(3, stCO2);
  }
}

// ================= MH-Z19C =================
bool readCO2(int &ppm) {
  static const uint8_t cmd[9] = {0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};
  while (Serial2.available()) Serial2.read();
  Serial2.write(cmd, 9);

  uint8_t buf[9];
  int n = 0;
  unsigned long t0 = millis();
  while (n < 9 && millis() - t0 < 500) {
    if (Serial2.available()) buf[n++] = Serial2.read();
  }
  if (n < 9) return false;
  if (buf[0] != 0xFF || buf[1] != 0x86) return false;

  uint8_t cs = 0;
  for (int i = 1; i < 8; i++) cs += buf[i];
  cs = 0xFF - cs + 1;
  if (cs != buf[8]) return false;

  ppm = buf[2] * 256 + buf[3];
  return true;
}

void setAbc(bool on) {
  uint8_t cmd[9] = {0xFF, 0x01, 0x79, on ? (uint8_t)0xA0 : (uint8_t)0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
  uint8_t cs = 0;
  for (int i = 1; i < 8; i++) cs += cmd[i];
  cmd[8] = 0xFF - cs + 1;
  Serial2.write(cmd, 9);
}

const char* co2Status(int ppm, unsigned long tS) {
  if (tS < CO2_WARMUP_S) return "WARMUP";
  if (ppm < 1000)  return "BAIK";
  if (ppm < 2000)  return "SEDANG(ventilasi)";
  if (ppm < 5000)  return "TINGGI";
  return "BAHAYA";
}

// ================= ADS1115 / MiCS =================
float readAdsVolts(bool &sat) {
  long sum = 0;
  for (int i = 0; i < N_SAMPEL; i++) sum += ads.readADC_SingleEnded(0);
  float avg = sum / (float)N_SAMPEL;
  sat = (fabs(avg) >= 32000.0);
  float v = ads.computeVolts((int16_t)avg);

  float av = fabs(v);
  if (gainIdx < 2 && (av > 0.92 * fsV[gainIdx] || sat)) {
    gainIdx++;
    ads.setGain(gains[gainIdx]);
  } else if (gainIdx > 0 && av < 0.40 * fsV[gainIdx - 1]) {
    gainIdx--;
    ads.setGain(gains[gainIdx]);
  }
  return v;
}

float voltsToRs(float v) {
  if (v < 0.0005 || v > VCC - 0.001) return NAN;
  return RL_OHM * (VCC - v) / v;
}

void startCalibration() {
  calActive = true;
  calStartMs = millis();
  calSum = 0.0; calN = 0; calMin = 1e12; calMax = 0.0;
  alarmOn = false; lowCnt = highCnt = 0;
  Serial.println(F("# Kalibrasi R0 dimulai: jaga sensor MiCS di udara bersih selama 120 detik..."));
}

void finishCalibration() {
  calActive = false;
  if (calN < 60) {
    Serial.println(F("# Kalibrasi gagal: data terlalu sedikit."));
    return;
  }
  float mean = calSum / calN;
  float spread = (calMax - calMin) / mean * 100.0;
  Serial.print(F("# Rs rata-rata = ")); Serial.print(mean / 1000.0, 1);
  Serial.print(F(" kOhm, simpangan max-min = ")); Serial.print(spread, 1);
  Serial.println(F(" %"));
  if (spread > CAL_MAX_SPREAD_PCT) {
    Serial.println(F("# DITOLAK: Rs masih bergerak/terganggu. R0 tidak diubah. Ulangi saat udara bersih dan stabil."));
    return;
  }
  r0Ohm = mean;
  prefs.putFloat("r0", r0Ohm);
  rsEma = 0.0;
  Serial.print(F("# R0 baru disimpan: ")); Serial.print(r0Ohm / 1000.0, 1);
  Serial.println(F(" kOhm"));
}

void handleSerial() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == 'r' || c == 'R') startCalibration();
    else if (c == 'd' || c == 'D') {
      r0Ohm = R0_DEFAULT_OHM;
      prefs.putFloat("r0", r0Ohm);
      rsEma = 0.0;
      Serial.println(F("# R0 dikembalikan ke default."));
    }
  }
}

// ================= setup / loop =================
void setup() {
  Serial.begin(115200);
  delay(1000);
  pinMode(PIN_BUZZER, OUTPUT);
  digitalWrite(PIN_BUZZER, LOW);

  Serial2.begin(9600, SERIAL_8N1, PIN_CO2_RX, PIN_CO2_TX);
  if (DISABLE_ABC) setAbc(false);

  Wire.begin(PIN_SDA, PIN_SCL);

  // LCD
  Wire.beginTransmission(LCD_ADDR);
  if (Wire.endTransmission() != 0) {
    Serial.println(F("# PERINGATAN: LCD tidak terdeteksi di alamat I2C yang diset (coba 0x3F / I2C scanner)"));
  }
  lcd.init();
  lcd.backlight();
  lcdLine(0, "CO + CO2 Monitor");
  lcdLine(1, "Starting...");

  if (!ads.begin(0x48)) {
    Serial.println(F("ADS1115 tidak terdeteksi di 0x48 -> cek SDA(21), SCL(22), VDD(3V3), ADDR(GND)"));
    lcdLine(0, "ADS1115 ERROR");
    lcdLine(1, "Cek wiring I2C");
    while (1) delay(1000);
  }
  ads.setGain(gains[gainIdx]);

  prefs.begin("mics", false);
  r0Ohm = prefs.getFloat("r0", R0_DEFAULT_OHM);

  Serial.print(F("# R0 aktif = ")); Serial.print(r0Ohm / 1000.0, 1); Serial.println(F(" kOhm"));
  Serial.println(F("# Perintah: r = ukur R0 MiCS (udara bersih), d = R0 default"));
  Serial.println(F("# Warmup: MH-Z19C 3 menit, MiCS (alarm CO) 5 menit"));
  Serial.println(F("t_s,V_mV,Rs_kohm,Rs_per_R0,CO_ppm_est,CO2_ppm,status_CO,status_CO2"));
  delay(1500);
}

void loop() {
  unsigned long loopStart = millis();
  handleSerial();

  unsigned long tS = millis() / 1000UL;

  // ---------- CO2 ----------
  int co2 = 0;
  bool co2Ok = readCO2(co2);

  // ---------- CO ----------
  bool sat;
  float v  = readAdsVolts(sat);
  float rs = sat ? NAN : voltsToRs(v);

  float ratio = NAN, ppm = 0.0;
  const char* statusCO = "OK";

  if (sat) {
    statusCO = "ADC_SATURASI";
  } else if (isnan(rs)) {
    statusCO = "ADC_ERR";
  } else {
    if (calActive) {
      calSum += rs; calN++;
      if (rs < calMin) calMin = rs;
      if (rs > calMax) calMax = rs;
      if (millis() - calStartMs >= CAL_SECONDS * 1000UL) finishCalibration();
    }

    rsEma = (rsEma <= 0.0) ? rs : (rsEma + EMA_ALPHA * (rs - rsEma));
    ratio = rsEma / r0Ohm;

    if (ratio >= 0.5) ppm = 0.0;                       // di bawah sekitar 10 ppm: tidak dihitung
    else              ppm = pow(A_COEF / ratio, 1.0 / BETA);

    if (calActive) {
      statusCO = "KALIBRASI_R0";
    } else if (tS < WARMUP_S) {
      statusCO = "WARMUP";
    } else {
      if (!alarmOn) {
        if (ppm >= ALARM_PPM) lowCnt++; else lowCnt = 0;
        if (lowCnt >= ALARM_CONFIRM_S) { alarmOn = true; highCnt = 0; }
      } else {
        if (ppm < CLEAR_PPM) highCnt++; else highCnt = 0;
        if (highCnt >= CLEAR_CONFIRM_S) { alarmOn = false; lowCnt = 0; }
      }
      if (alarmOn) statusCO = "ALARM(est)";
      else if (ppm > 1000.0) statusCO = "DI_ATAS_RENTANG";
      else if (ppm == 0.0) statusCO = "OK(<10ppm)";
    }
  }

  digitalWrite(PIN_BUZZER, alarmOn ? HIGH : LOW);

  const char* statusCO2 = co2Ok ? co2Status(co2, tS) : "CO2_ERR(cek TX/RX)";

  // ---------- LCD ----------
  updateLcd(ppm, !isnan(rs), co2, co2Ok, statusCO, statusCO2);

  // ---------- Output CSV ----------
  Serial.print(tS);                 Serial.print(',');
  Serial.print(v * 1000.0, 2);      Serial.print(',');
  if (isnan(rs)) Serial.print(F("n/a")); else Serial.print(rsEma / 1000.0, 1);
  Serial.print(',');
  if (isnan(ratio)) Serial.print(F("n/a")); else Serial.print(ratio, 3);
  Serial.print(',');
  Serial.print(ppm, 0);             Serial.print(',');
  if (co2Ok) Serial.print(co2); else Serial.print(F("n/a"));
  Serial.print(',');
  Serial.print(statusCO);           Serial.print(',');
  Serial.println(statusCO2);

  // loop dijaga 1 Hz supaya hitungan konfirmasi alarm benar-benar dalam detik
  while (millis() - loopStart < 1000UL) delay(5);
}