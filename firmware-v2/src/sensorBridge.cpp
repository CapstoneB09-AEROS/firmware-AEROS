#include "sensorBridge.h"

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include <Preferences.h>
#include <LiquidCrystal_I2C.h>
#include <atomic>
#include <cstdlib>
#include <cstring>
#include <math.h>

// sensorOriginal.inl adalah salinan byte-for-byte dari code sensor.ino.
// Adapter ini menangkap BARIS CSV yang memang dikeluarkan sketch asli.
// Tidak ada modifikasi terhadap pembacaan MH-Z19C/MiCS, kurva, R0, EMA,
// warm-up, histeresis, durasi alarm, dan update LCD.
namespace {
portMUX_TYPE snapshotMux = portMUX_INITIALIZER_UNLOCKED;
SensorSnapshot latest;
bool hasSnapshot = false;
constexpr size_t SAMPLE_RING_CAPACITY = 128;
SensorSnapshot sampleRing[SAMPLE_RING_CAPACITY];
size_t sampleHead = 0;
size_t sampleTail = 0;
size_t sampleCount = 0;
std::atomic<bool> muted(false);
std::atomic<bool> running(false);
std::atomic<bool> alarmFromSensor(false);   // true selama status CO2 WASPADA/BAHAYA

bool parseUnsigned(const char *text, int &value) {
  if (!text || !*text) return false;
  char *end = nullptr;
  const long parsed = strtol(text, &end, 10);
  if (end == text || *end != '\0' || parsed < 0 || parsed > 100000) return false;
  value = static_cast<int>(parsed);
  return true;
}

void invalidateSnapshot() {
  portENTER_CRITICAL(&snapshotMux);
  hasSnapshot = false;
  // Incomplete measurement windows must not mix old values with a new sensor epoch.
  sampleHead = sampleTail = sampleCount = 0;
  portEXIT_CRITICAL(&snapshotMux);
}

void captureCsvLine(char *line) {
  if (!line || *line < '0' || *line > '9') return;
  char *parts[10] = {};
  char *save = nullptr;
  size_t count = 0;
  for (char *token = strtok_r(line, ",", &save);
       token && count < 10; token = strtok_r(nullptr, ",", &save)) {
    parts[count++] = token;
  }
  if (count != 10) {   // format ringkas inti v2.0: t_s,V_mV,Rs_kohm,Rs_per_R0,CO_ppm_est,CO2_ppm,status_CO,status_CO2,jendela,bunyi
    invalidateSnapshot();
    return;
  }

  // Pemanasan, sensor gagal, atau gangguan: jangan pernah tampil sebagai ppm yang valid.
  if (strncmp(parts[7], "WARMUP", 6) == 0 ||
      strncmp(parts[7], "ERR", 3) == 0 ||
      strncmp(parts[7], "GANGGUAN", 8) == 0) {
    invalidateSnapshot();
    return;
  }

  int co = 0, co2 = 0;
  if (!parseUnsigned(parts[4], co) ||
      !parseUnsigned(parts[5], co2)) {
    invalidateSnapshot();
    return;
  }
  SensorSnapshot data;
  data.coPpm = co;                       // MVP: jalur CO nonaktif, nilainya selalu 0
  data.co2Ppm = co2;
  data.coAlarm = false;
  data.co2Level = strncmp(parts[7], "BAHAYA", 6) == 0 ? 2 :
                  strncmp(parts[7], "WASPADA", 7) == 0 ? 1 : 0;
  data.simulated = strstr(parts[7], "_SIM") != nullptr;
  data.windowState = strncmp(parts[8], "TURUN", 5) == 0 ? 1 :
                     strncmp(parts[8], "BAWAH", 5) == 0 ? 2 :
                     strncmp(parts[8], "NAIK", 4) == 0 ? 3 : 0;
  data.sampledAtMs = millis();
  alarmFromSensor.store(data.co2Level > 0);
  portENTER_CRITICAL(&snapshotMux);
  latest = data;
  hasSnapshot = true;
  if (sampleCount == SAMPLE_RING_CAPACITY) {
    // Bounded memory. Prefer the freshest samples if networking stalls too long.
    sampleHead = (sampleHead + 1) % SAMPLE_RING_CAPACITY;
    --sampleCount;
  }
  sampleRing[sampleTail] = data;
  sampleTail = (sampleTail + 1) % SAMPLE_RING_CAPACITY;
  ++sampleCount;
  portEXIT_CRITICAL(&snapshotMux);
}

// Menjembatani output CSV tanpa menyunting satu baris sketch sensor.
// Perintah 'r' dan 'd' tetap diteruskan ke Serial USB untuk kalibrasi R0.
class SensorSerialCapture : public Print {
 public:
  void begin(unsigned long baud) { ::Serial.begin(baud); }
  int available() { return ::Serial.available(); }
  int read() { return ::Serial.read(); }
  using Print::write;
  size_t write(uint8_t byte) override {
    ::Serial.write(byte);
    if (byte == '\n') {
      buffer_[used_] = '\0';
      captureCsvLine(buffer_);
      used_ = 0;
    } else if (byte != '\r') {
      if (used_ < sizeof(buffer_) - 1) buffer_[used_++] = static_cast<char>(byte);
      else used_ = 0;
    }
    return 1;
  }

