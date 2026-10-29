#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Preferences.h>
#include <FS.h>
#include <time.h>
#include <esp_system.h>
#include <mbedtls/md.h>
#include <atomic>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

#include "secrets.h"
#include "root_ca.h"
#include "sensorBridge.h"

// Firmware AEROS: portal custom, bukan WiFiManager.
// POST /save HANYA menerima kredensial. Firmware yang melakukan tepat
// lima percobaan di tingkat aplikasi dengan batas waktu tiap percobaan.
static const char *DEVICE_ID = "AEROS_01";
static const char *AP_SSID = "AEROS-Setup";
static constexpr uint16_t MQTT_PORT = 8883;
static constexpr uint8_t SAMPLES_PER_TELEMETRY = 5;
static constexpr uint32_t DATA_RETRY_MS = 6000;
// Mode ONLINE (keputusan 29 Okt 2026): tanpa antrean offline di flash. Penyangga kecil di RAM menahan beberapa data terbaru sampai ACK.
static constexpr size_t ONLINE_BUFFER = 4;               // jumlah data terbaru yang boleh menunggu ACK
static constexpr uint32_t DATA_MAX_AGE_MS = 30000;       // data yang menunggu lebih lama dari ini dibuang (bukan dikirim terlambat)
// Original sensor sketch owns GPIO25 and its exact CO alarm behavior.
static constexpr int8_t BUZZER_PIN = 27;   // buzzer inti v2.0 (GPIO27); GPIO26 = relay jendela
// Belum ada penggerak jendela. Jangan menebak pin atau posisi fisik.
static constexpr int window_open_gpio_dummy = -1;
static constexpr int window_close_gpio_dummy = -1;
static constexpr int window_position_dummy = -1;
static constexpr bool window_motor_enabled_dummy = false;
static const float co_warning_ppm_dummy = NAN;
static const float co2_warning_ppm_dummy = NAN;
static const float spike_threshold_dummy = NAN;
static constexpr uint32_t RETRY_MQTT_MS = 5000;
static constexpr uint32_t WIFI_BUTTON_HOLD_MS = 5000;
static constexpr uint32_t PORTAL_TIMEOUT_MS = 300000;
static constexpr uint32_t POST_RESPONSE_GRACE_MS = 2000;
static constexpr uint32_t WIFI_TRY_TIMEOUT_MS = 10000;
static constexpr uint32_t WIFI_RETRY_PAUSE_MS = 30000;
static constexpr uint8_t WIFI_MAX_TRIES = 5;
static constexpr int8_t MIN_RSSI_FOR_AUTH_DIAG_DBM = -75;
static constexpr time_t MIN_VALID_EPOCH = 1700000000;
static constexpr uint8_t BUTTON_PIN = 14;
static constexpr uint8_t SDA_PIN = 21;
static constexpr uint8_t SCL_PIN = 22;
static constexpr uint8_t LCD_COLS = 16;

LiquidCrystal_I2C lcd27(0x27, 16, 2);
LiquidCrystal_I2C lcd3f(0x3F, 16, 2);
LiquidCrystal_I2C *lcd = nullptr;
String lcdOld1, lcdOld2;

WebServer portalServer(80);
DNSServer dnsServer;
Preferences prefs;
WiFiClientSecure secureClient;
PubSubClient mqtt(secureClient);

enum class Mode { PORTAL, WIFI_TRY, WIFI_FAILED, WIFI_RETRY_WAIT, WAIT_BUTTON, NORMAL };
Mode mode = Mode::WIFI_FAILED;

String candidateSsid;
String candidatePassword;
String mqttClientId;
String statusTopic, commandTopic, commandAckTopic, dataAckTopic, telemetryTopic;
uint32_t portalStartedMs = 0;
uint32_t submittedAtMs = 0;
uint32_t tryStartedMs = 0;
uint32_t failedAtMs = 0;
uint32_t retryWaitStartedMs = 0;
uint32_t mqttLastAttemptMs = 0;
uint32_t dataLastAttemptMs = 0;
String pendingNonce;            // nonce data yang sedang menunggu ACK
bool awaitingDataAck = false;
bool alarmActive = false;
bool alarmMuted = false;
String activeEventId;
bool previousCoAlarm = false;
uint8_t sampleWindowCount = 0;
int coWindowPeak = 0;
int co2WindowPeak = 0;
uint8_t coPeakSecond = 0;
uint8_t co2PeakSecond = 0;
uint32_t ntpLastLogMs = 0;
uint8_t tryNumber = 0;
bool pendingWifiApply = false;
bool ntpStarted = false;
bool wifiFromPortal = false;  // Bedakan Wi-Fi baru dengan Wi-Fi yang sebelumnya berhasil.
bool saveWifiOnSuccess = false; // Hindari menulis flash saat setiap reconnect.
// Wi-Fi events dijalankan pada task lain: gunakan atomics, jangan update LCD di callback.
std::atomic<int> lastWiFiDisconnectReason(-1);
std::atomic<bool> authProblemThisAttempt(false);
uint8_t authProblemAttempts = 0;
std::atomic<int> explicitAuthFailures(0);
enum class ScanResult { FOUND, MISSING, ERROR };

std::atomic<bool> portalRequested(false);

// Task GPIO terpisah: tekan 5 detik tetap terdeteksi saat MQTT/TLS blocking.
// Task HANYA mengubah flag; seluruh operasi WebServer/MQTT tetap di loop utama.
void portalButtonTask(void *parameter) {
  bool wasDown = false;
  bool triggered = false;
  uint32_t pressedAt = 0;
  for (;;) {
    bool down = digitalRead(BUTTON_PIN) == LOW;
    if (down && !wasDown) {
      pressedAt = millis();
      triggered = false;
    }
    if (down && !triggered && millis() - pressedAt >= WIFI_BUTTON_HOLD_MS) {
      portalRequested.store(true);
      triggered = true;
    }
    if (!down) triggered = false;
    wasDown = down;
    vTaskDelay(pdMS_TO_TICKS(20));
  }
}

