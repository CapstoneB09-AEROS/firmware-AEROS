#pragma once
// Pin PCB AEROS dengan ESP32-C3 (firmware v2.0.1). Satu tempat untuk semua nomor pin.
// -1 = belum ditentukan / tidak dipasang: pin itu dilewati, tidak ada keluaran dan tidak ada tombol.
constexpr int AEROS_PIN_SDA    = 4;    // I2C SDA (LCD dan ADS1115)
constexpr int AEROS_PIN_SCL    = 5;    // I2C SCL
constexpr int AEROS_PIN_CO2_RX = 7;    // RX C3 <- TX sensor MH-Z19C
constexpr int AEROS_PIN_CO2_TX = 6;    // TX C3 -> RX sensor MH-Z19C
constexpr int AEROS_PIN_JENDELA = 3;   // sinyal relay jendela (dulu GPIO26)
constexpr int AEROS_PIN_BUZZER = -1;   // BELUM ADA: isi dengan GPIO buzzer di PCB (dulu GPIO27)
constexpr int AEROS_PIN_TOMBOL = -1;   // BELUM ADA: tombol portal Wi-Fi (dulu GPIO14); -1 = tidak dipasang