 private:
  char buffer_[192] = {};
  size_t used_ = 0;
};

SensorSerialCapture sensorSerialCapture;
}  // namespace

// Hanya GPIO buzzer yang diintersep. Mute tetap berlaku walaupun sketch
// sensor menjalankan digitalWrite(HIGH) lagi pada loop satu detik berikutnya.
void sensorDigitalWrite(uint8_t pin, uint8_t value) {
  // Fail safe: bila alarm baru mulai (bunyi HIGH) sebelum snapshot sempat diproses,
  // bunyi dibuka dari mute dulu supaya alarm baru tidak terbungkam oleh mute lama.
  if (pin == 27 && value == HIGH && !alarmFromSensor.load()) {
    muted.store(false);
  }
  if (pin == 27 && muted.load()) value = LOW;
  ::digitalWrite(pin, value);
}

// Original sensor sketch remains completely untouched on disk.
// Compile-time aliasing supplies different entry points and output hooks.
namespace sensorCore {   // global inti (lcd, prefs, ads, ...) tidak bentrok dengan kode jaringan
#define setup sensorOriginalSetup
#define loop sensorOriginalLoop
#define Serial sensorSerialCapture
#define digitalWrite sensorDigitalWrite
#include "sensorOriginal.inl"
#undef digitalWrite
#undef Serial
#undef loop
#undef setup
}  // namespace sensorCore

namespace {
void sensorTask(void *) {
  sensorCore::sensorOriginalSetup();
  for (;;) sensorCore::sensorOriginalLoop();  // The original loop runs at ~1 Hz.
}
}  // namespace

bool sensorBridgeStart() {
  if (running.load()) return true;
  // Disable the physical output until sensorOriginalSetup initializes it.
  muted.store(false);
  BaseType_t result = xTaskCreatePinnedToCore(
      sensorTask, "AEROS_sensor", 12288, nullptr, 1, nullptr, 1);
  running.store(result == pdPASS);
  return result == pdPASS;
}

bool sensorBridgeActive() { return running.load(); }

bool sensorBridgeGet(SensorSnapshot &out) {
  portENTER_CRITICAL(&snapshotMux);
  const bool exists = hasSnapshot;
  if (exists) out = latest;
  portEXIT_CRITICAL(&snapshotMux);
  // Reject stale snapshots if sensor task stopped producing output.
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

void sensorBridgeSetMuted(bool shouldMute) {
  muted.store(shouldMute);
  if (shouldMute) ::digitalWrite(27, LOW);
}

bool sensorBridgeBuzzerOn() {
  return alarmFromSensor.load() && !muted.load();   // MVP: alarm CO2 aktif dan belum dibungkam
}