void onWiFiEvent(WiFiEvent_t event, WiFiEventInfo_t info) {
  if (event == ARDUINO_EVENT_WIFI_STA_DISCONNECTED) {
    const int reason = info.wifi_sta_disconnected.reason;
    lastWiFiDisconnectReason.store(reason);
    if (reason == 202 || reason == 15 || reason == 204) {
      authProblemThisAttempt.store(true);
      if (reason == 202) explicitAuthFailures.fetch_add(1);
    }
    Serial.printf("[EVENT] WiFi disconnected, reason=%d\n", reason);
  } else if (event == ARDUINO_EVENT_WIFI_STA_GOT_IP) {
    Serial.println("[EVENT] WiFi berhasil mendapat IP");
  }
}

String fitLCD(String s) {
  if (s.length() > LCD_COLS) s.remove(LCD_COLS);
  while (s.length() < LCD_COLS) s += ' ';
  return s;
}

void showLCD(const String &first, const String &second) {
  // When sensor task runs, its untouched LCD driver owns the display.
  if (sensorBridgeActive()) return;
  if (!lcd) return;
  String a = fitLCD(first), b = fitLCD(second);
  if (a == lcdOld1 && b == lcdOld2) return;
  lcd->setCursor(0, 0);
  lcd->print(a);
  lcd->setCursor(0, 1);
  lcd->print(b);
  lcdOld1 = a;
  lcdOld2 = b;
}

void initLCD() {
  Wire.begin(SDA_PIN, SCL_PIN);
  for (uint8_t addr : {uint8_t(0x27), uint8_t(0x3F)}) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      lcd = (addr == 0x27) ? &lcd27 : &lcd3f;
      lcd->init();
      lcd->backlight();
      Serial.printf("[LCD] I2C address 0x%02X\n", addr);
      showLCD("AEROS starting", "Please wait");
      return;
    }
  }
  Serial.println("[LCD] 0x27 / 0x3F tidak ditemukan. Periksa LCD dan level tegangan I2C.");
}

bool settingsValid() {
  if (strlen(MQTT_HOST) == 0 || strlen(MQTT_USERNAME) == 0 ||
      strlen(MQTT_PASSWORD) == 0 || strlen(HMAC_SECRET) < 32 ||
      strlen(ROOT_CA) < 100 || strstr(ROOT_CA, "BEGIN CERTIFICATE") == nullptr ||
      strlen(CONFIG_AP_PASSWORD) < 8 || strlen(CONFIG_AP_PASSWORD) > 63) {
    Serial.println("[CONFIG] Lengkapi secrets.h/root_ca.h; CA PEM valid, AP 8-63, HMAC >= 32.");
    return false;
  }
  return true;
}

bool hmacHex(const char *message, char hexOut[65]) {
  const mbedtls_md_info_t *info = mbedtls_md_info_from_type(MBEDTLS_MD_SHA256);
  if (!info) return false;
  uint8_t digest[32];
  int rc = mbedtls_md_hmac(info,
      reinterpret_cast<const unsigned char *>(HMAC_SECRET), strlen(HMAC_SECRET),
      reinterpret_cast<const unsigned char *>(message), strlen(message), digest);
  if (rc != 0) return false;
  static const char hexChars[] = "0123456789abcdef";
  for (size_t i = 0; i < 32; ++i) {
    hexOut[2 * i] = hexChars[digest[i] >> 4];
    hexOut[2 * i + 1] = hexChars[digest[i] & 15];
  }
  hexOut[64] = '\0';
  return true;
}

bool signatureMatches(const String &message, const String &signature) {
  if (signature.length() != 64) return false;
  char expected[65];
  if (!hmacHex(message.c_str(), expected)) return false;
  unsigned char mismatch = 0;
  for (int i = 0; i < 64; ++i) {
    char c = signature[i];
    if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return false;
    mismatch |= static_cast<unsigned char>(expected[i] ^ c);
  }
  return mismatch == 0;
}

String newNonce() {
  char nonce[33];
  snprintf(nonce, sizeof(nonce), "%08lx%08lx%08lx%08lx",
           (unsigned long)esp_random(), (unsigned long)esp_random(),
           (unsigned long)esp_random(), (unsigned long)esp_random());
  return String(nonce);
}

String newEventId() {
  uint8_t b[16];
  for (int i = 0; i < 16; i += 4) {
    uint32_t r = esp_random();
    memcpy(&b[i], &r, 4);
  }
  b[6] = (b[6] & 0x0F) | 0x40; // UUID v4
  b[8] = (b[8] & 0x3F) | 0x80; // RFC 4122 variant
  char id[37];
  snprintf(id, sizeof(id),
           "%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x",
           b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7],
           b[8], b[9], b[10], b[11], b[12], b[13], b[14], b[15]);
  return String(id);
}

void refreshBuzzer() {
  sensorBridgeSetMuted(alarmMuted);
}

