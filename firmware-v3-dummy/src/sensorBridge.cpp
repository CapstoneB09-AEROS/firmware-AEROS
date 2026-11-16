#include "sensorBridge.h"

#include <Arduino.h>
#include <atomic>

// FIRMWARE v3 DUMMY: pengganti sensorBridge.cpp milik firmware-v2.
// Tidak membaca sensor apa pun dan tidak menyentuh pin apa pun (tanpa MH-Z19C, MiCS, ADS1115, LCD, buzzer, relay).
// Satu sampel per detik dibangkitkan dari skenario dummy, dengan antarmuka sensorBridge.h yang sama,
// sehingga main.cpp (Wi-Fi, MQTT, HMAC, event_id, ACK) berjalan apa adanya.
// Rencana dan tabel skenario: dokumentasi/tugas/rencana-simulator-integrasi.md bagian 6 dan 12.
namespace {
// Ambang (K6 di rencana): ambang rancangan. Mengganti ambang cukup di sini; skenario tidak berubah.
constexpr int CO2_WASPADA = 2500, CO2_BAHAYA = 4000, CO2_SELESAI = 2500;   // selesai: di bawah ini kembali normal
constexpr int CO_WASPADA = 35, CO_BAHAYA = 87, CO_SELESAI = 35;
constexpr uint8_t TURUN = 1, BAWAH = 2, NAIK = 3;   // windowState: 0 = tertutup (ATAS)
constexpr uint8_t DETIK_PER_PESAN = 5;              // main.cpp mengirim satu pesan tiap 5 sampel (hanya untuk cetakan)

// Satu langkah = satu fase dengan lama (detik) dan nilai yang naik/turun LINIER per detik dari "Dari" ke "Ke".
// Nilai tetap: Dari = Ke. Sampel terakhir tiap langkah tepat sama dengan nilai "Ke".
struct Langkah { const char *nama; uint16_t detik; int coDari; int coKe; int co2Dari; int co2Ke; uint8_t jendela; };
struct Skenario { const char *nama; const Langkah *langkah; size_t jumlah; };

#define JUMLAH(a) (sizeof(a) / sizeof((a)[0]))

// Profil waktu untuk SEMUA skenario (lihat rencana bagian 6):
//   normal (10 detik) -> naik bertahap normal ke bahaya (300 detik = 5 menit) -> bahaya (120 detik, jendela turun lalu terbuka)
//   -> turun (60 detik, tingkat bahaya bertahan sampai di bawah batas selesai, jadi bahaya total sekitar 3 menit)
//   -> jendela naik (5 detik). Setelah itu kembali ke idle normal. Firmware TIDAK punya logika berhenti: penghentian dilakukan dari luar.
constexpr int CO2_DASAR = 700, CO2_PUNCAK = 4100, CO2_AMAN = 2400, CO2_AKHIR = 800;
constexpr int CO_DASAR = 0, CO_PUNCAK = 90, CO_AMAN = 30;
constexpr uint16_t NAIK_DETIK = 300, BAHAYA_DETIK = 120, TURUN_DETIK = 60;

// MODE OTOMATIS: langsung jalan saat ESP menyala (tanpa perintah serial), berhenti saat USB dicabut (ESP mati).
// Satu gelombang = 15 menit: normal 120 s -> naik 300 s -> puncak 60 s -> turun 180 s -> normal 240 s.
// Kenaikan tiap gelombang = 70% kenaikan gelombang sebelumnya. Setelah 6 gelombang (90 menit) mulai lagi dari yang terbesar.
// Puncak CO2: 4300, 3220, 2464, 1935, 1564, 1305. Puncak CO: 95, 66, 47, 33, 23, 16 (ditambah derau acak kecil).
constexpr uint16_t GEL_NORMAL = 120, GEL_NAIK = 300, GEL_PUNCAK = 60, GEL_TURUN = 180, GEL_DETIK = 900;
constexpr int GEL_CO2_PUNCAK = 4300, GEL_CO_PUNCAK = 95;
constexpr float GEL_SUSUT = 0.70f;
constexpr uint8_t GEL_PER_RANGKAIAN = 6;
constexpr int DERAU_CO2 = 25, DERAU_CO = 1;     // derau acak +/- per detik supaya data tidak mulus sempurna
constexpr uint8_t JENDELA_GERAK_DETIK = 5;      // lama fase jendela TURUN/NAIK di mode otomatis

// S0. Normal
const Langkah L_NORMAL[] = {
  {"Normal", 40, CO_DASAR, CO_DASAR, CO2_DASAR, CO2_DASAR, 0},
};
// S1. CO2 tinggi
const Langkah L_CO2[] = {
  {"Normal", 10, CO_DASAR, CO_DASAR, CO2_DASAR, CO2_DASAR, 0},
  {"CO2 naik bertahap (normal ke bahaya)", NAIK_DETIK, CO_DASAR, CO_DASAR, CO2_DASAR, CO2_BAHAYA, 0},
  {"CO2 bahaya", 5, CO_DASAR, CO_DASAR, CO2_PUNCAK, CO2_PUNCAK, 0},
  {"Jendela turun", 5, CO_DASAR, CO_DASAR, CO2_PUNCAK, CO2_PUNCAK, TURUN},
  {"CO2 bahaya, jendela terbuka", BAHAYA_DETIK - 10, CO_DASAR, CO_DASAR, CO2_PUNCAK, CO2_PUNCAK, BAWAH},
  {"CO2 turun, jendela terbuka", TURUN_DETIK, CO_DASAR, CO_DASAR, CO2_PUNCAK, CO2_AMAN, BAWAH},
  {"CO2 aman, jendela naik", 5, CO_DASAR, CO_DASAR, CO2_AMAN, CO2_AKHIR, NAIK},
};
// S2. CO tinggi
const Langkah L_CO[] = {
  {"Normal", 10, CO_DASAR, CO_DASAR, CO2_DASAR, CO2_DASAR, 0},
  {"CO naik bertahap (normal ke bahaya)", NAIK_DETIK, CO_DASAR, CO_BAHAYA, CO2_DASAR, CO2_DASAR, 0},
  {"CO bahaya", 5, CO_PUNCAK, CO_PUNCAK, CO2_DASAR, CO2_DASAR, 0},
  {"Jendela turun", 5, CO_PUNCAK, CO_PUNCAK, CO2_DASAR, CO2_DASAR, TURUN},
  {"CO bahaya, jendela terbuka", BAHAYA_DETIK - 10, CO_PUNCAK, CO_PUNCAK, CO2_DASAR, CO2_DASAR, BAWAH},
  {"CO turun, jendela terbuka", TURUN_DETIK, CO_PUNCAK, CO_AMAN, CO2_DASAR, CO2_DASAR, BAWAH},
  {"CO aman, jendela naik", 5, CO_AMAN, CO_DASAR, CO2_DASAR, CO2_DASAR, NAIK},
};
// S3a. CO dan CO2 tinggi bersamaan
const Langkah L_CAMPURAN[] = {
  {"Normal", 10, CO_DASAR, CO_DASAR, CO2_DASAR, CO2_DASAR, 0},
  {"CO dan CO2 naik bertahap (normal ke bahaya)", NAIK_DETIK, CO_DASAR, CO_BAHAYA, CO2_DASAR, CO2_BAHAYA, 0},
  {"CO dan CO2 bahaya", 5, CO_PUNCAK, CO_PUNCAK, CO2_PUNCAK, CO2_PUNCAK, 0},
  {"Jendela turun", 5, CO_PUNCAK, CO_PUNCAK, CO2_PUNCAK, CO2_PUNCAK, TURUN},
  {"CO dan CO2 bahaya, jendela terbuka", BAHAYA_DETIK - 10, CO_PUNCAK, CO_PUNCAK, CO2_PUNCAK, CO2_PUNCAK, BAWAH},
  {"CO dan CO2 turun, jendela terbuka", TURUN_DETIK, CO_PUNCAK, CO_AMAN, CO2_PUNCAK, CO2_AMAN, BAWAH},
  {"Keduanya aman, jendela naik", 5, CO_AMAN, CO_DASAR, CO2_AMAN, CO2_AKHIR, NAIK},
};
// S3b. CO2 naik dulu, CO menyusul (firmware membuat event_id baru saat CO mulai). Keduanya sampai bahaya di detik ke-300.
// CO2 naik linier 700 -> 4000 dalam 300 detik: di detik ke-180 nilainya 2680 (sudah waspada sejak sekitar detik ke-164).
const Langkah L_BERTAHAP[] = {
  {"Normal", 10, CO_DASAR, CO_DASAR, CO2_DASAR, CO2_DASAR, 0},
  {"CO2 naik bertahap", 180, CO_DASAR, CO_DASAR, CO2_DASAR, 2680, 0},
  {"CO2 naik, CO mulai naik (CO2 sudah waspada)", 120, CO_DASAR, CO_BAHAYA, 2680, CO2_BAHAYA, 0},
  {"CO dan CO2 bahaya", 5, CO_PUNCAK, CO_PUNCAK, CO2_PUNCAK, CO2_PUNCAK, 0},
  {"Jendela turun", 5, CO_PUNCAK, CO_PUNCAK, CO2_PUNCAK, CO2_PUNCAK, TURUN},
  {"CO dan CO2 bahaya, jendela terbuka", BAHAYA_DETIK - 10, CO_PUNCAK, CO_PUNCAK, CO2_PUNCAK, CO2_PUNCAK, BAWAH},
  {"CO dan CO2 turun, jendela terbuka", TURUN_DETIK, CO_PUNCAK, CO_AMAN, CO2_PUNCAK, CO2_AMAN, BAWAH},
  {"Keduanya aman, jendela naik", 5, CO_AMAN, CO_DASAR, CO2_AMAN, CO2_AKHIR, NAIK},
};

// S4. CO2 langsung waspada 1 menit, lalu bahaya 2 menit, lalu turun cepat (tanpa fase naik 5 menit)
const Langkah L_WASPADA_BAHAYA[] = {
  {"CO2 waspada", 60, CO_DASAR, CO_DASAR, 2600, 2600, 0},
  {"CO2 bahaya", 5, CO_DASAR, CO_DASAR, CO2_PUNCAK, CO2_PUNCAK, 0},
  {"Jendela turun", 5, CO_DASAR, CO_DASAR, CO2_PUNCAK, CO2_PUNCAK, TURUN},
  {"CO2 bahaya, jendela terbuka", 110, CO_DASAR, CO_DASAR, CO2_PUNCAK, CO2_PUNCAK, BAWAH},
  {"CO2 turun cepat, jendela naik", 5, CO_DASAR, CO_DASAR, CO2_PUNCAK, CO2_AKHIR, NAIK},
};

// Urutan = nomor perintah serial (1 sampai 5); S0 = perintah 0.
const Skenario SKENARIO[] = {
  {"normal", L_NORMAL, JUMLAH(L_NORMAL)},
  {"co2", L_CO2, JUMLAH(L_CO2)},
  {"co", L_CO, JUMLAH(L_CO)},
  {"campuran", L_CAMPURAN, JUMLAH(L_CAMPURAN)},
  {"campuran-bertahap", L_BERTAHAP, JUMLAH(L_BERTAHAP)},
  {"waspada-bahaya", L_WASPADA_BAHAYA, JUMLAH(L_WASPADA_BAHAYA)},
};
constexpr int JUMLAH_SKENARIO = JUMLAH(SKENARIO);

portMUX_TYPE snapshotMux = portMUX_INITIALIZER_UNLOCKED;
SensorSnapshot latest;
bool hasSnapshot = false;
constexpr size_t SAMPLE_RING_CAPACITY = 128;
SensorSnapshot sampleRing[SAMPLE_RING_CAPACITY];
size_t sampleHead = 0, sampleTail = 0, sampleCount = 0;
std::atomic<bool> muted(false);
std::atomic<bool> running(false);
std::atomic<bool> alarmAktif(false);

// Keadaan pemutar skenario (hanya diakses dari task ini).
int aktif = -1;              // indeks SKENARIO yang sedang dimainkan; -1 = idle (data normal)
size_t langkahKe = 0;
uint16_t detikDiLangkah = 0;
uint32_t detikTotal = 0;
bool semuaBerurutan = false;
uint8_t levelCO = 0, levelCO2 = 0;

// Keadaan mode otomatis (berjalan saat aktif = -1).
uint32_t detikOtomatis = 0;   // detik sejak awal rangkaian 6 gelombang
uint8_t jendelaOtomatis = 0;
uint8_t detikJendela = 0;

void cetakBantuan() {
  Serial.println(F("# --- AEROS v3 DUMMY: data dummy, tanpa sensor ---"));
  Serial.println(F("# MODE OTOMATIS (bawaan): gelombang tiap 15 menit, tiap puncak 70% dari puncak sebelumnya, ulang tiap 6 gelombang."));
  Serial.println(F("# Data hanya tersimpan saat MQTT tersambung ('[BIRTH] ONLINE'). Cabut USB = ESP mati = berhenti mengirim."));
  Serial.println(F("# Skenario manual di bawah menjeda mode otomatis; setelah selesai, mode otomatis lanjut."));
  Serial.println(F("#   0 = normal (40 detik)   1 = CO2 tinggi   2 = CO tinggi   3 = CO dan CO2 bersamaan   4 = CO2 dulu lalu CO   5 = CO2 waspada 1 menit lalu bahaya 2 menit"));
  Serial.println(F("#   a = semua skenario berurutan (1,2,3,4; sekitar 33 menit)   h = bantuan"));
}

void mulaiSkenario(int indeks) {
  aktif = indeks;
  langkahKe = 0;
  detikDiLangkah = 0;
  levelCO = levelCO2 = 0;   // tiap skenario mulai dari keadaan bersih
  Serial.printf("[DUMMY] Mulai skenario '%s'\n", SKENARIO[indeks].nama);
}

void perintah(char c) {
  if (c >= '0' && c <= '5') { semuaBerurutan = false; mulaiSkenario(c - '0'); }
  else if (c == 'a' || c == 'A') { semuaBerurutan = true; mulaiSkenario(1); }
  else if (c == 'h' || c == 'H' || c == '?') cetakBantuan();
}

// Tingkat mengikuti firmware asli: naik langsung, dan bertahan di tingkat tertinggi sampai ppm turun di bawah
// batas selesai, lalu kembali normal (tidak turun bertahap dari bahaya ke waspada).
uint8_t perbaruiTingkat(uint8_t tingkat, int ppm, int waspada, int bahaya, int selesai) {
  const uint8_t baru = ppm >= bahaya ? 2 : (ppm >= waspada ? 1 : 0);
  if (baru > tingkat) return baru;
  return ppm < selesai ? 0 : tingkat;
}

void dorongSampel(const SensorSnapshot &data) {
  portENTER_CRITICAL(&snapshotMux);
  latest = data;
  hasSnapshot = true;
  if (sampleCount == SAMPLE_RING_CAPACITY) {
    sampleHead = (sampleHead + 1) % SAMPLE_RING_CAPACITY;
    --sampleCount;
  }
  sampleRing[sampleTail] = data;
  sampleTail = (sampleTail + 1) % SAMPLE_RING_CAPACITY;
  ++sampleCount;
  portEXIT_CRITICAL(&snapshotMux);
}

int derau(int batas) { return static_cast<int>(esp_random() % (2 * batas + 1)) - batas; }

// Satu detik mode otomatis: nilai gelombang + derau, tingkat, dan jendela (turun saat bahaya, naik saat kembali normal).
void detikGelombang(int &co, int &co2, uint8_t &jendela) {
  const uint8_t ke = detikOtomatis / GEL_DETIK;
  const uint16_t t = detikOtomatis % GEL_DETIK;
  float bentuk = 0;   // 0 = normal, 1 = puncak
  if (t >= GEL_NORMAL && t < GEL_NORMAL + GEL_NAIK) bentuk = float(t - GEL_NORMAL + 1) / GEL_NAIK;
  else if (t >= GEL_NORMAL + GEL_NAIK && t < GEL_NORMAL + GEL_NAIK + GEL_PUNCAK) bentuk = 1;
  else if (t >= GEL_NORMAL + GEL_NAIK + GEL_PUNCAK && t < GEL_NORMAL + GEL_NAIK + GEL_PUNCAK + GEL_TURUN)
    bentuk = 1 - float(t - GEL_NORMAL - GEL_NAIK - GEL_PUNCAK + 1) / GEL_TURUN;
  const float skala = powf(GEL_SUSUT, ke) * bentuk;
  co2 = max(400, CO2_DASAR + int((GEL_CO2_PUNCAK - CO2_DASAR) * skala) + derau(DERAU_CO2));
  co = max(0, CO_DASAR + int((GEL_CO_PUNCAK - CO_DASAR) * skala) + (bentuk > 0 ? derau(DERAU_CO) : 0));

  // Jendela memakai tingkat detik sebelumnya (levelCO/levelCO2 diperbarui di satuDetik).
  if (jendelaOtomatis == TURUN || jendelaOtomatis == NAIK) {
    if (++detikJendela >= JENDELA_GERAK_DETIK) jendelaOtomatis = jendelaOtomatis == TURUN ? BAWAH : 0;
  } else if (jendelaOtomatis == 0 && (levelCO == 2 || levelCO2 == 2)) {
    jendelaOtomatis = TURUN; detikJendela = 0;
  } else if (jendelaOtomatis == BAWAH && levelCO == 0 && levelCO2 == 0) {
    jendelaOtomatis = NAIK; detikJendela = 0;
  }
  jendela = jendelaOtomatis;

  if (t == 0 || t % 30 == 0) {
    Serial.printf("[OTOMATIS] gelombang %u/%u, detik %u/%u | CO=%d CO2=%d | level %u/%u | jendela=%u\n",
                  ke + 1, GEL_PER_RANGKAIAN, t, GEL_DETIK, co, co2, levelCO, levelCO2, jendela);
  }
  if (++detikOtomatis >= uint32_t(GEL_DETIK) * GEL_PER_RANGKAIAN) {
    detikOtomatis = 0;
    Serial.println(F("[OTOMATIS] 6 gelombang selesai, mulai lagi dari gelombang terbesar"));
  }
}

void satuDetik() {
  int co = CO_DASAR, co2 = CO2_DASAR;
  uint8_t jendela = 0;
  const Skenario *s = nullptr;
  const Langkah *l = nullptr;
  if (aktif < 0) detikGelombang(co, co2, jendela);
  else {
    s = &SKENARIO[aktif];
    l = &s->langkah[langkahKe];
    // Linier per detik; sampel terakhir langkah = nilai "Ke". Perkalian selalu di bawah batas int.
    const int i = detikDiLangkah + 1, n = l->detik;
    co = l->coDari + (l->coKe - l->coDari) * i / n;
    co2 = l->co2Dari + (l->co2Ke - l->co2Dari) * i / n;
    jendela = l->jendela;
  }
  levelCO = perbaruiTingkat(levelCO, co, CO_WASPADA, CO_BAHAYA, CO_SELESAI);
  levelCO2 = perbaruiTingkat(levelCO2, co2, CO2_WASPADA, CO2_BAHAYA, CO2_SELESAI);

  SensorSnapshot data;
  data.coPpm = co;
  data.co2Ppm = co2;
  data.coLevel = levelCO;
  data.co2Level = levelCO2;
  data.coAlarm = levelCO > 0;
  data.simulated = true;   // data dummy SELALU berlabel demo; worker menolaknya kecuali ALLOW_DEMO_READINGS=true
  data.windowState = jendela;
  data.sampledAtMs = millis();
  alarmAktif.store(levelCO > 0 || levelCO2 > 0);
  dorongSampel(data);

  ++detikTotal;
  if (!l) return;   // mode otomatis: cetakan sudah di detikGelombang
  if (detikDiLangkah == 0 || detikTotal % DETIK_PER_PESAN == 0) {
    Serial.printf("[DUMMY] %s | fase '%s' | CO=%d CO2=%d | level %u/%u | jendela=%u\n",
                  s->nama, l->nama, co, co2, levelCO, levelCO2, jendela);
  }

  if (++detikDiLangkah >= l->detik) {
    detikDiLangkah = 0;
    if (++langkahKe >= s->jumlah) {
      Serial.printf("[DUMMY] Skenario '%s' selesai\n", s->nama);
      if (semuaBerurutan && aktif < 4) mulaiSkenario(aktif + 1);
      else { aktif = -1; semuaBerurutan = false; jendelaOtomatis = 0; Serial.println(F("[DUMMY] Kembali ke mode otomatis (gelombang).")); }
    }
  }
}

void dummyTask(void *) {
  cetakBantuan();
  TickType_t terakhir = xTaskGetTickCount();
  for (;;) {
    while (Serial.available() > 0) perintah(static_cast<char>(Serial.read()));
    satuDetik();
    vTaskDelayUntil(&terakhir, pdMS_TO_TICKS(1000));   // 1 Hz, sama dengan inti sensor asli
  }
}
}  // namespace