void trackSensorAlarm(const SensorSnapshot &snapshot) {
  // CO alarm timing and hysteresis already happened inside the original sketch.
  // CO2 levels also come from that sketch; they do NOT change its buzzer rule.
  const bool hasGasEvent = snapshot.coAlarm || snapshot.co2Level > 0;
  const bool newEvent = hasGasEvent && !alarmActive;
  if (hasGasEvent && !alarmActive) {
    alarmActive = true;
    alarmMuted = false;
    activeEventId = newEventId();
    Serial.printf("[ALARM] Event sensor asli: %s\n", activeEventId.c_str());
  } else if (!hasGasEvent && alarmActive) {
    alarmActive = false;
    alarmMuted = false;
    activeEventId = "";
    Serial.println("[ALARM] Sensor kembali normal");
  }
  // CO can start a new buzzer episode while a CO2 warning stays active.
  // Rotate its ID too: an old acknowledgment must NEVER mute a new episode.
  if (snapshot.coAlarm && !previousCoAlarm) {
    if (!newEvent) {
      activeEventId = newEventId();
      Serial.printf("[ALARM] Episode CO baru: %s\n", activeEventId.c_str());
    }
    alarmMuted = false;
  }
  previousCoAlarm = snapshot.coAlarm;
  refreshBuzzer();
}

// ---------- Penyangga ONLINE di RAM (pengganti antrean flash) ----------
// Putus jaringan = data tidak disimpan. Alarm, buzzer, dan relay jendela tetap berjalan di inti ESP tanpa internet.
struct PendingData { String json; String nonce; uint32_t queuedMs; };
PendingData ramBuf[ONLINE_BUFFER];
size_t ramCount = 0;            // indeks 0 = tertua (yang sedang menunggu ACK)
uint32_t dibuangOffline = 0;

void ramBuangTertua() {
  for (size_t i = 1; i < ramCount; ++i) ramBuf[i - 1] = ramBuf[i];
  if (ramCount > 0) --ramCount;
  awaitingDataAck = false;      // yang menunggu ACK adalah data tertua; data berikutnya dikirim sebagai percobaan baru
}

bool enqueueReading(const String &json, const String &nonce) {
  if (!mqtt.connected()) {
    ++dibuangOffline;
    if (dibuangOffline == 1 || dibuangOffline % 12 == 0)
      Serial.printf("[DATA] MQTT putus: data tidak disimpan (mode online); total dibuang %lu\n", (unsigned long)dibuangOffline);
    return false;
  }
  if (ramCount == ONLINE_BUFFER) {
    Serial.println("[DATA] Penyangga penuh (ACK tidak datang): data tertua dibuang");
    ramBuangTertua();
  }
  ramBuf[ramCount++] = PendingData{json, nonce, millis()};
  return true;
}

void sampleAndQueue(const SensorSnapshot &snapshot, int coPeak, int co2Peak,
                    uint8_t coSecond, uint8_t co2Second) {
  const int co = snapshot.coPpm;
  const int co2 = snapshot.co2Ppm;
  const String status = snapshot.coAlarm || snapshot.co2Level == 2 ? "bahaya" :
                        snapshot.co2Level == 1 ? "waspada" : "normal";
  const String buzzer = sensorBridgeBuzzerOn() ? "on" : "off";
  // Posisi jendela hanya ESTIMASI dari timer (tidak ada sensor posisi): ATAS = 0, BAWAH = 50 (setengah),
  // sedang bergerak = null (tidak diketahui).
  const String windowText = snapshot.windowState == 0 ? "0" : (snapshot.windowState == 2 ? "50" : "-");
  const time_t epoch = time(nullptr);
  const bool validTime = epoch >= MIN_VALID_EPOCH;
  // A queued 1 Hz snapshot may be processed after a blocking Wi-Fi/TLS call.
  const long long timestamp = validTime
      ? (long long)epoch - (long long)((millis() - snapshot.sampledAtMs) / 1000U) : 0;
  char epochText[24];
  snprintf(epochText, sizeof(epochText), "%lld", timestamp);
  const String nonce = newNonce();
  const String eventId = alarmActive ? activeEventId : "";
  const String canonical = String("r3|") + DEVICE_ID + "|" + nonce + "|" +
      epochText + "|" + (validTime ? "1" : "0") + "|" + co + "|" +
      co2 + "|" + coPeak + "|" + co2Peak + "|" +
      String(coSecond) + "|" + String(co2Second) + "|" +
      status + "|" + buzzer + "|" + windowText + "|" +
      (eventId.isEmpty() ? "-" : eventId) + (snapshot.simulated ? "|1" : "|0");
  char signature[65];
  if (!hmacHex(canonical.c_str(), signature)) return;
  JsonDocument doc;
  doc["version"] = 3;
  doc["device_id"] = DEVICE_ID;
  doc["nonce"] = nonce;
  doc["timestamp"] = timestamp;
  doc["time_valid"] = validTime;
  doc["co_ppm"] = co;
  doc["co2_ppm"] = co2;
  doc["co_peak_ppm"] = coPeak;
  doc["co2_peak_ppm"] = co2Peak;
  doc["co_peak_second"] = coSecond;
  doc["co2_peak_second"] = co2Second;
  doc["status"] = status;
  doc["buzzer_state"] = buzzer;
  // Posisi tidak diketahui (sedang bergerak) = NULL, bukan 0% palsu.
  if (windowText == "-") doc["window_status"] = nullptr;
  else doc["window_status"] = windowText.toInt();
  if (eventId.isEmpty()) doc["event_id"] = nullptr;
  else doc["event_id"] = eventId;
  // demo = true hanya untuk data simulasi inti (perintah q<ppm>); data sensor nyata selalu false.
  doc["demo"] = snapshot.simulated;   // data simulasi (q<ppm>) SELALU berlabel demo; worker menolaknya kecuali ALLOW_DEMO_READINGS
  doc["signature"] = signature;
  String json;
  serializeJson(doc, json);
  enqueueReading(json, nonce);
}

void publishQueueHead() {
  if (ramCount == 0) return;
  if (!mqtt.connected()) {      // data basi tidak dikirim setelah tersambung lagi
    ramCount = 0; awaitingDataAck = false; pendingNonce = "";
    return;
  }
  while (ramCount > 0 && millis() - ramBuf[0].queuedMs > DATA_MAX_AGE_MS) {
    Serial.println("[DATA] Data terlalu tua tanpa ACK: dibuang");
    ramBuangTertua();
  }
  if (ramCount == 0) return;
  if (awaitingDataAck && millis() - dataLastAttemptMs < DATA_RETRY_MS) return;
  pendingNonce = ramBuf[0].nonce;
  if (mqtt.publish(telemetryTopic.c_str(), ramBuf[0].json.c_str())) {
    awaitingDataAck = true;
    dataLastAttemptMs = millis();
  } else {
    Serial.println("[DATA] Publish gagal; dicoba lagi pada siklus berikutnya.");
  }
}

void publishCommandAck(const String &commandId, const String &alertId, bool success) {
  const String result = success ? "success" : "failed";
  const String canonical = String("cmdack2|") + DEVICE_ID + "|" + commandId +
                           "|" + alertId + "|" + result;
  char signature[65];
  if (!hmacHex(canonical.c_str(), signature)) return;
  JsonDocument doc;
  doc["version"] = 2;
  doc["device_id"] = DEVICE_ID;
  doc["command_id"] = commandId;
  doc["alert_id"] = alertId;
  doc["result"] = result;
  doc["signature"] = signature;
  String json;
  serializeJson(doc, json);
  mqtt.publish(commandAckTopic.c_str(), json.c_str());
}

void publishWindowReceipt(const String &commandId, const String &alertId,
                          const String &action, bool accepted) {
  const String result = accepted ? "received" : "failed";
  const String canonical = String("cmdack3|") + DEVICE_ID + "|" + commandId +
                           "|" + alertId + "|" + action + "|" + result;
  char signature[65];
  if (!hmacHex(canonical.c_str(), signature)) return;
  JsonDocument ack;
  ack["version"] = 3;
  ack["device_id"] = DEVICE_ID;
  ack["command_id"] = commandId;
  ack["alert_id"] = alertId;
  ack["action"] = action;
  ack["result"] = result;
  ack["signature"] = signature;
  String json;
  serializeJson(ack, json);
  mqtt.publish(commandAckTopic.c_str(), json.c_str());
}

void handleCommand(JsonDocument &doc) {
  const int version = doc["version"] | 0;
  if (String(doc["device_id"] | "") != DEVICE_ID) return;
  String action = String(doc["action"] | "");
  const bool isMute = version == 2 && action == "MUTE_BUZZER";
  const bool isWindow = version == 3 &&
      (action == "WINDOW_OPEN" || action == "WINDOW_CLOSE");
  if (!isMute && !isWindow) return;
  String commandId = String(doc["command_id"] | "");
  String alertId = String(doc["alert_id"] | "");
  String signature = String(doc["signature"] | "");
  long long issuedAt = doc["issued_at"] | 0LL;
  const long long now = (long long)time(nullptr);
  if (commandId.length() != 36 || alertId.length() != 36 ||
      now < MIN_VALID_EPOCH || llabs(now - issuedAt) > 120) {
    Serial.println("[COMMAND] ID/waktu tidak valid");
    return;
  }
  char issuedAtText[24];
  snprintf(issuedAtText, sizeof(issuedAtText), "%lld", issuedAt);
  const String canonical = (isMute ? String("cmd2|") : String("cmd3|")) +
      DEVICE_ID + "|" + commandId + "|" + alertId + "|" + action + "|" + issuedAtText;
  if (!signatureMatches(canonical, signature)) {
    Serial.println("[SECURITY] HMAC command invalid");
    return;
  }
  // No alarm / a different alert => old acknowledgement must never mute a new event.
  const bool matchesCurrent = alarmActive && alertId == activeEventId;
  if (isWindow) {
    // Driver belum dipilih: tanda terima HMAC bukan bukti motor bergerak.
    // Alert yang tidak aktif harus ditolak, bahkan bila HMAC valid.
    publishWindowReceipt(commandId, alertId, action, matchesCurrent);
    return;
  }
  bool canMute = matchesCurrent && BUZZER_PIN >= 0;
  // CO2 warnings by themselves do not activate GPIO25 in the original sketch.
  // Repeated commands for an already muted event must remain idempotent.
  canMute = canMute && (sensorBridgeBuzzerOn() || alarmMuted);
  if (canMute) {
    alarmMuted = true;
    refreshBuzzer();
  }
  publishCommandAck(commandId, alertId, canMute);
}

void handleDataAck(JsonDocument &doc) {
  if (!awaitingDataAck || ramCount == 0 || String(doc["device_id"] | "") != DEVICE_ID ||
      (doc["version"] | 0) != 2 || String(doc["result"] | "") != "stored") return;
  const String nonce = String(doc["nonce"] | "");
  if (nonce != ramBuf[0].nonce) return;
  const String canonical = String("dataack2|") + DEVICE_ID + "|" + nonce + "|stored";
  if (!signatureMatches(canonical, String(doc["signature"] | ""))) return;
  ramBuangTertua();
  pendingNonce = "";
  Serial.printf("[ACK DATA] %s tersimpan di DB (menunggu: %u)\n", nonce.c_str(), (unsigned)ramCount);
}

void onMqttMessage(char *topic, byte *payload, unsigned int length) {
  if (length > 700) return;
  JsonDocument doc;
  if (deserializeJson(doc, payload, length)) return;
  if (strcmp(topic, commandTopic.c_str()) == 0) handleCommand(doc);
  else if (strcmp(topic, dataAckTopic.c_str()) == 0) handleDataAck(doc);
}