bool sensorBridgeStart() {
  if (running.load()) return true;
  muted.store(false);
  BaseType_t result = xTaskCreatePinnedToCore(dummyTask, "AEROS_dummy", 6144, nullptr, 1, nullptr, 1);
  running.store(result == pdPASS);
  return result == pdPASS;
}

bool sensorBridgeActive() { return running.load(); }

bool sensorBridgeGet(SensorSnapshot &out) {
  portENTER_CRITICAL(&snapshotMux);
  const bool exists = hasSnapshot;
  if (exists) out = latest;
  portEXIT_CRITICAL(&snapshotMux);
  return exists && millis() - out.sampledAtMs <= 30000;
}

bool sensorBridgePop(SensorSnapshot &out) {
  portENTER_CRITICAL(&snapshotMux);
  const bool available = sampleCount != 0;
  if (available) {
    out = sampleRing[sampleHead];
    sampleHead = (sampleHead + 1) % SAMPLE_RING_CAPACITY;
    --sampleCount;
  }
  portEXIT_CRITICAL(&snapshotMux);
  return available;
}

void sensorBridgeSetMuted(bool shouldMute) { muted.store(shouldMute); }

// Tidak ada buzzer fisik. "on" saat ada alarm (K10 di rencana) supaya buzzer_state di pesan konsisten dengan alarm.
bool sensorBridgeBuzzerOn() { return alarmAktif.load() && !muted.load(); }