// Escaping untuk SSID di halaman HTML.
String htmlEscape(const String &text) {
  String escaped;
  for (size_t i = 0; i < text.length(); ++i) {
    switch (text[i]) {
      case '&': escaped += "&amp;"; break;
      case '<': escaped += "&lt;"; break;
      case '>': escaped += "&gt;"; break;
      case '"': escaped += "&quot;"; break;
      case '\'': escaped += "&#39;"; break;
      default: escaped += text[i]; break;
    }
  }
  return escaped;
}

String htmlBegin(const char *title) {
  String html = F("<!doctype html><html lang='id'><head><meta charset='utf-8'>"
      "<meta name='viewport' content='width=device-width,initial-scale=1'>"
      "<style>body{font:16px system-ui,Arial;margin:32px auto;padding:0 18px;"
      "max-width:480px;color:#172b34}input,button{box-sizing:border-box;width:100%;"
      "font:inherit;padding:12px;margin:7px 0 18px;border-radius:8px;"
      "border:1px solid #a7bac0}button{background:#176d75;color:white;border:0}"
      "a{color:#176d75}small{color:#596d73}</style></head><body>");
  html += "<h2>";
  html += title;
  html += "</h2>";
  return html;
}

void sendPortalPage(bool doScan) {
  String html = htmlBegin("AEROS Wi-Fi Setup");
  html += F("<p>Masukkan Wi-Fi 2.4 GHz yang akan digunakan AEROS.</p>"
      "<form action='/save' method='post'>"
      "<label for='ssid'>Nama Wi-Fi (SSID)</label>"
      "<input id='ssid' name='ssid' maxlength='32' required "
      "placeholder='Contoh: WiFi_Rumah' autocomplete='off' list='ssids'>"
      "<label for='password'>Password Wi-Fi</label>"
      "<input id='password' type='password' name='password' maxlength='63' "
      "placeholder='Masukkan password Wi-Fi' autocomplete='new-password'>"
      "<button type='submit'>Simpan dan Hubungkan</button></form>"
      "<p><a href='/scan'>Scan daftar jaringan</a></p>"
      "<small>Setelah disimpan, ESP32 mencoba koneksi maksimal 5 kali "
      "(10 detik per percobaan).</small>");
  if (doScan) {
    showLCD("Scan WiFi...", "Please wait");
    int count = WiFi.scanNetworks(false, true);
    html += "<datalist id='ssids'>";
    for (int i = 0; i < count && i < 40; ++i) {
      html += "<option value=\"" + htmlEscape(WiFi.SSID(i)) + "\"></option>";
    }
    html += "</datalist>";
    WiFi.scanDelete();
    showLCD("PORTAL WIFI ON", WiFi.softAPIP().toString());
  } else {
    html += "<datalist id='ssids'></datalist>";
  }
  html += "</body></html>";
  portalServer.send(200, "text/html; charset=utf-8", html);
}

void handlePortalSave() {
  if (pendingWifiApply) {
    portalServer.send(409, "text/plain", "Konfigurasi sedang diproses.");
    return;
  }
  String ssid = portalServer.arg("ssid");
  String password = portalServer.arg("password");
  ssid.trim();
  if (ssid.length() == 0 || ssid.length() > 32 ||
      (password.length() != 0 && (password.length() < 8 || password.length() > 63))) {
    String html = htmlBegin("Input tidak valid");
    html += F("<p>SSID wajib diisi (maks. 32 byte). Password 8-63 karakter "
              "atau kosong untuk jaringan terbuka.</p><a href='/'>Kembali</a></body></html>");
    portalServer.send(400, "text/html; charset=utf-8", html);
    return;
  }
  candidateSsid = ssid;
  candidatePassword = password;
  wifiFromPortal = true;
  saveWifiOnSuccess = true;
  pendingWifiApply = true;
  submittedAtMs = millis();
  Serial.printf("[PORTAL] POST /save diterima: SSID=%s. Tidak ada percobaan WiFi di handler.\n",
                candidateSsid.c_str());
  showLCD("WiFi tersimpan", "Mulai retry 5x");
  String html = htmlBegin("Konfigurasi diterima");
  html += F("<p>SSID diterima. ESP32 akan mencoba maksimal 5 kali "
            "dan menampilkan hasil pada LCD.</p>"
            "<p>Jika gagal, hotspot AEROS-Setup akan dibuka lagi.</p>"
            "<small>Jangan simpan password pada halaman publik.</small></body></html>");
  portalServer.sendHeader("Connection", "close");
  portalServer.send(200, "text/html; charset=utf-8", html);
}

void registerPortalRoutes() {
  portalServer.on("/", HTTP_GET, []() { sendPortalPage(false); });
  portalServer.on("/wifi", HTTP_GET, []() { sendPortalPage(false); });
  portalServer.on("/scan", HTTP_GET, []() { sendPortalPage(true); });
  portalServer.on("/save", HTTP_POST, handlePortalSave);
  portalServer.onNotFound([]() {
    portalServer.sendHeader("Location", String("http://") + WiFi.softAPIP().toString() + "/", true);
    portalServer.send(302, "text/plain", "AEROS Wi-Fi Setup");
  });
}

void stopPortal() {
  if (mode != Mode::PORTAL) return;
  dnsServer.stop();
  portalServer.stop();
  WiFi.softAPdisconnect(true);
  Serial.println("[PORTAL] AP dan webserver dihentikan.");
}

void startPortal() {
  if (mode == Mode::PORTAL) return;
  if (mqtt.connected()) {
    mqtt.publish(statusTopic.c_str(), "OFFLINE", true);
    mqtt.disconnect();
  }
  WiFi.setAutoReconnect(false);
  WiFi.disconnect(false, false);
  WiFi.mode(WIFI_AP_STA); // STA diperlukan hanya jika user menekan tombol Scan Wi-Fi.
  WiFi.softAPConfig(IPAddress(192, 168, 4, 1), IPAddress(192, 168, 4, 1),
                    IPAddress(255, 255, 255, 0));
  if (!WiFi.softAP(AP_SSID, CONFIG_AP_PASSWORD)) {
    Serial.println("[PORTAL] ERROR: gagal mengaktifkan AP.");
    showLCD("Portal ERROR", "Cek Serial");
    mode = Mode::WIFI_FAILED;
    failedAtMs = millis();
    return;
  }
  dnsServer.start(53, "*", WiFi.softAPIP());
  portalServer.begin();
  pendingWifiApply = false;
  mode = Mode::PORTAL;
  portalStartedMs = millis();
  Serial.printf("[PORTAL] AKTIF: SSID=%s, IP=%s, URL=http://%s\n",
        AP_SSID, WiFi.softAPIP().toString().c_str(), WiFi.softAPIP().toString().c_str());
  showLCD("PORTAL WIFI ON", WiFi.softAPIP().toString());
}

void beginSingleWifiTry() {
  ++tryNumber;
  tryStartedMs = millis();
  // Reset evidence untuk setiap percobaan. Ignorable disconnect akibat reset koneksi
  // tidak dianggap error password karena reason-nya bukan 15/202/204.
  authProblemThisAttempt.store(false);
  lastWiFiDisconnectReason.store(-1);
  // Hindari menghapus kredensial NVS atau mematikan radio antar percobaan.
  WiFi.disconnect(false, false);
  WiFi.mode(WIFI_STA);
  Serial.printf("[WiFi] PERCOBAAN %u/%u; SSID=%s (maks. %lus)\n",
                tryNumber, WIFI_MAX_TRIES, candidateSsid.c_str(),
                (unsigned long)(WIFI_TRY_TIMEOUT_MS / 1000));
  showLCD("WiFi try " + String(tryNumber) + "/5", "Connecting...");
  WiFi.begin(candidateSsid.c_str(), candidatePassword.c_str());
}

void startFiveWifiTries() {
  mode = Mode::WIFI_TRY;
  ntpStarted = false;
  tryNumber = 0;
  authProblemAttempts = 0;
  explicitAuthFailures.store(0);
  WiFi.setAutoReconnect(false);
  beginSingleWifiTry();
}

void saveSuccessfulWifi() {
  if (prefs.begin("aeroswifi", false)) {
    prefs.putString("ssid", candidateSsid);
    prefs.putString("pass", candidatePassword);
    prefs.end();
    Serial.println("[WiFi] Kredensial BERHASIL disimpan ke NVS.");
  }
}

// Scan pada radio 2,4 GHz ESP32; hasilnya berbeda dengan scan laptop yang bisa 5 GHz.
// SSID tersembunyi tidak selalu bisa dikenali dari hasil scan.
ScanResult scanTargetSSID(int &bestRSSI) {
  bestRSSI = -127;
  if (candidateSsid.isEmpty()) return ScanResult::ERROR;
  Serial.printf("[SCAN] Memeriksa SSID: %s\n", candidateSsid.c_str());
  int count = WiFi.scanNetworks(false, true);
  if (count < 0) {
    Serial.printf("[SCAN] Scan gagal (hasil=%d), tidak menyimpulkan SSID hilang.\n", count);
    return ScanResult::ERROR;
  }
  bool found = false;
  for (int i = 0; i < count; ++i) {
    if (WiFi.SSID(i) == candidateSsid) {
      found = true;
      bestRSSI = max(bestRSSI, (int)WiFi.RSSI(i));
      Serial.printf("[SCAN] SSID ditemukan: channel=%ld, RSSI=%ld dBm\n",
                    (long)WiFi.channel(i), (long)WiFi.RSSI(i));
    }
  }
  WiFi.scanDelete();
  if (!found) Serial.println("[SCAN] SSID tidak terdeteksi oleh ESP32 (2.4 GHz).");
  return found ? ScanResult::FOUND : ScanResult::MISSING;
}

// Hanya jadikan kegagalan autentikasi sebagai dugaan kuat password salah jika:
// SSID benar-benar terlihat, dan alasan autentikasi muncul berulang.
// Reason 202 (AUTH_FAIL) lebih spesifik; 15/204 bisa juga karena sinyal buruk.
bool likelyWrongPassword(ScanResult scan, int rssi) {
  if (scan != ScanResult::FOUND) return false;
  if (explicitAuthFailures.load() >= 2) return true;
  return authProblemAttempts >= 2 && rssi >= MIN_RSSI_FOR_AUTH_DIAG_DBM;
}

void waitForHotspotWithLCD(ScanResult scan) {
  mode = Mode::WIFI_RETRY_WAIT;
  retryWaitStartedMs = millis();
  if (scan == ScanResult::MISSING) {
    Serial.println("[WiFi] SSID TIDAK DITEMUKAN. Kredensial tetap disimpan. Retry 30s.");
    showLCD("HOTSPOT TDK ADA", "Retry 30 detik");
  } else if (scan == ScanResult::ERROR) {
    Serial.println("[WiFi] Scan gagal; tidak bisa memastikan sebab. Retry 30s.");
    showLCD("Scan WiFi gagal", "Retry 30 detik");
  } else {
    Serial.println("[WiFi] SSID ADA tapi koneksi gagal; periksa sinyal/keamanan. Retry 30s.");
    showLCD("WiFi gagal konek", "Retry 30 detik");
  }
}

void processWifiTries() {
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("[WiFi] BERHASIL %u/%u, IP=%s\n", tryNumber, WIFI_MAX_TRIES,
                  WiFi.localIP().toString().c_str());
    if (saveWifiOnSuccess) {
      saveSuccessfulWifi();
      saveWifiOnSuccess = false;
    }
    candidatePassword = "";
    candidateSsid = "";
    wifiFromPortal = false;
    mode = Mode::NORMAL;
    // Semua reconnect dikelola state machine AEROS saja.
    WiFi.setAutoReconnect(false);
    showLCD("WiFi CONNECTED", WiFi.localIP().toString());
    mqttLastAttemptMs = millis() - RETRY_MQTT_MS;
    ntpStarted = false;
    return;
  }
  if (millis() - tryStartedMs < WIFI_TRY_TIMEOUT_MS) return;
  Serial.printf("[WiFi] GAGAL %u/%u (status=%d, reason=%d)\n", tryNumber,
                WIFI_MAX_TRIES, (int)WiFi.status(), lastWiFiDisconnectReason.load());
  if (authProblemThisAttempt.exchange(false)) ++authProblemAttempts;
  if (tryNumber < WIFI_MAX_TRIES) {
    beginSingleWifiTry();
    return;
  }
  // Pastikan ESP32 benar-benar tidak connected sebelum scan; scan SSID via 2.4 GHz.
  WiFi.disconnect(false, false);
  int rssi;
  ScanResult scan = scanTargetSSID(rssi);
  if (likelyWrongPassword(scan, rssi)) {
    Serial.printf("[WiFi] Dugaan kuat AUTENTIKASI GAGAL (%u percobaan terkait auth, "
                  "%d AUTH_FAIL, RSSI=%d). Buka portal untuk koreksi password.\n",
                  authProblemAttempts, explicitAuthFailures.load(), rssi);
    showLCD("CEK PASSWORD!", "Buka portal...");
    // Jangan hapus NVS lama: kredensial lama hanya diganti setelah koneksi baru sukses.
    candidateSsid = "";
    candidatePassword = "";
    wifiFromPortal = false;
    saveWifiOnSuccess = false;
    mode = Mode::WIFI_FAILED;
    failedAtMs = millis();
  } else {
    // Tidak ditemukan != password salah. AP mati/berubah band/hidden/sinyal lemah.
    // Credential tetap disimpan; jangan buka portal otomatis.
    waitForHotspotWithLCD(scan);
  }
}

void handleButton() {
  if (!portalRequested.exchange(false)) return;
  if (mode == Mode::PORTAL) {
    Serial.println("[BUTTON] Portal sudah aktif.");
    return;
  }
  Serial.println("[BUTTON] Hold 5s terdeteksi, membuka portal...");
  // Catatan: bila MQTT/TLS sedang blocking, event ini dieksekusi setelah call selesai.
  startPortal();
}

void startWiFiOnBoot() {
  if (prefs.begin("aeroswifi", true)) {
    candidateSsid = prefs.getString("ssid", "");
    candidatePassword = prefs.getString("pass", "");
    prefs.end();
  }
  if (candidateSsid.isEmpty() && strlen(WIFI_SSID) && strncmp(WIFI_SSID, "GANTI_", 6) != 0) {
    candidateSsid = WIFI_SSID;
    candidatePassword = WIFI_PASSWORD;
    saveWifiOnSuccess = true;  // Fallback baru disimpan jika berhasil.
  }
  wifiFromPortal = false;
  if (candidateSsid.isEmpty()) {
    Serial.println("[WiFi] Belum ada kredensial tersimpan. Buka portal.");
    startPortal();
  } else {
    Serial.printf("[WiFi] Boot: coba SSID %s dengan maksimal 5 percobaan.\n", candidateSsid.c_str());
    startFiveWifiTries();
  }
}

void connectMqtt() {
  if (mqtt.connected()) return;
  if (millis() - mqttLastAttemptMs < RETRY_MQTT_MS) return;
  mqttLastAttemptMs = millis();
  Serial.println("[MQTT] Connect TLS ke HiveMQ Cloud ...");
  showLCD("MQTT connecting", "TLS active");
  bool ok = mqtt.connect(mqttClientId.c_str(), MQTT_USERNAME, MQTT_PASSWORD,
                         statusTopic.c_str(), 1, true, "OFFLINE");
  if (!ok) {
    Serial.printf("[MQTT] GAGAL (state=%d)\n", mqtt.state());
    showLCD("MQTT gagal", "Retry 5 detik");
    return;
  }
  Serial.println("[MQTT] CONNECTED");
  if (!mqtt.subscribe(commandTopic.c_str(), 1))
    Serial.println("[MQTT] Gagal subscribe command");
  if (!mqtt.subscribe(dataAckTopic.c_str(), 1))
    Serial.println("[MQTT] Gagal subscribe data ACK");
  if (mqtt.publish(statusTopic.c_str(), "ONLINE", true))
    Serial.println("[BIRTH] ONLINE berhasil dikirim (retained)");
  else
    Serial.println("[BIRTH] GAGAL publish ONLINE");
  showLCD("AEROS ONLINE", "MQTT connected");
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\n=== AEROS ESP32 | Smart WiFi Diagnostic | Portal GPIO14 ===");
  initLCD();
  // Inti sensor, alarm, dan jendela dimulai PERTAMA: harus tetap jalan walau konfigurasi, flash, atau Wi-Fi bermasalah.
  if (!sensorBridgeStart()) {
    Serial.println("[FATAL] Gagal membuat task sensor. Pembacaan real nonaktif.");
  } else {
    Serial.println("[SENSOR] Inti firmware AEROS v2.0 (CO2, alarm, jendela) berjalan di task terpisah");
  }
  Serial.println("[DATA] Mode ONLINE: tanpa antrean offline; data hanya dikirim saat MQTT tersambung. Alarm dan jendela tetap jalan tanpa internet.");
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  BaseType_t taskStatus = xTaskCreatePinnedToCore(
      portalButtonTask, "AEROS_button", 2048, nullptr, 2, nullptr, 1);
  if (taskStatus != pdPASS) {
    Serial.println("[ERROR] Gagal membuat task tombol GPIO14!");
  }
  if (!settingsValid()) {
    // Tidak berhenti total: inti sensor sudah jalan. Jaringan saja yang tidak dimulai.
    Serial.println("[PERINGATAN] Konfigurasi jaringan tidak lengkap: Wi-Fi dan MQTT tidak dimulai. Alarm tetap jalan.");
    mode = Mode::WAIT_BUTTON;
    return;
  }
  WiFi.persistent(false);
  WiFi.onEvent(onWiFiEvent);
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false); // Diagnostik beacon timeout; butuh suplai daya stabil.
  WiFi.setAutoReconnect(false);
  mqttClientId = String("aeros-") + WiFi.macAddress();
  mqttClientId.replace(":", "");
  statusTopic = String("aeros/") + DEVICE_ID + "/status";
  telemetryTopic = String("aeros/") + DEVICE_ID + "/telemetry";
  commandTopic = String("aeros/") + DEVICE_ID + "/cmd";
  commandAckTopic = String("aeros/") + DEVICE_ID + "/cmd/ack";
  dataAckTopic = String("aeros/") + DEVICE_ID + "/telemetry/ack";
  secureClient.setCACert(ROOT_CA);
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(onMqttMessage);
  mqtt.setBufferSize(1024);
  mqtt.setKeepAlive(30);
  mqtt.setSocketTimeout(5); // Timeout respons MQTT; BUKAN deadline total TLS.
  secureClient.setTimeout(5000); // Timeout stream untuk uji coba.
  registerPortalRoutes();
  Serial.println("[BUTTON] Tahan GPIO14 ke GND 5 detik untuk buka portal.");
  startWiFiOnBoot();
}

void loop() {
  handleButton();
  // Drain real 1 Hz readings even after temporary network blocking.
  SensorSnapshot current;
  while (sensorBridgePop(current)) {
    trackSensorAlarm(current);
    ++sampleWindowCount;
    if (sampleWindowCount == 1 || current.coPpm > coWindowPeak) {
      coWindowPeak = current.coPpm;
      coPeakSecond = sampleWindowCount;
    }
    if (sampleWindowCount == 1 || current.co2Ppm > co2WindowPeak) {
      co2WindowPeak = current.co2Ppm;
      co2PeakSecond = sampleWindowCount;
    }
    if (sampleWindowCount == SAMPLES_PER_TELEMETRY) {
      sampleAndQueue(current, coWindowPeak, co2WindowPeak, coPeakSecond, co2PeakSecond);
      sampleWindowCount = 0;
    }
  }
  if (mode == Mode::PORTAL) {
    dnsServer.processNextRequest();
    portalServer.handleClient();
    if (pendingWifiApply && millis() - submittedAtMs >= POST_RESPONSE_GRACE_MS) {
      pendingWifiApply = false;
      stopPortal();
      startFiveWifiTries();
    } else if (!pendingWifiApply && millis() - portalStartedMs >= PORTAL_TIMEOUT_MS) {
      Serial.println("[PORTAL] Timeout 5 menit; buka ulang dengan tombol.");
      stopPortal();
      mode = Mode::WAIT_BUTTON;
      showLCD("Portal timeout", "Hold btn 5s");
    }
    delay(5);
    return;
  }
  if (mode == Mode::WIFI_TRY) {
    processWifiTries();
    delay(20);
    return;
  }
  if (mode == Mode::WIFI_FAILED) {
    // Password diduga salah setelah verifikasi reason + scan -> portal otomatis.
    if (millis() - failedAtMs > 2500) startPortal();
    delay(20);
    return;
  }
  if (mode == Mode::WIFI_RETRY_WAIT) {
    // SSID belum terdeteksi atau penyebab lain: retry satu batch 5 lagi tanpa portal.
    if (millis() - retryWaitStartedMs >= WIFI_RETRY_PAUSE_MS) {
      Serial.println("[WiFi] Mulai siklus retry berikutnya menggunakan kredensial sebelumnya.");
      startFiveWifiTries();
    }
    delay(20);
    return;
  }
  if (mode == Mode::WAIT_BUTTON) {
    // Portal timeout: tidak aktifkan kembali sampai tombol ditahan.
    delay(20);
    return;
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WiFi] Jaringan normal terputus. Mencoba lagi maks. 5 kali.");
    if (prefs.begin("aeroswifi", true)) {
      candidateSsid = prefs.getString("ssid", "");
      candidatePassword = prefs.getString("pass", "");
      prefs.end();
    }
    if (candidateSsid.isEmpty()) {
      candidateSsid = WIFI_SSID;
      candidatePassword = WIFI_PASSWORD;
    }
    wifiFromPortal = false;
    startFiveWifiTries();
    return;
  }
  if (!ntpStarted) {
    Serial.printf("[WiFi] CONNECTED; IP=%s\n", WiFi.localIP().toString().c_str());
    configTime(0, 0, "pool.ntp.org", "time.google.com");
    ntpStarted = true;
  }
  if (time(nullptr) < MIN_VALID_EPOCH) {
    if (millis() - ntpLastLogMs > 5000) {
      Serial.println("[NTP] Menunggu waktu valid untuk TLS...");
      showLCD("Sync NTP", "Please wait");
      ntpLastLogMs = millis();
    }
    delay(50);
    return;
  }
  connectMqtt();
  if (!mqtt.connected()) {
    delay(50);
    return;
  }
  mqtt.loop();
  publishQueueHead();
}
